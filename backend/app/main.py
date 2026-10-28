import os, uuid
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import FRONTEND_ORIGIN, UPLOAD_DIR, MAX_UPLOAD_BYTES, ALLOWED_IMAGE_TYPES
from .database import init_db, save_analysis, list_analyses
from .ai import generate_json
from .schemas import ValuationRequest, PlanRequest, DailyRequest

os.makedirs(UPLOAD_DIR, exist_ok=True)
app = FastAPI(title="Multimodal Construction Intelligence Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN,"http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
@app.on_event("startup")
def startup(): init_db()
@app.get("/api/health")
def health(): return {"status":"ok","service":"construction-intelligence-api"}
@app.get("/api/analyses")
def analyses(): return list_analyses(50)
@app.get("/api/dashboard")
def dashboard():
    items=list_analyses(100)
    return {"total_analyses":len(items),"safety_reviews":sum(x["kind"]=="site_safety" for x in items),
            "crack_reviews":sum(x["kind"]=="crack" for x in items),"planning_reports":sum(x["kind"]=="plan" for x in items),"recent":items[:5]}

async def read_image(file: UploadFile):
    if file.content_type not in ALLOWED_IMAGE_TYPES: raise HTTPException(415,"Upload JPG, PNG, or WEBP.")
    data=await file.read()
    if not data: raise HTTPException(400,"Image is empty.")
    if len(data)>MAX_UPLOAD_BYTES: raise HTTPException(413,"Maximum image size is 8 MB.")
    ext={"image/jpeg":".jpg","image/png":".png","image/webp":".webp"}[file.content_type]
    name=f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(UPLOAD_DIR,name),"wb") as f: f.write(data)
    return data,name

@app.post("/api/analyze/site-safety")
async def site_safety(file: UploadFile=File(...), site_context: str=Form(default="")):
    data,name=await read_image(file)
    fallback={"headline":"Preliminary site safety review","risk_level":"Review required",
      "observations":["Confirm workers use task-appropriate PPE.","Check access routes, edge protection, and housekeeping.","Verify equipment and materials are secured and exclusion zones are marked."],
      "recommended_actions":["Ask the site supervisor to inspect the area in person.","Log each hazard with an owner and target date.","Follow the approved site safety plan and local rules."],
      "limitations":"Demo mode provides a general checklist and does not inspect image pixels."}
    prompt=f"Review this construction photo for visible safety concerns. Context: {site_context}. Return JSON keys headline, risk_level, observations array, recommended_actions array, limitations. Be cautious and do not certify compliance."
    result,mode=generate_json(prompt,fallback,data,file.content_type)
    result.update({"mode":mode,"image_url":f"/uploads/{name}","site_context":site_context})
    return save_analysis("site_safety","Site safety review",result["headline"],result)

@app.post("/api/analyze/crack")
async def crack_review(file: UploadFile=File(...), context: str=Form(default="")):
    data,name=await read_image(file)
    fallback={"headline":"Preliminary crack observation","severity":"Unknown — professional inspection required",
      "observations":["Demo mode cannot determine crack depth, movement, width, or structural significance.","Photograph with a ruler for scale and record location, length, and date.","Track changes and note water ingress or displacement."],
      "recommended_actions":["Arrange a qualified structural engineer inspection for widening, stepped, diagonal, or displaced cracks.","Do not conceal a potentially structural crack before assessment."],
      "limitations":"No automated structural diagnosis is performed in demo mode."}
    prompt=f"Review this construction photo for possible cracks. Context: {context}. Return JSON keys headline, severity, observations array, recommended_actions array, limitations. Never diagnose structural safety from a photo."
    result,mode=generate_json(prompt,fallback,data,file.content_type)
    result.update({"mode":mode,"image_url":f"/uploads/{name}","context":context})
    return save_analysis("crack","Crack observation",result["headline"],result)

@app.post("/api/analyze/valuation")
def valuation(req: ValuationRequest):
    base=req.area_sqft*req.rate_per_sqft
    age_factor=max(.55,1-req.age_years*.008)
    cond={"Excellent":1.08,"Good":1.0,"Fair":.9,"Needs repair":.75}.get(req.condition,1.0)
    estimate=round(base*age_factor*cond)
    fallback={"headline":"Indicative property value estimate","estimated_value_inr":estimate,
      "range_inr":{"low":round(estimate*.9),"high":round(estimate*1.1)},
      "calculation":f"{req.area_sqft:,.0f} sq ft × ₹{req.rate_per_sqft:,.0f}/sq ft, adjusted for age and condition.",
      "factors_to_verify":["Recent comparable sales","Exact location and access","Title, approvals and encumbrances","Construction quality and maintenance"],
      "limitations":"Rule-of-thumb estimate only, not a formal appraisal or investment advice."}
    prompt=f"Comment on this real estate estimate. Inputs: {req.model_dump()}. Arithmetic estimate INR {estimate}. Return JSON keys headline, estimated_value_inr, range_inr low/high, calculation, factors_to_verify array, limitations. Do not invent live market data."
    result,mode=generate_json(prompt,fallback); result.update({"mode":mode,"inputs":req.model_dump()})
    return save_analysis("valuation",f"Valuation — {req.location}",result["headline"],result)

@app.post("/api/analyze/plan")
def plan(req: PlanRequest):
    fallback={"headline":f"Draft delivery plan: {req.project_name}","phases":[
      {"phase":"Requirements, survey & approvals","duration":"10% of schedule","tasks":["Confirm scope, survey, drawings, permits and responsibilities."]},
      {"phase":"Design & procurement","duration":"15% of schedule","tasks":["Coordinate drawings, quotations and long-lead materials."]},
      {"phase":"Site preparation & foundation","duration":"20% of schedule","tasks":["Set out site and complete approved excavation and foundation works."]},
      {"phase":"Structure & envelope","duration":"30% of schedule","tasks":["Sequence structure, masonry and weatherproofing with inspection hold points."]},
      {"phase":"Services & finishes","duration":"20% of schedule","tasks":["Install and test services, complete finishes and resolve defects."]},
      {"phase":"Handover","duration":"5% of schedule","tasks":["Complete quality checks, as-builts and owner handover."]}],
      "milestones":["Approved drawings and permits","Foundation sign-off","Structure topped out","Services testing","Practical completion"],
      "risks":["Weather delays","Material cost or delivery changes","Design coordination gaps","Rework from missed inspections"],
      "next_steps":["Validate durations and costs with the project team.","Add dependencies, owners, contingency and cost breakdown."],
      "limitations":"Planning template only; validate scope, schedule, cost and compliance with qualified professionals."}
    prompt=f"Create high-level construction plan for {req.model_dump()}. Return JSON keys headline, phases objects phase/duration/tasks, milestones array, risks array, next_steps array, limitations. Do not imply professional validation."
    result,mode=generate_json(prompt,fallback); result.update({"mode":mode,"inputs":req.model_dump()})
    return save_analysis("plan",f"Plan — {req.project_name}",result["headline"],result)

@app.post("/api/analyze/daily-assistance")
def daily(req: DailyRequest):
    fallback={"headline":"Daily site briefing","answer":f"For {req.work_stage.lower()}, hold a toolbox talk, confirm approved drawings and permits, inspect access and PPE, and assign a supervisor. Reported weather: {req.weather}.",
      "checklist":["Review planned work and method statement","Confirm PPE and equipment checks","Check access, housekeeping and exclusion zones","Record hazards and corrective actions","Stop work and escalate imminent danger"],
      "weather_advice":"No live weather data is connected. Check a trusted local forecast before lifting, working at height, pouring concrete, or outdoor electrical work.",
      "follow_up":"Share the task, materials, site conditions and local requirements for a more tailored checklist.",
      "limitations":"General guidance only; follow approved procedures and competent professional advice."}
    prompt=f"Answer construction site question safely: {req.model_dump()}. Return JSON keys headline, answer, checklist array, weather_advice, follow_up, limitations. Do not claim live weather access."
    result,mode=generate_json(prompt,fallback); result.update({"mode":mode,"inputs":req.model_dump()})
    return save_analysis("daily_assistance","Daily site assistance",result["headline"],result)

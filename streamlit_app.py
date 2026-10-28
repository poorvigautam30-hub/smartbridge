import os
import streamlit as st

try:
    os.environ.setdefault("GEMINI_API_KEY", str(st.secrets.get("GEMINI_API_KEY", "")))
except Exception:
    pass

from backend.app.ai import generate_json
from backend.app.database import init_db, list_analyses, save_analysis
from backend.app.schemas import DailyRequest, PlanRequest, ValuationRequest

st.set_page_config(page_title="BuildSense | Construction Intelligence", layout="wide")
init_db()

st.title("BuildSense")
st.caption("Multimodal construction intelligence - Advisory prototype")
st.warning("This prototype is not a certified engineering, safety, legal, or appraisal tool. Have qualified professionals verify decisions. Demo mode does not interpret image pixels.")

page = st.sidebar.radio("Workspace", ["Overview", "Site Safety", "Crack Observation", "Property Valuation", "Project Planning", "Daily Site Assistant", "Report History"])


def show_result(result):
    st.subheader(result.get("headline", result.get("title", "Analysis report")))
    if result.get("mode"):
        st.caption("Gemini AI" if result["mode"] == "gemini" else "Demo mode")
    st.json(result.get("result", result))


def persist(kind, title, result):
    item = save_analysis(kind, title, result.get("headline", title), result)
    st.session_state["last_result"] = item
    st.success("Report saved to this app's history.")


def image_workflow(kind):
    safety = kind == "site_safety"
    title = "Site Safety Review" if safety else "Crack Observation"
    with st.form("image_form"):
        image = st.file_uploader("Upload a site image (JPG, PNG, WEBP; max 8 MB)", type=["jpg", "jpeg", "png", "webp"])
        context = st.text_area("Site context" if safety else "Crack context")
        submitted = st.form_submit_button("Generate review", type="primary")
    if submitted:
        if image is None:
            st.error("Choose an image first.")
        elif image.size > 8 * 1024 * 1024:
            st.error("The maximum image size is 8 MB.")
        else:
            data = image.getvalue()
            if safety:
                fallback = {"headline":"Preliminary site safety review", "risk_level":"Review required", "observations":["Confirm workers use task-appropriate PPE.","Check access routes, edge protection, and housekeeping.","Verify equipment and materials are secured and exclusion zones are marked."], "recommended_actions":["Ask the site supervisor to inspect the area in person.","Log each hazard with an owner and target date.","Follow the approved site safety plan and local rules."], "limitations":"Demo mode provides a general checklist and does not inspect image pixels."}
                prompt = f"Review this construction photo for visible safety concerns. Context: {context}. Return JSON keys headline, risk_level, observations array, recommended_actions array, limitations. Be cautious and do not certify compliance."
            else:
                fallback = {"headline":"Preliminary crack observation", "severity":"Unknown - professional inspection required", "observations":["Demo mode cannot determine crack depth, movement, width, or structural significance.","Photograph with a ruler for scale and record location, length, and date.","Track changes and note water ingress or displacement."], "recommended_actions":["Arrange a qualified structural engineer inspection for widening, stepped, diagonal, or displaced cracks.","Do not conceal a potentially structural crack before assessment."], "limitations":"No automated structural diagnosis is performed in demo mode."}
                prompt = f"Review this construction photo for possible cracks. Context: {context}. Return JSON keys headline, severity, observations array, recommended_actions array, limitations. Never diagnose structural safety from a photo."
            with st.spinner("Preparing your review-"):
                result, mode = generate_json(prompt, fallback, data, image.type or "image/jpeg")
            result.update({"mode": mode, "site_context" if safety else "context": context})
            persist(kind, title, result)
            st.image(data, caption=image.name, use_container_width=True)
    if st.session_state.get("last_result"):
        show_result(st.session_state["last_result"])


if page == "Overview":
    reports = list_analyses(100)
    st.header("Your site, with more insight")
    st.write("Review site photos, organize observations, draft project plans, estimate value from your own assumptions, and prepare field checklists.")
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Total reports", "Safety reviews", "Crack reviews", "Planning reports"], [len(reports), sum(x["kind"] == "site_safety" for x in reports), sum(x["kind"] == "crack" for x in reports), sum(x["kind"] == "plan" for x in reports)]):
        col.metric(label, value)
    st.subheader("Recent activity")
    if reports:
        st.dataframe([{"Date": x["created_at"], "Type": x["kind"], "Title": x["title"], "Summary": x["summary"]} for x in reports[:10]], use_container_width=True, hide_index=True)
    else:
        st.info("Your saved reports will appear here.")
elif page == "Site Safety":
    st.header(page)
    image_workflow("site_safety")
elif page == "Crack Observation":
    st.header(page)
    image_workflow("crack")
elif page == "Property Valuation":
    st.header(page)
    with st.form("valuation"):
        location = st.text_input("Location", placeholder="Indore, Madhya Pradesh")
        property_type = st.text_input("Property type", "Residential apartment")
        c1, c2 = st.columns(2)
        area = c1.number_input("Built-up area (sq ft)", min_value=1.0, value=1000.0)
        rate = c2.number_input("Assumed rate (? / sq ft)", min_value=1.0, value=5000.0)
        c3, c4 = st.columns(2)
        age = c3.number_input("Property age (years)", min_value=0, max_value=300, value=0)
        condition = c4.selectbox("Condition", ["Excellent", "Good", "Fair", "Needs repair"])
        submitted = st.form_submit_button("Generate indicative estimate", type="primary")
    if submitted:
        try:
            req = ValuationRequest(location=location, property_type=property_type, area_sqft=area, rate_per_sqft=rate, age_years=age, condition=condition)
            estimate = round(req.area_sqft * req.rate_per_sqft * max(.55, 1 - req.age_years * .008) * {"Excellent":1.08,"Good":1.0,"Fair":.9,"Needs repair":.75}.get(req.condition,1.0))
            fallback = {"headline":"Indicative property value estimate", "estimated_value_inr":estimate, "range_inr":{"low":round(estimate*.9),"high":round(estimate*1.1)}, "calculation":f"{req.area_sqft:,.0f} sq ft - ?{req.rate_per_sqft:,.0f}/sq ft, adjusted for age and condition.", "factors_to_verify":["Recent comparable sales","Exact location and access","Title, approvals and encumbrances","Construction quality and maintenance"], "limitations":"Rule-of-thumb estimate only, not a formal appraisal or investment advice."}
            result, mode = generate_json(f"Comment on this real estate estimate. Inputs: {req.model_dump()}. Arithmetic estimate INR {estimate}. Return JSON keys headline, estimated_value_inr, range_inr low/high, calculation, factors_to_verify array, limitations. Do not invent live market data.", fallback)
            result.update({"mode": mode, "inputs": req.model_dump()})
            persist("valuation", f"Valuation - {req.location}", result)
        except Exception as exc:
            st.error(str(exc))
    if st.session_state.get("last_result"):
        show_result(st.session_state["last_result"])
elif page == "Project Planning":
    st.header(page)
    with st.form("planning"):
        project_name = st.text_input("Project name")
        c1, c2 = st.columns(2)
        project_type = c1.selectbox("Project type", ["Residential", "Commercial", "Industrial", "Infrastructure", "Renovation"])
        site_area = c2.number_input("Site area (sq ft)", min_value=1.0, value=1000.0)
        c3, c4, c5 = st.columns(3)
        floors = c3.number_input("Floors", min_value=1, max_value=150, value=2)
        months = c4.number_input("Duration (months)", min_value=1, max_value=240, value=12)
        budget = c5.number_input("Budget (?)", min_value=1.0, value=1000000.0)
        notes = st.text_area("Project notes")
        submitted = st.form_submit_button("Generate project plan", type="primary")
    if submitted:
        try:
            req = PlanRequest(project_name=project_name, project_type=project_type, site_area_sqft=site_area, floors=floors, target_months=months, budget_inr=budget, notes=notes)
            fallback = {"headline":f"Draft delivery plan: {req.project_name}", "phases":[{"phase":"Requirements, survey & approvals","duration":"10% of schedule","tasks":["Confirm scope, survey, drawings, permits and responsibilities."]},{"phase":"Design & procurement","duration":"15% of schedule","tasks":["Coordinate drawings, quotations and long-lead materials."]},{"phase":"Site preparation & foundation","duration":"20% of schedule","tasks":["Set out site and complete approved excavation and foundation works."]},{"phase":"Structure & envelope","duration":"30% of schedule","tasks":["Sequence structure, masonry and weatherproofing with inspection hold points."]},{"phase":"Services & finishes","duration":"20% of schedule","tasks":["Install and test services, complete finishes and resolve defects."]},{"phase":"Handover","duration":"5% of schedule","tasks":["Complete quality checks, as-builts and owner handover."]}], "milestones":["Approved drawings and permits","Foundation sign-off","Structure topped out","Services testing","Practical completion"], "risks":["Weather delays","Material cost or delivery changes","Design coordination gaps","Rework from missed inspections"], "next_steps":["Validate durations and costs with the project team.","Add dependencies, owners, contingency and cost breakdown."], "limitations":"Planning template only; validate scope, schedule, cost and compliance with qualified professionals."}
            result, mode = generate_json(f"Create high-level construction plan for {req.model_dump()}. Return JSON keys headline, phases objects phase/duration/tasks, milestones array, risks array, next_steps array, limitations. Do not imply professional validation.", fallback)
            result.update({"mode": mode, "inputs": req.model_dump()})
            persist("plan", f"Plan - {req.project_name}", result)
        except Exception as exc:
            st.error(str(exc))
    if st.session_state.get("last_result"):
        show_result(st.session_state["last_result"])
elif page == "Daily Site Assistant":
    st.header(page)
    with st.form("daily"):
        question = st.text_area("Your question", placeholder="What should we check before pouring concrete today?")
        c1, c2 = st.columns(2)
        city = c1.text_input("City / location")
        weather = c2.text_input("Reported weather", "Not provided")
        stage = st.selectbox("Work stage", ["General site work","Excavation","Foundation","Concrete pouring","Working at height","Electrical work","Finishing","Inspection and handover"])
        submitted = st.form_submit_button("Get site guidance", type="primary")
    st.info("No live weather feed is connected. Verify current conditions against a trusted local forecast.")
    if submitted:
        try:
            req = DailyRequest(question=question, city=city, weather=weather, work_stage=stage)
            fallback = {"headline":"Daily site briefing", "answer":f"For {req.work_stage.lower()}, hold a toolbox talk, confirm approved drawings and permits, inspect access and PPE, and assign a supervisor. Reported weather: {req.weather}.", "checklist":["Review planned work and method statement","Confirm PPE and equipment checks","Check access, housekeeping and exclusion zones","Record hazards and corrective actions","Stop work and escalate imminent danger"], "weather_advice":"No live weather data is connected. Check a trusted local forecast before lifting, working at height, pouring concrete, or outdoor electrical work.", "follow_up":"Share the task, materials, site conditions and local requirements for a more tailored checklist.", "limitations":"General guidance only; follow approved procedures and competent professional advice."}
            result, mode = generate_json(f"Answer construction site question safely: {req.model_dump()}. Return JSON keys headline, answer, checklist array, weather_advice, follow_up, limitations. Do not claim live weather access.", fallback)
            result.update({"mode": mode, "inputs": req.model_dump()})
            persist("daily_assistance", "Daily site assistance", result)
        except Exception as exc:
            st.error(str(exc))
    if st.session_state.get("last_result"):
        show_result(st.session_state["last_result"])
    st.caption("Guidance is general and does not replace approved procedures or competent professional advice.")
elif page == "Report History":
    st.header(page)
    reports = list_analyses(100)
    if reports:
        selected = st.selectbox("Select a report", reports, format_func=lambda x: f"{x['created_at']} - {x['title']}")
        show_result(selected)
    else:
        st.info("No saved reports yet. Complete a workflow to create one.")


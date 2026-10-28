import os
import streamlit as st

try:
    os.environ.setdefault("GEMINI_API_KEY", str(st.secrets.get("GEMINI_API_KEY", "")))
except Exception:
    pass

from backend.app.ai import generate_json
from backend.app.database import init_db, list_analyses, save_analysis
from backend.app.schemas import DailyRequest, PlanRequest, ValuationRequest

st.set_page_config(page_title="BuildSense | Construction Intelligence", page_icon="B", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
:root { font-family: 'DM Sans', sans-serif; color: #17243b; }
[data-testid="stAppViewContainer"] { background: #f5f7fb; color: #17243b; }
[data-testid="stHeader"] { background: rgba(245,247,251,.92); }
[data-testid="stSidebar"] { background: #101d3b; border-right: 0; }
[data-testid="stSidebar"] * { color: #d8e1f2; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #8da3ca; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { border-radius: 9px; padding: 8px 10px; font-weight: 600; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: #243b6b; }
[data-testid="stSidebar"] [data-testid="stRadio"] [data-checked="true"] + div { color: #fff; }
.block-container { max-width: 1440px; padding: 1.8rem 2.2rem 2rem; }
h1,h2,h3,h4 { font-family: 'Manrope','DM Sans',sans-serif !important; color: #17243b !important; letter-spacing: -.35px; }
h1 { font-weight: 800 !important; font-size: 2rem !important; }
h2 { font-weight: 800 !important; }
p, label, [data-testid="stMarkdownContainer"] { color: #53627a; }
.brand { display:flex; align-items:center; gap:11px; padding: 4px 4px 28px; }
.brand-badge { display:grid; place-items:center; width:38px; height:38px; background:#2b65ed; border-radius:11px; color:white; font-weight:800; }
.brand-name { color:white; font:800 16px Manrope,sans-serif; letter-spacing:1px; }
.brand-sub { color:#8da3ca; font-size:8px; letter-spacing:1px; margin-top:3px; }
.nav-caption,.eyebrow { color:#7892bc; text-transform:uppercase; font-size:10px; font-weight:700; letter-spacing:1.4px; }
.eyebrow { color:#4774d8; margin:2px 0 7px; }
.topline { display:flex; justify-content:space-between; align-items:center; color:#8390a5; font-size:12px; margin:0 0 25px; padding:0 0 15px; border-bottom:1px solid #e5eaf2; }
.chip { display:inline-flex; background:#fff; border:1px solid #e6eaf2; border-radius:9px; padding:8px 12px; color:#64738c; }
.hero { display:grid; grid-template-columns:1.04fr .96fr; min-height:265px; border-radius:17px; overflow:hidden; color:#fff; background:linear-gradient(112deg,#14284c,#214b93); margin:20px 0 28px; box-shadow:0 16px 35px #15294c18; }
.hero-copy { padding:30px 34px; }
.hero .eyebrow { color:#b5cdf5; }
.hero h2 { color:#fff !important; font-size:30px !important; line-height:1.2; margin:16px 0 10px; }
.hero h2 em { color:#9bc2ff; font-style:normal; }
.hero p { color:#c8d8f3; max-width:390px; font-size:13px; }
.hero-art { display:flex; align-items:end; justify-content:center; gap:14px; padding:40px 20px 0; background:radial-gradient(ellipse at 70% 55%,#5f9bfa55,transparent 60%), linear-gradient(90deg,transparent 49%,#ffffff0b 50%); }
.tower { width:92px; height:150px; border:1px solid #c1d9ff; background:repeating-linear-gradient(0deg,transparent 0 19px,#d7e8ffbb 20px 30px),linear-gradient(135deg,#8ab7ff,#365d9d); box-shadow:10px 8px 0 #14284c; }
.tower.small { width:70px; height:105px; background:repeating-linear-gradient(0deg,transparent 0 16px,#d7e8ffbb 17px 25px),linear-gradient(135deg,#bad8ff,#4777bc); }
.section-head { margin:27px 0 13px; }
.section-sub { color:#8792a4; font-size:12px; margin-top:-7px; }
[data-testid="stMetric"] { background:#fff; border:1px solid #e8ebf2; border-radius:13px; padding:17px 18px; box-shadow:0 5px 18px #23385e08; }
[data-testid="stMetricLabel"] p { color:#6d7b91 !important; font-size:12px; }
[data-testid="stMetricValue"] { color:#17243b !important; font-family:'Manrope',sans-serif; }
div[data-testid="stForm"] { background:#fff; border:1px solid #e6eaf2; border-radius:15px; padding:22px; }
[data-testid="stFileUploader"] section { background:#f7f9fd; border:1px dashed #aebbd0; border-radius:12px; }
.stButton button[kind="primary"],button[kind="primaryFormSubmit"] { background:#326ef0; border:0; border-radius:8px; color:#fff; font-weight:700; padding:.65rem 1rem; }
.stButton button[kind="primary"]:hover,button[kind="primaryFormSubmit"]:hover { background:#225ddd; color:#fff; }
.stButton button:not([kind="primary"]),button[kind="secondaryFormSubmit"] { border-radius:8px; }
[data-testid="stAlert"] { border-radius:10px; }
.card { background:#fff; border:1px solid #e7ebf3; border-radius:13px; padding:18px 20px; margin:10px 0; box-shadow:0 5px 18px #23385e08; }
.card-title { color:#17243b; font-weight:700; font-size:14px; }
.card-muted { color:#8390a5; font-size:11px; margin-top:5px; }
.report { background:#fff; border:1px solid #e6eaf2; border-radius:14px; padding:22px; margin-top:16px; }
.report-label { color:#4774d8; font-size:10px; font-weight:700; letter-spacing:1px; text-transform:uppercase; }
.report li { margin:.35rem 0; }
hr { border-color:#e8ebf2 !important; }
footer { color:#8a96a8; font-size:11px; margin-top:34px; padding-top:16px; border-top:1px solid #e5eaf2; }
@media(max-width:850px) { .block-container{padding:1.2rem 1rem}.hero{grid-template-columns:1fr}.hero-art{min-height:150px}.topline{font-size:10px} }
</style>
""", unsafe_allow_html=True)

init_db()

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-badge">BS</div><div><div class="brand-name">BUILDSENSE</div><div class="brand-sub">CONSTRUCTION INTELLIGENCE</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-caption">WORKSPACE</div>', unsafe_allow_html=True)
    page = st.radio("Workspace", ["Overview", "Site Safety", "Crack Observation", "Property Valuation", "Project Planning", "Daily Site Assistant", "Report History"], label_visibility="collapsed")
    st.markdown('<div class="card" style="background:#1a2b4d;border-color:#304264;margin-top:32px"><div class="card-title" style="color:white">AI site intelligence</div><div class="card-muted" style="color:#aab9d4">Turn site data into clearer next steps.</div></div><div class="card-muted">PROJECT WORKSPACE<br>Individual account</div>', unsafe_allow_html=True)


def page_header(title, subtitle):
    st.markdown(f'<div class="topline"><span>Workspace　/　<b style="color:#24324b">{title}</b></span><span class="chip">Project workspace</span></div><div class="eyebrow">MULTIMODAL CONSTRUCTION PLATFORM</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)


def save_result(kind, title, result):
    item = save_analysis(kind, title, result.get("headline", title), result)
    st.session_state["last_result"] = item
    st.success("Report saved to your workspace.")


def render_report(item):
    result = item.get("result", item)
    st.markdown('<div class="report"><div class="report-label">REPORT GENERATED</div></div>', unsafe_allow_html=True)
    st.subheader(result.get("headline", item.get("title", "Analysis report")))
    if result.get("mode"):
        st.caption("Gemini AI" if result["mode"] == "gemini" else "Demo mode")
    if result.get("estimated_value_inr") is not None:
        st.metric("Indicative property value", f"INR {result['estimated_value_inr']:,.0f}")
        if result.get("range_inr"):
            st.caption(f"Estimated range: INR {result['range_inr']['low']:,.0f} - INR {result['range_inr']['high']:,.0f}")
    for key, heading in [("risk_level", "Risk level"), ("severity", "Severity"), ("answer", "Guidance"), ("calculation", "Calculation")]:
        if result.get(key):
            st.markdown(f"**{heading}:** {result[key]}")
    for key, heading in [("observations", "Observations"), ("recommended_actions", "Recommended actions"), ("checklist", "Checklist"), ("milestones", "Milestones"), ("risks", "Risks to manage"), ("factors_to_verify", "Factors to verify"), ("next_steps", "Next steps")]:
        if result.get(key):
            st.markdown(f"#### {heading}")
            for text in result[key]:
                st.markdown(f"- {text}")
    if result.get("phases"):
        st.markdown("#### Project phases")
        for phase in result["phases"]:
            st.markdown(f"**{phase['phase']}** · {phase['duration']}")
            for task in phase.get("tasks", []):
                st.markdown(f"- {task}")
    for key, heading in [("weather_advice", "Weather advisory"), ("follow_up", "Suggested follow-up"), ("limitations", "Important limitation")]:
        if result.get(key):
            st.markdown(f"**{heading}:** {result[key]}")


def image_workflow(kind):
    safety = kind == "site_safety"
    with st.form("image_form"):
        image = st.file_uploader("Choose a site image", type=["jpg", "jpeg", "png", "webp"])
        st.caption("JPG, PNG, or WEBP · Maximum 8 MB")
        context = st.text_area("Site context" if safety else "Crack context", placeholder="Add a short description to help frame the review.")
        submitted = st.form_submit_button("Generate safety review" if safety else "Review crack observations", type="primary")
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
                report_title = "Site safety review"
            else:
                fallback = {"headline":"Preliminary crack observation", "severity":"Unknown - professional inspection required", "observations":["Demo mode cannot determine crack depth, movement, width, or structural significance.","Photograph with a ruler for scale and record location, length, and date.","Track changes and note water ingress or displacement."], "recommended_actions":["Arrange a qualified structural engineer inspection for widening, stepped, diagonal, or displaced cracks.","Do not conceal a potentially structural crack before assessment."], "limitations":"No automated structural diagnosis is performed in demo mode."}
                prompt = f"Review this construction photo for possible cracks. Context: {context}. Return JSON keys headline, severity, observations array, recommended_actions array, limitations. Never diagnose structural safety from a photo."
                report_title = "Crack observation"
            with st.spinner("Preparing your review..."):
                result, mode = generate_json(prompt, fallback, data, image.type or "image/jpeg")
            result.update({"mode": mode, "site_context" if safety else "context": context})
            save_result(kind, report_title, result)
            st.image(data, caption=image.name, use_container_width=True)
    if st.session_state.get("last_result"):
        render_report(st.session_state["last_result"])


if page == "Overview":
    reports = list_analyses(100)
    page_header("Overview", "A single workspace for site safety, visual observations, planning, and field guidance.")
    st.markdown('<section class="hero"><div class="hero-copy"><div class="eyebrow">YOUR SITE, WITH MORE INSIGHT</div><h2>Build with confidence.<br><em>Plan with clarity.</em></h2><p>Bring photos, project details, and field questions together in one intelligent workspace.</p></div><div class="hero-art"><div class="tower"></div><div class="tower small"></div></div></section>', unsafe_allow_html=True)
    st.markdown("### Workspace at a glance")
    st.caption("Live totals from your saved reports")
    metrics = st.columns(4)
    values = [len(reports), sum(x["kind"] == "site_safety" for x in reports), sum(x["kind"] == "crack" for x in reports), sum(x["kind"] == "plan" for x in reports)]
    for col, label, value in zip(metrics, ["Total analyses", "Safety reviews", "Crack reviews", "Planning reports"], values):
        col.metric(label, value)
    st.markdown("### Recent activity")
    st.caption("Your latest saved analysis reports")
    if reports:
        st.dataframe([{"Date": x["created_at"], "Type": x["kind"], "Title": x["title"], "Summary": x["summary"]} for x in reports[:5]], use_container_width=True, hide_index=True)
    else:
        st.info("Your completed analyses will appear here.")
elif page == "Site Safety":
    page_header(page, "Review a site image and create a practical safety checklist.")
    st.warning("Photo analysis is advisory. It cannot certify safety.")
    image_workflow("site_safety")
elif page == "Crack Observation":
    page_header(page, "Record visible cracking and organize professional follow-up.")
    st.warning("This workflow cannot diagnose structural integrity from a photograph.")
    image_workflow("crack")
elif page == "Property Valuation":
    page_header(page, "Create an indicative estimate from your own assumptions.")
    with st.form("valuation"):
        location = st.text_input("Location", placeholder="Indore, Madhya Pradesh")
        property_type = st.text_input("Property type", "Residential apartment")
        c1, c2 = st.columns(2)
        area = c1.number_input("Built-up area (sq ft)", min_value=1.0, value=1000.0)
        rate = c2.number_input("Assumed rate (INR / sq ft)", min_value=1.0, value=5000.0)
        c3, c4 = st.columns(2)
        age = c3.number_input("Property age (years)", min_value=0, max_value=300, value=0)
        condition = c4.selectbox("Condition", ["Excellent", "Good", "Fair", "Needs repair"])
        submitted = st.form_submit_button("Generate indicative estimate", type="primary")
    if submitted:
        try:
            req = ValuationRequest(location=location, property_type=property_type, area_sqft=area, rate_per_sqft=rate, age_years=age, condition=condition)
            estimate = round(req.area_sqft * req.rate_per_sqft * max(.55, 1 - req.age_years * .008) * {"Excellent":1.08,"Good":1.0,"Fair":.9,"Needs repair":.75}.get(req.condition,1.0))
            fallback = {"headline":"Indicative property value estimate", "estimated_value_inr":estimate, "range_inr":{"low":round(estimate*.9),"high":round(estimate*1.1)}, "calculation":f"{req.area_sqft:,.0f} sq ft x INR {req.rate_per_sqft:,.0f}/sq ft, adjusted for age and condition.", "factors_to_verify":["Recent comparable sales","Exact location and access","Title, approvals and encumbrances","Construction quality and maintenance"], "limitations":"Rule-of-thumb estimate only, not a formal appraisal or investment advice."}
            result, mode = generate_json(f"Comment on this real estate estimate. Inputs: {req.model_dump()}. Arithmetic estimate INR {estimate}. Return JSON keys headline, estimated_value_inr, range_inr low/high, calculation, factors_to_verify array, limitations. Do not invent live market data.", fallback)
            result.update({"mode": mode, "inputs": req.model_dump()})
            save_result("valuation", f"Valuation - {req.location}", result)
        except Exception as exc:
            st.error(str(exc))
    if st.session_state.get("last_result"):
        render_report(st.session_state["last_result"])
elif page == "Project Planning":
    page_header(page, "Draft project phases, milestones, and common risks.")
    with st.form("planning"):
        project_name = st.text_input("Project name")
        c1, c2 = st.columns(2)
        project_type = c1.selectbox("Project type", ["Residential", "Commercial", "Industrial", "Infrastructure", "Renovation"])
        site_area = c2.number_input("Site area (sq ft)", min_value=1.0, value=1000.0)
        c3, c4, c5 = st.columns(3)
        floors = c3.number_input("Floors", min_value=1, max_value=150, value=2)
        months = c4.number_input("Duration (months)", min_value=1, max_value=240, value=12)
        budget = c5.number_input("Budget (INR)", min_value=1.0, value=1000000.0)
        notes = st.text_area("Project notes")
        submitted = st.form_submit_button("Generate project plan", type="primary")
    if submitted:
        try:
            req = PlanRequest(project_name=project_name, project_type=project_type, site_area_sqft=site_area, floors=floors, target_months=months, budget_inr=budget, notes=notes)
            fallback = {"headline":f"Draft delivery plan: {req.project_name}", "phases":[{"phase":"Requirements, survey & approvals","duration":"10% of schedule","tasks":["Confirm scope, survey, drawings, permits and responsibilities."]},{"phase":"Design & procurement","duration":"15% of schedule","tasks":["Coordinate drawings, quotations and long-lead materials."]},{"phase":"Site preparation & foundation","duration":"20% of schedule","tasks":["Set out site and complete approved excavation and foundation works."]},{"phase":"Structure & envelope","duration":"30% of schedule","tasks":["Sequence structure, masonry and weatherproofing with inspection hold points."]},{"phase":"Services & finishes","duration":"20% of schedule","tasks":["Install and test services, complete finishes and resolve defects."]},{"phase":"Handover","duration":"5% of schedule","tasks":["Complete quality checks, as-builts and owner handover."]}], "milestones":["Approved drawings and permits","Foundation sign-off","Structure topped out","Services testing","Practical completion"], "risks":["Weather delays","Material cost or delivery changes","Design coordination gaps","Rework from missed inspections"], "next_steps":["Validate durations and costs with the project team.","Add dependencies, owners, contingency and cost breakdown."], "limitations":"Planning template only; validate scope, schedule, cost and compliance with qualified professionals."}
            result, mode = generate_json(f"Create high-level construction plan for {req.model_dump()}. Return JSON keys headline, phases objects phase/duration/tasks, milestones array, risks array, next_steps array, limitations. Do not imply professional validation.", fallback)
            result.update({"mode": mode, "inputs": req.model_dump()})
            save_result("plan", f"Plan - {req.project_name}", result)
        except Exception as exc:
            st.error(str(exc))
    if st.session_state.get("last_result"):
        render_report(st.session_state["last_result"])
elif page == "Daily Site Assistant":
    page_header(page, "Prepare a field checklist for your current work stage.")
    with st.form("daily"):
        question = st.text_area("Your question", placeholder="What should we check before pouring concrete today?")
        c1, c2 = st.columns(2)
        city = c1.text_input("City / location")
        weather = c2.text_input("Reported weather", "Not provided")
        stage = st.selectbox("Work stage", ["General site work","Excavation","Foundation","Concrete pouring","Working at height","Electrical work","Finishing","Inspection and handover"])
        submitted = st.form_submit_button("Get site guidance", type="primary")
    st.info("No live weather feed is connected. Verify conditions against a trusted local forecast.")
    if submitted:
        try:
            req = DailyRequest(question=question, city=city, weather=weather, work_stage=stage)
            fallback = {"headline":"Daily site briefing", "answer":f"For {req.work_stage.lower()}, hold a toolbox talk, confirm approved drawings and permits, inspect access and PPE, and assign a supervisor. Reported weather: {req.weather}.", "checklist":["Review planned work and method statement","Confirm PPE and equipment checks","Check access, housekeeping and exclusion zones","Record hazards and corrective actions","Stop work and escalate imminent danger"], "weather_advice":"No live weather data is connected. Check a trusted local forecast before lifting, working at height, pouring concrete, or outdoor electrical work.", "follow_up":"Share the task, materials, site conditions and local requirements for a more tailored checklist.", "limitations":"General guidance only; follow approved procedures and competent professional advice."}
            result, mode = generate_json(f"Answer construction site question safely: {req.model_dump()}. Return JSON keys headline, answer, checklist array, weather_advice, follow_up, limitations. Do not claim live weather access.", fallback)
            result.update({"mode": mode, "inputs": req.model_dump()})
            save_result("daily_assistance", "Daily site assistance", result)
        except Exception as exc:
            st.error(str(exc))
    if st.session_state.get("last_result"):
        render_report(st.session_state["last_result"])
elif page == "Report History":
    page_header(page, "Your latest saved analysis reports.")
    reports = list_analyses(100)
    if reports:
        selected = st.selectbox("Select a report", reports, format_func=lambda x: f"{x['created_at']} - {x['title']}")
        render_report(selected)
    else:
        st.info("No saved reports yet. Complete a workflow to build your history.")

st.markdown("<footer>BuildSense prototype · AI output is advisory and requires professional verification.</footer>", unsafe_allow_html=True)

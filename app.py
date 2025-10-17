# TriChoice — Tricuspid Repair vs Replacement (Educational)
# NOT a medical device or clinical decision support tool.

import streamlit as st
from PIL import Image

# -----------------------------
# App config
# -----------------------------
st.set_page_config(page_title="TriChoice (Educational): TriClip vs TTVR", layout="wide")
st.title("TriChoice — Tricuspid Repair vs Replacement (Educational)")
st.caption("For education & Heart Team planning discussion only — **not** clinical decision support.")

# -----------------------------
# Sidebar: structured inputs
# -----------------------------
with st.sidebar:
    st.header("Clinical context")
    etiology = st.selectbox("TR etiology", ["Secondary (functional)", "Primary (degenerative)", "CIED lead-related", "Mixed/uncertain"])
    tr_severity = st.selectbox("TR grade", ["Severe", "Massive", "Torrential"])
    rv_function = st.selectbox("RV function (echo/CMR)", ["Normal/mildly impaired", "Moderately impaired", "Severely impaired"])
    ph_status = st.selectbox("Pulmonary hypertension", ["None/mild", "Moderate", "Severe/pre-capillary"])
    cied_lead = st.selectbox("CIED lead crossing TV", ["No", "Yes — not impinging", "Yes — impinging / causal"])
    surgical_risk = st.selectbox("Surgical risk", ["Intermediate", "High", "Prohibitive"])
    organ_dysf = st.multiselect("End-organ dysfunction (select all that apply)", ["Hepatic congestion/cirrhosis", "Renal insufficiency/failure", "Cachexia/malnutrition"])

    st.markdown("---")
    st.header("GLIDE inputs (TEE-based)")
    # GLIDE: five 'unfavorable' flags (1 point each)
    gap = st.selectbox("Septolateral coaptation gap", ["Favorable (small/moderate)", "Unfavorable (large)"])
    loc = st.selectbox("TR jet location", ["Favorable (central)", "Unfavorable (commissural/off-axis/multiple)"])
    imgq = st.selectbox("TEE image quality for grasping view", ["Good/Excellent", "Suboptimal/Shadowing"])
    density = st.selectbox("Chordal structure density", ["Low/typical", "High/dense (tethered/subvalvular crowding)"])
    enface = st.selectbox("En-face TR morphology", ["Focal/single", "Diffuse/multi-jet"])

    st.markdown("---")
    st.header("Echo screenshot (optional)")
    up = st.file_uploader("Upload TEE/TTE screenshot (PNG/JPG)", type=["png", "jpg", "jpeg"])

# -----------------------------
# GLIDE computation
# -----------------------------
def point(x):
    return 1 if "Unfavorable" in x or x in ["Suboptimal/Shadowing",
                                            "High/dense (tethered/subvalvular crowding)",
                                            "Diffuse/multi-jet"] else 0

glide = point(gap) + point(loc) + point(imgq) + point(density) + point(enface)

if glide <= 1:
    repair_bucket = "High likelihood of successful T‑TEER (GLIDE 0–1)"
elif 2 <= glide <= 3:
    repair_bucket = "Intermediate likelihood of T‑TEER success (GLIDE 2–3)"
else:
    repair_bucket = "Low likelihood of T‑TEER success (GLIDE ≥4)"

# -----------------------------
# Decision logic (educational)
# -----------------------------
def recommend(glide, rv_function, ph_status, tr_severity, cied_lead):
    """
    Educational rule set:
    - GLIDE 0–1 → Repair favored (TriClip), unless severe PH or severe RV failure argue futility.
    - GLIDE 2–3 → Borderline; weigh RV function, PH, torrential TR, lead issues.
    - GLIDE ≥4 → Replacement favored (TTVR) if anatomy suitable and RV can tolerate afterload change;
                 consider futility if end-stage RV/organ failure.
    """
    choice = "Borderline — Heart Team review"
    reasons = []

    severe_rv = (rv_function == "Severely impaired")
    severe_ph = (ph_status == "Severe/pre-capillary")
    torrential = (tr_severity == "Torrential")
    lead_imping = (cied_lead == "Yes — impinging / causal")

    if glide <= 1:
        choice = "Repair favored (TriClip — T‑TEER)"
        reasons.append("GLIDE 0–1 is associated with a high probability of acute T‑TEER success (JACC CV Imaging 2024).")
        if severe_ph or severe_rv:
            reasons.append("Severe PH or end‑stage RV dysfunction may limit benefit; consider futility even if repair‑leaning.")
        if lead_imping:
            reasons.append("CIED lead interaction requires strategy (work‑around vs lead management).")

    elif glide >= 4:
        choice = "Replacement favored (TTVR)"
        reasons.append("GLIDE ≥4 predicts low probability of T‑TEER success; consider TTVR if anatomy is suitable.")
        if severe_rv:
            reasons.append("Beware RV afterload mismatch and potential need for pacing after TTVR; assess RV tolerance carefully.")
        if lead_imping:
            reasons.append("Plan lead management before TTVR to avoid lead entrapment.")

    else:
        choice = "Borderline — Heart Team review"
        reasons.append("GLIDE 2–3 = intermediate T‑TEER success; use RV function, PH, TR extent, and lead status to choose.")
        if not (severe_rv or severe_ph) and not torrential:
            reasons.append("If RV is preserved and PH not severe, a stepwise repair may be preferred for safety and incremental reduction.")
        if torrential or lead_imping:
            reasons.append("If TR is torrential or anatomy/lead unfavorable for grasping, replacement may provide more reliable elimination of TR.")

    return choice, reasons

choice, reasons = recommend(glide, rv_function, ph_status, tr_severity, cied_lead)

# -----------------------------
# Layout & output
# -----------------------------
col1, col2 = st.columns([1,1])

with col1:
    st.subheader("GLIDE score")
    st.metric(label="GLIDE (0–5)", value=str(glide), delta=repair_bucket)
    st.markdown(
        "- **GLIDE components (1 point each if unfavorable):** Gap, Location, Image quality, chordal **D**ensity, **E**n‑face TR morphology. "
        "Higher scores predict lower chance of acute T‑TEER success."
    )

    st.subheader("Suggested therapy direction (educational)")
    # ✅ FIX: use if/elif/else instead of ternary to avoid Streamlit magic auto-print error
    if "Repair" in choice:
        st.success(choice)
    elif "Borderline" in choice:
        st.warning(choice)
    else:
        st.error(choice)

    st.markdown("\n".join([f"- {r}" for r in reasons]))

    st.markdown("---")
    st.markdown("**Key evidence and indications (context):**")
    st.write(
        "• **TriClip (T‑TEER)**: FDA‑approved; improves QoL; many patients achieve TR ≤ moderate at 1 year (TRILUMINATE). "
        "Indicated for symptomatic severe TR at ≥ intermediate surgical risk when T‑TEER is expected to reduce TR to ≤ moderate."
    )
    st.write(
        "• **TTVR (e.g., EVOQUE)**: randomized data show sustained TR elimination with QoL benefit but higher pacemaker/RV‑failure risks than repair—"
        "consider in anatomies unfavorable for T‑TEER."
    )
    st.write(
        "• Selection should integrate **RV function, PH, anatomy, and leads**; lean to **repair** for incremental reduction with lower pacing risk, "
        "and to **replacement** for refractory/torrential TR or difficult leaflet grasping."
    )

with col2:
    st.subheader("Echo screenshot (optional)")
    if up:
        img = Image.open(up)
        st.image(img, caption="Uploaded echo screenshot", use_column_width=True)
    else:
        st.info("Upload a TEE/TTE screenshot to display here.")

st.markdown("---")
st.markdown("### Export educational report")
report = f"""
# TriChoice — Educational Report (Not for clinical use)

**Etiology:** {etiology}  
**TR severity:** {tr_severity}  
**RV function:** {rv_function}  
**Pulmonary hypertension:** {ph_status}  
**CIED lead across TV:** {cied_lead}  
**Surgical risk:** {surgical_risk}  
**End-organ dysfunction:** {', '.join(organ_dysf) if organ_dysf else 'None'}

## GLIDE Score
- Gap: {gap}
- Location: {loc}
- Image quality: {imgq}
- Chordal density: {density}
- En-face TR morphology: {enface}

**GLIDE total:** {glide}  → {repair_bucket}

## Suggested therapy direction (educational)
**{choice}**  
{chr(10).join(['- ' + r for r in reasons])}

## Notes
- GLIDE: 5-component anatomic score predicting T‑TEER success (JACC CV Imaging 2024).
- TriClip (T‑TEER) & TTVR evidence indicate different tradeoffs (QoL benefit with both; pacing/RV risks higher after TTVR).
- Therapy choice should always be individualized by the Heart Team based on imaging, anatomy, RV/PH status, and device IFU.

> This document is for **education and planning discussion** only. Always rely on device IFU/labeling, contemporary guidance, and real-time Heart Team assessment.
"""
# Assign to _ to avoid auto-printing the return value
_ = st.download_button("Download report (.md)", report, file_name="TriChoice_report.md")

st.caption("© 2025 — Educational prototype")

import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="Provenance Guard", layout="wide")
st.title("Provenance Guard — Analytics Dashboard")

FLASK_URL = "http://127.0.0.1:5000"
LABELS = ["clearly AI", "likely AI", "uncertain", "likely human", "clearly human"]
COLORS = ["#e74c3c", "#e67e22", "#95a5a6", "#3498db", "#2ecc71"]


# ── Fetch data ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def fetch_log():
    try:
        response = requests.get(f"{FLASK_URL}/log", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the Flask API. Make sure the server is running on port 5000.")
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e}")
        st.stop()


submissions = fetch_log()

if not submissions:
    st.info("No submissions yet.")
    st.stop()


# ── Derived metrics ───────────────────────────────────────────────────────────

total = len(submissions)
total_appeals = sum(1 for s in submissions if s.get("status") == "under_review")

verdict_counts = {label: 0 for label in LABELS}
for s in submissions:
    label = s.get("label")
    if label in verdict_counts:
        verdict_counts[label] += 1

confidence_sums = {label: [] for label in LABELS}
for s in submissions:
    label = s.get("label")
    confidence = s.get("confidence")
    if label in confidence_sums and confidence is not None:
        confidence_sums[label].append(confidence)

HUMAN_LABELS = {"likely human", "clearly human"}

avg_confidence = {}
for label, vals in confidence_sums.items():
    if not vals:
        avg_confidence[label] = 0
    else:
        avg = sum(vals) / len(vals)
        avg_confidence[label] = round(1 - avg, 2) if label in HUMAN_LABELS else round(avg, 2)


# ── KPI row ───────────────────────────────────────────────────────────────────

st.subheader("Overview")
col1, col2, col3 = st.columns(3)

ai_verdicts = verdict_counts["clearly AI"] + verdict_counts["likely AI"]
human_verdicts = verdict_counts["clearly human"] + verdict_counts["likely human"]
ai_ratio = round((ai_verdicts / total) * 100) if total else 0
human_ratio = round((human_verdicts / total) * 100) if total else 0

col1.metric("Total Submissions", total)
col2.metric("AI vs. Human Ratio", f"{ai_ratio}% AI / {human_ratio}% Human")
col3.metric("Appeal Rate", f"{round((total_appeals / total) * 100, 1)}%", f"{total_appeals} appeals")

st.divider()


# ── Charts row ────────────────────────────────────────────────────────────────

left, right = st.columns(2)

with left:
    st.subheader("Verdict Distribution")
    fig = go.Figure(go.Bar(
        x=list(verdict_counts.keys()),
        y=list(verdict_counts.values()),
        marker_color=COLORS,
        text=list(verdict_counts.values()),
        textposition="outside",
    ))
    fig.update_layout(
        xaxis_title="Label",
        yaxis_title="Submissions",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20),
        yaxis=dict(gridcolor="rgba(128,128,128,0.2)"),
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Average Confidence per Label")
    conf_values = [round(avg_confidence[label] * 100) for label in LABELS]
    fig2 = go.Figure(go.Bar(
        x=LABELS,
        y=conf_values,
        marker_color=COLORS,
        text=[f"{v}%" for v in conf_values],
        textposition="outside",
    ))
    fig2.update_layout(
        xaxis_title="Label",
        yaxis_title="Avg. Confidence (%)",
        yaxis=dict(range=[0, 110], gridcolor="rgba(128,128,128,0.2)"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()


# ── Recent submissions ────────────────────────────────────────────────────────

st.subheader("Recent Submissions")

header = st.columns([2, 2, 2, 2, 2, 1])
for col, label in zip(header, ["Content ID", "Creator", "Timestamp", "Label", "Confidence", "Status"]):
    col.markdown(f"**{label}**")
st.divider()

for s in submissions:
    row = st.columns([2, 2, 2, 2, 2, 1])
    row[0].code(s.get("content_id", "—"), language=None)
    row[1].write(s.get("creator_id", "—"))
    row[2].write(s.get("timestamp", "—"))
    row[3].write(s.get("label", "—"))
    confidence = s.get("confidence")
    if confidence is not None:
        display_confidence = (1 - confidence) if s.get("label") in HUMAN_LABELS else confidence
        row[4].write(f"{round(display_confidence * 100)}%")
    else:
        row[4].write("—")
    row[5].write("🔄" if s.get("status") == "under_review" else "✅")

    with st.expander("View details"):
        d1, d2 = st.columns(2)
        with d1:
            st.markdown("**Attribution**")
            st.write(s.get("attribution", "—"))
            st.markdown("**LLM Score**")
            st.write(s.get("llm_ai_probability", "—"))
            st.markdown("**LLM Reasoning**")
            st.write(s.get("llm_reasoning", "—"))
        with d2:
            st.markdown("**Stylometrics Score**")
            st.write(s.get("stylometrics_score", "—"))
            st.markdown("**Burstiness Score**")
            st.write(s.get("burstiness_score", "—"))
            st.markdown("**Punctuation Entropy Score**")
            st.write(s.get("punctuation_entropy_score", "—"))

        if s.get("status") == "under_review":
            st.markdown("**Appeal Received**")
            st.write(s.get("appeal_timestamp", "—"))
            st.markdown("**Creator Reasoning**")
            st.write(s.get("creator_reasoning", "—"))

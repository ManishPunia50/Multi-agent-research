import streamlit as st
import time
from pipeline import run_research_pipeline

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔬",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f1117;
        color: #e0e0e0;
    }

    /* Title */
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #888;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Pipeline step cards */
    .step-card {
        background: #1a1d27;
        border: 1px solid #2a2d3e;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-bottom: 1rem;
    }
    .step-card.active {
        border-color: #4f8ef7;
        box-shadow: 0 0 12px rgba(79,142,247,0.25);
    }
    .step-card.done {
        border-color: #2ecc71;
        box-shadow: 0 0 8px rgba(46,204,113,0.15);
    }

    /* Step header row */
    .step-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 1rem;
        font-weight: 600;
        color: #c8d0e0;
        margin-bottom: 0.4rem;
    }
    .step-icon { font-size: 1.3rem; }

    /* Result text area inside card */
    .result-text {
        background: #12141c;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        font-size: 0.85rem;
        color: #b0bcd4;
        white-space: pre-wrap;
        max-height: 220px;
        overflow-y: auto;
        line-height: 1.55;
        font-family: 'Courier New', monospace;
    }

    /* Final report card */
    .report-card {
        background: #131824;
        border: 1px solid #4f8ef7;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-top: 1.2rem;
    }
    .report-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #4f8ef7;
        margin-bottom: 0.8rem;
    }
    .report-body {
        font-size: 0.92rem;
        color: #cdd5e0;
        white-space: pre-wrap;
        line-height: 1.7;
    }

    /* Critic card */
    .critic-card {
        background: #131f1a;
        border: 1px solid #2ecc71;
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-top: 1rem;
    }
    .critic-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #2ecc71;
        margin-bottom: 0.8rem;
    }
    .critic-body {
        font-size: 0.9rem;
        color: #b8d4c0;
        white-space: pre-wrap;
        line-height: 1.65;
    }

    /* Run button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4f8ef7 0%, #6a5acd 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 2.5rem;
        font-size: 1.05rem;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.88; }

    /* Input field */
    .stTextInput > div > div > input {
        background-color: #1a1d27;
        color: #e0e0e0;
        border: 1px solid #2a2d3e;
        border-radius: 10px;
        font-size: 1rem;
        padding: 0.6rem 1rem;
    }

    /* Divider */
    hr { border-color: #2a2d3e; }

    /* Status badge */
    .badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-waiting  { background:#2a2d3e; color:#888; }
    .badge-running  { background:#1e3a5f; color:#4f8ef7; }
    .badge-done     { background:#1a3a25; color:#2ecc71; }
    .badge-error    { background:#3a1a1a; color:#e74c3c; }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🔬 Multi-Agent Research System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Search → Scrape → Write → Critique &nbsp;|&nbsp; Powered by LangChain agents</div>', unsafe_allow_html=True)
st.markdown("---")


# ── Input section ────────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([4, 1])
with col_input:
    topic = st.text_input(
        label="Research Topic",
        placeholder="e.g.  Quantum computing breakthroughs in 2025",
        label_visibility="collapsed",
    )
with col_btn:
    run_clicked = st.button("🚀 Run Pipeline")


# ── Pipeline steps UI helper ─────────────────────────────────────────────────────
STEPS = [
    ("🔍", "Search Agent",   "Finding recent and reliable information across the web..."),
    ("📄", "Reader Agent",   "Scraping top URL for deeper content..."),
    ("✍️",  "Writer Chain",  "Drafting a comprehensive research report..."),
    ("🧐", "Critic Chain",  "Reviewing and providing feedback on the report..."),
]

def render_step(index, icon, label, description, status="waiting", content=None):
    """Render a single pipeline step card."""
    card_class = "step-card"
    if status == "running":
        card_class += " active"
    elif status == "done":
        card_class += " done"

    badge_html = {
        "waiting": '<span class="badge badge-waiting">⏳ Waiting</span>',
        "running": '<span class="badge badge-running">⚡ Running</span>',
        "done":    '<span class="badge badge-done">✅ Done</span>',
        "error":   '<span class="badge badge-error">❌ Error</span>',
    }.get(status, "")

    result_html = ""
    if content:
        result_html = f'<div class="result-text">{content}</div>'

    st.markdown(f"""
    <div class="{card_class}">
        <div class="step-header">
            <span class="step-icon">{icon}</span>
            <span>Step {index+1} — {label}</span>
            &nbsp;&nbsp;{badge_html}
        </div>
        <div style="color:#666; font-size:0.82rem; margin-bottom:0.4rem;">{description}</div>
        {result_html}
    </div>
    """, unsafe_allow_html=True)


# ── Main pipeline execution ──────────────────────────────────────────────────────
if run_clicked:
    if not topic.strip():
        st.warning("⚠️ Please enter a research topic before running.")
    else:
        st.markdown("---")
        st.markdown("### 🔄 Pipeline Running...")

        # Placeholders for each step
        placeholders = [st.empty() for _ in STEPS]

        # Render all steps as "waiting" initially
        for i, (icon, label, desc) in enumerate(STEPS):
            with placeholders[i]:
                render_step(i, icon, label, desc, status="waiting")

        state = {}

        # ── Step 1: Search Agent ─────────────────────────────────────────────
        with placeholders[0]:
            render_step(0, *STEPS[0], status="running")

        try:
            from agents import build_search_agent
            search_agent = build_search_agent()
            search_result = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
            })
            state["search_results"] = search_result['messages'][-1].content

            with placeholders[0]:
                render_step(0, *STEPS[0], status="done",
                            content=state["search_results"][:600] + "...")
        except Exception as e:
            with placeholders[0]:
                render_step(0, *STEPS[0], status="error", content=str(e))
            st.error(f"Search Agent failed: {e}")
            st.stop()

        # ── Step 2: Reader Agent ─────────────────────────────────────────────
        with placeholders[1]:
            render_step(1, *STEPS[1], status="running")

        try:
            from agents import build_reader_agent
            reader_agent = build_reader_agent()
            reader_result = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}"
                )]
            })
            state["scraped_content"] = reader_result['messages'][-1].content

            with placeholders[1]:
                render_step(1, *STEPS[1], status="done",
                            content=state["scraped_content"][:600] + "...")
        except Exception as e:
            with placeholders[1]:
                render_step(1, *STEPS[1], status="error", content=str(e))
            st.error(f"Reader Agent failed: {e}")
            st.stop()

        # ── Step 3: Writer Chain ─────────────────────────────────────────────
        with placeholders[2]:
            render_step(2, *STEPS[2], status="running")

        try:
            from agents import writer_chain
            research_combined = (
                f"SEARCH RESULTS:\n{state['search_results']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
            )
            state["report"] = writer_chain.invoke({
                "topic": topic,
                "research": research_combined
            })

            with placeholders[2]:
                render_step(2, *STEPS[2], status="done",
                            content=str(state["report"])[:600] + "...")
        except Exception as e:
            with placeholders[2]:
                render_step(2, *STEPS[2], status="error", content=str(e))
            st.error(f"Writer Chain failed: {e}")
            st.stop()

        # ── Step 4: Critic Chain ─────────────────────────────────────────────
        with placeholders[3]:
            render_step(3, *STEPS[3], status="running")

        try:
            from agents import critic_chain
            state["feedback"] = critic_chain.invoke({
                "report": state["report"]
            })

            with placeholders[3]:
                render_step(3, *STEPS[3], status="done",
                            content=str(state["feedback"])[:600] + "...")
        except Exception as e:
            with placeholders[3]:
                render_step(3, *STEPS[3], status="error", content=str(e))
            st.error(f"Critic Chain failed: {e}")
            st.stop()

        # ── Final Results ────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📑 Final Results")

        tab_report, tab_feedback, tab_raw = st.tabs(["📄 Research Report", "🧐 Critic Feedback", "🗂️ Raw Data"])

        with tab_report:
            st.markdown(f"""
            <div class="report-card">
                <div class="report-title">📄 Research Report: {topic}</div>
                <div class="report-body">{state.get("report", "")}</div>
            </div>
            """, unsafe_allow_html=True)

            # Download button
            st.download_button(
                label="⬇️ Download Report (.txt)",
                data=str(state.get("report", "")),
                file_name=f"report_{topic[:30].replace(' ', '_')}.txt",
                mime="text/plain",
            )

        with tab_feedback:
            st.markdown(f"""
            <div class="critic-card">
                <div class="critic-title">🧐 Critic Review</div>
                <div class="critic-body">{state.get("feedback", "")}</div>
            </div>
            """, unsafe_allow_html=True)

        with tab_raw:
            with st.expander("🔍 Search Results (raw)", expanded=False):
                st.text(state.get("search_results", ""))
            with st.expander("📄 Scraped Content (raw)", expanded=False):
                st.text(state.get("scraped_content", ""))

        st.success("✅ Pipeline completed successfully!")


# ── Sidebar ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 About")
    st.markdown("""
    This system chains **4 AI agents** to produce a full research report:

    1. **🔍 Search Agent** — web searches using tools
    2. **📄 Reader Agent** — scrapes the best URL
    3. **✍️ Writer Chain** — drafts a structured report
    4. **🧐 Critic Chain** — reviews and suggests improvements

    Built with **LangChain** + **Streamlit**.
    """)

    st.markdown("---")
    st.markdown("### ⚙️ Stack")
    st.code("""
LangChain
Streamlit
Groq / Gemini API
Custom tools (tools.py)
Custom agents (agents.py)
    """, language="text")

    st.markdown("---")
    st.caption("Multi-Agent Research System v1.0")
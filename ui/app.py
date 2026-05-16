import re
import time

import requests
import streamlit as st

st.set_page_config(
    page_title="Voyager AI · Travel Planner",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BACKEND_URL = "http://127.0.0.1:8000/generate-plan"


def inject_css():
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

    :root {
        --bg-base: #090c14;
        --bg-surface: #0f1320;
        --bg-elevated: #151b2e;
        --bg-card: #1a2035;
        --border: rgba(255,255,255,0.06);
        --border-glow: rgba(99,179,237,0.25);
        --accent-blue: #63b3ed;
        --accent-cyan: #4ecdc4;
        --accent-amber: #f6ad55;
        --accent-rose: #fc8181;
        --accent-violet: #b794f4;
        --text-primary: #e8eaf0;
        --text-secondary: #8892a4;
        --text-muted: #4a5568;
        --gradient-hero: linear-gradient(135deg, #0d1b3e 0%, #090c14 50%, #0a1628 100%);
        --shadow-card: 0 8px 32px rgba(0,0,0,0.5);
        --radius-card: 16px;
        --radius-sm: 8px;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg-base) !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--gradient-hero) !important;
    }

    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image:
            radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,0.15) 0%, transparent 100%),
            radial-gradient(1px 1px at 80% 10%, rgba(255,255,255,0.1) 0%, transparent 100%),
            radial-gradient(1px 1px at 50% 70%, rgba(255,255,255,0.08) 0%, transparent 100%),
            radial-gradient(1px 1px at 10% 85%, rgba(255,255,255,0.12) 0%, transparent 100%),
            radial-gradient(1px 1px at 90% 60%, rgba(255,255,255,0.1) 0%, transparent 100%);
        pointer-events: none;
        z-index: 0;
    }

    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stSidebar"] { background: var(--bg-surface) !important; }
    [data-testid="stDecoration"] { display: none; }
    .block-container {
        padding: 2rem 3rem 4rem !important;
        max-width: 1200px !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Syne', sans-serif !important;
        letter-spacing: -0.02em;
    }

    .voyager-hero {
        text-align: center;
        padding: 3.5rem 2rem 2rem;
        position: relative;
    }

    .voyager-logo {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-family: 'Syne', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: var(--accent-blue);
        background: rgba(99,179,237,0.08);
        border: 1px solid rgba(99,179,237,0.2);
        padding: 6px 16px;
        border-radius: 100px;
        margin-bottom: 1.5rem;
    }

    .voyager-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 800;
        line-height: 1.1;
        margin: 0 0 1rem;
        background: linear-gradient(135deg, #e8eaf0 0%, #63b3ed 50%, #4ecdc4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .voyager-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        font-weight: 300;
        max-width: 520px;
        margin: 0 auto 2rem;
        line-height: 1.6;
    }

    .input-wrapper {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2rem;
        margin: 0 auto 1.5rem;
        max-width: 780px;
        box-shadow: var(--shadow-card), 0 0 60px rgba(99,179,237,0.04);
        transition: border-color 0.3s ease;
    }

    .input-wrapper:hover {
        border-color: rgba(99,179,237,0.15);
    }

    .input-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
    }

    [data-testid="stTextArea"] textarea {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 300 !important;
        line-height: 1.6 !important;
        padding: 1rem !important;
        resize: none !important;
        transition: border-color 0.3s !important;
        caret-color: var(--accent-blue) !important;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--border-glow) !important;
        box-shadow: 0 0 0 3px rgba(99,179,237,0.08) !important;
    }

    [data-testid="stTextArea"] label { display: none !important; }

    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin-bottom: 2rem;
    }

    .pill {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 0.82rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-family: 'DM Sans', sans-serif;
        user-select: none;
    }

    .pill:hover {
        border-color: rgba(99,179,237,0.3);
        color: var(--accent-blue);
        background: rgba(99,179,237,0.06);
    }

    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #2b6cb0 0%, #2c7a7b 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        padding: 0.75rem 2rem !important;
        width: 100% !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 24px rgba(43,108,176,0.3) !important;
        cursor: pointer !important;
    }

    [data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 32px rgba(43,108,176,0.45) !important;
        filter: brightness(1.1) !important;
    }

    [data-testid="stButton"] > button:active {
        transform: translateY(0) !important;
    }

    .agent-workflow {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 2rem;
        max-width: 560px;
        margin: 2rem auto;
    }

    .agent-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
        color: var(--text-primary);
    }

    .agent-step {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 12px 0;
        border-bottom: 1px solid var(--border);
        opacity: 0.35;
        transition: opacity 0.4s ease;
    }

    .agent-step.active { opacity: 1; }
    .agent-step.done { opacity: 0.6; }
    .agent-step:last-child { border-bottom: none; }

    .agent-dot {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
    }

    .agent-dot.spinning {
        border-top-color: var(--accent-blue);
        animation: spin 0.9s linear infinite;
        border-color: var(--border);
    }

    .agent-dot.done-dot {
        background: rgba(78,205,196,0.15);
        border-color: var(--accent-cyan);
        color: var(--accent-cyan);
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .agent-info { flex: 1; }

    .agent-name {
        font-family: 'Syne', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    .agent-desc {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 2px;
    }

    .agent-badge {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 4px;
    }

    .badge-active {
        background: rgba(99,179,237,0.15);
        color: var(--accent-blue);
    }

    .badge-done {
        background: rgba(78,205,196,0.12);
        color: var(--accent-cyan);
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 2.5rem 0 1.25rem;
    }

    .section-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }

    .icon-blue { background: rgba(99,179,237,0.12); }
    .icon-cyan { background: rgba(78,205,196,0.12); }
    .icon-amber { background: rgba(246,173,85,0.12); }
    .icon-rose { background: rgba(252,129,129,0.12); }
    .icon-violet { background: rgba(183,148,244,0.12); }

    .section-label {
        font-family: 'Syne', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .section-divider {
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    .dest-card {
        background: linear-gradient(135deg, var(--bg-elevated) 0%, var(--bg-card) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-card);
    }

    .dest-card::before {
        content: '';
        position: absolute;
        top: -40px;
        right: -40px;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(99,179,237,0.08) 0%, transparent 70%);
        pointer-events: none;
    }

    .dest-name {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 0.5rem;
        background: linear-gradient(90deg, var(--text-primary) 0%, var(--accent-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .dest-tagline {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 300;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }

    .dest-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .dest-tag {
        background: rgba(255,255,255,0.04);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
    }

    .weather-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
        margin-top: 0.5rem;
    }

    .weather-card {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem 1rem;
        text-align: center;
    }

    .weather-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .weather-val {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    .weather-key {
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-top: 4px;
    }

    .attraction-card {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        height: 100%;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }

    .attraction-card:hover {
        border-color: rgba(99,179,237,0.2);
        transform: translateY(-2px);
    }

    .attr-number {
        font-family: 'Syne', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        color: var(--accent-blue);
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .attr-name {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
        color: var(--text-primary);
    }

    .attr-desc {
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }

    .day-card {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent-blue);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
    }

    .day-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--accent-blue);
        margin-bottom: 0.25rem;
    }

    .day-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }

    .timeline-item {
        display: flex;
        gap: 12px;
        margin-bottom: 0.9rem;
        align-items: flex-start;
    }

    .timeline-time {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--accent-cyan);
        min-width: 60px;
        padding-top: 2px;
        font-family: 'Syne', sans-serif;
    }

    .timeline-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-blue);
        flex-shrink: 0;
        margin-top: 6px;
        box-shadow: 0 0 8px rgba(99,179,237,0.5);
    }

    .timeline-text {
        font-size: 0.88rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }

    .budget-card {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 10px;
    }

    .budget-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }

    .budget-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.88rem;
        color: var(--text-secondary);
    }

    .budget-amount {
        font-family: 'Syne', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .budget-bar-bg {
        height: 4px;
        background: rgba(255,255,255,0.06);
        border-radius: 2px;
        overflow: hidden;
    }

    .budget-bar-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 1s ease;
    }

    .total-card {
        background: linear-gradient(135deg, rgba(43,108,176,0.2) 0%, rgba(44,122,123,0.2) 100%);
        border: 1px solid rgba(99,179,237,0.2);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 1rem;
    }

    .total-label {
        font-size: 0.75rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--accent-blue);
        font-family: 'Syne', sans-serif;
        margin-bottom: 0.5rem;
    }

    .total-amount {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-cyan) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    [data-testid="metric-container"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
    }

    [data-testid="metric-container"] label {
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        font-family: 'Syne', sans-serif !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1.5rem !important;
    }

    [data-testid="stTabs"] [role="tablist"] {
        background: var(--bg-surface) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
        border-bottom: none !important;
    }

    [data-testid="stTabs"] [role="tab"] {
        background: transparent !important;
        color: var(--text-muted) !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        border-radius: 7px !important;
        border: none !important;
        transition: all 0.2s !important;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stTabs"] [role="tabpanel"] {
        padding-top: 1.5rem !important;
    }

    [data-testid="stExpander"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }

    [data-testid="stExpander"] summary {
        color: var(--text-primary) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        padding: 1rem 1.25rem !important;
    }

    .error-banner {
        background: rgba(252,129,129,0.08);
        border: 1px solid rgba(252,129,129,0.2);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        color: var(--accent-rose);
        font-size: 0.9rem;
        margin: 1rem 0;
    }

    .info-banner {
        background: rgba(99,179,237,0.06);
        border: 1px solid rgba(99,179,237,0.15);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: var(--text-secondary);
        font-size: 0.88rem;
        margin: 0.5rem 0;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }

    .voyager-footer {
        text-align: center;
        padding: 3rem 0 1rem;
        color: var(--text-muted);
        font-size: 0.78rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
    <div class="voyager-hero">
        <div class="voyager-logo">✦ Voyager AI · Multi-Agent Travel Planner</div>
        <h1 class="voyager-title">Plan Your Perfect Journey</h1>
        <p class="voyager-subtitle">
            Describe your dream trip and our AI agents will craft a personalized
            itinerary, budget breakdown, and travel insights — in seconds.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


EXAMPLES = [
    "🏯 10 days in Japan, ¥200k budget",
    "🏖 Bali honeymoon, 7 nights",
    "🗼 Paris & Rome, 2 weeks, €3000",
    "🏔 Patagonia trekking, 12 days",
    "🌴 Thailand backpacker, ₹1500",
    "🏜 Morocco desert, 5 days",
]


def render_example_pills():
    pills_html = '<div class="pill-row">' + "".join(
        f'<span class="pill">{example}</span>' for example in EXAMPLES
    ) + "</div>"
    st.markdown(pills_html, unsafe_allow_html=True)


def render_input_form():
    _, col, _ = st.columns([1, 2.4, 1])
    with col:
        st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="input-label">Where do you want to go?</div>', unsafe_allow_html=True)

        user_query = st.text_area(
            label="query",
            placeholder='e.g. "Plan a 7-day trip to Japan in October for 2 people with a ₹3000 budget, including Tokyo, Kyoto, and Osaka."',
            height=120,
            key="user_query",
            label_visibility="collapsed",
        )
        st.markdown("&nbsp;", unsafe_allow_html=True)
        submit = st.button("✦ Generate My Travel Plan", key="submit_btn")
        st.markdown("</div>", unsafe_allow_html=True)
    return user_query.strip(), submit


AGENTS = [
    ("🧭", "Intent Agent", "Understanding your travel goals & preferences"),
    ("🔍", "Research Agent", "Fetching destination insights & local tips"),
    ("📅", "Itinerary Agent", "Crafting your day-by-day plan"),
    ("💰", "Budget Agent", "Calculating costs & optimizing spend"),
]


def render_agent_workflow(active_idx: int):
    steps_html = ""
    for index, (icon, name, desc) in enumerate(AGENTS):
        if index < active_idx:
            cls = "agent-step done"
            dot = '<div class="agent-dot done-dot">✓</div>'
            badge = '<span class="agent-badge badge-done">Done</span>'
        elif index == active_idx:
            cls = "agent-step active"
            dot = '<div class="agent-dot spinning"></div>'
            badge = '<span class="agent-badge badge-active">Running</span>'
        else:
            cls = "agent-step"
            dot = f'<div class="agent-dot">{icon}</div>'
            badge = ""

        steps_html += f"""
        <div class="{cls}">
            {dot}
            <div class="agent-info">
                <div class="agent-name">{name}</div>
                <div class="agent-desc">{desc}</div>
            </div>
            {badge}
        </div>
        """

    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown(
            f"""
        <div class="agent-workflow">
            <div class="agent-title">AI Agents at Work&nbsp; ·&nbsp; {active_idx}/{len(AGENTS)}</div>
            {steps_html}
        </div>
        """,
            unsafe_allow_html=True,
        )


def call_backend_api(user_query: str):
    placeholder = st.empty()
    for step_idx in range(len(AGENTS)):
        with placeholder.container():
            render_agent_workflow(step_idx)
        if step_idx < len(AGENTS) - 1:
            time.sleep(1.1)

    try:
        response = requests.post(
            BACKEND_URL,
            json={"user_query": user_query},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        placeholder.empty()
        return data, None
    except requests.exceptions.ConnectionError:
        placeholder.empty()
        return None, "🔌 Cannot reach the backend. Make sure the FastAPI server is running on `http://127.0.0.1:8000`."
    except requests.exceptions.Timeout:
        placeholder.empty()
        return None, "⏱ The request timed out (120 s). Try a simpler query or check backend performance."
    except requests.exceptions.HTTPError as error:
        placeholder.empty()
        return None, f"🚫 Backend returned HTTP {error.response.status_code}: {error.response.text[:200]}"
    except Exception as error:
        placeholder.empty()
        return None, f"⚠️ Unexpected error: {str(error)}"


def section_header(icon: str, label: str, color_class: str = "icon-blue"):
    st.markdown(
        f"""
    <div class="section-header">
        <div class="section-icon {color_class}">{icon}</div>
        <span class="section-label">{label}</span>
        <div class="section-divider"></div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_destination(data: dict):
    dest = data.get("destination_overview", {})
    if not dest:
        return

    section_header("🌍", "Destination Overview", "icon-blue")

    name = dest.get("name", "Your Destination")
    tagline = dest.get("description", dest.get("tagline", ""))
    tags = dest.get("highlights", dest.get("tags", []))
    best = dest.get("best_time", "")
    language = dest.get("language", "")
    currency = dest.get("currency", "")

    tags_html = "".join(f'<span class="dest-tag">{tag}</span>' for tag in tags[:6])
    st.markdown(
        f"""
    <div class="dest-card">
        <div class="dest-name">{name}</div>
        <div class="dest-tagline">{tagline}</div>
        <div class="dest-tags">{tags_html}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if any([best, language, currency]):
        st.markdown("<br>", unsafe_allow_html=True)
        metrics = st.columns(3)
        if best:
            metrics[0].metric("📅 Best Time to Visit", best)
        if language:
            metrics[1].metric("🗣 Language", language)
        if currency:
            metrics[2].metric("💳 Currency", currency)


def render_weather(data: dict):
    weather = data.get("weather", {})
    if not weather:
        return

    section_header("🌤", "Weather & Climate", "icon-cyan")

    temperature = weather.get("temperature", weather.get("avg_temperature", "—"))
    condition = weather.get("condition", weather.get("description", "—"))
    humidity = weather.get("humidity", "—")
    wind = weather.get("wind_speed", weather.get("wind", ""))
    uv = weather.get("uv_index", weather.get("uv", ""))
    rain = weather.get("rainfall", weather.get("rain_chance", ""))

    cards = [
        ("🌡", str(temperature), "Temperature"),
        ("⛅", str(condition), "Condition"),
        ("💧", str(humidity), "Humidity"),
    ]
    if wind:
        cards.append(("💨", str(wind), "Wind"))
    if uv:
        cards.append(("☀️", str(uv), "UV Index"))
    if rain:
        cards.append(("🌧", str(rain), "Rain"))

    grid_html = '<div class="weather-grid">'
    for icon, value, key in cards:
        grid_html += f"""
        <div class="weather-card">
            <div class="weather-icon">{icon}</div>
            <div class="weather-val">{value}</div>
            <div class="weather-key">{key}</div>
        </div>"""
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)


def render_attractions(data: dict):
    attractions = data.get("attractions", data.get("top_attractions", []))
    if not attractions:
        return

    section_header("🏛", "Top Attractions", "icon-violet")

    cols_per_row = 3
    for index in range(0, len(attractions), cols_per_row):
        row = attractions[index:index + cols_per_row]
        cols = st.columns(len(row))
        for row_index, attraction in enumerate(row):
            with cols[row_index]:
                if isinstance(attraction, dict):
                    name = attraction.get("name", f"Attraction {index + row_index + 1}")
                    desc = attraction.get("description", attraction.get("details", ""))
                    cat = attraction.get("category", attraction.get("type", ""))
                else:
                    name = str(attraction)
                    desc = ""
                    cat = ""

                ordinal = f"0{index + row_index + 1}" if index + row_index + 1 < 10 else str(index + row_index + 1)
                st.markdown(
                    f"""
                <div class="attraction-card">
                    <div class="attr-number">— {ordinal}</div>
                    <div class="attr-name">{name}</div>
                    <div class="attr-desc">{desc or cat}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)


def render_itinerary(data: dict):

    itinerary = data.get("itinerary", {})

    if not itinerary:
        return

    days_data = itinerary.get("days", {})

    if not days_data:
        return

    section_header(
        "📅",
        "Day-by-Day Itinerary",
        "icon-amber"
    )

    for day_name, activities in days_data.items():

        with st.expander(
            day_name,
            expanded=True
        ):

            st.markdown(
                '<div class="day-card">',
                unsafe_allow_html=True
            )

            for activity in activities:

                st.markdown(
                    f"""
                    <div class="timeline-item">
                        <div class="timeline-dot"></div>
                        <div class="timeline-text">
                            {activity}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

BUDGET_PALETTE = {
    "hotel": ("#63b3ed", "🏨"),
    "accommodation": ("#63b3ed", "🏨"),
    "food": ("#4ecdc4", "🍜"),
    "meals": ("#4ecdc4", "🍜"),
    "transport": ("#f6ad55", "✈️"),
    "transportation": ("#f6ad55", "✈️"),
    "activities": ("#b794f4", "🎯"),
    "entertainment": ("#b794f4", "🎯"),
    "misc": ("#fc8181", "🧳"),
    "miscellaneous": ("#fc8181", "🧳"),
}


def _extract_number(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^\d.]", "", str(value))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def render_budget(data: dict):
    budget = data.get("budget_breakdown", data.get("budget", {}))
    if not budget:
        return

    section_header("💰", "Budget Breakdown", "icon-amber")

    items = {}
    total_value = 0.0
    for key, value in budget.items():
        if key.lower() in ("total", "total_cost", "grand_total"):
            total_value = _extract_number(value)
        else:
            items[key] = _extract_number(value)

    if not total_value and items:
        total_value = sum(items.values())

    col1, col2 = st.columns([1.6, 1])

    with col1:
        for key, amount in items.items():
            pct = amount / total_value * 100 if total_value else 0
            color, icon = BUDGET_PALETTE.get(key.lower(), ("#8892a4", "•"))
            st.markdown(
                f"""
            <div class="budget-card">
                <div class="budget-row">
                    <div class="budget-label">{icon} {key.replace('_', ' ').title()}</div>
                    <div class="budget-amount">₹{amount:,.0f}</div>
                </div>
                <div class="budget-bar-bg">
                    <div class="budget-bar-fill" style="width:{pct:.1f}%; background:{color};"></div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            f"""
        <div class="total-card">
            <div class="total-label">Estimated Total</div>
            <div class="total-amount">₹{total_value:,.0f}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        days = len(data.get("itinerary", data.get("day_wise_itinerary", [1])))
        if days and total_value:
            per_day = total_value / max(days, 1)
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("📊 Per-Day Average", f"₹{per_day:,.0f}")

        if items:
            largest_key = max(items, key=lambda key: items[key])
            pct_str = f"{items[largest_key] / total_value * 100:.0f}%" if total_value else "—"
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("🔺 Biggest Spend", f"{largest_key.title()} ({pct_str})")


def render_tips(data: dict):
    tips = data.get("travel_tips", data.get("tips", data.get("essential_info", [])))
    if not tips:
        return

    section_header("💡", "Travel Tips & Essentials", "icon-cyan")
    if isinstance(tips, list):
        for index, tip in enumerate(tips):
            icon = ["🛂", "💊", "📱", "🔌", "💬", "🏧", "🧥", "🛡"][index % 8]
            label = tip if isinstance(tip, str) else tip.get("tip", str(tip))
            st.markdown(f'<div class="info-banner">{icon} {label}</div>', unsafe_allow_html=True)
    elif isinstance(tips, str):
        st.markdown(f'<div class="info-banner">💡 {tips}</div>', unsafe_allow_html=True)

def render_plan(plan: dict):

    if not isinstance(plan, dict):

        st.markdown(
            '''
            <div class="error-banner">
                ⚠️ Invalid backend response.
            </div>
            ''',
            unsafe_allow_html=True
        )

        return

    if "error" in plan:

        st.markdown(
            f'''
            <div class="error-banner">
                ⚠️ {plan["error"]}
            </div>
            ''',
            unsafe_allow_html=True
        )

        return

    if "intent" not in plan:

        st.markdown(
            '''
            <div class="error-banner">
                ⚠️ Backend response missing required data.
            </div>
            ''',
            unsafe_allow_html=True
        )

        st.json(plan)

        return

    transformed_data = {

        "destination_overview": {
            "name": plan["intent"]["destination"],
            "description": plan["research"]["weather"],
            "tags": plan["intent"]["preferences"],
            "best_time": plan["research"]["best_time_to_visit"],
        },

        "weather": plan.get(
            "weather",
            {}
        ),

        "attractions": plan[
            "research"
        ].get(
            "attractions",
            []
        ),

        "itinerary": plan.get(
            "itinerary",
            {}
        ),

        "budget_breakdown": plan.get(
            "budget",
            {}
        ),

        "travel_tips": plan[
            "research"
        ].get(
            "local_transport",
            []
        )
    }

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    render_destination(
        transformed_data
    )

    render_weather(
        transformed_data
    )

    render_attractions(
        transformed_data
    )

    render_itinerary(
        transformed_data
    )

    render_budget(
        transformed_data
    )

    render_tips(
        transformed_data
    )

    with st.expander(
        "🔧 Raw API Response",
        expanded=False
    ):
        st.json(plan)

    st.markdown(
        '''
        <div class="voyager-footer">
            Powered by Voyager AI · Multi-Agent Travel Planning
        </div>
        ''',
        unsafe_allow_html=True
    )
    
def main():
    inject_css()
    render_hero()
    render_example_pills()
    user_query, submitted = render_input_form()

    if submitted:
        if not user_query:
            st.markdown('<div class="error-banner">✦ Please describe your trip before generating a plan.</div>', unsafe_allow_html=True)
            return

        st.markdown("<br>", unsafe_allow_html=True)
        plan_data, error = call_backend_api(user_query)

        if error:
            st.markdown(f'<div class="error-banner">{error}</div>', unsafe_allow_html=True)
            st.markdown(
                """
            <div class="info-banner">
                ℹ️ Make sure your FastAPI backend is running:<br>
                <code style="background:rgba(255,255,255,0.06);padding:2px 6px;border-radius:4px;">
                    uvicorn main:app --host 127.0.0.1 --port 8000
                </code>
            </div>
            """,
                unsafe_allow_html=True,
            )
            return

        if not plan_data:
            st.markdown('<div class="error-banner">⚠️ Received an empty response from the backend.</div>', unsafe_allow_html=True)
            return

        render_plan(plan_data)
    else:
        st.markdown(
            """
        <div style="text-align:center; padding: 2rem 0; color: #4a5568; font-size: 0.88rem;">
            ↑ Enter your trip details above to get started
        </div>
        """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()

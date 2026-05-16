import re
import time
import textwrap
import random

import requests
import streamlit as st

st.set_page_config(
    page_title="Pātheyātrā AI · Travel Planner",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BACKEND_URL = "http://127.0.0.1:8000/generate-plan"


def inject_css():
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@300;400;500;600&display=swap');

    :root {
        /* Modern light palette */
        --bg-base: #fafbfc;
        --bg-surface: #ffffff;
        --bg-elevated: #f8f9fb;
        --bg-card: #ffffff;
        --border: rgba(0,0,0,0.08);
        --border-light: rgba(0,0,0,0.04);

        /* Modern travel palette */
        --accent-primary: #00b4d8;
        --accent-secondary: #0096c7;
        --accent-earth: #d4a574;
        --accent-sunset: #f77f00;
        --accent-emerald: #06a77d;

        /* Text colors */
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;

        --shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
        --shadow-md: 0 8px 24px rgba(0,0,0,0.1);
        --shadow-lg: 0 16px 48px rgba(0,0,0,0.12);
        --radius-card: 16px;
        --radius-sm: 10px;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg-base) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #fafbfc 0%, #f0f4f8 100%) !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stSidebar"] { background: transparent !important; }
    [data-testid="stDecoration"] { display: none; }
    
    .block-container {
        padding: 2.5rem 2rem 3.5rem !important;
        max-width: 1100px !important;
        margin: 0 auto !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: -0.015em;
        color: var(--text-primary);
        font-weight: 700;
    }

    /* Hero Section */
    .Pātheyātrā-hero {
        text-align: center;
        padding: 4rem 2rem 3rem;
        margin: 0 auto 2rem;
        max-width: 900px;
        border-radius: var(--radius-card);
        background: linear-gradient(135deg, rgba(0,180,216,0.08) 0%, rgba(6,167,125,0.08) 100%);
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
        color: var(--text-primary);
        position: relative;
        overflow: hidden;
    }

    .Pātheyātrā-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(0,180,216,0.1) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .Pātheyātrā-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--accent-primary);
        background: rgba(0,180,216,0.1);
        border: 1px solid rgba(0,180,216,0.2);
        padding: 7px 16px;
        border-radius: 999px;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(10px);
    }

    .Pātheyātrā-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: clamp(2.2rem, 6vw, 3.5rem);
        font-weight: 800;
        line-height: 1.1;
        margin: 0 0 0.8rem;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }

    .Pātheyātrā-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        font-weight: 400;
        max-width: 700px;
        margin: 0 auto 2rem;
        line-height: 1.7;
    }

    /* Input Section */
    .input-wrapper {
        background: var(--bg-surface);
        border: 2px solid var(--border-light);
        border-radius: var(--radius-card);
        padding: 2rem;
        margin: 1.5rem auto;
        max-width: 800px;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }

    .input-wrapper:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 12px 32px rgba(0,180,216,0.12);
    }

    .input-label {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.75rem;
        display: block;
    }

    [data-testid="stTextArea"] textarea {
        background: var(--bg-elevated) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        padding: 1.2rem !important;
        resize: vertical !important;
        transition: all 0.2s ease !important;
        caret-color: var(--accent-primary) !important;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(0,180,216,0.1) !important;
    }

    [data-testid="stTextArea"] label { display: none !important; }

    /* Example Pills */
    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin: 1.5rem 0;
    }

    .pill {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        padding: 10px 16px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .pill:hover {
        transform: translateY(-2px);
        color: var(--accent-primary);
        border-color: var(--accent-primary);
        box-shadow: 0 4px 12px rgba(0,180,216,0.15);
    }

    /* Buttons */
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        padding: 0.95rem 1.8rem !important;
        width: auto !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 8px 20px rgba(0,180,216,0.25) !important;
        cursor: pointer !important;
    }

    [data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 28px rgba(0,180,216,0.35) !important;
    }

    [data-testid="stButton"] > button:active {
        transform: translateY(0) !important;
    }

    /* Agent Workflow */
    .agent-workflow {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 1.5rem;
        max-width: 600px;
        margin: 2rem auto;
        box-shadow: var(--shadow-md);
    }

    .agent-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
    }

    .agent-step {
        display: flex;
        gap: 16px;
        align-items: flex-start;
        padding: 1rem 0;
        border-bottom: 1px solid var(--border-light);
        opacity: 0.5;
        transition: opacity 0.3s ease;
    }

    .agent-step:last-child {
        border-bottom: none;
    }

    .agent-step.active {
        opacity: 1;
    }

    .agent-step.done {
        opacity: 0.7;
    }

    .agent-dot {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: var(--bg-elevated);
        border: 2px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
        font-weight: 700;
    }

    .agent-dot.spinning {
        border-color: var(--accent-primary);
        animation: pulse 1.2s ease-in-out infinite;
    }

    .agent-dot.done-dot {
        background: rgba(0,180,216,0.1);
        color: var(--accent-primary);
        border-color: var(--accent-primary);
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }

    .agent-info {
        flex: 1;
    }

    .agent-name {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .agent-desc {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-top: 0.2rem;
    }

    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 3rem 0 1.5rem;
        justify-content: center;
    }

    .section-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
    }

    .icon-blue { background: rgba(0,180,216,0.12); }
    .icon-earth { background: rgba(212,165,116,0.12); }
    .icon-sunset { background: rgba(247,127,0,0.12); }
    .icon-emerald { background: rgba(6,167,125,0.12); }
    .icon-muted { background: rgba(148,163,184,0.12); }

    .section-label {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    /* Cards */
    .dest-card, .attraction-card, .day-card, .budget-card, .total-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-card);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }

    .dest-card {
        max-width: 700px;
        margin: 0 auto;
        border: 2px solid var(--border-light);
    }

    .dest-card:hover {
        border-color: var(--accent-primary);
        box-shadow: var(--shadow-md);
    }

    .dest-name {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }

    .dest-tagline {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 1rem;
        line-height: 1.6;
    }

    .dest-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .dest-tag {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        padding: 7px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .weather-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
        margin: 1.5rem 0;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }

    .weather-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-light);
        padding: 1.5rem;
        text-align: center;
        border-radius: var(--radius-sm);
        box-shadow: var(--shadow-sm);
    }

    .weather-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .weather-val {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .weather-key {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 0.4rem;
        font-weight: 500;
    }

    .attraction-card {
        max-width: 280px;
        text-align: center;
    }

    .attraction-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-md);
        border-color: var(--accent-primary);
    }

    .attr-number {
        color: var(--accent-primary);
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
    }

    .attr-name {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }

    .attr-desc {
        color: var(--text-muted);
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .day-card {
        border-left: 4px solid var(--accent-primary);
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }

    .timeline-item {
        display: flex;
        gap: 16px;
        padding: 1rem 0;
        border-bottom: 1px solid var(--border-light);
    }

    .timeline-item:last-child {
        border-bottom: none;
    }

    .timeline-dot {
        width: 10px;
        height: 10px;
        background: var(--accent-primary);
        border-radius: 50%;
        margin-top: 0.5rem;
        flex-shrink: 0;
        box-shadow: 0 0 12px rgba(0,180,216,0.3);
    }

    .timeline-text {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Budget Section */
    .budget-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        max-width: 900px;
        margin: 0 auto;
    }

    .budget-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
    }

    .budget-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }

    .budget-label {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.95rem;
    }

    .budget-amount {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        color: var(--accent-primary);
        font-size: 1rem;
    }

    .budget-bar-bg {
        width: 100%;
        height: 6px;
        background: var(--bg-elevated);
        border-radius: 999px;
        overflow: hidden;
    }

    .budget-bar-fill {
        height: 100%;
        border-radius: 999px;
        transition: width 0.4s ease;
    }

    .total-card {
        background: linear-gradient(135deg, rgba(0,180,216,0.08) 0%, rgba(6,167,125,0.08) 100%);
        border: 2px solid var(--border-light);
        text-align: center;
        padding: 2rem 1.5rem;
        height: fit-content;
    }

    .total-label {
        color: var(--text-muted);
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }

    .total-amount {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--accent-primary);
    }

    [data-testid="metric-container"] {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-sm) !important;
        padding: 1.2rem !important;
    }

    /* Tabs */
    [data-testid="stTabs"] [role="tablist"] {
        background: transparent !important;
        border-bottom: 2px solid var(--border) !important;
    }

    [data-testid="stTabs"] [role="tab"] {
        color: var(--text-muted) !important;
        font-weight: 600 !important;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--accent-primary) !important;
        border-bottom-color: var(--accent-primary) !important;
    }

    /* Banners */
    .error-banner {
        background: rgba(239,68,68,0.08);
        border: 1px solid rgba(239,68,68,0.2);
        color: #dc2626;
        padding: 1.2rem;
        border-radius: var(--radius-sm);
        font-weight: 500;
        margin: 1rem 0;
    }

    .info-banner {
        background: rgba(0,180,216,0.08);
        border: 1px solid rgba(0,180,216,0.2);
        color: var(--text-secondary);
        padding: 1rem;
        border-radius: var(--radius-sm);
        font-size: 0.95rem;
        margin: 0.8rem 0;
        line-height: 1.6;
    }

    .info-banner code {
        background: rgba(0,0,0,0.05);
        padding: 2px 8px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-elevated);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-primary);
    }

    /* Footer */
    .Pātheyātrā-footer {
        text-align: center;
        padding: 3rem 0 1rem;
        color: var(--text-muted);
        font-size: 0.85rem;
        margin-top: 2rem;
    }

    /* Responsive */
    @media (max-width: 1100px) {
        .budget-container {
            grid-template-columns: 1fr;
        }

        .block-container {
            padding: 1.5rem !important;
        }

        .Pātheyātrā-hero {
            padding: 2.5rem 1.5rem;
        }

        .Pātheyātrā-title {
            font-size: clamp(1.6rem, 6vw, 2.5rem);
        }

        .pill-row {
            justify-content: center;
        }

        [data-testid="stButton"] > button {
            width: 100% !important;
        }
    }

    @media (max-width: 600px) {
        .weather-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .dest-name {
            font-size: 1.5rem;
        }

        .pill {
            padding: 8px 12px;
            font-size: 0.8rem;
        }

        .section-header {
            flex-direction: column;
            gap: 8px;
        }

        .agent-workflow {
            padding: 1rem;
        }
    }

    /* Loading overlay */
    .loading-overlay {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
    }

    .loading-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-light);
        padding: 2rem;
        border-radius: 14px;
        box-shadow: var(--shadow-md);
        max-width: 680px;
        text-align: center;
        margin: 0 auto;
    }

    .loading-spinner {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        border: 6px solid rgba(255,255,255,0.06);
        border-top-color: var(--accent-primary);
        margin: 0 auto 1rem;
        animation: spin 1s linear infinite;
    }

    .completed-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(90deg, rgba(6,167,125,0.12), rgba(0,180,216,0.08));
        color: var(--text-primary);
        padding: 10px 14px;
        border-radius: 999px;
        font-weight: 700;
        border: 1px solid var(--border-light);
    }

    @keyframes spin { to { transform: rotate(360deg); } }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
    <div class="Pātheyātrā-hero">
        <div class="Pātheyātrā-badge">✦ Pātheyātrā AI · Smart Travel Planning</div>
        <h1 class="Pātheyātrā-title">Your Perfect Journey Awaits</h1>
        <p class="Pātheyātrā-subtitle">
            Tell us about your dream destination and let our AI agents craft a personalized
            itinerary, budget breakdown, and insider travel tips instantly.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


EXAMPLES = [
    "🏯 Japan · 10 days · ¥200k budget",
    "🏖 Bali · Honeymoon · 7 nights",
    "🗼 Europe · Paris & Rome · 2 weeks",
    "🏔 Patagonia · Trekking · 12 days",
    "🌴 Thailand · Backpacker · ₹50k",
    "🏜 Morocco · Desert · 5 days",
]


def render_example_pills():
    pills_html = '<div class="pill-row">' + "".join(
        f'<span class="pill">{example}</span>' for example in EXAMPLES
    ) + "</div>"
    st.markdown(pills_html, unsafe_allow_html=True)


def render_input_form():
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
    st.markdown('<label class="input-label">✈️ Where do you want to go?</label>', unsafe_allow_html=True)

    user_query = st.text_area(
        label="query",
        placeholder='e.g. "Plan a 7-day trip to Japan in October for 2 people with a ₹80,000 budget, including Tokyo, Kyoto, and Osaka."',
        height=120,
        key="user_query",
        label_visibility="collapsed",
    )
    
    st.markdown("&nbsp;", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        submit = st.button("✦ Generate My Plan", key="submit_btn", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    return user_query.strip(), submit


AGENTS = [
    ("🧭", "Intent Agent", "Understanding your travel goals"),
    ("🔍", "Research Agent", "Fetching destination insights"),
    ("📅", "Itinerary Agent", "Crafting your day-by-day plan"),
    ("💰", "Budget Agent", "Calculating costs & optimizing"),
    ("☁️", "Weather Agent", "Live weather conditions"),
    ("✨", "Finalizer", "Compiling your travel plan"),
]


def render_agent_workflow(active_idx=None):
    """Render the full list of agent steps.

    If `active_idx` is None, all agents are shown as pending. Otherwise indices < active_idx are shown done,
    index == active_idx is active, others pending.
    """
    steps_html = ""
    for index, (icon, name, desc) in enumerate(AGENTS):
        if active_idx is None:
            cls = "agent-step"
            dot = f'<div class="agent-dot">{icon}</div>'
        else:
            if index < active_idx:
                cls = "agent-step done"
                dot = '<div class="agent-dot done-dot">✓</div>'
            elif index == active_idx:
                cls = "agent-step active"
                dot = '<div class="agent-dot spinning"></div>'
            else:
                cls = "agent-step"
                dot = f'<div class="agent-dot">{icon}</div>'

        steps_html += (
            f'<div class="{cls}">'
            f'{dot}'
            f'<div class="agent-info">'
            f'<div class="agent-name">{name}</div>'
            f'<div class="agent-desc">{desc}</div>'
            f'</div>'
            f'</div>'
        )

    if active_idx is None:
        title = f"AI Agents · Pending ({len(AGENTS)})"
    else:
        # completed count should not include the currently active agent
        if active_idx >= len(AGENTS):
            completed = len(AGENTS)
        else:
            completed = active_idx
        title = f"AI Agents Processing · {completed}/{len(AGENTS)}"

    html = (
        f'<div class="agent-workflow">'
        f'<div class="agent-title">{title}</div>'
        f'{steps_html}'
        f'</div>'
    )
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


def render_agent_loading(active_idx: int):
    """Show a focused loading card for the currently active agent."""
    if active_idx < 0 or active_idx >= len(AGENTS):
        active_idx = 0
    icon, name, desc = AGENTS[active_idx]

    html = (
        '<div class="loading-overlay">'
        '<div class="loading-card">'
        '<div class="loading-spinner"></div>'
        f'<div style="font-size:1.25rem;font-weight:800;color:var(--text-primary);margin-bottom:6px;">{name} — Working</div>'
        f'<div style="color:var(--text-muted);margin-bottom:12px;">{desc}</div>'
        '<div style="color:var(--text-secondary);font-size:0.95rem;">Please wait while our agents craft your personalized plan...</div>'
        '</div>'
        '</div>'
    )
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


def render_agent_completed(agent_idx: int):
    """Show a concise completed badge for an agent."""
    if agent_idx < 0 or agent_idx >= len(AGENTS):
        agent_idx = 0
    icon, name, desc = AGENTS[agent_idx]

    html = (
        '<div class="loading-overlay">'
        '<div class="loading-card">'
        f'<div class="completed-badge">✅ {name} Completed</div>'
        f'<div style="margin-top:12px;color:var(--text-muted);">{desc}</div>'
        '</div>'
        '</div>'
    )
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


def call_backend_api(user_query: str):
    placeholder = st.empty()

    # reveal all agents as pending
    with placeholder.container():
        render_agent_workflow(None)

    # step through first N-1 agents with randomized durations, updating status in-place
    num_pre = len(AGENTS) - 1
    durations = [random.uniform(0.6, 1.8) for _ in range(num_pre)]

    for i in range(num_pre):
        # show i as active (completed count = i)
        with placeholder.container():
            render_agent_workflow(i)

        # simulate work duration per agent (randomized)
        time.sleep(durations[i])

        # mark this agent done and move to next (shows completed count = i+1)
        with placeholder.container():
            render_agent_workflow(i + 1)

    # now show finalizer as active (index = last)
    final_idx = len(AGENTS) - 1
    with placeholder.container():
        render_agent_workflow(final_idx)

    try:
        response = requests.post(
            BACKEND_URL,
            json={"user_query": user_query},
            timeout=120,
        )

        response.raise_for_status()
        data = response.json()

        with placeholder.container():
            render_agent_workflow(6)

        time.sleep(0.8)
        placeholder.empty()

        return data, None

    except requests.exceptions.ConnectionError:
        placeholder.empty()
        return None, "🔌 Cannot reach the backend. Make sure FastAPI is running."

    except requests.exceptions.Timeout:
        placeholder.empty()
        return None, "⏱ Request timed out. Please try again."

    except requests.exceptions.HTTPError as error:
        placeholder.empty()
        return None, f"🚫 Backend error: HTTP {error.response.status_code}"

    except Exception as error:
        placeholder.empty()
        return None, f"⚠️ Error: {str(error)}"


def section_header(icon: str, label: str, color_class: str = "icon-blue"):
    st.markdown(
        f"""
    <div class="section-header">
        <div class="section-icon {color_class}">{icon}</div>
        <span class="section-label">{label}</span>
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
            metrics[0].metric("📅 Best Time", best)
        if language:
            metrics[1].metric("🗣 Language", language)
        if currency:
            metrics[2].metric("💳 Currency", currency)


def render_weather(data: dict):
    weather = data.get("weather", {})
    if not weather:
        return

    section_header("🌤", "Weather & Climate", "icon-emerald")

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

    section_header("🏛", "Top Attractions", "icon-sunset")

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

    section_header("📅", "Day-by-Day Itinerary", "icon-earth")

    for day_name, activities in days_data.items():
        with st.expander(day_name, expanded=True):
            st.markdown('<div class="day-card">', unsafe_allow_html=True)

            for activity in activities:
                st.markdown(
                    f"""
                    <div class="timeline-item">
                        <div class="timeline-dot"></div>
                        <div class="timeline-text">{activity}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)


BUDGET_PALETTE = {
    "hotel": ("var(--accent-primary)", "🏨"),
    "accommodation": ("var(--accent-primary)", "🏨"),

    "food": ("var(--accent-emerald)", "🍜"),
    "meals": ("var(--accent-emerald)", "🍜"),

    "flights": ("#8b5cf6", "🛫"),

    "transport": ("var(--accent-sunset)", "🚌"),
    "transportation": ("var(--accent-sunset)", "🚌"),

    "activities": ("var(--accent-earth)", "🎯"),
    "entertainment": ("var(--accent-earth)", "🎯"),

    "misc": ("#ef4444", "🧳"),
    "miscellaneous": ("#ef4444", "🧳"),
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

    section_header("💰", "Budget Breakdown", "icon-sunset")

    items = {}
    total_value = 0.0
    for key, value in budget.items():
        if key.lower() in ("total", "total_cost", "grand_total"):
            total_value = _extract_number(value)
        else:
            items[key] = _extract_number(value)

    if not total_value and items:
        total_value = sum(items.values())

    st.markdown('<div class="budget-container">', unsafe_allow_html=True)

    # Left column - items
    st.markdown('<div style="grid-column: 1;">', unsafe_allow_html=True)
    for key, amount in items.items():
        pct = amount / total_value * 100 if total_value else 0
        color, icon = BUDGET_PALETTE.get(key.lower(), ("var(--text-muted)", "•"))
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
    st.markdown('</div>', unsafe_allow_html=True)

    # Right column - total
    st.markdown('<div style="grid-column: 2;">', unsafe_allow_html=True)
    st.markdown(
        f"""
    <div class="total-card">
        <div class="total-label">Estimated Total</div>
        <div class="total-amount">₹{total_value:,.0f}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    itinerary_data = data.get("itinerary", {})
    days_data = itinerary_data.get("days", {})
    days = len(days_data)

    if days > 0 and total_value:
        per_day = total_value / days
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("📊 Per-Day Average", f"₹{per_day:,.0f}")

    if items:
        largest_key = max(items, key=lambda key: items[key])
        pct_str = f"{items[largest_key] / total_value * 100:.0f}%" if total_value else "—"
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("🔺 Biggest Spend", f"{largest_key.title()} ({pct_str})")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_tips(data: dict):
    tips = data.get("travel_tips", data.get("tips", data.get("essential_info", [])))
    if not tips:
        return

    section_header("💡", "Travel Tips & Essentials", "icon-muted")
    if isinstance(tips, list):
        for index, tip in enumerate(tips):
            icon = ["🛂", "💊", "📱", "🔌", "💬", "🏧", "🧥", "🛡"][index % 8]
            label = tip if isinstance(tip, str) else tip.get("tip", str(tip))
            st.markdown(f'<div class="info-banner">{icon} {label}</div>', unsafe_allow_html=True)
    elif isinstance(tips, str):
        st.markdown(f'<div class="info-banner">💡 {tips}</div>', unsafe_allow_html=True)


def render_plan(plan: dict):
    if not isinstance(plan, dict):
        st.markdown('<div class="error-banner">⚠️ Invalid backend response.</div>', unsafe_allow_html=True)
        return

    if "error" in plan:
        st.markdown(f'<div class="error-banner">⚠️ {plan["error"]}</div>', unsafe_allow_html=True)
        return

    if "intent" not in plan:
        st.markdown('<div class="error-banner">⚠️ Backend response missing required data.</div>', unsafe_allow_html=True)
        st.json(plan)
        return

    transformed_data = {
        "destination_overview": {
            "name": plan["intent"]["destination"],
            "description": plan["research"]["weather"],
            "tags": plan["intent"]["preferences"],
            "best_time": plan["research"]["best_time_to_visit"],
        },
        "weather": plan.get("weather", {}),
        "attractions": plan["research"].get("attractions", []),
        "itinerary": plan.get("itinerary", {}),
        "budget_breakdown": plan.get("budget", {}),
        "travel_tips": plan["research"].get("local_transport", [])
    }

    st.markdown("<br>", unsafe_allow_html=True)
    render_destination(transformed_data)
    render_weather(transformed_data)
    render_attractions(transformed_data)
    render_itinerary(transformed_data)
    render_budget(transformed_data)
    render_tips(transformed_data)

    st.markdown(
        '''
        <div class="Pātheyātrā-footer">
            ✦ Powered by Pātheyātrā AI · Your Intelligent Travel Companion
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
                <code>uvicorn main:app --host 127.0.0.1 --port 8000</code>
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
        <div style="text-align:center; padding: 3rem 0; color: #94a3b8; font-size: 1rem;">
            ↑ Describe your dream trip above to get started
        </div>
        """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()

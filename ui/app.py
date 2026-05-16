"""
Pātheyātrā AI — Cinematic Travel Planner (single-file Streamlit app)

Run:
    streamlit run app.py

Backend contract (unchanged):
    POST {BACKEND_URL}    body: { "user_query": str }
    Response: { intent, research, weather, itinerary, budget }
"""

import os
import sys
import time
import json
import requests
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.agents import render_agents
from components.ui_helpers import section_head

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000/generate-plan")

st.set_page_config(
    page_title="Pātheyātrā AI · Cinematic Travel Planner",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

EXAMPLES = [
    "🏯 Japan · 10 days · ₹200k budget",
    "🏖 Bali · Honeymoon · 7 nights",
    "🗼 Europe · Paris & Rome · 2 weeks",
    "🏔 Patagonia · Trekking · 12 days",
    "🌴 Thailand · Backpacker · ₹50k",
    "🏜 Morocco · Desert · 5 days",
]

AGENTS = [
    ("🧭", "Intent Agent",    "Understanding your travel goals"),
    ("🔍", "Research Agent",  "Fetching destination insights"),
    ("📅", "Itinerary Agent", "Crafting your day-by-day plan"),
    ("💰", "Budget Agent",    "Calculating costs & optimizing"),
    ("☁️", "Weather Agent",   "Live weather conditions"),
    ("✨", "Finalizer",        "Compiling your travel plan"),
]

INSPIRATIONS = [
    {
        "name": "Kyoto", "kicker": "Japan · Spring",
        "desc": "Cherry blossoms, lantern-lit alleys, and timeless temples.",
        "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1400&q=80",
        "query": "Plan a 7-day cherry blossom trip to Kyoto in April for 2 people, ₹1,20,000 budget, with day trips to Nara and Osaka.",
    },
    {
        "name": "Santorini", "kicker": "Greece · Summer",
        "desc": "Whitewashed cliffs, Aegean sunsets, and slow island mornings.",
        "img": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=1400&q=80",
        "query": "Plan a 5-day romantic getaway to Santorini in June for 2 people with a €2,500 budget.",
    },
    {
        "name": "Patagonia", "kicker": "Argentina · Trekking",
        "desc": "Glacial valleys, granite spires, and wind-carved silence.",
        "img": "https://images.unsplash.com/photo-1531065208531-4036c0dba3ca?auto=format&fit=crop&w=1400&q=80",
        "query": "Plan a 12-day trekking adventure across Patagonia covering Torres del Paine and El Chaltén, mid-range budget.",
    },
    {
        "name": "Marrakech", "kicker": "Morocco · Desert",
        "desc": "Souk spices, riad courtyards, and a night under Saharan stars.",
        "img": "https://images.unsplash.com/photo-1539020140153-e479b8c22e70?auto=format&fit=crop&w=1400&q=80",
        "query": "Plan a 6-day Morocco trip from Marrakech to the Sahara for 2 people with a $1,500 budget.",
    },
    {
        "name": "Bali", "kicker": "Indonesia · Honeymoon",
        "desc": "Rice terraces, jungle villas, and warm volcanic shores.",
        "img": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1400&q=80",
        "query": "Plan a 7-night honeymoon to Bali covering Ubud and Uluwatu with a ₹1,50,000 budget.",
    },
    {
        "name": "Iceland", "kicker": "Nordic · Aurora",
        "desc": "Black sand coasts, glacier lagoons, and dancing northern lights.",
        "img": "https://images.unsplash.com/photo-1500039436846-25ae2f11882e?auto=format&fit=crop&w=1400&q=80",
        "query": "Plan a 6-day Iceland ring-road trip in February to chase the northern lights, mid-range budget.",
    },
]

SAMPLE_PLAN = {
    "title": "Kyoto · 5 Days in Spring",
    "chip": "Sample itinerary",
    "days": [
        ("Day 01 · Arrival in Kyoto", "Settle into a Gion machiya, slow stroll along Shirakawa canal, kaiseki dinner at a quiet ryokan."),
        ("Day 02 · Eastern Temples",  "Kiyomizu-dera at sunrise, Sannenzaka tea break, Yasaka shrine, evening geisha district walk."),
        ("Day 03 · Arashiyama",       "Bamboo grove before crowds, Tenryū-ji garden, Hozugawa river boat, sunset at Iwatayama."),
        ("Day 04 · Day trip to Nara", "Friendly deer in Nara Park, Tōdai-ji great Buddha, matcha tasting back in Uji."),
        ("Day 05 · Fushimi & Farewell","Dawn at Fushimi Inari's torii tunnels, sake brewery lunch, shinkansen onward."),
    ],
    "stats": [
        ("Total budget", "₹1,18,400"),
        ("Per-day avg",  "₹23,680"),
        ("Hotels",       "38%"),
        ("Food & sake",  "22%"),
        ("Transport",    "20%"),
    ],
}

BUDGET_PALETTE = {
    "hotel":           ("#22d3ee", "🏨"),
    "accommodation":   ("#22d3ee", "🏨"),
    "food":            ("#34d399", "🍜"),
    "meals":           ("#34d399", "🍜"),
    "flights":         ("#a78bfa", "🛫"),
    "transport":       ("#fb923c", "🚌"),
    "transportation":  ("#fb923c", "🚌"),
    "activities":      ("#f59e0b", "🎯"),
    "entertainment":   ("#f59e0b", "🎯"),
    "misc":            ("#f87171", "🧳"),
    "miscellaneous":   ("#f87171", "🧳"),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

#MainMenu, header, footer { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section.main > div { padding: 0 !important; }
html, body, [class*="css"] {
  font-family: 'Inter', system-ui, sans-serif !important;
  background: #07070b !important;
  color: #f4f3ef !important;
}

:root {
  --bg: #07070b; --bg-2: #0d0d14;
  --surface: rgba(255,255,255,0.04);
  --surface-2: rgba(255,255,255,0.07);
  --border: rgba(255,255,255,0.08);
  --border-strong: rgba(255,255,255,0.16);
  --text: #f4f3ef;
  --text-dim: rgba(244,243,239,0.7);
  --text-mute: rgba(244,243,239,0.45);
  --amber: #e8b14e;
  --amber-glow: rgba(232,177,78,0.35);
  --cyan: #6ee7e7;
}

.serif { font-family: 'Cormorant Garamond', serif; }

/* ===== HERO ===== */
.pt-hero { position: relative; min-height: 92vh; overflow: hidden; isolation: isolate; }
.pt-hero-bg {
  position: absolute; inset: 0; z-index: -2;
  background-image:
    linear-gradient(180deg, rgba(7,7,11,0.35) 0%, rgba(7,7,11,0.55) 45%, rgba(7,7,11,0.95) 100%),
    url('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=2400&q=80');
  background-size: cover; background-position: center;
  animation: kenburns 28s ease-in-out infinite alternate;
}
.pt-hero-grain {
  position: absolute; inset: 0; z-index: -1; pointer-events: none;
  background:
    radial-gradient(circle at 20% 30%, rgba(232,177,78,0.18), transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(110,231,231,0.12), transparent 55%);
  mix-blend-mode: screen;
}
@keyframes kenburns { 0% { transform: scale(1); } 100% { transform: scale(1.12) translate(-1%, -2%); } }

.pt-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 28px clamp(20px, 5vw, 60px);
}
.pt-logo {
  display: flex; align-items: center; gap: 12px;
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem; font-weight: 600;
}
.pt-logo-mark {
  width: 38px; height: 38px; border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, var(--amber), #8a5a1e);
  box-shadow: 0 0 24px var(--amber-glow);
  display: flex; align-items: center; justify-content: center;
}
.pt-nav-links {
  display: flex; gap: 32px;
  font-size: 0.8rem; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--text-dim);
}
.pt-nav-links a { color: inherit; text-decoration: none; }
.pt-nav-links a:hover { color: var(--amber); }

.pt-hero-content {
  text-align: center;
  padding: 60px clamp(20px, 5vw, 60px) 100px;
  max-width: 980px; margin: 0 auto;
}
.pt-badge {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 9px 18px; border-radius: 999px;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border); backdrop-filter: blur(14px);
  font-size: 0.7rem; letter-spacing: 0.25em; text-transform: uppercase;
  color: var(--amber); margin-bottom: 28px;
}
.pt-badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--amber); box-shadow: 0 0 10px var(--amber-glow);
  animation: pulse 2s infinite;
}
.pt-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.6rem, 7vw, 5.2rem);
  font-weight: 500; line-height: 1.02; margin: 0 0 18px;
}
.pt-title em {
  font-style: italic;
  background: linear-gradient(120deg, var(--amber), #f5d28d);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.pt-subtitle {
  font-size: clamp(0.95rem, 1.4vw, 1.1rem);
  color: var(--text-dim); max-width: 56ch;
  line-height: 1.7; font-weight: 300;
  margin: 0 auto 32px;
}

/* ===== PROMPT (wraps Streamlit text_area) ===== */
.pt-prompt-wrap {
  max-width: 780px; margin: 0 auto;
  background: rgba(15,15,22,0.6);
  border: 1px solid var(--border-strong);
  border-radius: 22px; padding: 22px;
  backdrop-filter: blur(20px);
  box-shadow: 0 30px 60px -20px rgba(0,0,0,0.6);
}
.pt-prompt-label {
  font-size: 0.7rem; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--text-mute); margin-bottom: 10px;
}
.pt-prompt-wrap .stTextArea textarea {
  background: transparent !important;
  border: none !important; outline: none !important;
  color: var(--text) !important;
  font-size: 1.05rem !important; line-height: 1.6 !important;
  font-weight: 300 !important; padding: 0 !important;
  min-height: 110px !important; box-shadow: none !important;
}
.pt-prompt-wrap .stTextArea label { display: none !important; }
.pt-prompt-wrap div[data-testid="stTextArea"] > div { border: none !important; background: transparent !important; }

.stButton > button {
  background: linear-gradient(135deg, var(--amber), #d59437) !important;
  color: #1a1207 !important; font-weight: 700 !important;
  border: none !important; border-radius: 999px !important;
  padding: 12px 24px !important; letter-spacing: 0.04em !important;
  box-shadow: 0 12px 30px -8px var(--amber-glow) !important;
  transition: transform .2s, box-shadow .2s !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 18px 40px -8px var(--amber-glow) !important;
}

/* ===== SECTIONS ===== */
.pt-section {
  padding: 80px clamp(20px, 5vw, 60px);
  max-width: 1200px; margin: 0 auto;
}
.pt-section-head { display: flex; align-items: center; gap: 16px; margin-bottom: 36px; }
.pt-section-icon {
  width: 52px; height: 52px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem;
  background: var(--surface); border: 1px solid var(--border);
}
.pt-section-title { font-family: 'Cormorant Garamond', serif; font-size: clamp(1.8rem, 3vw, 2.4rem); font-weight: 500; margin: 0; }
.pt-section-sub  { color: var(--text-mute); font-size: 0.8rem; letter-spacing: 0.2em; text-transform: uppercase; margin: 0; }

/* ===== AGENT WORKFLOW ===== */
.pt-agents-wrap {
  max-width: 720px; margin: 0 auto;
  background: rgba(15,15,22,0.7);
  border: 1px solid var(--border-strong);
  border-radius: 22px; padding: 32px;
  backdrop-filter: blur(20px);
}
.pt-agents-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 18px; padding-bottom: 18px;
  border-bottom: 1px solid var(--border);
}
.pt-agents-title { font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; font-weight: 500; margin: 0; }
.pt-agents-count { font-size: 0.78rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--amber); }
.pt-agent-step {
  display: flex; gap: 16px; align-items: center;
  padding: 14px 0; border-bottom: 1px solid var(--border);
}
.pt-agent-step:last-child { border-bottom: none; }
.pt-agent-step.pending { opacity: 0.4; }
.pt-agent-step.done    { opacity: 0.75; }
.pt-agent-dot {
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--surface); border: 1.5px solid var(--border-strong);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.pt-agent-dot.active {
  border-color: var(--amber); background: rgba(232,177,78,0.12);
  animation: pulse-ring 1.4s infinite;
}
.pt-agent-dot.done-dot { border-color: var(--amber); color: var(--amber); background: rgba(232,177,78,0.1); }
.pt-agent-name { font-weight: 600; font-size: 0.98rem; }
.pt-agent-desc { font-size: 0.85rem; color: var(--text-mute); margin-top: 2px; }

/* ===== INSPIRATION ===== */
.pt-insp-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 22px; }
.pt-insp-card {
  position: relative; overflow: hidden;
  border-radius: 20px; height: 340px;
  border: 1px solid var(--border); isolation: isolate;
}
.pt-insp-img {
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  transition: transform 1.2s ease;
}
.pt-insp-card:hover .pt-insp-img { transform: scale(1.12); }
.pt-insp-card::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(180deg, transparent 30%, rgba(7,7,11,0.92) 100%);
}
.pt-insp-body { position: absolute; left: 0; right: 0; bottom: 0; padding: 22px; z-index: 2; }
.pt-insp-kicker { font-size: 0.7rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--amber); margin-bottom: 6px; }
.pt-insp-name { font-family: 'Cormorant Garamond', serif; font-size: 1.7rem; font-weight: 500; margin: 0 0 6px; }
.pt-insp-desc { color: var(--text-dim); font-size: 0.88rem; line-height: 1.5; }

/* ===== SAMPLE PLAN ===== */
.pt-sample-wrap {
  background: linear-gradient(160deg, rgba(232,177,78,0.06), rgba(110,231,231,0.03));
  border: 1px solid var(--border-strong);
  border-radius: 24px; padding: clamp(28px, 4vw, 48px);
  position: relative; overflow: hidden;
}
.pt-sample-wrap::before {
  content: ''; position: absolute; top: -50%; left: -10%;
  width: 480px; height: 480px;
  background: radial-gradient(circle, var(--amber-glow), transparent 70%);
  pointer-events: none; opacity: 0.6;
}
.pt-sample-head {
  display: flex; justify-content: space-between; align-items: flex-end;
  flex-wrap: wrap; gap: 16px; margin-bottom: 28px; position: relative;
}
.pt-sample-title { font-family: 'Cormorant Garamond', serif; font-size: clamp(1.8rem, 3vw, 2.4rem); font-weight: 500; margin: 0; }
.pt-sample-chip {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-radius: 999px;
  background: rgba(232,177,78,0.12); color: var(--amber);
  border: 1px solid rgba(232,177,78,0.3);
  font-size: 0.72rem; letter-spacing: 0.18em; text-transform: uppercase;
}
.pt-sample-grid {
  display: grid; grid-template-columns: 1.4fr 1fr;
  gap: 24px; position: relative;
}
@media (max-width: 820px) { .pt-sample-grid { grid-template-columns: 1fr; } }
.pt-sample-day {
  background: rgba(15,15,22,0.55);
  border: 1px solid var(--border);
  border-left: 3px solid var(--amber);
  border-radius: 14px; padding: 18px 22px; margin-bottom: 14px;
}
.pt-sample-day h4 { font-family: 'Cormorant Garamond', serif; margin: 0 0 6px; color: var(--amber); font-size: 1.2rem; font-weight: 500; }
.pt-sample-day p  { margin: 0; color: var(--text-dim); font-size: 0.92rem; line-height: 1.6; }
.pt-sample-stats {
  background: rgba(15,15,22,0.6);
  border: 1px solid var(--border-strong);
  border-radius: 18px; padding: 22px;
}
.pt-sample-stat {
  display: flex; justify-content: space-between;
  padding: 10px 0; border-bottom: 1px solid var(--border); font-size: 0.92rem;
}
.pt-sample-stat:last-child { border-bottom: none; }
.pt-sample-stat span:first-child { color: var(--text-mute); }
.pt-sample-stat span:last-child  { color: var(--amber); font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 600; }

/* ===== DEST / WEATHER / ATTRACTIONS / ITINERARY / BUDGET / TIPS ===== */
.pt-dest {
  background: linear-gradient(135deg, rgba(232,177,78,0.08), rgba(110,231,231,0.04));
  border: 1px solid var(--border-strong);
  border-radius: 22px; padding: 40px;
  max-width: 860px; margin: 0 auto; position: relative; overflow: hidden;
}
.pt-dest::before {
  content: ''; position: absolute; top: -40%; right: -10%;
  width: 380px; height: 380px;
  background: radial-gradient(circle, var(--amber-glow), transparent 70%);
}
.pt-dest-name { font-family: 'Cormorant Garamond', serif; font-size: clamp(2.2rem, 4vw, 3rem); font-weight: 500; margin: 0 0 14px; position: relative; }
.pt-dest-desc { color: var(--text-dim); font-size: 1.05rem; line-height: 1.7; font-weight: 300; margin: 0 0 24px; position: relative; }
.pt-tag { padding: 7px 14px; border-radius: 999px; background: rgba(255,255,255,0.06); border: 1px solid var(--border); font-size: 0.82rem; color: var(--text-dim); display: inline-block; margin: 4px; }

.pt-weather-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 16px; }
.pt-weather-card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 24px; text-align: center; }
.pt-weather-icon { font-size: 2.2rem; margin-bottom: 10px; }
.pt-weather-val  { font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 600; }
.pt-weather-key  { font-size: 0.76rem; color: var(--text-mute); margin-top: 6px; letter-spacing: 0.1em; text-transform: uppercase; }

.pt-attr-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px,1fr)); gap: 22px; }
.pt-attr-card { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 28px; transition: all .3s; }
.pt-attr-card:hover { transform: translateY(-6px); border-color: var(--amber); box-shadow: 0 20px 40px -20px var(--amber-glow); }
.pt-attr-num  { font-family: 'Cormorant Garamond', serif; font-style: italic; color: var(--amber); font-size: 0.95rem; margin-bottom: 10px; }
.pt-attr-name { font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; font-weight: 500; margin: 0 0 8px; }
.pt-attr-desc { color: var(--text-mute); font-size: 0.92rem; line-height: 1.6; }

.pt-day { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--amber); border-radius: 18px; padding: 28px; margin-bottom: 18px; }
.pt-day-name { font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 500; margin: 0 0 18px; color: var(--amber); }
.pt-timeline { display: flex; gap: 14px; padding: 12px 0; border-bottom: 1px solid var(--border); }
.pt-timeline:last-child { border-bottom: none; }
.pt-timeline-dot  { width: 8px; height: 8px; border-radius: 50%; background: var(--amber); margin-top: 8px; flex-shrink: 0; box-shadow: 0 0 10px var(--amber-glow); }
.pt-timeline-text { color: var(--text-dim); font-size: 0.96rem; line-height: 1.7; }

.pt-budget-item { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 18px; margin-bottom: 12px; }
.pt-budget-row  { display: flex; justify-content: space-between; margin-bottom: 12px; }
.pt-budget-label  { font-weight: 500; font-size: 0.95rem; }
.pt-budget-amount { font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 1.1rem; color: var(--amber); }
.pt-bar-bg   { width: 100%; height: 6px; border-radius: 999px; background: rgba(255,255,255,0.06); overflow: hidden; }
.pt-bar-fill { height: 100%; border-radius: 999px; }
.pt-total {
  background: linear-gradient(135deg, rgba(232,177,78,0.18), rgba(110,231,231,0.08));
  border: 1px solid var(--border-strong);
  border-radius: 22px; padding: 32px; text-align: center;
}
.pt-total-label { font-size: 0.74rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--text-mute); margin-bottom: 10px; }
.pt-total-amt   { font-family: 'Cormorant Garamond', serif; font-size: clamp(2rem, 4vw, 2.8rem); font-weight: 600; color: var(--amber); }

.pt-tip { display: flex; gap: 16px; background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 18px 22px; margin-bottom: 10px; }
.pt-tip-icon { font-size: 1.3rem; }
.pt-tip-text { color: var(--text-dim); line-height: 1.6; font-size: 0.96rem; }

/* ===== FOOTER ===== */
.pt-footer {
  position: relative; margin-top: 60px;
  padding: 80px clamp(20px, 5vw, 60px) 32px;
  border-top: 1px solid var(--border);
  background:
    radial-gradient(circle at 20% 0%, rgba(232,177,78,0.10), transparent 50%),
    radial-gradient(circle at 80% 100%, rgba(110,231,231,0.06), transparent 50%),
    var(--bg-2);
  overflow: hidden;
}
.pt-footer-cta {
  max-width: 1200px; margin: 0 auto 50px;
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 24px;
  padding-bottom: 50px; border-bottom: 1px solid var(--border);
}
.pt-footer-cta h3 {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  font-weight: 500; margin: 0; max-width: 22ch;
}
.pt-footer-cta p { color: var(--text-mute); margin: 8px 0 0; max-width: 40ch; }
.pt-footer-grid {
  max-width: 1200px; margin: 0 auto;
  display: grid; grid-template-columns: 1.4fr repeat(3, 1fr); gap: 40px;
}
@media (max-width: 820px) {
  .pt-footer-grid { grid-template-columns: 1fr 1fr; gap: 32px; }
  .pt-footer-cta  { flex-direction: column; align-items: flex-start; }
}
.pt-footer-brand .pt-logo { margin-bottom: 14px; }
.pt-footer-tag { color: var(--text-dim); font-size: 0.92rem; line-height: 1.6; max-width: 32ch; }
.pt-footer-col h5 { font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--amber); margin: 0 0 16px; }
.pt-footer-col ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.pt-footer-col a  { color: var(--text-dim); text-decoration: none; font-size: 0.92rem; }
.pt-footer-col a:hover { color: var(--amber); }
.pt-footer-bottom {
  max-width: 1200px; margin: 50px auto 0;
  padding-top: 24px; border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px; color: var(--text-mute); font-size: 0.82rem;
}
.pt-footer-mark { font-family: 'Cormorant Garamond', serif; font-style: italic; color: var(--amber); font-size: 1.1rem; }
.pt-footer-socials { display: flex; gap: 10px; }
.pt-footer-social {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text-dim); text-decoration: none;
}
.pt-footer-social:hover { color: var(--amber); border-color: var(--amber); }
.pt-footer-watermark {
  position: absolute; bottom: -60px; left: 50%;
  transform: translateX(-50%);
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(8rem, 22vw, 20rem);
  font-style: italic; font-weight: 500;
  color: rgba(232,177,78,0.04);
  pointer-events: none; white-space: nowrap; letter-spacing: -0.03em;
}

@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.6; transform: scale(1.15); } }
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 var(--amber-glow); }
  70%  { box-shadow: 0 0 0 10px rgba(232,177,78,0); }
  100% { box-shadow: 0 0 0 0 rgba(232,177,78,0); }
}
.pt-fade-in { animation: fadeUp .8s ease both; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 720px) {
  .pt-nav-links { display: none; }
  .pt-section { padding: 60px 20px; }
  .pt-dest { padding: 28px; }
  .pt-insp-card { height: 280px; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

def extract_number(v):
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        digits = "".join(c for c in v if c.isdigit() or c == ".")
        try:
            return float(digits) if digits else 0.0
        except ValueError:
            return 0.0
    return 0.0


def call_backend(user_query: str):
    res = requests.post(
        BACKEND_URL,
        json={"user_query": user_query},
        timeout=120,
    )
    res.raise_for_status()
    return res.json()




if "query" not in st.session_state:
    st.session_state.query = ""
if "plan" not in st.session_state:
    st.session_state.plan = None
if "error" not in st.session_state:
    st.session_state.error = None


st.markdown(
    """
    <section class="pt-hero">
      <div class="pt-hero-bg"></div>
      <div class="pt-hero-grain"></div>
      <nav class="pt-nav">
        <div class="pt-logo">
          <span class="pt-logo-mark">✦</span>
          <span>Pātheyātrā <em style="font-style:italic;color:var(--amber)">AI</em></span>
        </div>
        <div class="pt-nav-links">
          <a href="#inspiration">Inspiration</a>
          <a href="#sample">Example</a>
          <a href="#how">How it works</a>
        </div>
      </nav>
      <div class="pt-hero-content">
        <div class="pt-badge"><span class="pt-badge-dot"></span> Cinematic AI Travel Planning</div>
        <h1 class="pt-title">Your perfect <em>journey</em> awaits</h1>
        <p class="pt-subtitle">
          Describe a dream — a city, a season, a budget. Our multi-agent AI composes a
          tailored itinerary, weather brief, budget breakdown, and insider tips in seconds.
        </p>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

left, mid, right = st.columns([1, 4, 1])
with mid:
    st.markdown('<div class="pt-prompt-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="pt-prompt-label">✈ Where do you want to go?</div>', unsafe_allow_html=True)
    st.session_state.query = st.text_area(
        "prompt",
        value=st.session_state.query,
        placeholder='e.g. "Plan a 7-day trip to Japan in October for 2 people with a ₹80,000 budget, including Tokyo, Kyoto and Osaka."',
        label_visibility="collapsed",
        height=120,
        key="prompt_input",
    )
    cta_col1, cta_col2 = st.columns([3, 2])
    with cta_col2:
        generate = st.button("✦  Generate My Plan", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:24px;">', unsafe_allow_html=True)
    pill_cols = st.columns(len(EXAMPLES))
    for i, ex in enumerate(EXAMPLES):
        with pill_cols[i]:
            if st.button(ex, key=f"pill_{i}", use_container_width=True):
                clean = ex.split(" ", 1)[1] if " " in ex else ex
                st.session_state.query = clean
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
 
plan_slot = st.empty()
if st.session_state.plan:
    with plan_slot:
        render_plan(st.session_state.plan)

if st.session_state.error:
    st.markdown(
        f"""
        <div class="pt-section">
          <div style="max-width:780px;margin:0 auto;background:rgba(240,163,163,0.08);
                      border:1px solid rgba(240,163,163,0.3);color:#f0a3a3;
                      padding:18px 22px;border-radius:14px;">{st.session_state.error}</div>
          <div style="max-width:780px;margin:12px auto 0;background:rgba(110,231,231,0.06);
                      border:1px solid rgba(110,231,231,0.2);color:rgba(244,243,239,0.7);
                      padding:14px 18px;border-radius:12px;font-size:0.9rem;">
            ℹ️ Make sure your FastAPI backend is running:
            <code style="background:rgba(0,0,0,0.4);padding:2px 8px;border-radius:4px;color:#6ee7e7;">
              uvicorn main:app --host 127.0.0.1 --port 8000
            </code>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_plan(plan):
    if not isinstance(plan, dict) or plan.get("error") or not plan.get("intent"):
        st.markdown('<div class="pt-section">', unsafe_allow_html=True)
        st.warning("Backend response missing required data.")
        st.json(plan)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    intent     = plan.get("intent", {})
    research   = plan.get("research", {})
    weather    = plan.get("weather", {})
    itinerary  = plan.get("itinerary", {})
    budget     = plan.get("budget", {})

    dest_name = intent.get("destination")
    if dest_name:
        st.markdown('<div class="pt-section pt-fade-in">', unsafe_allow_html=True)
        section_head("🌍", "Destination Overview", "Where you're going")
        tags = intent.get("preferences", []) or []
        tag_html = "".join(f'<span class="pt-tag">{t}</span>' for t in tags[:6])
        meta_html = ""
        for label, val in [
            ("📅 Best Time", research.get("best_time_to_visit")),
            ("⏱ Duration",  intent.get("duration")),
            ("💳 Budget",    intent.get("budget")),
        ]:
            if val:
                meta_html += f"""
                <div style="background:rgba(0,0,0,0.25);border:1px solid var(--border);
                            border-radius:14px;padding:18px;">
                  <div style="font-size:0.7rem;letter-spacing:0.2em;text-transform:uppercase;
                              color:var(--text-mute);margin-bottom:8px;">{label}</div>
                  <div style="font-family:'Cormorant Garamond',serif;font-size:1.4rem;font-weight:500;">{val}</div>
                </div>"""
        dest_desc_html = f'<p class="pt-dest-desc">{research.get("weather","")}</p>' if research.get("weather") else ''
        st.markdown(
            f"""
            <div class="pt-dest">
              <h3 class="pt-dest-name">{dest_name}</h3>
              {dest_desc_html}
              <div style="position:relative;">{tag_html}</div>
              <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
                          gap:16px;margin-top:28px;position:relative;">{meta_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if weather:
        cards = [
            ("🌡", weather.get("temperature") or weather.get("avg_temperature") or "—", "Temperature"),
            ("⛅", weather.get("condition")   or weather.get("description")     or "—", "Condition"),
            ("💧", weather.get("humidity")    or "—", "Humidity"),
        ]
        if weather.get("wind_speed") or weather.get("wind"):
            cards.append(("💨", weather.get("wind_speed") or weather.get("wind"), "Wind"))
        if weather.get("uv_index") or weather.get("uv"):
            cards.append(("☀️", weather.get("uv_index") or weather.get("uv"), "UV Index"))
        if weather.get("rainfall") or weather.get("rain_chance"):
            cards.append(("🌧", weather.get("rainfall") or weather.get("rain_chance"), "Rain"))

        st.markdown('<div class="pt-section pt-fade-in">', unsafe_allow_html=True)
        section_head("🌤", "Weather & Climate", "Conditions on the ground")
        cards_html = "".join(
            f'<div class="pt-weather-card"><div class="pt-weather-icon">{i}</div>'
            f'<div class="pt-weather-val">{v}</div><div class="pt-weather-key">{k}</div></div>'
            for i, v, k in cards
        )
        st.markdown(f'<div class="pt-weather-grid">{cards_html}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    attractions = research.get("attractions", []) or []
    if attractions:
        st.markdown('<div class="pt-section pt-fade-in">', unsafe_allow_html=True)
        section_head("🏛", "Top Attractions", "What you can't miss")
        cards = []
        for i, a in enumerate(attractions):
            if isinstance(a, str):
              name, desc = a, ""
            else:
              name = a.get("name", f"Attraction {i+1}")
              desc = a.get("description") or a.get("details") or a.get("category") or ""
            desc_html = f'<div class="pt-attr-desc">{desc}</div>' if desc else ''
            cards.append(
              f'<div class="pt-attr-card"><div class="pt-attr-num">— {i+1:02d}</div>'
              f'<div class="pt-attr-name">{name}</div>'
              f'{desc_html}</div>'
            )
        st.markdown(f'<div class="pt-attr-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    days = (itinerary or {}).get("days", {}) or {}
    if days:
        st.markdown('<div class="pt-section pt-fade-in">', unsafe_allow_html=True)
        section_head("📅", "Day-by-Day Itinerary", "Your journey, hour by hour")
        st.markdown('<div style="max-width:900px;margin:0 auto;">', unsafe_allow_html=True)
        for day, acts in days.items():
            acts = acts if isinstance(acts, list) else [acts]
            timeline = "".join(
                f'<div class="pt-timeline"><div class="pt-timeline-dot"></div>'
                f'<div class="pt-timeline-text">{a if isinstance(a,str) else json.dumps(a)}</div></div>'
                for a in acts
            )
            st.markdown(
                f'<div class="pt-day"><h3 class="pt-day-name">{day}</h3>{timeline}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div></div>", unsafe_allow_html=True)

    if budget:
        items, total = {}, 0.0
        for k, v in budget.items():
            if k.lower() in ("total", "total_cost", "grand_total"):
                total = extract_number(v)
            else:
                items[k] = extract_number(v)
        if not total:
            total = sum(items.values())

        st.markdown('<div class="pt-section pt-fade-in">', unsafe_allow_html=True)
        section_head("💰", "Budget Breakdown", "Where your money goes")
        bcol1, bcol2 = st.columns([1.4, 1])
        with bcol1:
            for k, v in items.items():
                pct = (v / total * 100) if total else 0
                color, icon = BUDGET_PALETTE.get(k.lower(), ("#888", "•"))
                st.markdown(
                    f"""
                    <div class="pt-budget-item">
                      <div class="pt-budget-row">
                        <span class="pt-budget-label">{icon} {k.replace('_',' ').title()}</span>
                        <span class="pt-budget-amount">₹{v:,.0f}</span>
                      </div>
                      <div class="pt-bar-bg"><div class="pt-bar-fill"
                        style="width:{pct:.1f}%;background:{color};"></div></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        with bcol2:
            days_n = len(days)
            per_day = (total / days_n) if days_n and total else 0
            largest = max(items.items(), key=lambda kv: kv[1]) if items else None
            extras = ""
            if per_day:
                extras += f'<div class="pt-sample-stat"><span>📊 Per-Day Avg</span><span>₹{per_day:,.0f}</span></div>'
            if largest and total:
                extras += (
                    f'<div class="pt-sample-stat"><span>🔺 Biggest Spend</span>'
                    f'<span>{largest[0].title()} · {largest[1]/total*100:.0f}%</span></div>'
                )
            if days_n:
                extras += f'<div class="pt-sample-stat"><span>📆 Days</span><span>{days_n}</span></div>'
            st.markdown(
                f"""
                <div class="pt-total">
                  <div class="pt-total-label">Estimated Total</div>
                  <div class="pt-total-amt">₹{total:,.0f}</div>
                  <div style="display:grid;gap:6px;text-align:left;border-top:1px solid var(--border);
                              padding-top:18px;margin-top:18px;">{extras}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    tips = research.get("local_transport", []) or []
    if tips:
        st.markdown('<div class="pt-section pt-fade-in">', unsafe_allow_html=True)
        section_head("💡", "Travel Tips & Essentials", "Insider knowledge")
        icons = ["🛂", "💊", "📱", "🔌", "💬", "🏧", "🧥", "🛡"]
        arr = tips if isinstance(tips, list) else [tips]
        for i, t in enumerate(arr):
            text = t if isinstance(t, str) else (t.get("tip") if isinstance(t, dict) else json.dumps(t))
            st.markdown(
                f'<div class="pt-tip"><span class="pt-tip-icon">{icons[i % len(icons)]}</span>'
                f'<span class="pt-tip-text">{text}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# plan rendering will be placed above the Inspiration section so it appears earlier

if generate:
    q = (st.session_state.query or "").strip()
    if not q:
        st.session_state.error = "Please describe your trip before generating a plan."
        st.session_state.plan = None
    else:
        st.session_state.error = None
        st.session_state.plan = None

        st.markdown('<div class="pt-section pt-fade-in" id="agents">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="pt-agents-wrap">
              <div class="pt-agents-head">
                <h3 class="pt-agents-title">AI agents at work</h3>
                <span class="pt-agents-count">0 / {len(AGENTS)}</span>
              </div>
            """,
            unsafe_allow_html=True,
        )
        agent_slot = st.empty()

        try:
          for i in range(len(AGENTS) - 1):
            render_agents(agent_slot, i, AGENTS)
            time.sleep(0.55)
            render_agents(agent_slot, len(AGENTS) - 1, AGENTS)
            data = call_backend(q)
            render_agents(agent_slot, len(AGENTS), AGENTS)
            time.sleep(0.3)
            st.session_state.plan = data
            # Render into the persistent placeholder created above so the plan
            # appears immediately below the hero (centered area)
            try:
              with plan_slot:
                render_plan(data)
            except Exception:
              pass
        except requests.exceptions.ConnectionError:
            st.session_state.error = f"🔌 Cannot reach the backend at {BACKEND_URL}. Make sure FastAPI is running."
        except requests.exceptions.HTTPError as e:
            st.session_state.error = f"🚫 Backend error: {e}"
        except Exception as e:
            st.session_state.error = f"⚠️ {e}"
        finally:
            st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown('<div class="pt-section" id="inspiration">', unsafe_allow_html=True)
section_head("🌅", "Wander somewhere new", "Inspiration · Tap any place to plan")

cards_html = ""
for p in INSPIRATIONS:
    cards_html += f"""
    <div class="pt-insp-card">
      <div class="pt-insp-img" style="background-image:url('{p['img']}');"></div>
      <div class="pt-insp-body">
        <div class="pt-insp-kicker">{p['kicker']}</div>
        <h3 class="pt-insp-name">{p['name']}</h3>
        <p class="pt-insp-desc">{p['desc']}</p>
      </div>
    </div>
    """
st.markdown(f'<div class="pt-insp-grid">{cards_html}</div>', unsafe_allow_html=True)

st.markdown('<div style="max-width:1200px;margin:22px auto 0;">', unsafe_allow_html=True)
insp_cols = st.columns(3)
for i, p in enumerate(INSPIRATIONS):
    with insp_cols[i % 3]:
        if st.button(f"✦  Plan {p['name']}", key=f"insp_{i}", use_container_width=True):
            st.session_state.query = p["query"]
            st.rerun()
st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown('<div class="pt-section" id="sample">', unsafe_allow_html=True)
section_head("📜", "A taste of what you'll get", "Example plan · Generated in seconds")

days_html = "".join(
    f'<div class="pt-sample-day"><h4>{name}</h4><p>{text}</p></div>'
    for name, text in SAMPLE_PLAN["days"]
)
stats_html = "".join(
    f'<div class="pt-sample-stat"><span>{k}</span><span>{v}</span></div>'
    for k, v in SAMPLE_PLAN["stats"]
)
st.markdown(
    f"""
    <div class="pt-sample-wrap">
      <div class="pt-sample-head">
        <h3 class="pt-sample-title">{SAMPLE_PLAN['title']}</h3>
        <span class="pt-sample-chip">✦ {SAMPLE_PLAN['chip']}</span>
      </div>
      <div class="pt-sample-grid">
        <div>{days_html}</div>
        <div><div class="pt-sample-stats">{stats_html}</div></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <footer class="pt-footer" id="how">
      <div class="pt-footer-cta">
        <div>
          <h3>Ready to compose your next <em style="font-style:italic;color:var(--amber)">journey</em>?</h3>
          <p>Tell us where your mind keeps wandering. We'll handle the rest.</p>
        </div>
      </div>

      <div class="pt-footer-grid">
        <div class="pt-footer-brand">
          <div class="pt-logo">
            <span class="pt-logo-mark">✦</span>
            <span>Pātheyātrā <em style="font-style:italic;color:var(--amber)">AI</em></span>
          </div>
          <p class="pt-footer-tag">
            A cinematic, multi-agent travel companion that turns a single sentence into a
            complete journey — itinerary, weather, budget, and insider tips.
          </p>
        </div>

        <div class="pt-footer-col">
          <h5>Explore</h5>
          <ul>
            <li><a href="#inspiration">Destinations</a></li>
            <li><a href="#sample">Example plan</a></li>
            <li><a href="#agents">Agents</a></li>
          </ul>
        </div>

        <div class="pt-footer-col">
          <h5>Agents</h5>
          <ul>
            <li><a href="#agents">Intent · Research</a></li>
            <li><a href="#agents">Itinerary · Budget</a></li>
            <li><a href="#agents">Weather · Finalizer</a></li>
          </ul>
        </div>

        <div class="pt-footer-col">
          <h5>Company</h5>
          <ul>
            <li><a href="#">About</a></li>
            <li><a href="#">Contact</a></li>
            <li><a href="#">Privacy</a></li>
          </ul>
        </div>
      </div>

      <div class="pt-footer-bottom">
        <div>© 2026 <span class="pt-footer-mark">Pātheyātrā AI</span> · Crafted with multi-agent intelligence</div>
        <div class="pt-footer-socials">
          <a class="pt-footer-social" href="#" aria-label="Twitter">𝕏</a>
          <a class="pt-footer-social" href="#" aria-label="Instagram">◎</a>
          <a class="pt-footer-social" href="#" aria-label="GitHub">⌥</a>
          <a class="pt-footer-social" href="#" aria-label="Email">✉</a>
        </div>
      </div>

      <div class="pt-footer-watermark" aria-hidden="true">pātheyātrā</div>
    </footer>
    """,
    unsafe_allow_html=True,
)

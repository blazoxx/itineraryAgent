import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";

export const Route = createFileRoute("/")({
  component: Index,
});

/* ============================================================
   BACKEND CONTRACT — UNCHANGED
   POST {BACKEND_URL}  body: { user_query: string }
   Response shape: { intent, research, weather, itinerary, budget }
   ============================================================ */
const BACKEND_URL =
  (import.meta.env.VITE_BACKEND_URL as string | undefined) ??
  "http://127.0.0.1:8000/generate-plan";

const EXAMPLES = [
  "🏯 Japan · 10 days · ¥200k budget",
  "🏖 Bali · Honeymoon · 7 nights",
  "🗼 Europe · Paris & Rome · 2 weeks",
  "🏔 Patagonia · Trekking · 12 days",
  "🌴 Thailand · Backpacker · ₹50k",
  "🏜 Morocco · Desert · 5 days",
];

const AGENTS = [
  { icon: "🧭", name: "Intent Agent", desc: "Understanding your travel goals" },
  { icon: "🔍", name: "Research Agent", desc: "Fetching destination insights" },
  {
    icon: "📅",
    name: "Itinerary Agent",
    desc: "Crafting your day-by-day plan",
  },
  { icon: "💰", name: "Budget Agent", desc: "Calculating costs & optimizing" },
  { icon: "☁️", name: "Weather Agent", desc: "Live weather conditions" },
  { icon: "✨", name: "Finalizer", desc: "Compiling your travel plan" },
];

const BUDGET_PALETTE: Record<string, { color: string; icon: string }> = {
  hotel: { color: "#22d3ee", icon: "🏨" },
  accommodation: { color: "#22d3ee", icon: "🏨" },
  food: { color: "#34d399", icon: "🍜" },
  meals: { color: "#34d399", icon: "🍜" },
  flights: { color: "#a78bfa", icon: "🛫" },
  transport: { color: "#fb923c", icon: "🚌" },
  transportation: { color: "#fb923c", icon: "🚌" },
  activities: { color: "#f59e0b", icon: "🎯" },
  entertainment: { color: "#f59e0b", icon: "🎯" },
  misc: { color: "#f87171", icon: "🧳" },
  miscellaneous: { color: "#f87171", icon: "🧳" },
};

function extractNumber(value: unknown): number {
  if (typeof value === "number") return value;
  if (typeof value === "string") {
    const n = parseFloat(value.replace(/[^\d.]/g, ""));
    return isNaN(n) ? 0 : n;
  }
  return 0;
}

/* ============================================================
   Inline CSS — cinematic dark theme
   ============================================================ */
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

.pt-root {
  --bg: #07070b;
  --bg-2: #0d0d14;
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
  --rose: #f0a3a3;
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--text);
  background: var(--bg);
  min-height: 100vh;
  overflow-x: hidden;
}

.pt-root *, .pt-root *::before, .pt-root *::after { box-sizing: border-box; }
.pt-root .serif { font-family: 'Cormorant Garamond', serif; }

/* ===== HERO ===== */
.pt-hero {
  position: relative;
  min-height: 100vh;
  width: 100%;
  overflow: hidden;
  isolation: isolate;
}
.pt-hero-bg {
  position: absolute; inset: 0; z-index: -2;
  background-image:
    linear-gradient(180deg, rgba(7,7,11,0.35) 0%, rgba(7,7,11,0.55) 45%, rgba(7,7,11,0.95) 100%),
    url('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=2400&q=80');
  background-size: cover;
  background-position: center;
  animation: kenburns 28s ease-in-out infinite alternate;
}
.pt-hero-grain {
  position: absolute; inset: 0; z-index: -1; pointer-events: none;
  background:
    radial-gradient(circle at 20% 30%, rgba(232,177,78,0.18), transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(110,231,231,0.12), transparent 55%);
  mix-blend-mode: screen;
}
@keyframes kenburns {
  0%   { transform: scale(1) translate(0,0); }
  100% { transform: scale(1.12) translate(-1%, -2%); }
}

.pt-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 28px clamp(20px, 5vw, 60px);
  position: relative; z-index: 10;
}
.pt-logo {
  display: flex; align-items: center; gap: 12px;
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem; font-weight: 600; letter-spacing: 0.02em;
}
.pt-logo-mark {
  width: 38px; height: 38px; border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, var(--amber), #8a5a1e);
  box-shadow: 0 0 24px var(--amber-glow);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.05rem;
}
.pt-nav-links {
  display: flex; gap: 32px;
  font-size: 0.85rem; letter-spacing: 0.15em; text-transform: uppercase;
  color: var(--text-dim);
}
.pt-nav-links a { color: inherit; text-decoration: none; transition: color .2s; }
.pt-nav-links a:hover { color: var(--amber); }

.pt-hero-content {
  display: flex; flex-direction: column; align-items: center;
  text-align: center;
  padding: clamp(40px, 8vh, 90px) clamp(20px, 5vw, 60px) 80px;
  max-width: 1100px; margin: 0 auto;
  position: relative; z-index: 5;
}
.pt-badge {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 9px 18px; border-radius: 999px;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border);
  backdrop-filter: blur(14px);
  font-size: 0.7rem; letter-spacing: 0.25em; text-transform: uppercase;
  color: var(--amber);
  margin-bottom: 28px;
}
.pt-badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--amber); box-shadow: 0 0 10px var(--amber-glow);
  animation: pulse 2s infinite;
}
.pt-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.6rem, 7vw, 5.2rem);
  font-weight: 500; line-height: 1.02; letter-spacing: -0.015em;
  margin: 0 0 18px; max-width: 16ch;
}
.pt-title em {
  font-style: italic; color: var(--amber);
  background: linear-gradient(120deg, var(--amber), #f5d28d);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.pt-subtitle {
  font-size: clamp(0.95rem, 1.4vw, 1.1rem);
  color: var(--text-dim); max-width: 56ch;
  line-height: 1.7; font-weight: 300;
  margin: 0 0 44px;
}

/* ===== PROMPT BOX ===== */
.pt-prompt {
  width: 100%; max-width: 760px;
  background: rgba(15,15,22,0.6);
  border: 1px solid var(--border-strong);
  border-radius: 22px;
  padding: 22px;
  backdrop-filter: blur(20px);
  box-shadow:
    0 30px 60px -20px rgba(0,0,0,0.6),
    0 0 0 1px rgba(255,255,255,0.02) inset;
  transition: border-color .3s, box-shadow .3s;
}
.pt-prompt:focus-within {
  border-color: var(--amber);
  box-shadow:
    0 30px 60px -20px rgba(0,0,0,0.6),
    0 0 0 4px rgba(232,177,78,0.12);
}
.pt-prompt-label {
  font-size: 0.7rem; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--text-mute); margin-bottom: 14px;
  display: flex; align-items: center; gap: 8px;
}
.pt-textarea {
  width: 100%; min-height: 110px;
  background: transparent; border: none; outline: none; resize: none;
  color: var(--text); font-family: inherit;
  font-size: 1.05rem; line-height: 1.6; font-weight: 300;
  padding: 0;
}
.pt-textarea::placeholder { color: var(--text-mute); font-style: italic; }
.pt-prompt-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 18px; padding-top: 16px;
  border-top: 1px solid var(--border);
  gap: 12px; flex-wrap: wrap;
}
.pt-hint { font-size: 0.78rem; color: var(--text-mute); }
.pt-cta {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 12px 24px; border-radius: 999px;
  background: linear-gradient(135deg, var(--amber), #d59437);
  color: #1a1207; font-family: inherit; font-weight: 700;
  font-size: 0.92rem; letter-spacing: 0.04em;
  border: none; cursor: pointer;
  box-shadow: 0 12px 30px -8px var(--amber-glow);
  transition: transform .2s, box-shadow .2s;
}
.pt-cta:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 18px 40px -8px var(--amber-glow);
}
.pt-cta:disabled { opacity: 0.55; cursor: not-allowed; }

/* ===== PILLS ===== */
.pt-pills {
  display: flex; flex-wrap: wrap; gap: 10px;
  justify-content: center; margin-top: 30px;
  max-width: 760px;
}
.pt-pill {
  padding: 9px 16px; border-radius: 999px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  color: var(--text-dim); font-size: 0.84rem;
  cursor: pointer; transition: all .2s;
  backdrop-filter: blur(10px);
}
.pt-pill:hover {
  color: var(--amber); border-color: var(--amber);
  transform: translateY(-2px);
  background: rgba(232,177,78,0.08);
}

/* ===== SECTIONS ===== */
.pt-section {
  padding: 80px clamp(20px, 5vw, 60px);
  max-width: 1200px; margin: 0 auto;
}
.pt-section-head {
  display: flex; align-items: center; gap: 16px;
  margin-bottom: 36px;
}
.pt-section-icon {
  width: 52px; height: 52px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem;
  background: var(--surface); border: 1px solid var(--border);
}
.pt-section-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 500; margin: 0; letter-spacing: -0.01em;
}
.pt-section-sub {
  color: var(--text-mute); font-size: 0.85rem;
  letter-spacing: 0.2em; text-transform: uppercase;
  margin: 0;
}

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
  margin-bottom: 22px; padding-bottom: 18px;
  border-bottom: 1px solid var(--border);
}
.pt-agents-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.4rem; font-weight: 500; margin: 0;
}
.pt-agents-count {
  font-size: 0.8rem; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--amber);
}
.pt-agent-step {
  display: flex; gap: 16px; align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
  transition: opacity .3s;
}
.pt-agent-step:last-child { border-bottom: none; }
.pt-agent-step.pending { opacity: 0.4; }
.pt-agent-step.done { opacity: 0.75; }
.pt-agent-dot {
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--surface); border: 1.5px solid var(--border-strong);
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; flex-shrink: 0;
}
.pt-agent-dot.active {
  border-color: var(--amber);
  background: rgba(232,177,78,0.12);
  box-shadow: 0 0 0 0 var(--amber-glow);
  animation: pulse-ring 1.4s infinite;
}
.pt-agent-dot.done-dot {
  border-color: var(--amber); color: var(--amber);
  background: rgba(232,177,78,0.1);
}
.pt-agent-name {
  font-weight: 600; font-size: 0.98rem;
}
.pt-agent-desc {
  font-size: 0.85rem; color: var(--text-mute); margin-top: 2px;
}

/* ===== DEST CARD ===== */
.pt-dest {
  background: linear-gradient(135deg, rgba(232,177,78,0.08), rgba(110,231,231,0.04));
  border: 1px solid var(--border-strong);
  border-radius: 22px; padding: 40px;
  max-width: 860px; margin: 0 auto;
  position: relative; overflow: hidden;
}
.pt-dest::before {
  content: ''; position: absolute; top: -40%; right: -10%;
  width: 380px; height: 380px;
  background: radial-gradient(circle, var(--amber-glow), transparent 70%);
  pointer-events: none;
}
.pt-dest-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.2rem, 4vw, 3rem);
  font-weight: 500; margin: 0 0 14px;
  letter-spacing: -0.02em; position: relative;
}
.pt-dest-desc {
  color: var(--text-dim); font-size: 1.05rem;
  line-height: 1.7; font-weight: 300; margin: 0 0 24px;
  position: relative;
}
.pt-dest-tags {
  display: flex; flex-wrap: wrap; gap: 8px;
  position: relative;
}
.pt-tag {
  padding: 7px 14px; border-radius: 999px;
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--border);
  font-size: 0.82rem; color: var(--text-dim);
}
.pt-meta-row {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
  gap: 16px; margin-top: 28px; position: relative;
}
.pt-meta {
  background: rgba(0,0,0,0.25); border: 1px solid var(--border);
  border-radius: 14px; padding: 18px;
}
.pt-meta-label {
  font-size: 0.72rem; letter-spacing: 0.2em;
  text-transform: uppercase; color: var(--text-mute);
  margin-bottom: 8px;
}
.pt-meta-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.4rem; font-weight: 500;
}

/* ===== WEATHER GRID ===== */
.pt-weather-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px,1fr));
  gap: 16px;
}
.pt-weather-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 16px; padding: 24px; text-align: center;
  transition: transform .25s, border-color .25s;
}
.pt-weather-card:hover {
  transform: translateY(-4px);
  border-color: var(--border-strong);
}
.pt-weather-icon { font-size: 2.2rem; margin-bottom: 10px; }
.pt-weather-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem; font-weight: 600;
}
.pt-weather-key {
  font-size: 0.78rem; color: var(--text-mute);
  margin-top: 6px; letter-spacing: 0.1em; text-transform: uppercase;
}

/* ===== ATTRACTIONS ===== */
.pt-attr-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px,1fr));
  gap: 22px;
}
.pt-attr-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 18px; padding: 28px;
  transition: all .3s;
}
.pt-attr-card:hover {
  transform: translateY(-6px);
  border-color: var(--amber);
  background: var(--surface-2);
  box-shadow: 0 20px 40px -20px var(--amber-glow);
}
.pt-attr-num {
  font-family: 'Cormorant Garamond', serif;
  font-style: italic; color: var(--amber);
  font-size: 0.95rem; margin-bottom: 10px;
}
.pt-attr-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.4rem; font-weight: 500;
  margin: 0 0 8px;
}
.pt-attr-desc {
  color: var(--text-mute); font-size: 0.92rem;
  line-height: 1.6;
}

/* ===== ITINERARY ===== */
.pt-day {
  background: var(--surface); border: 1px solid var(--border);
  border-left: 3px solid var(--amber);
  border-radius: 18px; padding: 28px;
  margin-bottom: 18px;
}
.pt-day-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem; font-weight: 500;
  margin: 0 0 18px; color: var(--amber);
}
.pt-timeline {
  display: flex; gap: 14px; padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.pt-timeline:last-child { border-bottom: none; }
.pt-timeline-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--amber); margin-top: 8px; flex-shrink: 0;
  box-shadow: 0 0 10px var(--amber-glow);
}
.pt-timeline-text {
  color: var(--text-dim); font-size: 0.96rem; line-height: 1.7;
}

/* ===== BUDGET ===== */
.pt-budget-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 24px;
}
@media (max-width: 820px) {
  .pt-budget-grid { grid-template-columns: 1fr; }
}
.pt-budget-item {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 14px; padding: 18px;
  margin-bottom: 12px;
}
.pt-budget-row {
  display: flex; justify-content: space-between;
  margin-bottom: 12px;
}
.pt-budget-label {
  font-weight: 500; font-size: 0.95rem;
}
.pt-budget-amount {
  font-family: 'Cormorant Garamond', serif;
  font-weight: 600; font-size: 1.1rem;
  color: var(--amber);
}
.pt-bar-bg {
  width: 100%; height: 6px; border-radius: 999px;
  background: rgba(255,255,255,0.06); overflow: hidden;
}
.pt-bar-fill {
  height: 100%; border-radius: 999px;
  transition: width .8s ease;
}
.pt-total {
  background: linear-gradient(135deg, rgba(232,177,78,0.18), rgba(110,231,231,0.08));
  border: 1px solid var(--border-strong);
  border-radius: 22px; padding: 32px; text-align: center;
  height: fit-content;
}
.pt-total-label {
  font-size: 0.75rem; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--text-mute); margin-bottom: 10px;
}
.pt-total-amt {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2rem, 4vw, 2.8rem);
  font-weight: 600; color: var(--amber);
  margin-bottom: 24px;
}
.pt-total-meta {
  display: grid; gap: 14px; text-align: left;
  border-top: 1px solid var(--border); padding-top: 18px;
}
.pt-total-meta-row {
  display: flex; justify-content: space-between;
  font-size: 0.88rem;
}
.pt-total-meta-row span:first-child { color: var(--text-mute); }
.pt-total-meta-row span:last-child { font-weight: 600; }

/* ===== TIPS ===== */
.pt-tips { display: grid; gap: 12px; max-width: 860px; margin: 0 auto; }
.pt-tip {
  display: flex; gap: 16px; align-items: flex-start;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 14px; padding: 18px 22px;
  transition: border-color .2s;
}
.pt-tip:hover { border-color: var(--border-strong); }
.pt-tip-icon { font-size: 1.3rem; }
.pt-tip-text { color: var(--text-dim); line-height: 1.6; font-size: 0.96rem; }

/* ===== BANNERS ===== */
.pt-error {
  max-width: 760px; margin: 0 auto;
  background: rgba(240,163,163,0.08);
  border: 1px solid rgba(240,163,163,0.3);
  color: var(--rose); padding: 18px 22px;
  border-radius: 14px;
}
.pt-info {
  max-width: 760px; margin: 12px auto 0;
  background: rgba(110,231,231,0.06);
  border: 1px solid rgba(110,231,231,0.2);
  color: var(--text-dim); padding: 14px 18px;
  border-radius: 12px; font-size: 0.9rem;
}
.pt-info code {
  background: rgba(0,0,0,0.4); padding: 2px 8px;
  border-radius: 4px; color: var(--cyan);
  font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
}


/* ===== ANIMATIONS ===== */
@keyframes pulse {
  0%,100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.15); }
}
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 var(--amber-glow); }
  70%  { box-shadow: 0 0 0 10px rgba(232,177,78,0); }
  100% { box-shadow: 0 0 0 0 rgba(232,177,78,0); }
}
.pt-fade-in { animation: fadeUp .8s ease both; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ===== INSPIRATION GALLERY ===== */
.pt-insp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 22px;
}
.pt-insp-card {
  position: relative; overflow: hidden;
  border-radius: 20px;
  height: 340px;
  border: 1px solid var(--border);
  cursor: pointer;
  isolation: isolate;
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
.pt-insp-body {
  position: absolute; left: 0; right: 0; bottom: 0;
  padding: 22px; z-index: 2;
}
.pt-insp-kicker {
  font-size: 0.7rem; letter-spacing: 0.25em; text-transform: uppercase;
  color: var(--amber); margin-bottom: 6px;
}
.pt-insp-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.7rem; font-weight: 500; margin: 0 0 6px;
}
.pt-insp-desc {
  color: var(--text-dim); font-size: 0.88rem; line-height: 1.5;
}

/* ===== SAMPLE PLAN ===== */
.pt-sample-wrap {
  background: linear-gradient(160deg, rgba(232,177,78,0.06), rgba(110,231,231,0.03));
  border: 1px solid var(--border-strong);
  border-radius: 24px;
  padding: clamp(28px, 4vw, 48px);
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
  flex-wrap: wrap; gap: 16px; margin-bottom: 28px;
  position: relative;
}
.pt-sample-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 500; margin: 0;
}
.pt-sample-chip {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 16px; border-radius: 999px;
  background: rgba(232,177,78,0.12); color: var(--amber);
  border: 1px solid rgba(232,177,78,0.3);
  font-size: 0.75rem; letter-spacing: 0.18em; text-transform: uppercase;
}
.pt-sample-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 24px;
  position: relative;
}
@media (max-width: 820px) {
  .pt-sample-grid { grid-template-columns: 1fr; }
}
.pt-sample-days { display: grid; gap: 14px; }
.pt-sample-day {
  background: rgba(15,15,22,0.55);
  border: 1px solid var(--border);
  border-left: 3px solid var(--amber);
  border-radius: 14px;
  padding: 18px 22px;
}
.pt-sample-day h4 {
  font-family: 'Cormorant Garamond', serif;
  margin: 0 0 6px; color: var(--amber);
  font-size: 1.2rem; font-weight: 500;
}
.pt-sample-day p {
  margin: 0; color: var(--text-dim);
  font-size: 0.92rem; line-height: 1.6;
}
.pt-sample-side {
  display: grid; gap: 16px; align-content: start;
}
.pt-sample-stats {
  background: rgba(15,15,22,0.6);
  border: 1px solid var(--border-strong);
  border-radius: 18px; padding: 22px;
}
.pt-sample-stat {
  display: flex; justify-content: space-between;
  padding: 10px 0; border-bottom: 1px solid var(--border);
  font-size: 0.92rem;
}
.pt-sample-stat:last-child { border-bottom: none; }
.pt-sample-stat span:first-child { color: var(--text-mute); }
.pt-sample-stat span:last-child {
  color: var(--amber); font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem; font-weight: 600;
}

/* ===== FOOTER (cinematic) ===== */
.pt-footer {
  position: relative;
  margin-top: 80px;
  padding: 80px clamp(20px, 5vw, 60px) 32px;
  border-top: 1px solid var(--border);
  background:
    radial-gradient(circle at 20% 0%, rgba(232,177,78,0.10), transparent 50%),
    radial-gradient(circle at 80% 100%, rgba(110,231,231,0.06), transparent 50%),
    var(--bg-2);
  overflow: hidden;
}
.pt-footer-cta {
  max-width: 1200px; margin: 0 auto 60px;
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 24px;
  padding-bottom: 50px; border-bottom: 1px solid var(--border);
}
.pt-footer-cta h3 {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  font-weight: 500; margin: 0; max-width: 22ch;
  letter-spacing: -0.01em;
}
.pt-footer-cta p {
  color: var(--text-mute); margin: 8px 0 0; max-width: 40ch;
}
.pt-footer-grid {
  max-width: 1200px; margin: 0 auto;
  display: grid;
  grid-template-columns: 1.4fr repeat(3, 1fr);
  gap: 40px;
}
@media (max-width: 820px) {
  .pt-footer-grid { grid-template-columns: 1fr 1fr; gap: 32px; }
  .pt-footer-cta { flex-direction: column; align-items: flex-start; }
}
.pt-footer-brand .pt-logo { margin-bottom: 14px; }
.pt-footer-tag {
  color: var(--text-dim); font-size: 0.92rem;
  line-height: 1.6; max-width: 32ch;
}
.pt-footer-col h5 {
  font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--amber); margin: 0 0 16px;
}
.pt-footer-col ul {
  list-style: none; padding: 0; margin: 0;
  display: grid; gap: 10px;
}
.pt-footer-col a {
  color: var(--text-dim); text-decoration: none;
  font-size: 0.92rem; transition: color .2s;
}
.pt-footer-col a:hover { color: var(--amber); }
.pt-footer-bottom {
  max-width: 1200px; margin: 50px auto 0;
  padding-top: 24px; border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
  color: var(--text-mute); font-size: 0.82rem;
}
.pt-footer-mark {
  font-family: 'Cormorant Garamond', serif;
  font-style: italic; color: var(--amber);
  font-size: 1.1rem;
}
.pt-footer-socials { display: flex; gap: 10px; }
.pt-footer-social {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text-dim); text-decoration: none;
  transition: all .2s;
}
.pt-footer-social:hover {
  color: var(--amber); border-color: var(--amber);
  transform: translateY(-2px);
}
.pt-footer-watermark {
  position: absolute; bottom: -60px; left: 50%;
  transform: translateX(-50%);
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(8rem, 22vw, 20rem);
  font-style: italic; font-weight: 500;
  color: rgba(232,177,78,0.04);
  pointer-events: none; white-space: nowrap;
  letter-spacing: -0.03em;
}

@media (max-width: 720px) {
  .pt-nav-links { display: none; }
  .pt-section { padding: 60px 20px; }
  .pt-dest { padding: 28px; }
  .pt-agents-wrap { padding: 22px; }
  .pt-insp-card { height: 280px; }
}
`;

const INSPIRATIONS = [
  {
    name: "Kyoto",
    kicker: "Japan · Spring",
    desc: "Cherry blossoms, lantern-lit alleys, and timeless temples.",
    img: "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1400&q=80",
    query:
      "Plan a 7-day cherry blossom trip to Kyoto in April for 2 people, ₹1,20,000 budget, with day trips to Nara and Osaka.",
  },
  {
    name: "Santorini",
    kicker: "Greece · Summer",
    desc: "Whitewashed cliffs, Aegean sunsets, and slow island mornings.",
    img: "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=1400&q=80",
    query:
      "Plan a 5-day romantic getaway to Santorini in June for 2 people with a €2,500 budget.",
  },
  {
    name: "Patagonia",
    kicker: "Argentina · Trekking",
    desc: "Glacial valleys, granite spires, and wind-carved silence.",
    img: "https://images.unsplash.com/photo-1531065208531-4036c0dba3ca?auto=format&fit=crop&w=1400&q=80",
    query:
      "Plan a 12-day trekking adventure across Patagonia covering Torres del Paine and El Chaltén, mid-range budget.",
  },
  {
    name: "Marrakech",
    kicker: "Morocco · Desert",
    desc: "Souk spices, riad courtyards, and a night under Saharan stars.",
    img: "https://images.unsplash.com/photo-1539020140153-e479b8c22e70?auto=format&fit=crop&w=1400&q=80",
    query:
      "Plan a 6-day Morocco trip from Marrakech to the Sahara for 2 people with a $1,500 budget.",
  },
  {
    name: "Bali",
    kicker: "Indonesia · Honeymoon",
    desc: "Rice terraces, jungle villas, and warm volcanic shores.",
    img: "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=1400&q=80",
    query:
      "Plan a 7-night honeymoon to Bali covering Ubud and Uluwatu with a ₹1,50,000 budget.",
  },
  {
    name: "Iceland",
    kicker: "Nordic · Aurora",
    desc: "Black sand coasts, glacier lagoons, and dancing northern lights.",
    img: "https://images.unsplash.com/photo-1500039436846-25ae2f11882e?auto=format&fit=crop&w=1400&q=80",
    query:
      "Plan a 6-day Iceland ring-road trip in February to chase the northern lights, mid-range budget.",
  },
];

const SAMPLE_PLAN = {
  title: "Kyoto · 5 Days in Spring",
  chip: "Sample itinerary",
  days: [
    {
      name: "Day 01 · Arrival in Kyoto",
      text: "Settle into a Gion machiya, slow stroll along Shirakawa canal, kaiseki dinner at a quiet ryokan.",
    },
    {
      name: "Day 02 · Eastern Temples",
      text: "Kiyomizu-dera at sunrise, Sannenzaka tea break, Yasaka shrine, evening geisha district walk.",
    },
    {
      name: "Day 03 · Arashiyama",
      text: "Bamboo grove before crowds, Tenryū-ji garden, Hozugawa river boat, sunset at Iwatayama.",
    },
    {
      name: "Day 04 · Day trip to Nara",
      text: "Friendly deer in Nara Park, Tōdai-ji great Buddha, matcha tasting back in Uji.",
    },
    {
      name: "Day 05 · Fushimi & Farewell",
      text: "Dawn at Fushimi Inari's torii tunnels, sake brewery lunch, shinkansen onward.",
    },
  ],
  stats: [
    { k: "Total budget", v: "₹1,18,400" },
    { k: "Per-day avg", v: "₹23,680" },
    { k: "Hotels", v: "38%" },
    { k: "Food & sake", v: "22%" },
    { k: "Transport", v: "20%" },
  ],
};

/* ============================================================
   Component
   ============================================================ */
function Index() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeAgent, setActiveAgent] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [plan, setPlan] = useState<any | null>(null);
  const resultRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (plan && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [plan]);

  const transformed = useMemo(() => {
    if (!plan || typeof plan !== "object") return null;
    if (plan.error) return null;
    if (!plan.intent) return null;
    return {
      destination_overview: {
        name: plan.intent?.destination,
        description: plan.research?.weather,
        tags: plan.intent?.preferences ?? [],
        best_time: plan.research?.best_time_to_visit,
      },
      weather: plan.weather ?? {},
      attractions: plan.research?.attractions ?? [],
      itinerary: plan.itinerary ?? {},
      budget_breakdown: plan.budget ?? {},
      travel_tips: plan.research?.local_transport ?? [],
      intent: plan.intent,
    };
  }, [plan]);

  async function handleSubmit() {
    const q = query.trim();
    if (!q) {
      setError("Please describe your trip before generating a plan.");
      return;
    }
    setError(null);
    setPlan(null);
    setLoading(true);
    setActiveAgent(0);

    // Cinematic agent stepping while request is in-flight
    const stepper = (async () => {
      for (let i = 0; i < AGENTS.length - 1; i++) {
        setActiveAgent(i);
        await new Promise((r) => setTimeout(r, 700 + Math.random() * 500));
      }
      setActiveAgent(AGENTS.length - 1);
    })();

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_query: q }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data && typeof data === "object" && "error" in data) {
        throw new Error(
          String(
            (data as { error?: unknown }).error ?? "Unknown backend error",
          ),
        );
      }
      await stepper;
      setActiveAgent(AGENTS.length);
      await new Promise((r) => setTimeout(r, 400));
      setPlan(data);
    } catch (err: any) {
      const msg = err?.message ?? "Unknown error";
      if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
        setError(
          "🔌 Cannot reach the backend. Make sure FastAPI is running at " +
            BACKEND_URL,
        );
      } else if (msg.includes("HTTP")) {
        setError(`🚫 Backend error: ${msg}`);
      } else {
        setError(`⚠️ ${msg}`);
      }
    } finally {
      setLoading(false);
      setActiveAgent(null);
    }
  }

  return (
    <>
      <style>{CSS}</style>
      <div className="pt-root">
        {/* HERO */}
        <section className="pt-hero">
          <div className="pt-hero-bg" />
          <div className="pt-hero-grain" />

          <nav className="pt-nav">
            <div className="pt-logo">
              <span className="pt-logo-mark">✦</span>
              <span>
                Pātheyātrā{" "}
                <em style={{ fontStyle: "italic", color: "var(--amber)" }}>
                  AI
                </em>
              </span>
            </div>
            <div className="pt-nav-links">
              <a href="#plan-generation">Agents</a>
              <a href="#how">How it works</a>
              <a href="#examples">Examples</a>
            </div>
          </nav>

          <div className="pt-hero-content">
            <div className="pt-badge">
              <span className="pt-badge-dot" />
              Cinematic AI Travel Planning
            </div>
            <h1 className="pt-title">
              Your perfect <em>journey</em> awaits
            </h1>
            <p className="pt-subtitle">
              Describe a dream — a city, a season, a budget. Our multi-agent AI
              composes a tailored itinerary, weather brief, budget breakdown,
              and insider tips in seconds.
            </p>

            <div className="pt-prompt">
              <div className="pt-prompt-label">
                <span>✈</span> Where do you want to go?
              </div>
              <textarea
                className="pt-textarea"
                placeholder='e.g. "Plan a 7-day trip to Japan in October for 2 people with a ₹80,000 budget, including Tokyo, Kyoto and Osaka."'
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if ((e.metaKey || e.ctrlKey) && e.key === "Enter")
                    handleSubmit();
                }}
              />
              <div className="pt-prompt-row">
                <span className="pt-hint">⌘ / Ctrl + Enter to generate</span>
                <button
                  className="pt-cta"
                  onClick={handleSubmit}
                  disabled={loading}
                >
                  {loading ? "Crafting your plan…" : "✦ Generate My Plan"}
                </button>
              </div>
            </div>

            <div className="pt-pills" id="examples">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  className="pt-pill"
                  onClick={() => setQuery(ex.replace(/^[^\w]+\s*/, ""))}
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        </section>

        {(loading || error || transformed || plan) && (
          <section className="pt-section pt-fade-in" id="plan-generation">
            {loading && (
              <div className="pt-agents-wrap">
                <div className="pt-agents-head">
                  <h2 className="pt-agents-title">AI agents at work</h2>
                  <span className="pt-agents-count">
                    {Math.min(activeAgent ?? 0, AGENTS.length)} /{" "}
                    {AGENTS.length}
                  </span>
                </div>
                {AGENTS.map((a, i) => {
                  let cls = "pending";
                  let dotCls = "";
                  let dotContent: React.ReactNode = a.icon;
                  if (activeAgent !== null) {
                    if (i < activeAgent) {
                      cls = "done";
                      dotCls = "done-dot";
                      dotContent = "✓";
                    } else if (i === activeAgent) {
                      cls = "active";
                      dotCls = "active";
                      dotContent = a.icon;
                    }
                  }
                  return (
                    <div key={a.name} className={`pt-agent-step ${cls}`}>
                      <div className={`pt-agent-dot ${dotCls}`}>
                        {dotContent}
                      </div>
                      <div>
                        <div className="pt-agent-name">{a.name}</div>
                        <div className="pt-agent-desc">{a.desc}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {error && (
              <div className="pt-error" style={{ marginBottom: 24 }}>
                {error}
              </div>
            )}

            <div ref={resultRef}>
              {transformed && <PlanView data={transformed} />}
              {plan && !transformed && (
                <div className="pt-error">
                  ⚠️ We couldn't generate a complete plan right now.
                </div>
              )}
            </div>
          </section>
        )}

        {/* INSPIRATION GALLERY */}
        <section className="pt-section" id="inspiration">
          <SectionHead
            icon="🌅"
            title="Wander somewhere new"
            sub="Inspiration · Tap any place to plan"
          />
          <div className="pt-insp-grid">
            {INSPIRATIONS.map((p) => (
              <button
                key={p.name}
                className="pt-insp-card"
                onClick={() => {
                  setQuery(p.query);
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
                style={{
                  padding: 0,
                  background: "transparent",
                  textAlign: "left",
                }}
              >
                <div
                  className="pt-insp-img"
                  style={{ backgroundImage: `url(${p.img})` }}
                />
                <div className="pt-insp-body">
                  <div className="pt-insp-kicker">{p.kicker}</div>
                  <h3 className="pt-insp-name">{p.name}</h3>
                  <p className="pt-insp-desc">{p.desc}</p>
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* SAMPLE PLAN PREVIEW */}
        <section className="pt-section" id="sample">
          <SectionHead
            icon="📜"
            title="A taste of what you'll get"
            sub="Example plan · Generated in seconds"
          />
          <div className="pt-sample-wrap">
            <div className="pt-sample-head">
              <h3 className="pt-sample-title">{SAMPLE_PLAN.title}</h3>
              <span className="pt-sample-chip">✦ {SAMPLE_PLAN.chip}</span>
            </div>
            <div className="pt-sample-grid">
              <div className="pt-sample-days">
                {SAMPLE_PLAN.days.map((d) => (
                  <div key={d.name} className="pt-sample-day">
                    <h4>{d.name}</h4>
                    <p>{d.text}</p>
                  </div>
                ))}
              </div>
              <div className="pt-sample-side">
                <div className="pt-sample-stats">
                  {SAMPLE_PLAN.stats.map((s) => (
                    <div key={s.k} className="pt-sample-stat">
                      <span>{s.k}</span>
                      <span>{s.v}</span>
                    </div>
                  ))}
                </div>
                <button
                  className="pt-cta"
                  onClick={() => {
                    setQuery(INSPIRATIONS[0].query);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                  style={{ justifyContent: "center" }}
                >
                  ✦ Generate a plan like this
                </button>
              </div>
            </div>
          </div>
        </section>

        <footer className="pt-footer" id="how">
          <div className="pt-footer-cta">
            <div>
              <h3>
                Ready to compose your next{" "}
                <em style={{ fontStyle: "italic", color: "var(--amber)" }}>
                  journey
                </em>
                ?
              </h3>
              <p>
                Tell us where your mind keeps wandering. We'll handle the rest.
              </p>
            </div>
            <button
              className="pt-cta"
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            >
              ✦ Start planning
            </button>
          </div>

          <div className="pt-footer-grid">
            <div className="pt-footer-brand">
              <div className="pt-logo">
                <span className="pt-logo-mark">✦</span>
                <span>
                  Pātheyātrā{" "}
                  <em style={{ fontStyle: "italic", color: "var(--amber)" }}>
                    AI
                  </em>
                </span>
              </div>
              <p className="pt-footer-tag">
                A cinematic, multi-agent travel companion that turns a single
                sentence into a complete journey — itinerary, weather, budget,
                and insider tips.
              </p>
            </div>

            <div className="pt-footer-col">
              <h5>Explore</h5>
              <ul>
                <li>
                  <a href="#inspiration">Destinations</a>
                </li>
                <li>
                  <a href="#sample">Example plan</a>
                </li>
                <li>
                  <a href="#examples">Quick prompts</a>
                </li>
              </ul>
            </div>

            <div className="pt-footer-col">
              <h5>Agents</h5>
              <ul>
                <li>
                  <a href="#plan-generation">Intent · Research</a>
                </li>
                <li>
                  <a href="#plan-generation">Itinerary · Budget</a>
                </li>
                <li>
                  <a href="#plan-generation">Weather · Finalizer</a>
                </li>
              </ul>
            </div>

            <div className="pt-footer-col">
              <h5>Company</h5>
              <ul>
                <li>
                  <a href="#">About</a>
                </li>
                <li>
                  <a href="#">Contact</a>
                </li>
                <li>
                  <a href="#">Privacy</a>
                </li>
              </ul>
            </div>
          </div>

          <div className="pt-footer-bottom">
            <div>
              © {new Date().getFullYear()}{" "}
              <span className="pt-footer-mark">Pātheyātrā AI</span> · Crafted
              with multi-agent intelligence
            </div>
            <div className="pt-footer-socials">
              <a className="pt-footer-social" href="#" aria-label="Twitter">
                𝕏
              </a>
              <a className="pt-footer-social" href="#" aria-label="Instagram">
                ◎
              </a>
              <a className="pt-footer-social" href="#" aria-label="GitHub">
                ⌥
              </a>
              <a className="pt-footer-social" href="#" aria-label="Email">
                ✉
              </a>
            </div>
          </div>

          <div className="pt-footer-watermark" aria-hidden="true">
            pātheyātrā
          </div>
        </footer>
      </div>
    </>
  );
}

/* ============================================================
   Plan view (destination, weather, attractions, itinerary, budget, tips)
   ============================================================ */
function PlanView({ data }: { data: any }) {
  return (
    <div className="pt-fade-in">
      <DestinationSection data={data} />
      <WeatherSection data={data} />
      <AttractionsSection data={data} />
      <ItinerarySection data={data} />
      <BudgetSection data={data} />
      <TipsSection data={data} />
    </div>
  );
}

function SectionHead({
  icon,
  title,
  sub,
}: {
  icon: string;
  title: string;
  sub: string;
}) {
  return (
    <div className="pt-section-head">
      <div className="pt-section-icon">{icon}</div>
      <div>
        <p className="pt-section-sub">{sub}</p>
        <h2 className="pt-section-title">{title}</h2>
      </div>
    </div>
  );
}

function DestinationSection({ data }: { data: any }) {
  const d = data.destination_overview ?? {};
  if (!d?.name) return null;
  const tags: string[] = Array.isArray(d.tags) ? d.tags.slice(0, 6) : [];
  const intent = data.intent ?? {};
  return (
    <section className="pt-section">
      <SectionHead
        icon="🌍"
        title="Destination Overview"
        sub="Where you're going"
      />
      <div className="pt-dest">
        <h3 className="pt-dest-name">{d.name}</h3>
        {d.description && <p className="pt-dest-desc">{d.description}</p>}
        {tags.length > 0 && (
          <div className="pt-dest-tags">
            {tags.map((t) => (
              <span key={t} className="pt-tag">
                {t}
              </span>
            ))}
          </div>
        )}
        <div className="pt-meta-row">
          {d.best_time && (
            <div className="pt-meta">
              <div className="pt-meta-label">📅 Best Time</div>
              <div className="pt-meta-val">{d.best_time}</div>
            </div>
          )}
          {intent.duration && (
            <div className="pt-meta">
              <div className="pt-meta-label">⏱ Duration</div>
              <div className="pt-meta-val">{intent.duration}</div>
            </div>
          )}
          {intent.budget && (
            <div className="pt-meta">
              <div className="pt-meta-label">💳 Budget</div>
              <div className="pt-meta-val">{intent.budget}</div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function WeatherSection({ data }: { data: any }) {
  const w = data.weather ?? {};
  if (!w || Object.keys(w).length === 0) return null;
  const cards = [
    {
      icon: "🌡",
      val: w.temperature ?? w.avg_temperature ?? "—",
      key: "Temperature",
    },
    { icon: "⛅", val: w.condition ?? w.description ?? "—", key: "Condition" },
    { icon: "💧", val: w.humidity ?? "—", key: "Humidity" },
  ];
  if (w.wind_speed || w.wind)
    cards.push({ icon: "💨", val: w.wind_speed ?? w.wind, key: "Wind" });
  if (w.uv_index || w.uv)
    cards.push({ icon: "☀️", val: w.uv_index ?? w.uv, key: "UV Index" });
  if (w.rainfall || w.rain_chance)
    cards.push({ icon: "🌧", val: w.rainfall ?? w.rain_chance, key: "Rain" });

  return (
    <section className="pt-section">
      <SectionHead
        icon="🌤"
        title="Weather & Climate"
        sub="Conditions on the ground"
      />
      <div className="pt-weather-grid">
        {cards.map((c) => (
          <div key={c.key} className="pt-weather-card">
            <div className="pt-weather-icon">{c.icon}</div>
            <div className="pt-weather-val">{String(c.val)}</div>
            <div className="pt-weather-key">{c.key}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function AttractionsSection({ data }: { data: any }) {
  const list = data.attractions ?? [];
  if (!Array.isArray(list) || list.length === 0) return null;
  return (
    <section className="pt-section">
      <SectionHead
        icon="🏛"
        title="Top Attractions"
        sub="What you can't miss"
      />
      <div className="pt-attr-grid">
        {list.map((a: any, i: number) => {
          const name =
            typeof a === "string" ? a : (a.name ?? `Attraction ${i + 1}`);
          const desc =
            typeof a === "string"
              ? ""
              : (a.description ?? a.details ?? a.category ?? a.type ?? "");
          const ord = (i + 1).toString().padStart(2, "0");
          return (
            <div key={i} className="pt-attr-card">
              <div className="pt-attr-num">— {ord}</div>
              <div className="pt-attr-name">{name}</div>
              {desc && <div className="pt-attr-desc">{desc}</div>}
            </div>
          );
        })}
      </div>
    </section>
  );
}

function ItinerarySection({ data }: { data: any }) {
  const days = data.itinerary?.days ?? {};
  const dayKeys = Object.keys(days);
  if (dayKeys.length === 0) return null;
  return (
    <section className="pt-section">
      <SectionHead
        icon="📅"
        title="Day-by-Day Itinerary"
        sub="Your journey, hour by hour"
      />
      <div style={{ maxWidth: 900, margin: "0 auto" }}>
        {dayKeys.map((day) => {
          const acts = days[day] ?? [];
          return (
            <div key={day} className="pt-day">
              <h3 className="pt-day-name">{day}</h3>
              {(Array.isArray(acts) ? acts : [acts]).map(
                (a: any, idx: number) => (
                  <div key={idx} className="pt-timeline">
                    <div className="pt-timeline-dot" />
                    <div className="pt-timeline-text">
                      {typeof a === "string" ? a : JSON.stringify(a)}
                    </div>
                  </div>
                ),
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

function BudgetSection({ data }: { data: any }) {
  const budget = data.budget_breakdown ?? {};
  const keys = Object.keys(budget);
  if (keys.length === 0) return null;

  const items: Record<string, number> = {};
  let total = 0;
  for (const k of keys) {
    if (["total", "total_cost", "grand_total"].includes(k.toLowerCase())) {
      total = extractNumber(budget[k]);
    } else {
      items[k] = extractNumber(budget[k]);
    }
  }
  if (!total) total = Object.values(items).reduce((s, v) => s + v, 0);

  const days = Object.keys(data.itinerary?.days ?? {}).length;
  const perDay = days > 0 && total ? total / days : 0;
  const largest = Object.entries(items).sort((a, b) => b[1] - a[1])[0];

  return (
    <section className="pt-section">
      <SectionHead
        icon="💰"
        title="Budget Breakdown"
        sub="Where your money goes"
      />
      <div className="pt-budget-grid">
        <div>
          {Object.entries(items).map(([k, v]) => {
            const pct = total ? (v / total) * 100 : 0;
            const p = BUDGET_PALETTE[k.toLowerCase()] ?? {
              color: "#888",
              icon: "•",
            };
            return (
              <div key={k} className="pt-budget-item">
                <div className="pt-budget-row">
                  <span className="pt-budget-label">
                    {p.icon}{" "}
                    {k
                      .replace(/_/g, " ")
                      .replace(/\b\w/g, (m) => m.toUpperCase())}
                  </span>
                  <span className="pt-budget-amount">
                    ₹{v.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                  </span>
                </div>
                <div className="pt-bar-bg">
                  <div
                    className="pt-bar-fill"
                    style={{ width: `${pct.toFixed(1)}%`, background: p.color }}
                  />
                </div>
              </div>
            );
          })}
        </div>
        <div className="pt-total">
          <div className="pt-total-label">Estimated Total</div>
          <div className="pt-total-amt">
            ₹{total.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
          </div>
          <div className="pt-total-meta">
            {perDay > 0 && (
              <div className="pt-total-meta-row">
                <span>📊 Per-Day Avg</span>
                <span>
                  ₹
                  {perDay.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                </span>
              </div>
            )}
            {largest && total > 0 && (
              <div className="pt-total-meta-row">
                <span>🔺 Biggest Spend</span>
                <span>
                  {largest[0].replace(/\b\w/g, (m) => m.toUpperCase())} ·{" "}
                  {((largest[1] / total) * 100).toFixed(0)}%
                </span>
              </div>
            )}
            {days > 0 && (
              <div className="pt-total-meta-row">
                <span>📆 Days</span>
                <span>{days}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function TipsSection({ data }: { data: any }) {
  const tips = data.travel_tips ?? [];
  if (!tips || (Array.isArray(tips) && tips.length === 0)) return null;
  const icons = ["🛂", "💊", "📱", "🔌", "💬", "🏧", "🧥", "🛡"];
  const arr = Array.isArray(tips) ? tips : [tips];
  return (
    <section className="pt-section">
      <SectionHead
        icon="💡"
        title="Travel Tips & Essentials"
        sub="Insider knowledge"
      />
      <div className="pt-tips">
        {arr.map((t: any, i: number) => {
          const text =
            typeof t === "string" ? t : (t?.tip ?? JSON.stringify(t));
          return (
            <div key={i} className="pt-tip">
              <span className="pt-tip-icon">{icons[i % icons.length]}</span>
              <span className="pt-tip-text">{text}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

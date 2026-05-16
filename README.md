# Pātheyātrā AI — Multi-Agent Travel Planner

Pātheyātrā AI is an AI-powered multi-agent travel planning system that generates personalized travel itineraries, budget breakdowns, destination insights, and weather information using orchestrated AI agents.

The project demonstrates modular AI-agent architecture using FastAPI, Streamlit, Gemini API, and asynchronous orchestration.

---

# Features

- Multi-Agent AI Architecture
- Intent Extraction from Natural Language
- Destination Research & Recommendations
- Day-wise AI Itinerary Generation
- Smart Budget Estimation
- Live Weather Integration
- FastAPI Backend
- Streamlit Frontend
- Gemini API Integration
- Modular & Scalable Code Structure
- Async Workflow Orchestration
- Structured JSON-based Agent Communication

---

# AI Agent Workflow

Pātheyātrā AI uses multiple specialized AI agents coordinated by a central orchestrator.

## Intent Agent
Extracts:
- destination
- duration
- budget
- travel preferences

from the user's natural language query.

---

## Research Agent
Collects:
- destination insights
- top attractions
- local transport methods
- best time to visit

---

## Itinerary Agent
Generates a personalized day-by-day itinerary based on:
- trip duration
- user preferences
- destination context

---

## Budget Agent
Calculates realistic travel expenses including:
- hotel
- food
- flights
- local transport
- activities

while keeping estimates close to the user's budget.

---

## Weather Agent
Fetches live weather data for the selected destination using weather APIs.

---

# System Architecture

```text
                ┌────────────────────┐
                │   Streamlit UI     │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │    FastAPI API     │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Travel Orchestrator│
                └─────────┬──────────┘
                          │
      ┌───────────────────┼───────────────────┐
      ▼                   ▼                   ▼
┌────────────┐    ┌────────────┐    ┌────────────┐
│Intent Agent│    │Research Ag.│    │Itinerary Ag│
└────────────┘    └────────────┘    └────────────┘
      ▼                   ▼                   ▼
┌────────────┐    ┌────────────┐
│Budget Agent│    │Weather Ag. │
└────────────┘    └────────────┘


# Detailed Tech Stack

## Frontend
- Streamlit
- Custom CSS
- Responsive UI Components

## Backend
- FastAPI
- Uvicorn
- Asyncio

## AI & LLM
- Gemini 2.5 Flash API
- Prompt Engineering
- Multi-Agent Orchestration

## Data Validation
- Pydantic

## APIs
- Gemini API
- OpenWeatherMap API

## Utilities
- Requests
- JSON
- Regex
- Environment Variables (.env)

## Development Tools
- VS Code
- Python Virtual Environment (venv)
- Git & GitHub
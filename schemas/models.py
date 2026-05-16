from pydantic import BaseModel
from typing import List, Dict


class IntentData(BaseModel):
    destination: str
    duration: int
    budget: int
    preferences: List[str]


class ResearchData(BaseModel):
    weather: str
    attractions: List[str]
    best_time_to_visit: str
    local_transport: List[str]


class ItineraryData(BaseModel):
    days: Dict[str, List[str]]


class BudgetData(BaseModel):
    hotel: int
    food: int
    transport: int
    activities: int
    total: int


class FinalPlan(BaseModel):
    intent: IntentData
    research: ResearchData
    itinerary: ItineraryData
    budget: BudgetData
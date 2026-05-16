from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="AI Travel Planner"
)

app.include_router(router)
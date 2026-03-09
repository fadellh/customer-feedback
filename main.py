from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models  # registers all models with Base
from routers import feedback

app = FastAPI(
    title="Customer Feedback API",
    description="Demo API for handling customer feedback submissions",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback.router)

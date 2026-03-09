from fastapi import FastAPI
import models  # registers all models with Base
from routers import feedback

app = FastAPI(title="Customer Feedback API")
app.include_router(feedback.router)

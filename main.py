from fastapi import FastAPI
import models  # registers all models with Base

app = FastAPI(title="Customer Feedback API")

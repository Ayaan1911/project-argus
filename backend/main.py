from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze, submissions

app = FastAPI(title="Project Argus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(submissions.router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Project Argus"}

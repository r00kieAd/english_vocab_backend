import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.vocab_router import router as vocab_api_router
from routers.score_router import router as score_api_router
from database.database import engine, Base

app = FastAPI(title="English Vocabulary API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"status": "API Active"}

app.include_router(vocab_api_router)
app.include_router(score_api_router)

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False
    )

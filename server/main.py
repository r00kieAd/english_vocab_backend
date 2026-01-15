from fastapi import FastAPI
from routers.vocab_router import router as vocab_api_router
from routers.score_router import router as score_api_router
from models.vocab import EnglishVocab 
from models.scores import ScoreSheet 
from database.database import engine, Base
from fastapi.responses import RedirectResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="English Vocabulary API")

@app.get("/")
async def root():
    return "API Active"

app.include_router(vocab_api_router)
app.include_router(score_api_router)

if __name__ == "__main__":
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run("main:app", host=host, port=port, reload=False)

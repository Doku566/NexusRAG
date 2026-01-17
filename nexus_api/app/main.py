from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
import asyncio
import time
import random

# Import C++ Core
try:
    import nexus_core
except ImportError:
    # Hack for local dev if not installed
    import sys
    import os
    sys.path.append(os.path.abspath("../../nexus_core/build"))
    import nexus_core

app = FastAPI(title="NexusRAG API", version="1.0.0")

# Global Index
# Dimension 1536 (OpenAI Ada-002 compatible)
DIMENSION = 1536
index = nexus_core.VectorIndex(DIMENSION)

class SearchRequest(BaseModel):
    query: List[float]
    k: int = 5

class SearchResult(BaseModel):
    id: int
    distance: float

@app.on_event("startup")
async def load_index():
    print("Loading Index...")
    # Simulate loading 10k vectors
    # In C++, adding is fast, but let's do it to show it works
    # This runs in main thread, but startup is once.
    for i in range(1000):
        # Random vector
        vec = [random.random() for _ in range(DIMENSION)]
        index.add_item(i, vec)
    print("Index Loaded with 1000 vectors.")

@app.post("/search", response_model=List[SearchResult])
async def search_vectors(payload: SearchRequest):
    if len(payload.query) != DIMENSION:
        raise HTTPException(status_code=400, detail="Invalid dimension")
    
    # CRITICAL: This call calls C++. 
    # Because we used `py::call_guard<py::gil_scoped_release>()`,
    # functionality inside `search` will NOT block other Python threads.
    # To truly benefit in FastAPI, we should run this in a threadpool 
    # if it blocks the *event loop*, but since it releases GIL, 
    # standard python threads (like those in uvicorn workers or run_in_executor) thrive.
    
    # Using run_in_executor to ensure the main event loop isn't blocked 
    # by the C++ computation time (even if GIL is free, the thread is busy).
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(
        None, 
        lambda: index.search(payload.query, payload.k)
    )
    
    return [{"id": r.id, "distance": r.distance} for r in results]

@app.get("/health")
def health_check():
    return {"status": "ok", "vectors": "mocked_1000"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

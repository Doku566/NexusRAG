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
    for i in range(1000):
        vec = [random.random() for _ in range(DIMENSION)]
        index.add_item(i, vec)
    print("Index Loaded with 1000 vectors.")

# Dedicated thread pool for CPU-bound C++ tasks
# Setting max_workers to CPU count * 2 to ensure we saturate cores even if some slight IO overhead exists
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 2)

@app.post("/search", response_model=List[SearchResult])
async def search_vectors(payload: SearchRequest):
    if len(payload.query) != DIMENSION:
        raise HTTPException(status_code=400, detail="Invalid dimension")
    
    # Offload the pure C++ computation to our thread pool.
    # Since index.search() releases the GIL, these threads will run in parallel 
    # on physical cores, while the main AsyncIO loop handles HTTP traffic.
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(
        executor, 
        lambda: index.search(payload.query, payload.k)
    )
    
    return [{"id": r.id, "distance": r.distance} for r in results]

@app.get("/health")
def health_check():
    return {"status": "ok", "vectors": "mocked_1000"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

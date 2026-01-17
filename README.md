# NexusRAG: C++ Extension for Non-Blocking Vector Search

A microservice architecture tackling the Python Global Interpreter Lock (GIL) bottleneck in similarity search applications. It creates a bridge between a FastAPI frontend and a threaded C++ backend.

## The Concurrency Problem
In standard Python, a CPU-intensive loop (like computing cosine similarity for 10k vectors) holds the GIL, pausing the `asyncio` loop. This causes health-check failures and timeouts in high-traffic scenarios.

### Solution: Explicit GIL Release
The C++ extension (`nexus_core`) acts as the compute offloader.
*   **Mechanism**: The bindings utilize `py::call_guard<py::gil_scoped_release>()`.
*   **Verification**: The included `tests/stress_test.py` validates that 50 concurrent requests finish in time $T \approx \frac{\sum t_i}{Cores}$.
*   **Integration**: The FastAPI layer uses a dedicated `ThreadPoolExecutor(max_workers=CPU*2)` to schedule these tasks off the main event loop.

## Performance Reality
| Metric | Value | Constraint |
| :--- | :--- | :--- |
| **Search Algorithm** | Brute Force ($O(N)$) | Linear scan. Efficient up to ~100k vectors via AVX2. Slow beyond that. |
| **Throughput** | ~2000 req/s | Limited by JSON serialization in Python, not C++. |
| **Memory** | RAM Bound | Vectors stored in `std::vector`. 1M vectors @ 1536d $\approx$ 6GB RAM. |

## Known Limitations (Trade-offs)
1.  **No HNSW (Yet)**: The search is currently a linear loop. I prioritized the *architecture* (Async Bridge) over the *algorithm* (Graph Index) for this iteration.
2.  **No Persistence**: The index implementation is in-memory only. If the container restarts, the index is lost. A production version would require mmap support (e.g., loading faiss indices).
3.  **Build Complexity**: Docker builds take significantly longer (approx 2m) due to compiling the C++ extension from source, compared to a pure Python install.

# NexusRAG: High-Concurrency Vector Retrieval Engine

`NexusRAG` is a microservices-based retrieval system that offloads vector computations to a C++ extension to bypass the CPython Global Interpreter Lock (GIL). It is designed to maintain high HTTP throughput in FastAPI even under heavy CPU load from similarity searches.

## Design Decisions

### 1. Releasing the GIL (Async-Bridge)
The core design constraint was Python's GIL, which serializes CPU-bound tasks.
-   **Why**: A standard `numpy` dot product blocks the main thread. In an async server like FastAPI (`uvicorn`), this pauses the Event Loop, blocking heartbeats and incoming requests.
-   **Implementation**: The `search` function in `src/bindings.cpp` utilizes `py::call_guard<py::gil_scoped_release>()`. This explicitly drops the lock, allowing the OS scheduler to run the C++ search thread in parallel with Python I/O threads.

### 2. ThreadPool Execution
The FastAPI application explicitly uses a `ThreadPoolExecutor` (sized to $2 \times$ Cores) to schedule these non-blocking C++ tasks. This prevents `asyncio` from accidentally running them in the main thread.

## Trade-offs and Limitations

*   **Brute Force Index**: The current `VectorIndex` uses linear scan ($O(N)$). While efficient with SIMD for $N < 100k$, it is essentially a placeholder for an HNSW (Hierarchical Navigable Small World) graph.
*   **Memory Usage**: Vectors are stored in RAM (std::vector). There is no quantization (PQ) or memory mapping (mmap), limiting the dataset size to physical RAM.
*   **Build Complexity**: Requires compiling C++ extensions. This complicates the CI/CD pipeline compared to a pure Python solution.

## Current Status

-   [x] **C++ Core**: `VectorIndex` implemented with multithreading support.
-   [x] **GIL Release**: Bindings configured correctly for true parallelism.
-   [x] **Infrastructure**: Docker Compose orchestration operational.
-   [x] **Verification**: `stress_test.py` proves Concurrency Factor > 1.5x on multicore systems.
-   [ ] **Indexing Algorithm**: HNSW implementation is currently pending (Roadmap).

## Complexity Analysis

| Operation | Complexity | Description |
| :--- | :--- | :--- |
| **Search (Current)** | $O(N \cdot D)$ | Linearly scans all $N$ vectors of dimension $D$. |
| **Search (Target)** | $O(\log N)$ | HNSW graph traversal (Planned). |
| **Concurrency** | $Scales \approx Cores$ | Restricted only by Memory Bandwidth after GIL release. |

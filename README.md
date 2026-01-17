# NexusRAG: High-Performance Technical Support Intelligence

![FastAPI](https://img.shields.io/badge/FastAPI-0.95-green.svg) ![C++](https://img.shields.io/badge/C++-17-blue.svg) ![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)

**NexusRAG** es una plataforma de "Retrieval-Augmented Generation" diseñada para escalar a millones de documentos técnicos. Se diferencia de las soluciones estándar (LangChain puro) al implementar su propio motor de búsqueda vectorial en **C++ nativo**, optimizado para alta concurrencia.

## 🏛️ Arquitectura

El sistema sigue un diseño de microservicios:
*   **Vector Engine (`nexus_core`)**: Módulo C++ compilado con `pybind11`. Gestiona el índice en memoria y realiza búsquedas de vecinos más cercanos (k-NN).
*   **API Gateway (`nexus_api`)**: Servicio FastAPI asíncrono. Delega la computación pesada al motor C++ mediante un ThreadPool.
*   **Storage**: PostgreSQL para metadatos y Redis para caché de queries frecuentes.

## 🚀 Retos Técnicos Superados

### Bypassing the GIL (Global Interpreter Lock)
En Python, el GIL impide que múltiples hilos ejecuten bytecodes simultáneamente, lo que hace que las tareas CPU-intensive bloqueen el servidor web.
*   **Solución**: En los bindings de C++ (`bindings.cpp`), utilizo `py::call_guard<py::gil_scoped_release>()`. Esto libera explícitamente el GIL antes de entrar en el bucle de búsqueda vectorial (`compute_l2_sq`).
*   **Resultado**: El servidor FastAPI puede manejar cientos de requests concurrentes; mientras un hilo espera el resultado de C++, otros hilos pueden procesar I/O o nuevas peticiones, logrando un paralelismo real en multicore.

## 📊 Análisis de Complejidad Computacional

### Búsqueda Vectorial
Para un índice de tamaño $N$ y dimensión $D$:
*   **Brute Force (Baseline implementado)**: $O(N \cdot D)$. Con SIMD (AVX2), procesamos 8 floats por ciclo.
*   **HNSW (Planned Production)**: $O(\log N \cdot D)$. La estructura de grafo jerárquico permite "saltar" rápidamente hacia la vecindad del query.

## 🛠️ Build & Run
```bash
docker-compose up --build
```
El servicio estará disponible en `http://localhost:8000/docs`.

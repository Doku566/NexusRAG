FROM python:3.9-slim AS builder

# Install build tools for C++ Extension
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy C++ Core
COPY nexus_core /app/nexus_core
WORKDIR /app/nexus_core
RUN mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc)

# Final Stage
FROM python:3.9-slim

WORKDIR /app

# Copy compiled extension
COPY --from=builder /app/nexus_core/build/nexus_core*.so /app/
# Copy API code
COPY nexus_api /app/nexus_api

# Install dependencies
RUN pip install fastapi uvicorn pydantic

ENV PYTHONPATH=/app

CMD ["uvicorn", "nexus_api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

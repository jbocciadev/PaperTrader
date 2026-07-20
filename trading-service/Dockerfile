# Build and compile dependencies
FROM python:3.11-slim AS builder
WORKDIR /build
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Compile wheels to local
RUN pip wheel --no-cache-dir --no-deps --wheel-dir=/build/wheels -r requirements.txt

# Runtime env
FROM python:3.11-slim AS runner
WORKDIR /app

COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY app/ ./app
COPY main.py .

# Open gRPC port
EXPOSE 50051

# Run worker engine
CMD ["python", "main.py"]
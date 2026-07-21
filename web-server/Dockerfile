# Build and compile dependencies
FROM python:3.11-slim AS builder
WORKDIR /build

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
# If wheels used, run:
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# If wheels not used, run:
    # RUN pip install --no-cache-dir -r requirements.txt


COPY app/ ./app

# Open external port
EXPOSE 8000

# Run worker engine
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

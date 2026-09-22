FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Run data preparation and evaluation setup
RUN python scripts/prepare_data.py && \
    python scripts/train_all_models.py

EXPOSE 8000 8501

# Default launch command runs API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

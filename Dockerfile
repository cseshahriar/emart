# Use official Python 3.12 slim image
FROM python:3.12-slim

# ----------------------------
# Environment settings
# ----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ----------------------------
# Set working directory
# ----------------------------
WORKDIR /app

# ----------------------------
# Install system dependencies
# ----------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Copy and install Python dependencies
# ----------------------------
COPY requirements ./requirements
RUN pip install --upgrade pip
RUN pip install -r requirements/local.txt

# ----------------------------
# Copy project code
# ----------------------------
COPY . .

# ----------------------------
# Make entrypoint executable
# ----------------------------
RUN chmod +x docker/entrypoint.sh

# ----------------------------
# Set container entrypoint
# ----------------------------
ENTRYPOINT ["docker/entrypoint.sh"]

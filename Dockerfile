# -------- Stage 1: Builder --------
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


# -------- Stage 2: Runtime --------
FROM python:3.11-slim

ENV TZ=UTC

WORKDIR /app

# Install cron + timezone tools
RUN apt-get update && apt-get install -y cron tzdata && rm -rf /var/lib/apt/lists/*

# Set timezone to UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Copy cron job file
#COPY deploy/mycron /etc/cron.d/mycron
COPY cron/2fa-cron /etc/cron.d/mycron
RUN chmod 0644 /etc/cron.d/mycron

# Create volume directories
RUN mkdir -p /data /cron && chmod 755 /data /cron

# Prepare cron log file
RUN touch /cron/last_code.txt && chmod 666 /cron/last_code.txt

# Copy entrypoint
RUN chmod +x deploy/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["deploy/entrypoint.sh"]

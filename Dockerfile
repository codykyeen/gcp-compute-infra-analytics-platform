FROM python:3.10-slim

WORKDIR /app

# Copy everything into container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install dbt
RUN pip install dbt-bigquery

# Make script executable
RUN chmod +x scripts/compute_pipeline.sh

# Set environment variables (optional defaults)
ENV PYTHONUNBUFFERED=1

# Create logs directory
RUN mkdir -p /app/logs

# Run pipeline
CMD ["./scripts/compute_pipeline.sh"]
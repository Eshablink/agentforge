FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && useradd --create-home --uid 10001 agentforge
COPY backend /app
RUN chown -R agentforge:agentforge /app
USER agentforge
EXPOSE 8000
# Run migrations separately as a one-shot job. Never migrate concurrently in
# every API replica; a failed migration must stop the deployment.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "127.0.0.1"]

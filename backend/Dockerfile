FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt && useradd --create-home --uid 10001 agentforge
COPY backend /app
RUN chown -R agentforge:agentforge /app
USER agentforge
EXPOSE 8000
CMD ["sh", "-c", "alembic -c alembic.ini upgrade head && exec python serve.py"]

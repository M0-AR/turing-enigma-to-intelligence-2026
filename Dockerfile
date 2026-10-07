FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY experiments/ ./experiments/
COPY tests/ ./tests/
COPY data/ ./data/
COPY Makefile ./Makefile
CMD ["python3", "experiments/run_all.py"]

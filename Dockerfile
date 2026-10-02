FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY app ./app
COPY etl ./etl
COPY tests ./tests

CMD ["python", "-m", "app.main"]
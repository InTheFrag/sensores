FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir requests

COPY sensor.py .

CMD ["python", "sensor.py"]

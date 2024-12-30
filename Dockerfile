FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dyndns_updater.py .

CMD ["python", "dyndns_updater.py"]
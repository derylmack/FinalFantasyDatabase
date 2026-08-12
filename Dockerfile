FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ffxiv_tracker.py

EXPOSE 5000

CMD ["python", "ffxiv_tracker.py"]
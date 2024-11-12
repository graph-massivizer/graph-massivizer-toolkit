FROM python:3.9-slim

WORKDIR /app

COPY runtime/workload_manager/ /app/

RUN pip install --no-cache-dir -r requirements.txt  # Include kazoo in requirements.txt

CMD ["python", "main.py"]
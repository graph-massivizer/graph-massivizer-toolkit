# components/client/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY components/client/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY commons /app/commons
COPY components/client /app/

ENV PYTHONPATH=/app

CMD ["python", "client.py"]
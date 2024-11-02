# components/metafactory/Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY components/metafactory/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY commons /app/commons
COPY components/metafactory /app/

ENV PYTHONPATH=/app

CMD ["python", "metafactory.py"]
# runtime/task_manager/Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY runtime/task_manager/ /app/

RUN pip install --no-cache-dir kazoo

CMD ["python", "main.py"]
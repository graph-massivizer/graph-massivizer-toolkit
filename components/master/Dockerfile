# components/master/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Copy the requirements file and install dependencies
COPY components/master/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the commons package
COPY commons /app/commons

# Copy the master component code
COPY components/master /app/

# Ensure the commons package is discoverable
ENV PYTHONPATH=/app

# Expose ports for web interface and API
EXPOSE 5001 5002

CMD ["python", "main.py"]
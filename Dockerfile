# file: src/graphmassivizer/runtime/Dockerfile

FROM python:3.10-slim

# We'll work in /app inside the container
WORKDIR /app

# Copy the *entire* repository from 3 levels up:
#  - The Dockerfile is in src/graphmassivizer/runtime/
#  - Going up 3 directories gets us to the project root
COPY . /app

# Upgrade pip first:
RUN python -m pip install --upgrade pip setuptools wheel

# Now install your code + dependencies, e.g.:
# If you have a requirements.txt in the repo root, do:
# RUN pip install --no-cache-dir -r requirements.txt

# Or if you use setup.py / setup.cfg, do:
RUN pip install --no-cache-dir .

# Copy + make executable the start.sh script (also in runtime/).
# It's already in your COPY above, but we'll re-copy if you want:
# COPY start.sh /app/start.sh
RUN chmod +x /app/src/graphmassivizer/runtime/start.sh

# If you have your start.sh in the same folder, use:
#  RUN chmod +x start.sh

# Default command: run the start.sh script, which checks ROLE.
CMD ["/app/src/graphmassivizer/runtime/start.sh"]
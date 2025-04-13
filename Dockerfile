FROM python:3.11-slim

WORKDIR /app

# System packages for audio processing
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY project_code/requirements.txt ./requirements.txt
COPY project_code/torch_reqs.txt ./torch_reqs.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install -r torch_reqs.txt

# Copy app and model
COPY app.py .
COPY model/ ./model
COPY project_code/ ./project_code

# Run FastAPI app
COPY serve /usr/local/bin/serve
RUN chmod +x /usr/local/bin/serve
ENTRYPOINT ["serve"]
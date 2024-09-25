FROM ubuntu:jammy-20240530


ENV PYTHONPATH="/run"

# Set working directory for the application
WORKDIR /run

# Update and install required packages, clean up lists to reduce image size
RUN apt-get update -qq && apt-get upgrade -y -qq && \
    apt-get install -y -qq --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    python3-pip \
    git \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements.txt and install Python dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# Copy the application code to the working directory
#COPY . /app

# Command to run the application
CMD ["python3", "-m", "fastapi", "dev", "src/server.py", "--host", "0.0.0.0", "--port", "8000"]
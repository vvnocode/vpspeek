# Use the appropriate base image
FROM python:3.9-slim

ENV TZ=Asia/Shanghai

# Install system dependencies needed to compile Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements.txt into the image
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY templates ./templates
COPY app.py .
COPY conf.yaml.default .

# Define the default command to run the app
CMD ["python", "app.py"]
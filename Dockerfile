# Stage 1: Build Stage
FROM python:3.9-alpine AS build

ENV TZ=Asia/Shanghai

# Install system dependencies needed to compile Python packages
RUN apk --no-cache add \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    make

# Set the working directory
WORKDIR /app

# Copy the requirements.txt into the build stage
COPY requirements.txt requirements.txt

# Install Python dependencies in a temporary directory
RUN pip install --no-cache-dir --target=/install -r requirements.txt

# Stage 2: Final Image
FROM python:3.9-alpine

ENV TZ=Asia/Shanghai

# Set the working directory
WORKDIR /app

# Install runtime dependencies only
RUN apk --no-cache add curl

# Copy the installed dependencies from the build stage
COPY --from=build /install /usr/local/lib/python3.9/site-packages

# Copy the rest of the application code
COPY templates ./templates
COPY app.py .
COPY conf.yaml.default .

# Define the default command to run the app
CMD ["python", "app.py"]
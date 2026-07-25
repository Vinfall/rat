# Use the official Python image as the base image
# https://hub.docker.com/_/python
FROM python:3.14-slim-trixie

# Set the working directory to /app
WORKDIR /app

# Copy the local requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Expose port 8886
EXPOSE 8886

# Copy the local code to the container
COPY . .

# Run the Python script with Uvicorn, binding to all available network interfaces
CMD ["gunicorn", "app:app", "--max-requests", "50", "--worker-class", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8886"]

# Use a Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script into the container
COPY monitor.py /app/monitor.py

# Copy the requirements file and install dependencies
COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y libpq-dev

RUN pip install -r requirements.txt

# Set environment variables (to be overridden in Kubernetes)
ENV POSTGRES_HOST=localhost
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=mydatabase
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword
ENV INTERVAL_MINUTES=10
ENV IDLE_THRESHOLD="1 hour"

# Command to run the Python script
CMD ["python", "monitor.py"]

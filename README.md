# PostgMon

This project is designed to monitor idle PostgreSQL connections and terminate those that have been idle for a specified amount of time (default: 1 hour). The configuration can be adjusted using environment variables.



Steps:

## Prerequisites

- Docker
- Kubernetes
- Access to a PostgreSQL database


### 1. Build the Docker image

```bash
docker build -t postgres-idle-monitor:latest .

docker tag postgres-idle-monitor:latest your-docker-repo/postgres-idle-monitor:latest
docker push your-docker-repo/postgres-idle-monitor:latest



postgresql://<username>:<password>@<host>:<port>/<database>
POSTGRES_URL="postgresql://myuser:mypassword@postgres-container:5432/mydatabase"


Base Image:

python:3.9-alpine

Choice of Base Image:

>The base image python:3.9-alpine is a lightweight version of Python built on Alpine Linux. This choice is intentional for the following reasons:

> Minimal Size: Alpine images are significantly smaller than other distributions, which reduces the overall image size and speeds up downloads and deployments.

> Security: The smaller attack surface of Alpine makes it a more secure choice for deploying applications.

> Python Compatibility: This image includes Python 3.9, ensuring compatibility with the latest features and libraries.






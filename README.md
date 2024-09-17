# PostgreSQL Idle Connection Monitor

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





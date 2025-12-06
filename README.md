## EmberAlert Infrastructure & Performance Testing

This repository contains the infrastructure setup (via Docker Compose) and performance testing scripts used for evaluating the EmberAlert backend, and notification pipeline.

It includes:
- A Dockerized environment for:
    - PostgreSQL database
    - Scheduler service (fetches CalFire data and inserts fires into DB)
    - Backend service (API + WebSocket notifications)

- Automated tests measuring:
    - REST API latency
    - Notification latency via WebSocket

## Important: Replace the `AWS_IP` Placeholder in Tests

The test scripts reference the backend using a placeholder value:
``` shell
BASE_URL = "http://<AWS_IP>"
```
> It is left as a placeholder so sensitive infrastructure details are not committed to the repository.

Before running the tests, replace `<AWS_IP>` with one of the following:

### Option 1 — Your own EC2 Public IP

If your backend is deployed on an AWS EC2 instance:

```shell
BASE_URL = "http://<your-ec2-public-ip>"
```
### Option 2 — Localhost (*if running everything via Docker Compose locally*)

```shell
BASE_URL = "http://localhost:8000"
```


## Docker Image Versions
The compose file uses the latest `backend` and `scheduler` images for `linux/amd64` platforms.
If you need `linux/arm64`, update the image fields in the compose file to:

```yaml
scheduler:
    image: carlosqmv/scheduler:linux-amd64
    ...


backend:
    image: carlosqmv/backend:linux-amd64
```
Docker Hub links for reference:

- Backend: https://hub.docker.com/r/carlosqmv/backend  
- Scheduler: https://hub.docker.com/r/carlosqmv/scheduler
> **Note**: Numeric image tags are associated with `linux/amd64` platforms.
`linux-arm64` tags are for `linux/arm64` platforms.


## 
```shell
infrastructure/
├── docker/
│   ├── docker-compose.yml      # Docker compose for DB, backend, scheduler
│   └── init.sql                # Database initialization script
│
├── tests/
│   ├── get_fires_test.py       # Measures REST API latency for fetching fires
│   ├── notifications_test.py   # Measures latency of notifications via WebSocket
│   └── notifications_test_parallel.py  # Parallel version for llatency of notifications
│
├── requirements.txt            # Python test dependencies
└── .gitignore
```

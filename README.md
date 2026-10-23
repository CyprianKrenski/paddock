# paddock

Replay of past Formula 1 races, built as microservices for the BTH course PA2577.

## Local development

```bash
cp .env.example .env            # then fill in POSTGRES_PASSWORD
uv sync
docker compose up -d postgres
uv run --env-file .env alembic -c services/catalogue/alembic.ini upgrade head
uv run --env-file .env pytest -q          # integration tests included
uv run pytest -q                          # unit tests only, integration skipped
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run --env-file .env uvicorn catalogue.main:from_env --factory --port 8001
```

## Containers

One `Dockerfile` builds any service (`--build-arg SERVICE=catalogue|analysis|web`).

```bash
docker compose up --build -d        # postgres, one-shot migrate, catalogue :8000, analysis :8001, web :8080
open http://localhost:8080          # load a season, load a race, open its replay (race trace kept as a fallback view)
docker compose logs -f web
scripts/build-push.sh <dockerhub-user> 0.1.0   # multi-arch images for Kubernetes (needs docker login)
```

## Kubernetes (Docker Desktop)

```bash
source scripts/kube-env.sh          # writes ~/.kube/paddock with the docker-desktop context only
kubectl apply -f k8s/00-namespace.yaml
kubectl create secret generic paddock-secret --from-literal=POSTGRES_PASSWORD=<password>
kubectl apply -f k8s/                # postgres, then catalogue (migrates first), analysis, web
kubectl get pods -w
open http://localhost                # web is the only Service of type LoadBalancer
kubectl logs deployment/catalogue -c migrate
```

The secret is never stored in the repository. Deleting the manifests keeps the Postgres volume:

```bash
kubectl delete -f k8s/postgres.yaml && kubectl apply -f k8s/postgres.yaml   # data survives
kubectl delete pvc data-postgres-0                                           # drops the data
```

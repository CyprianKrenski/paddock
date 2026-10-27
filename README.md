# paddock

Replay of past Formula 1 races, built as two microservices on Kubernetes for the BTH course PA2577.
`catalogue` ingests races from the Jolpica F1 API into Postgres and computes race traces and replay
keyframes; `web` renders the pages and talks to `catalogue` over REST.

## Layout

```
catalogue/   ingest, storage, computations (api, features, entities, infrastructure, alembic)
web/         pages, replay, tables (api, features, entities, infrastructure, templates)
tests/       tests per package, fakes next to them
k8s/         manifests, applied in alphabetical order by kubectl
scripts/     kube-env.sh, metrics-server.sh, build-push.sh, load.sh
```

## Local development

```bash
cp .env.example .env            # then fill in POSTGRES_PASSWORD
uv sync --all-extras
docker compose up -d postgres
uv run --env-file .env alembic upgrade head
uv run --env-file .env pytest -q          # integration tests included
uv run pytest -q                          # unit tests only, integration skipped
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run --env-file .env uvicorn catalogue.main:from_env --factory --port 8001
```

## Containers

One `Dockerfile` builds either service (`--build-arg SERVICE=catalogue|web`); each image installs
only its own extra from `pyproject.toml`.

```bash
docker compose up --build -d        # postgres, one-shot migrate, catalogue :8000, web :8080
open http://localhost:8080          # load a season, load a race, open its replay
docker compose logs -f web
scripts/build-push.sh cypriankrenski93 0.3.0   # multi-arch images for Kubernetes
```

## Kubernetes (Docker Desktop)

Enable Kubernetes in Docker Desktop first. Every command below runs in the `paddock` namespace:
`scripts/kube-env.sh` writes `~/.kube/paddock` with only the `docker-desktop` context and sets the
namespace; without it, add `-n paddock` to every `kubectl` call.

```bash
source scripts/kube-env.sh
kubectl apply -f k8s/00-namespace.yaml
kubectl create secret generic paddock-secret \
  --from-literal=POSTGRES_PASSWORD="$(sed -n 's/^POSTGRES_PASSWORD=//p' .env)"   # read from .env, never typed into the shell history
scripts/metrics-server.sh                       # once per cluster; needed by kubectl top and the HPA
kubectl apply -f k8s/
kubectl rollout status deployment/catalogue     # waits for the Alembic initContainer and readiness
kubectl rollout status deployment/web
kubectl get pods,svc,hpa
```

`kubectl apply -f k8s/` applies the files in alphabetical order, so for a few seconds the catalogue
pod may wait for the ConfigMap and the HPA may report `<unknown>`; the controllers converge on their
own. The secret is never stored in the repository. `http://localhost` is the `web` Service of type
LoadBalancer; `catalogue` and `postgres` are reachable only inside the cluster (NetworkPolicy, not
enforced by the Docker Desktop network plugin, enforced on AKS).

Migration proof: `kubectl exec postgres-0 -- psql -U paddock -d paddock -c "select * from alembic_version"`
(the initContainer prints nothing, `alembic.ini` has no logging section).

Persistence test: delete only the database manifest, never the whole directory (deleting the
namespace removes the volume claim and the data):

```bash
kubectl delete -f k8s/postgres.yaml && kubectl apply -f k8s/postgres.yaml   # data survives
kubectl delete pvc data-postgres-0                                           # drops the data
```

Scaling: load a season and a race in the browser first, then

```bash
scripts/load.sh                                 # oha, 10 users for 60 s against a replay fragment
kubectl get hpa -w                              # web 1-4 and catalogue 1-3 scale on CPU
kubectl scale deployment web --replicas=3
```

`oha` is a single binary from https://github.com/hatoo/oha/releases (pick `oha-linux-amd64` or
`oha-linux-arm64` for your CPU).

The replay script in `web/templates/replay.html` has no browser test; `node tests/web/harness/replay_harness.js`
runs it against a recorded payload with a DOM stub and prints positions at chosen moments.

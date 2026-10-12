from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

router = APIRouter(prefix="/health")


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request) -> dict[str, str]:
    try:
        with request.app.state.session_factory() as session:
            session.execute(text("SELECT 1"))
    except OperationalError as error:
        raise HTTPException(status_code=503, detail="database unavailable") from error
    return {"status": "ok"}

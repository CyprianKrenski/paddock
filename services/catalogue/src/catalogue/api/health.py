from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from catalogue.api.dependencies import DbSession

router = APIRouter(prefix="/health")


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(session: DbSession) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    except OperationalError as error:
        raise HTTPException(status_code=503, detail="database unavailable") from error
    return {"status": "ok"}

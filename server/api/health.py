from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text

from server.database import AsyncSession, get_db

router = APIRouter()


@router.get("/", tags=["Health"])
async def healthcheck(session: AsyncSession = Depends(get_db)):
    try:
        await session.execute(text("SELECT 1"))
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "error", "detail": str(e)}
        )

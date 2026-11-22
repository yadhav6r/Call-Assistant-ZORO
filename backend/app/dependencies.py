from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db(request: Request):
    factory = request.app.state.db_session_factory
    async with factory() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]

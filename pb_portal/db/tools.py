from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from pb_portal.db.db import get_async_session
from pb_portal.db.models import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from pb_portal.auth.schemas import UserRoles
from sqlalchemy import text, select, insert
from pb_portal.config import logger


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def prepare_user_roles():
    async for session in get_async_session():
        db_roles = await session.execute(select(UserRole))
        roles = db_roles.scalars().all()
        roles = {role.name: role.id for role in roles}
        for role in UserRoles:
            if role.name not in roles and role.value not in roles.values():
                await session.execute(
                    insert(UserRole).values(name=role.name, id=role.value)
                )
            elif role.name in roles and roles[role.name] != role.value:
                logger.error(f"Role {role.name} has id {roles[role.name]} but should have id {role.value}")
                raise ValueError(f"Role {role.name} has id {roles[role.name]} but should have id {role.value}")
        await session.commit()
        await session.close()

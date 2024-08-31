from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from pb_portal.db.db import get_async_session
from pb_portal.db.models import User, UserRole, ProductScheldule
from sqlalchemy.ext.asyncio import AsyncSession
from pb_portal.auth.schemas import UserRoles
from sqlalchemy import select, insert
from pb_portal.config import logger
from datetime import datetime, timezone


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


async def get_users(page: int = 1, per_page: int = 10) -> list[User]:
    async for session in get_async_session():
        users = await session.execute(
            select(User)
            .order_by(User.id)
            .limit(per_page)
            .offset((page - 1) * per_page)
        )
        users = users.scalars().all()
        return users


async def get_user(user_id: int) -> User | None:
    async for session in get_async_session():
        user = await session.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        return user


async def edit_user(user_id: int, email: str, role: int, password: str = None):
    async for session in get_async_session():
        user = await session.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        user.email = email
        user.role_id = role
        if password:
            user.hashed_password = password
        await session.commit()


async def rm_user(user_id: int):
    async for session in get_async_session():
        user = await session.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        await session.delete(user)
        await session.commit()


async def create_user(email: str, password: str, role: int):
    async for session in get_async_session():
        user = User(
            email=email,
            hashed_password=password,
            role_id=role,
            is_active=True,
            is_superuser=False,
            is_verified=True
        )
        session.add(user)
        await session.commit()
        return user


async def sign_agreement(user_id: int) -> User | None:
    async for session in get_async_session():
        user = await session.execute(select(User).filter(User.id == user_id))
        user = user.scalar_one_or_none()
        if not user or user.signed_agreement_date:
            return
        user.signed_agreement_date = datetime.now(timezone.utc).date()
        await session.commit()
        return user


async def add_schedule(product_id: int, date_time: datetime):
    async for session in get_async_session():
        schedule = ProductScheldule(
            product_id=product_id,
            date_time=date_time.replace(tzinfo=None)
        )
        session.add(schedule)
        await session.commit()


async def set_filed_schedule(product_id: int) -> bool:
    async for session in get_async_session():
        schedule = await session.execute(select(ProductScheldule).filter(ProductScheldule.product_id == product_id))
        schedule = schedule.scalar_one_or_none()
        if not schedule:
            return False
        schedule.is_filed = True
        await session.commit()
        return True


async def pop_publish_queue():
    async for session in get_async_session():
        schedules = await session.execute(
            select(
                ProductScheldule
            ).filter(
                ProductScheldule.is_filed == True,
                ProductScheldule.date_time <= datetime.now(timezone.utc).replace(tzinfo=None)
            ))
        schedules = schedules.scalars().all()
        queue = [schedule.product_id for schedule in schedules]
        for schedule in schedules:
            await session.delete(schedule)
        await session.commit()
        return queue

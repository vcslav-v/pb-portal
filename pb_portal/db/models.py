from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from fastapi_users.db import SQLAlchemyBaseUserTable
from datetime import date, datetime


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTable[int], Base):
    """Users."""

    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)

    signed_agreement_date: Mapped[date] = mapped_column(nullable=True)
    creator_id: Mapped[int] = mapped_column(nullable=True)

    role_id: Mapped[int] = mapped_column(ForeignKey('user_role.id'))
    role: Mapped['UserRole'] = relationship(back_populates='users')


class UserRole(Base):
    """Roles."""

    __tablename__ = 'user_role'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    users: Mapped[list['User']] = relationship()


class ProductScheldule(Base):
    """Product schedule."""

    __tablename__ = 'product_schedule'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column()
    date_time: Mapped[datetime] = mapped_column()
    is_filed: Mapped[bool] = mapped_column(default=False)

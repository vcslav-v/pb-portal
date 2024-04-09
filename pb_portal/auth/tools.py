from pb_portal.auth.manager import get_user_manager
from pb_portal.auth.backend import auth_backend
from pb_portal.db.models import User
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
optional_active_user = fastapi_users.current_user(active=True, optional=True)
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

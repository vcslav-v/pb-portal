from fastapi import Request
from fastapi.responses import RedirectResponse


async def http_exception_handler(request: Request, exc):
    if exc.status_code == 401:
        return RedirectResponse(request.url_for('login'), status_code=303)
    return await request.app.default_exception_handler(request, exc)

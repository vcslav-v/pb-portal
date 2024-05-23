from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse


async def http_exception_handler(request: Request, exc):
    if exc.status_code == 401:
        return RedirectResponse(request.url_for('login'), status_code=303)
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

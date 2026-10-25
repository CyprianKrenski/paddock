from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from web.entities.errors import NotFound, UpstreamDown


def render_error(request: Request, status_code: int, message: str) -> HTMLResponse:
    templates: Jinja2Templates = request.app.state.templates
    context = {"status_code": status_code, "message": message}
    return templates.TemplateResponse(request, "error.html", context, status_code=status_code)


def not_found(request: Request, error: Exception) -> HTMLResponse:
    return render_error(request, 404, str(error))


def upstream_down(request: Request, error: Exception) -> HTMLResponse:
    return render_error(request, 503, str(error))


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFound, not_found)
    app.add_exception_handler(UpstreamDown, upstream_down)

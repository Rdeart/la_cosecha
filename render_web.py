"""Adaptador de despliegue: web e interfaz en un solo servicio Render.

Los archivos originales app/ y front/index.html permanecen intactos.
- Navegacion a / abre el HTML.
- Las llamadas a la API (Accept: */* o application/json) siguen usando /.
- Todas las rutas originales (/docs, /auth, /productos, etc.) se delegan sin cambios.
"""

import os
from pathlib import Path
from urllib.parse import urlencode

from starlette.requests import Request
from starlette.responses import FileResponse, PlainTextResponse, RedirectResponse

from app.main import app as api_original

ARCHIVO_HTML = Path(__file__).resolve().parent / "front" / "index.html"


class InterfazYAPl:
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            # Es fundamental preservar el evento lifespan del FastAPI original,
            # que inicializa PostgreSQL y el primer usuario administrador.
            await api_original(scope, receive, send)
            return

        ruta = scope.get("path", "")
        metodo = scope.get("method", "")
        request = Request(scope, receive=receive)

        if ruta == "/" and metodo == "HEAD":
            await PlainTextResponse("", status_code=200)(scope, receive, send)
            return

        pide_interfaz = "text/html" in request.headers.get("accept", "").lower()
        if metodo == "GET" and (ruta == "/interfaz" or ruta == "/" and pide_interfaz):
            # La propia pagina soporta ?api=URL; se aprovecha sin editar el HTML.
            # Render provee el enlace publico correcto para este mismo servicio.
            if not request.query_params.get("api"):
                url_api = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
                if not url_api:
                    url_api = str(request.base_url).rstrip("/")
                parametros = list(request.query_params.multi_items()) + [("api", url_api)]
                destino = str(request.url.replace(query=urlencode(parametros)))
                await RedirectResponse(destino, status_code=307)(scope, receive, send)
                return
            await FileResponse(ARCHIVO_HTML, media_type="text/html; charset=utf-8")(scope, receive, send)
            return

        # Dejar la API intacta, incluida su respuesta JSON en GET /.
        await api_original(scope, receive, send)


app = InterfazYAPl()

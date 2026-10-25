# La Cosecha - mostrar la interfaz desde el mismo enlace Render

## Diagnostico confirmado por tus logs
- El deploy ha sido exitoso: `Build successful`, `Application startup complete`, `Your service is live`.
- `GET /` respondia el JSON `{"mensaje":"API de La Cosecha en línea 🌾"}` porque se estaba ejecutando `fastapi run app/main.py --port $PORT` (solo API).
- `front/index.html` existe, pero no se estaba sirviendo por el proceso de FastAPI.
- El HTML apunta en ausencia de `?api` a `https://la-cosecha-api.onrender.com`; la API real es `https://la-cosecha-cakn.onrender.com`.

## Solucion incluida (SIN editar archivos originales)
Un archivo nuevo `render_web.py` presenta `front/index.html` al navegar desde el navegador, y conserva intacto el FastAPI en todas las rutas originales. No edita ningun archivo de `app/`, `front/`, `requirements.txt`, `.env.example` ni `README.md`. Aplica la opcion `?api=` que ya esta en el frontend original. Usa `RENDER_EXTERNAL_URL`, variable automatica de Render.

## En tu mismo servicio Render (el ya publicado)
1. Descomprime el ZIP y sube los archivos a TU repositorio GitHub `https://github.com/Rdeart/la_cosecha` en la raiz. No borres datos del servicio ni las variables secretas de Render. Las carpetas `app/` y `front/` deben quedar al mismo nivel que `render_web.py`.
2. Comprueba que GitHub contiene el nuevo archivo `render_web.py` y `requirements-render.txt`. Haz commit.
3. Ve a Render Dashboard > tu Web Service > Settings > Build & Deploy. Deja **Root Directory** vacio si los archivos estan en la raiz.
4. En **Build Command** coloca exactamente:

   `pip install -r requirements-render.txt`

5. En **Start Command** coloca exactamente:

   `uvicorn render_web:app --host 0.0.0.0 --port $PORT`

6. Conserva tus Environment Variables existentes, particularmente `DATABASE_URL`, `SECRET_KEY`, `ADMIN_NOMBRE`, `ADMIN_CORREO` y `ADMIN_CONTRASENA`. No las publiques en GitHub.
7. En Render haz **Manual Deploy > Deploy latest commit** si no se dispara solo; espera `Your service is live`.
8. Abre `https://la-cosecha-cakn.onrender.com/` desde el navegador. Debe redirigir a la misma URL agregando `?api=` y presentar las pantallas de La Cosecha.
9. Para verificar el backend sigue disponible `https://la-cosecha-cakn.onrender.com/docs`.

## Validaciones / notas
- Las llamadas fetch de la interfaz a `GET /` obtienen JSON, mientras que la navegacion desde el navegador recibe HTML. Eso es intencional.
- Como interfaz y API estan bajo el mismo dominio, no hace falta configurar un segundo Static Site ni modificar CORS.
- No hace falta crear otra base de datos ni otro servicio; se reutilizan los existentes.
- Si la interfaz abre pero el inicio de sesion falla, revisa las variables de administrador y los logs; la contraseña de un usuario ya creado no cambia solo por editar `ADMIN_CONTRASENA`.
- Si el servicio sigue mostrando el JSON en el navegador, casi seguro sigue ejecutandose el Start Command viejo, o no esta desplegado el commit que contiene `render_web.py`.
- La respuesta visual aun depende de que el servicio actual en Render reciba el nuevo archivo y reinicie correctamente.

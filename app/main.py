from fastapi import FastAPI

from app.routes import health, links, web

app = FastAPI(title="Encurtador de Links", version="0.1.0")

app.include_router(health.router)
app.include_router(web.router)
# Por último, porque contém a rota "pega-tudo" /{code}.
app.include_router(links.router)

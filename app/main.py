from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.middleware import RequestIdMiddleware, LoggingMiddleware, RateLimitMiddleware

# Importar todos los routers del microservicio
from app.api.routes import (
    products,
    suppliers,
    categories,
    units,
    product_attributes
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="product-service",
        version="1.0.0"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middlewares
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Rutas principales
    app.include_router(products.router, prefix=settings.API_V1_STR)
    app.include_router(suppliers.router, prefix=settings.API_V1_STR)
    app.include_router(categories.router, prefix=settings.API_V1_STR)
    app.include_router(units.router, prefix=settings.API_V1_STR)
    app.include_router(product_attributes.router, prefix=settings.API_V1_STR)

    @app.get("/health")
    async def health():
        return {"ok": True}

    return app


app = create_app()

"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.tipo_equipos import router as tipo_equipos_router
from backend.app.api.routes.subtipo_equipos import router as subtipo_equipos_router
from backend.app.api.routes.marcas import router as marcas_router
from backend.app.api.routes.empleados import router as empleados_router
from backend.app.api.routes.clientes import router as clientes_router
from backend.app.api.routes.departamentos import router as departamentos_router
from backend.app.api.routes.equipos import router as equipos_router
from backend.app.api.routes.ordenes_servicio import router as ordenes_servicio_router

# Legacy routes — disabled until infrastructure is migrated to new schema
# from backend.app.api.routes.onedrive import router as onedrive_router
from backend.app.api.routes.pdf import router as pdf_router
# from backend.app.api.routes.attachments import router as attachments_router
# from backend.app.api.routes.categories import router as categories_router
# from backend.app.api.routes.public import router as public_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance.
    """
    app = FastAPI(
        title="Ofiuco Medical API",
        description="Biomedical equipment service order management system",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers (authenticated)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(tipo_equipos_router, prefix="/api/v1")
    app.include_router(subtipo_equipos_router, prefix="/api/v1")
    app.include_router(marcas_router, prefix="/api/v1")
    app.include_router(empleados_router, prefix="/api/v1")
    app.include_router(clientes_router, prefix="/api/v1")
    app.include_router(departamentos_router, prefix="/api/v1")
    app.include_router(equipos_router, prefix="/api/v1")
    app.include_router(ordenes_servicio_router, prefix="/api/v1")

    # Legacy routes — disabled until infrastructure is migrated to new schema
    # app.include_router(onedrive_router, prefix="/api/v1")
    app.include_router(pdf_router, prefix="/api/v1")
    # app.include_router(attachments_router, prefix="/api/v1")
    # app.include_router(categories_router, prefix="/api/v1")

    # Public routes (no auth) — disabled until migrated
    # app.include_router(public_router)
    
    # Health endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> JSONResponse:
        """Health check endpoint.
        
        Returns:
            JSON response with status information.
        """
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "ofiuco-medical-api",
                "version": "1.0.0",
            }
        )
    
    return app


# Create the app instance for uvicorn
app = create_app()

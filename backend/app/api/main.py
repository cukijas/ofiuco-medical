"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.clients import router as clients_router
from backend.app.api.routes.equipment import router as equipment_router
from backend.app.api.routes.service_orders import router as service_orders_router
from backend.app.api.routes.onedrive import router as onedrive_router
from backend.app.api.routes.pdf import router as pdf_router
from backend.app.api.routes.attachments import router as attachments_router
from backend.app.api.routes.categories import router as categories_router
from backend.app.api.routes.public import router as public_router


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
    app.include_router(clients_router, prefix="/api/v1")
    app.include_router(equipment_router, prefix="/api/v1")
    app.include_router(service_orders_router, prefix="/api/v1")
    app.include_router(onedrive_router, prefix="/api/v1")
    app.include_router(pdf_router, prefix="/api/v1")
    app.include_router(attachments_router, prefix="/api/v1")
    app.include_router(categories_router, prefix="/api/v1")

    # Public routes (no auth)
    app.include_router(public_router)
    
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

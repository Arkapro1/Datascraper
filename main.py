# main.py
from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.responses import FileResponse
import os
import logging
from dadscrapergapi import get_places_gApi
from invoice import router as invoice_router
from datascraper import PlacesResponse, get_places, normalize_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Invoice Generator API",
    description="API for generating PDF invoices",
    version="1.0.0"
)

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))




# Include the invoice router
app.include_router(invoice_router, prefix="/api", tags=["invoices"])

@app.get("/")
async def read_root():
    """Root endpoint returning API status."""
    return {
        "message": "Invoice Generator API is running",
        "version": "1.0.0",
        "endpoints": {
            "generate_invoice": "/api/invoice_generator/",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "invoice-generator"}

@app.get("/places", response_model=PlacesResponse)
def search_places(
    location: str = Query(..., description="Any address, area, or ward (e.g., 'Ward 94 Kolkata', 'Ballygunge Kolkata')"),
    type: str = Query(..., description="One or more types (comma-separated, e.g., 'restaurant,hotel,cafe')"),
    radius: int = Query(5000, ge=1000, le=20000, description="Search radius in meters (default 5000=5km)"),
    limit: int = Query(10, ge=1, le=50, description="Number of results (default 10, max 50)")
):
    user_types = [t.strip() for t in type.split(",") if t.strip()]
    places = get_places(user_types, location, radius, limit)
    return PlacesResponse(query=location, types=user_types, radius=radius, results=places)

@app.get("/gplaces", response_model=PlacesResponse)
def search_gplaces(
    location: str = Query(..., description="Any address, area, or ward (e.g., 'Ward 94 Kolkata', 'Ballygunge Kolkata')"),
    type: str = Query(..., description="One or more types (comma-separated, e.g., 'restaurant,hotel,cafe')"),
    radius: int = Query(5000, ge=1000, le=20000, description="Search radius in meters (default 5000=5km)"),
    limit: int = Query(10, ge=1, le=50, description="Number of results (default 10, max 50)")
):
    user_types = [t.strip() for t in type.split(",") if t.strip()]
    places = get_places_gApi(user_types, location, radius, limit)
    return PlacesResponse(query=location, types=user_types, radius=radius, results=places)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )

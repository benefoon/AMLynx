from fastapi import status
from app.schemas import HealthCheckResponse

app = FastAPI(...)

@app.get(
    "/health",
    tags=["Monitoring"],
    summary="Perform a Health Check",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK
)
def perform_health_check():
    """
    Simple health check endpoint.
    Returns `status: "ok"` if the service is running.
    """
    return HealthCheckResponse(status="ok")

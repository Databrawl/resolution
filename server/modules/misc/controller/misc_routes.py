from fastapi import APIRouter

misc_router = APIRouter()


@misc_router.get("/")
def root():
    """
    Root endpoint to check the status of the API.
    """
    return {"status": "OK"}


@misc_router.get("/healthz", tags=["Health"])
def healthz():
    return {"status": "ok"}

# routes/swagger_routes.py

from fastapi import APIRouter

router = APIRouter()

@router.get("/docs", tags=["Docs"], include_in_schema=False)
def get_docs():
    return {"message": "Swagger documentation available at /docs"}

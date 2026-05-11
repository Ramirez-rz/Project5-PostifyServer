from app.routers import users
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allowed_origins=['https://localhost5173']
)

app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/scalar',include_in_schema=False)
def get_docs_scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware 
from src.api.endpoints.immich.immich import router as immich_router
from src.api.endpoints.journiv.journiv import router as journiv_router


app = FastAPI()

app.include_router(immich_router, prefix="/api")
app.include_router(journiv_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "*"
    ],
    allow_credentials=True,
    allow_methods=["OPTIONS", "POST", "GET", "DELETE", "PUT", "PATCH"],
    allow_headers=["Content-Type"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
import uvicorn
from fastapi import FastAPI

from app.api import router
from .config import config

app = FastAPI()

app.include_router(router.router)

if __name__ == '__main__':
    uvicorn.run("main:app", port=config.PORT, host=config.HOST, reload=True)
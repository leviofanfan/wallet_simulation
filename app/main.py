import uvicorn
from fastapi import FastAPI

from app.api import router


app = FastAPI()


app.include_router(router.router)


if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, host='127.0.0.1', reload=True)
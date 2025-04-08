from fastapi import FastAPI

from src.controllers.auth_controller import router as auth_router
from src.controllers.item_controller import router as item_router
from src.controllers.preferences_controller import router as preferences_router
from src.controllers.web_scraping_controller import router as web_scraping_router
from src.data_access_layer import connect_to_db

app = FastAPI()

connect_to_db()

app.include_router(auth_router, prefix="/api/auth")
app.include_router(item_router, prefix="/api")
app.include_router(preferences_router, prefix="/api")
app.include_router(web_scraping_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)

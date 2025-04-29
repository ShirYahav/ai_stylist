from fastapi import FastAPI
from src.controllers.auth_controller import router as auth_router
from src.controllers.wardrobe_controller import router as wardrobe_router
from src.controllers.wishlist_controller import router as wishlist_router
from src.controllers.preferences_controller import router as preferences_router
from src.controllers.weather_controller import router as weather_router
from src.data_access_layer import connect_to_db
from src.controllers.serpai_controller import router as serpai_router
from src.controllers.web_scraping_controller import router as web_scraping_router
from src.controllers.llama3_chat_controller import router as llama_chat_router

app = FastAPI()

connect_to_db()

app.include_router(auth_router, prefix="/api/auth")
app.include_router(preferences_router, prefix="/api")
app.include_router(wardrobe_router, prefix="/api/wardrobe")
app.include_router(wishlist_router, prefix="/api/wishlist")
app.include_router(weather_router, prefix="/api")   
app.include_router(serpai_router, prefix="/api")
app.include_router(web_scraping_router, prefix="/api/scrape")
app.include_router(llama_chat_router, prefix="/api/chat")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
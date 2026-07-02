

# import uvicorn
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from database import engine, Base  

# # 🔌 ទាញយកម៉ូដែលទាំងអស់មក ដើម្បីឱ្យ SQLAlchemy បង្កើតតារាងក្នុង PostgreSQL អូតូ
# from app.models.user import User
# from app.models.category import Category 
# from app.models.item import Item

# # 🔌 ទាញយកផ្លូវ API ទាំងអស់មកប្រើ
# from app.routes.user_routes import router as user_router
# from app.routes.auth_routes import router as auth_router     
# from app.routes.category_routes import router as category_router 
# from app.routes.item_routes import router as item_router

# # បង្កើត Tables ទាំងអស់ទៅក្នុង PostgreSQL ស្វ័យប្រវត្តិ
# Base.metadata.create_all(bind=engine)
# print("Database Tables Synced Successfully! 🎉")

# # បង្កើត Instance របស់ FastAPI
# app = FastAPI(title="FastAPI Standard Project Structure with JWT Auth")

# # បើកទ្វារឱ្យ Browser អាចចូលមើលរូបភាពក្នុង Folder static បាន
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # ភ្ជាប់ផ្លូវ Routers ទាំងអស់ចូលកម្មវិធីមេ
# app.include_router(user_router)
# app.include_router(auth_router)      
# app.include_router(category_router)  
# app.include_router(item_router)

# @app.get("/")
# def index():
#     return {"message": "Welcome to FastAPI Secure Project!"}

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base  

# 🔌 ទាញយកម៉ូដែលទាំងអស់មក ដើម្បីឱ្យ SQLAlchemy បង្កើតតារាងក្នុង PostgreSQL អូតូ
from app.models.user import User
from app.models.category import Category 
from app.models.item import Item

# 🔌 ទាញយកផ្លូវ API ទាំងអស់មកប្រើ
from app.routes.user_routes import router as user_router
from app.routes.auth_routes import router as auth_router     
from app.routes.category_routes import router as category_router 
from app.routes.item_routes import router as item_router

# បង្កើត Tables ទាំងអស់ទៅក្នុង PostgreSQL ស្វ័យប្រវត្តិ
Base.metadata.create_all(bind=engine)
print("Database Tables Synced Successfully! 🎉")

# បង្កើត Instance របស់ FastAPI
app = FastAPI(title="FastAPI Standard Project Structure with JWT Auth")

# កំណត់បញ្ជីឈ្មោះ Website (Frontend) ដែលយើងអនុញ្ញាតឱ្យហៅ API បាន
origins = [
    "http://localhost:3000",  # ផ្លូវរបស់ Next.js Frontend របស់អ្នក
    "http://127.0.0.1:3000",
]

# ដាក់ Middleware CORS ចូលទៅក្នុងកម្មវិធីមេ app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # អនុញ្ញាតឱ្យឈ្មោះខាងលើចូលប្រើបាន
    allow_credentials=True,
    allow_methods=["*"],              # អនុញ្ញាតគ្រប់ Method (GET, POST, PUT, DELETE, ...)
    allow_headers=["*"],              # អនុញ្ញាតគ្រប់ HTTP Headers
)

# ✅ បើកទ្វារឱ្យ Browser/Chrome ចូលមើលរូបភាពក្នុង Folder static បាន
app.mount("/static", StaticFiles(directory="static"), name="static")

# ភ្ជាប់ផ្លូវ Routers ទាំងអស់ចូលកម្មវិធីមេ
app.include_router(user_router)
app.include_router(auth_router)      
app.include_router(category_router)  
app.include_router(item_router)

@app.get("/")
def index():
    return {"message": "Welcome to FastAPI Secure Project!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
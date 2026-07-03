import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base  

# 🔌 ១. នាំចូលម៉ូដែលទាំងអស់ (Models)
from app.models.user import User
from app.models.category import Category 
from app.models.item import Item
from app.models.cart import CartItem  
from app.models.order import Order, OrderItem  

# 🔌 ២. នាំចូលផ្លូវ API (Routes)
from app.routes.user_routes import router as user_router
from app.routes.auth_routes import router as auth_router     
from app.routes.category_routes import router as category_router 
from app.routes.item_routes import router as item_router
from app.routes.cart_routes import router as cart_router  
from app.routes.order_routes import router as order_router 
from app.routes.dashboard import router as dashboard_router  # នាំចូល Router នៃ Dashboard

# បង្កើត Tables ទាំងអស់ទៅក្នុង Database ស្វ័យប្រវត្តិកាលណា Server ចាប់ផ្តើមរត់
Base.metadata.create_all(bind=engine)
print("Database Tables Synced Successfully! 🎉")

# បង្កើត Instance របស់ FastAPI
app = FastAPI(title="FastAPI Secure E-commerce Backend")

# កំណត់ CORS ដើម្បីឱ្យ Frontend ហៅ API បាន
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# បើកទ្វារឱ្យ Browser មើលរូបភាពក្នុង Folder static បាន
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🔌 ៣. ភ្ជាប់ផ្លូវ Routers ទាំងអស់ចូលកម្មវិធីមេ
app.include_router(user_router)
app.include_router(auth_router)      
app.include_router(category_router)  
app.include_router(item_router)
app.include_router(cart_router)  
app.include_router(order_router) 
app.include_router(dashboard_router) # ភ្ជាប់ Dashboard Router មកទីនេះ

@app.get("/")
def index():
    return {"message": "Welcome to FastAPI Secure E-commerce Project!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
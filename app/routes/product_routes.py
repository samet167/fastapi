import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from database import get_db
from app.models.products import Product
from app.schemas.product_schema import ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

UPLOAD_DIR = "static/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===========================================================
# 1. CREATE: បង្កើតទំនិញថ្មី និង Upload រូបភាព (POST)
# ===========================================================
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # រៀបចំរក្សាទុករូបភាព
    file_extension = os.path.splitext(file.filename)[1]
    
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # កត់ត្រាទិន្នន័យចូល Database
    new_product = Product(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        image=f"/{file_path}"
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# ===========================================================
# 2. READ ALL: ទាញយកបញ្ជីទំនិញទាំងអស់ (GET)
# ===========================================================
@router.get("/", response_model=list[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

# ===========================================================
# 3. READ ONE: ទាញយកទំនិញម្នាក់តាម ID (GET)
# ===========================================================
@router.get("/{id}", response_model=ProductResponse)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"រកមិនឃើញទំនិញដែលមាន ID = {id}")
    return product

# ===========================================================
# 4. UPDATE: កែប្រែទិន្នន័យ និងដូររូបភាពទំនិញ (PUT)
# ===========================================================
@router.put("/{id}", response_model=ProductResponse)
def update_product(
    id: int,
    name: str = Form(None),         # ដាក់ None ដើម្បីឱ្យវាទៅជា Optional (មិនបង្ខំឱ្យដូរ)
    description: str = Form(None),
    price: int = Form(None),
    quantity: int = Form(None),
    file: UploadFile = File(None),   # អាចដូររូបភាព ឬមិនដូរក៏បាន
    db: Session = Depends(get_db)
):
    # ស្វែងរកទំនិញចាស់
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"មិនអាចកែប្រែបានទេ ព្រោះរកមិនឃើញ ID = {id}")

    # បើមានការបញ្ជូនអក្សរថ្មីមក ឱ្យដូរទិន្នន័យចាស់ចោល
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if quantity is not None:
        product.quantity = quantity

    # បើភ្ញៀវមានបោះ File រូបភាពថ្មីមកកែប្រែ
    if file is not None:
        # ១. លុបរូបភាពចាស់ចេញពី Folder static/products/ (ដើម្បីកុំឱ្យធ្ងន់ម៉ាស៊ីន)
        # កូដលុបសញ្ញា "/" ចេញពីមុខផ្លូវកាត់ (ឧទាហរណ៍: /static/... ទៅជា static/...)
        old_image_path = product.image.lstrip("/") 
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

        # ២. បង្កើត និងរក្សាទុករូបភាពថ្មីចូលជំនួស
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        new_file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # ៣. កែប្រែផ្លូវ Link រូបភាពនៅក្នុង Database
        product.image = f"/{new_file_path}"

    db.commit()
    db.refresh(product)
    return product

# ===========================================================
# 5. DELETE: លុបទំនិញ និងលុបរូបភាពចេញពីម៉ាស៊ីន (DELETE)
# ===========================================================
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(get_db)):
    # ស្វែងរកទំនិញចាស់
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"មិនអាចលុបបានទេ ព្រោះរកមិនឃើញ ID = {id}")

    # ១. ទៅលុបឯកសាររូបភាពពិតប្រាកដនៅក្នុង Folder static/products ចោលសិន
    image_path = product.image.lstrip("/")
    if os.path.exists(image_path):
        os.remove(image_path)

    # ២. លុបទិន្នន័យចេញពី Database ដាច់ជាផ្លូវការ
    db.delete(product)
    db.commit()
    return None
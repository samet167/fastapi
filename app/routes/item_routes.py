


import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from database import get_db
from app.models.item import Item
from app.models.category import Category
from app.schemas.item_schema import ItemResponse

# 🔒 ហៅជំនួយការឆែក Authorization មកប្រើ
from app.core.dependencies import RoleChecker

router = APIRouter(prefix="/items", tags=["Items"])

UPLOAD_DIR = "static/items"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🛡️ បង្កើតច្បាប់ការពារ៖ ទាល់តែមាន Role ជា "admin" ទើបអនុញ្ញាតឱ្យឆ្លងកាត់
admin_only = RoleChecker(["admin"])


# 1. CREATE ITEM (🔒 ត្រូវការសិទ្ធិជា ADMIN)
@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    name: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    category_id: int = Form(...),  
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin = Depends(admin_only) # 🔒 ដាក់សោរ Authorization (Admin Only)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="មិនអាចបង្កើតបានទេ ព្រោះរកមិនឃើញ Category ID នេះឡើយ")

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_item = Item(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        category_id=category_id,
        image=f"/{file_path}"
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


# 2. READ ALL ITEMS (🔓 ភ្ញៀវទូទៅមើលបានសេរី - Public)
@router.get("/", response_model=list[ItemResponse])
def get_all_items(db: Session = Depends(get_db)):
    return db.query(Item).all()


# 3. READ ONE ITEM (🔓 ភ្ញៀវទូទៅមើលបានសេរី - Public)
@router.get("/{id}", response_model=ItemResponse)
def get_item_by_id(id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="រកមិនឃើញទំនិញនេះទេ")
    return item


# 4. UPDATE ITEM (🔒 ត្រូវការសិទ្ធិជា ADMIN)
@router.put("/{id}", response_model=ItemResponse)
def update_item(
    id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: int = Form(None),
    quantity: int = Form(None),
    category_id: int = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_admin = Depends(admin_only) # 🔒 ដាក់សោរ Authorization (Admin Only)
):
    item = db.query(Item).filter(Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="រកមិនឃើញទំនិញនេះទេ")

    if category_id is not None:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category ID ថ្មីនេះមិនត្រឹមត្រូវទេ")
        item.category_id = category_id

    if name is not None: item.name = name
    if description is not None: item.description = description
    if price is not None: item.price = price
    if quantity is not None: item.quantity = quantity

    if file is not None:
        old_image_path = item.image.lstrip("/") 
        if os.path.exists(old_image_path):
            os.remove(old_image_path)

        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        new_file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        item.image = f"/{new_file_path}"

    db.commit()
    db.refresh(item)
    return item


# 5. DELETE ITEM (🔒 ត្រូវការសិទ្ធិជា ADMIN)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(admin_only) # 🔒 ដាក់សោរ Authorization (Admin Only)
):
    item = db.query(Item).filter(Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="រកមិនឃើញទំនិញនេះទេ")

    image_path = item.image.lstrip("/")
    if os.path.exists(image_path):
        os.remove(image_path)

    db.delete(item)
    db.commit()
    return None
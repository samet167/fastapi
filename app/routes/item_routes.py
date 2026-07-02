import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status, Request
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
    request: Request, # ◄ ✅ ហៅ Request មកដើម្បីចាប់យក Domain URL (http://127.0.0.1:8000) ដោយស្វ័យប្រវត្តិ
    name: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    quantity: int = Form(...),
    category_id: int = Form(...),  
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # current_admin = Depends(admin_only) # 🔒 បើកសោរការពារឡើងវិញនៅពេលលែងតេស្ត
):
    # កាពារទី១៖ ឆែកមើលក្រែងលោមានឈ្មោះទំនិញនេះរួចហើយ
    existing_item = db.query(Item).filter(Item.name == name).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="ឈ្មោះទំនិញនេះមានរួចហើយ មិនអាចបង្កើតស្ទួនបានទេ")

    # កាពារទី២៖ ឆែកមើលថាតើមាន Category ID ហ្នឹងពិតមែនអត់
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="មិនអាចបង្កើតបានទេ ព្រោះរកមិនឃើញ Category ID នេះឡើយ")

    # ចាប់យក extension និងបង្កើតឈ្មោះឯកសារថ្មីជា UUID
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".png"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # រក្សាទុករូបភាពទៅក្នុង Folder static/items
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"មិនអាចរក្សាទុករូបភាពបានទេ: {str(e)}")

    # បង្កើត URL ពេញលេញសម្រាប់មើលលើ Chrome (ឧទាហរណ៍៖ http://127.0.0.1:8000/static/items/abc.png)
    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/{file_path.replace(os.sep, '/')}"

    # បញ្ចូលទិន្នន័យទៅក្នុង Database ដោយសុវត្ថិភាព
    try:
        new_item = Item(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            category_id=category_id,
            image=image_url # ✅ រក្សាទុកជា Link ពេញលេញ ងាយស្រួលបើកមើលលើ Chrome
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except Exception as db_err:
        db.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"កំហុសប្រព័ន្ធទិន្នន័យ (អាចមកពីជល់ ID ក្នុង DB): {str(db_err)}")


# 2. READ ALL ITEMS (🔓 Public)
@router.get("/", response_model=list[ItemResponse])
def get_all_items(db: Session = Depends(get_db)):
    return db.query(Item).all()


# 3. READ ONE ITEM (🔓 Public)
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
    request: Request, # ◄ ✅ ហៅមកប្រើសម្រាប់ករណីប្តូររូបភាពថ្មី
    name: str = Form(None),
    description: str = Form(None),
    price: int = Form(None),
    quantity: int = Form(None),
    category_id: int = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    # current_admin = Depends(admin_only) # 🔒 ដាក់សោរ Authorization
):
    item = db.query(Item).filter(Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="រកមិនឃើញទំនិញនេះទេ")

    if category_id is not None:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category ID ថ្មីនេះមិនត្រឹមត្រូវទេ")
        item.category_id = category_id

    if name is not None:
        existing_name = db.query(Item).filter(Item.name == name, Item.id != id).first()
        if existing_name:
            raise HTTPException(status_code=400, detail="ឈ្មោះទំនិញថ្មីនេះមានរួចហើយ")
        item.name = name

    if description is not None: item.description = description
    if price is not None: item.price = price
    if quantity is not None: item.quantity = quantity

    # ប្រសិនបើអ្នកប្រើប្រាស់មានបោះរូបភាពថ្មីមកដូរ
    if file is not None:
        # ទាញយកឈ្មោះឯកសារចាស់ចេញពី URL ដើម្បីយកទៅលុបក្នុងម៉ាស៊ីន
        if item.image:
            old_filename = item.image.split("/static/items/")[-1]
            old_image_path = os.path.join(UPLOAD_DIR, old_filename)
            if os.path.exists(old_image_path):
                try:
                    os.remove(old_image_path)
                except Exception:
                    pass

        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".png"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        new_file_path = os.path.join(UPLOAD_DIR, unique_filename)

        try:
            with open(new_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"មិនអាចរក្សាទុករូបភាពថ្មីបានទេ: {str(e)}")
        
        base_url = str(request.base_url).rstrip("/")
        item.image = f"{base_url}/{new_file_path.replace(os.sep, '/')}"

    try:
        db.commit()
        db.refresh(item)
        return item
    except Exception as db_err:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"មិនអាចកែប្រែទិន្នន័យបានទេ: {str(db_err)}")


# 5. DELETE ITEM (🔒 ត្រូវការសិទ្ធិជា ADMIN)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(admin_only) # 🔒 ដាក់សោរ Authorization
):
    item = db.query(Item).filter(Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="រកមិនឃើញទំនិញនេះទេ")

    # ទាញយកឈ្មោះឯកសារចាស់យកទៅលុបក្នុងម៉ាស៊ីនមុននឹងលុបក្នុង DB
    if item.image:
        filename = item.image.split("/static/items/")[-1]
        image_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass

    try:
        db.delete(item)
        db.commit()
        return None  
    except Exception as db_err:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"មិនអាចលុបទិន្នន័យបានទេ: {str(db_err)}")
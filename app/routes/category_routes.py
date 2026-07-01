# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from database import get_db
# from app.models.category import Category
# from app.schemas.category_schema import CategoryCreate, CategoryResponse

# router = APIRouter(prefix="/categories", tags=["Categories"])

# @router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
# def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
#     db_category = db.query(Category).filter(Category.name == category_data.name).first()
#     if db_category:
#         raise HTTPException(status_code=400, detail="ឈ្មោះប្រភេទទំនិញនេះមានរួចហើយ")
    
#     new_category = Category(name=category_data.name)
#     db.add(new_category)
#     db.commit()
#     db.refresh(new_category)
#     return new_category

# @router.get("/", response_model=list[CategoryResponse])
# def get_all_categories(db: Session = Depends(get_db)):
#     return db.query(Category).all()

# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_category(id: int, db: Session = Depends(get_db)):
#     category = db.query(Category).filter(Category.id == id).first()
#     if not category:
#         raise HTTPException(status_code=404, detail="រកមិនឃើញ ID នេះឡើយ")
#     db.delete(category)
#     db.commit()
#     return None




from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category_schema import CategoryCreate, CategoryResponse
# នាំចូល Dependencies សម្រាប់ពិនិត្យសិទ្ធិ
from app.core.dependencies import get_current_user, RoleChecker

router = APIRouter(prefix="/categories", tags=["Categories"])

# កំណត់សិទ្ធិទុកជាមុន (Admin ប៉ុណ្ណោះសម្រាប់សកម្មភាពកែប្រែទិន្នន័យ)
admin_only = RoleChecker(["admin"])
admin_or_user = RoleChecker(["admin", "user"])


# ១. បង្កើត Category (Admin ប៉ុណ្ណោះ)
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate, 
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_only) # 🔒 ការពារដោយ Admin Role
):
    db_category = db.query(Category).filter(Category.name == category_data.name).first()
    if db_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ឈ្មោះប្រភេទទំនិញនេះមានរួចហើយ")
    
    new_category = Category(name=category_data.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


# ២. ទាញយក Category ទាំងអស់ (បានទាំង User និង Admin)
@router.get("/", response_model=list[CategoryResponse])
def get_all_categories(
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_or_user) # 🔒 ត្រូវតែ Login ទើបមើលបាន
):
    return db.query(Category).all()


# ៣. ទាញយក Category មួយតាម ID (បានទាំង User និង Admin)
@router.get("/{id}", response_model=CategoryResponse)
def get_category_by_id(
    id: int, 
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_or_user) # 🔒 ត្រូវតែ Login ទើបមើលបាន
):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="រកមិនឃើញ ID នេះឡើយ")
    return category


# ៤. កែប្រែ Category (Admin ប៉ុណ្ណោះ)
@router.put("/{id}", response_model=CategoryResponse)
def update_category(
    id: int, 
    category_data: CategoryCreate, 
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_only) # 🔒 ការពារដោយ Admin Role
):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="រកមិនឃើញ ID នេះឡើយ")
    
    # ឆែកមើលក្រែងលោប្តូរឈ្មោះទៅជាន់ជាមួយ category ផ្សេងដែលមានស្រាប់
    existing_name = db.query(Category).filter(Category.name == category_data.name, Category.id != id).first()
    if existing_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ឈ្មោះប្រភេទទំនិញនេះមានរួចហើយ")

    category.name = category_data.name
    db.commit()
    db.refresh(category)
    return category


# ៥. លុប Category (Admin ប៉ុណ្ណោះ)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    id: int, 
    db: Session = Depends(get_db),
    _current_user: User = Depends(admin_only) # 🔒 ការពារដោយ Admin Role
):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="រកមិនឃើញ ID នេះឡើយ")
    db.delete(category)
    db.commit()
    return None
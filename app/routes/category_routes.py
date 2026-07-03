from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from database import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category_schema import CategoryCreate, CategoryResponse
# នាំចូល Dependencies សម្រាប់ពិនិត្យសិទ្ធិ
from app.core.dependencies import get_current_user, RoleChecker
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

router = APIRouter(prefix="/categories", tags=["Categories"])

# កំណត់សិទ្ធិទុកជាមុន (Admin ប៉ុណ្ណោះសម្រាប់សកម្មភាពកែប្រែទិន្នន័យ)
admin_only = RoleChecker(["admin"])
admin_or_user = RoleChecker(["admin", "user"])


## កែប្រែត្រង់វគ្គ @router.post ក្នុង app/routes/category_routes.py របស់អ្នក

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    name: str = Form(...), 
    db: Session = Depends(get_db),
    # current_admin = Depends(admin_only) # 🔒 បើចង់តេស្តឱ្យដឹងថាគាំងកូដ ឬគាំងសិទ្ធិ អាចបិទខមិននេះសិន
):
    try:
        # ពិនិត្យឈ្មោះស្ទួន
        db_category = db.query(Category).filter(Category.name == name).first()
        if db_category:
            raise HTTPException(status_code=400, detail="ឈ្មោះប្រភេទទំនិញនេះមានរួចហើយ")
        
        # បញ្ចូលទៅ Database
        new_category = Category(name=name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category

    except HTTPException as http_err:
        raise http_err # បើជាកំហុសឈ្មោះស្ទួន ឱ្យបោះទៅធម្មតា
    except Exception as e:
        db.rollback() # ការពារ database session គាំង
        raise HTTPException(status_code=500, detail=f"កំហុសប្រព័ន្ធខាងក្នុង: {str(e)}")



@router.get("/", response_model=list[CategoryResponse])
def get_all_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="ចំនួនទិន្នន័យដែលរំលង"),
    limit: int = Query(10, ge=1, le=100, description="ចំនួនទិន្នន័យក្នុងមួយទំព័រ"),
):
    categories = (
        db.query(Category)
        .order_by(desc(Category.id))  # ID ពីធំទៅតូច
        .offset(skip)                 # Pagination
        .limit(limit)
        .all()
    )

    return categories


# ៣. ទាញយក Category មួយតាម ID (🔒 ត្រូវតែ Login ទើបមើលបាន)
@router.get("/{id}", response_model=CategoryResponse)
def get_category_by_id(
    id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(admin_or_user) # 🔒 ត្រូវតែ Login (ជា User ឬ Admin ក៏បាន)
):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="រកមិនឃើញ ID នេះឡើយ")
    return category


# ៤. កែប្រែ Category (🔒 ត្រូវការសិទ្ធិជា ADMIN និងប្រើ form-data)
@router.put("/{id}", response_model=CategoryResponse)
def update_category(
    id: int, 
    name: str = Form(...), # ✅ ទទួលទិន្នន័យជា Form ដូចការបង្កើតដែរ
    db: Session = Depends(get_db),
    current_admin = Depends(admin_only) # 🔒 ការពារដោយ Admin Role
):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="រកមិនឃើញ ID នេះឡើយ")
    
    # ឆែកមើលក្រែងលោប្តូរឈ្មោះទៅជាន់ជាមួយ category ផ្សេងដែលមានស្រាប់ (តែមិនមែនខ្លួនឯង)
    existing_name = db.query(Category).filter(Category.name == name, Category.id != id).first()
    if existing_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ឈ្មោះប្រភេទទំនិញនេះមានរួចហើយ")

    category.name = name # ✅ កែពី category_data.name មកប្រើ name ផ្ទាល់
    db.commit()
    db.refresh(category)
    return category


# ៥. លុប Category (🔒 ត្រូវការសិទ្ធិជា ADMIN)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(admin_only) # 🔒 ការពារដោយ Admin Role
):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="រកមិនឃើញ ID នេះឡើយ")
        
    db.delete(category)
    db.commit()
    return None
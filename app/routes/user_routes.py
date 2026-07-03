


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db 
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.core.security import hash_password  # 🔒 សម្រាប់កិនកូដ Password
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db 
from app.models.user import User
from app.schemas.user_schema import UserResponse
from sqlalchemy import desc


router = APIRouter(prefix="/users", tags=["Users"])

# ==========================================
# 1. CREATE: បង្កើត User ថ្មី
# ==========================================
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # ឆែកមើលអ៊ីមែលជាន់គ្នា
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email នេះមានគេប្រើរួចហើយ!")

    # បង្កើត User ដោយកិន Password ឱ្យទៅជាកូដសម្ងាត់
    new_user = User(
        username=user_in.username, 
        email=user_in.email,
        password=hash_password(user_in.password),
        role=user_in.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user  # 💡 បោះទៅវិញដោយលាក់ Password អូតូ ព្រោះប្រើ UserResponse


# # ==========================================
# # 2. READ ALL: មើល User ទាំងអស់
# # ==========================================
# @router.get("/", response_model=list[UserResponse])
# def get_all_users(db: Session = Depends(get_db)):
#     return db.query(User).all()  # 💡 លាក់ Password ទាំងអស់អូតូ




@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    users = (
        db.query(User)
        .order_by(desc(User.id))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return users


# ==========================================
# 3. READ ONE: មើល User ម្នាក់តាម ID
# ==========================================
@router.get("/{id}", response_model=UserResponse)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="រកមិនឃើញអ្នកប្រើប្រាស់នេះទេ")
    return user  # 💡 លាក់ Password អូតូ


# ==========================================
# 4. UPDATE: កែប្រែទិន្នន័យ User
# ==========================================
@router.put("/{id}", response_model=UserResponse)
def update_user(id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="រកមិនឃើញអ្នកប្រើប្រាស់នេះទេ")
    
    # បើមានការបោះទិន្នន័យថ្មីមក ឱ្យដូរចូលភ្លាម
    if user_in.username: user.username = user_in.username
    if user_in.email: user.email = user_in.email
    if user_in.role: user.role = user_in.role
    if user_in.password: user.password = hash_password(user_in.password) # បើដូរសោរ ត្រូវកិនសិន

    db.commit()      
    db.refresh(user) 
    return user  # 💡 លាក់ Password អូតូ


# ==========================================
# 5. DELETE: លុប User ចោល
# ==========================================
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="រកមិនឃើញអ្នកប្រើប្រាស់នេះទេ")
    
    db.delete(user) 
    db.commit()     
    return None
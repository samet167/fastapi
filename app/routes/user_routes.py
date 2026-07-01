# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from database import get_db 
# from app.models.user import User
# from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse

# router = APIRouter(prefix="/users", tags=["Users"])

# # ==========================================
# # 1. CREATE: បង្កើតអ្នកប្រើប្រាស់ថ្មី (POST)
# # ==========================================
# @router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
#     try:
#         new_user = User(username=user_in.username, email=user_in.email)
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#         return new_user
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, 
#             detail=f"Username ឬ Email ជាន់គ្នា: {str(e)}"
#         )

# # ==========================================
# # 2. READ ALL: ទាញយកអ្នកប្រើប្រាស់ទាំងអស់ (GET)
# # ==========================================
# @router.get("/", response_model=list[UserResponse])
# def get_all_users(db: Session = Depends(get_db)):
#     try:
#         users = db.query(User).all()
#         return users
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
#             detail=str(e)
#         )

# # ==========================================
# # 3. READ ONE: ទាញយកអ្នកប្រើប្រាស់ម្នាក់តាម ID (GET)
# # ==========================================
# @router.get("/{id}", response_model=UserResponse)
# def get_user_by_id(id: int, db: Session = Depends(get_db)):
#     # ស្វែងរក user ក្នុង Database តាម ID
#     user = db.query(User).filter(User.id == id).first()
    
#     # បើរកមិនឃើញ បោះ Error 404 Not Found ភ្លាម
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             detail=f"រកមិនឃើញអ្នកប្រើប្រាស់ដែលមាន ID = {id} ឡើយ"
#         )
#     return user

# # ==========================================
# # 4. UPDATE: កែប្រែទិន្នន័យអ្នកប្រើប្រាស់តាម ID (PUT)
# # ==========================================
# @router.put("/{id}", response_model=UserResponse)
# def update_user(id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
#     # ស្វែងរក user ចាស់សិន
#     user = db.query(User).filter(User.id == id).first()
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             detail=f"មិនអាចកែប្រែបានទេ ព្រោះរកមិនឃើញ ID = {id}"
#         )
    
#     try:
#         # បើភ្ញៀវបោះ username ថ្មីមក ឱ្យដូរ username ចាស់ចោល
#         if user_in.username is not None:
#             user.username = user_in.username
            
#         # បើភ្ញៀវបោះ email ថ្មីមក ឱ្យដូរ email ចាស់ចោល
#         if user_in.email is not None:
#             user.email = user_in.email

#         db.commit()      # រក្សាទុកការកែប្រែចូល Database
#         db.refresh(user) # ទាញយក Data ដែលទើបកែរួចមកបង្ហាញ
#         return user
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, 
#             detail=f"មិនអាចកែប្រែបានទេ ទិន្នន័យថ្មីអាចនឹងជាន់គេ: {str(e)}"
#         )

# # ==========================================
# # 5. DELETE: លុបអ្នកប្រើប្រាស់ចោលតាម ID (DELETE)
# # ==========================================
# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_user(id: int, db: Session = Depends(get_db)):
#     # ស្វែងរក user ចាស់សិន
#     user = db.query(User).filter(User.id == id).first()
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, 
#             detail=f"មិនអាចលុបបានទេ ព្រោះរកមិនឃើញ ID = {id}"
#         )
    
#     try:
#         db.delete(user) # បញ្ជាឱ្យលុបចេញពីតុរង់ចាំ
#         db.commit()     # បញ្ជាឱ្យលុបដាច់ចេញពី PostgreSQL តែម្ដង
#         return None     # ធម្មតាការលុបជោគជ័យ (204) គឺមិនបាច់បោះទិន្នន័យអ្វីទៅវិញទេ
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
#             detail=str(e)
#         )



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db 
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.core.security import hash_password  # 🔒 សម្រាប់កិនកូដ Password

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


# ==========================================
# 2. READ ALL: មើល User ទាំងអស់
# ==========================================
@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()  # 💡 លាក់ Password ទាំងអស់អូតូ


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
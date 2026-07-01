from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str 

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ១. API REGISTER
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    # ឆែកមើលអ៊ីមែលជាន់គ្នា
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email នេះត្រូវបានប្រើប្រាស់រួចហើយ!")

    secure_hashed_password = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=secure_hashed_password,
        role="user"  # លំនាំដើមពេលចុះឈ្មោះគឺ "user" ធម្មតា
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ២. API LOGIN (បោះ JWT Token ត្រឡប់ទៅវិញ)
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # ស្វែងរកតាមរយៈ Email (Form របស់ FastAPI បង្ខំឱ្យដាក់ឈ្មោះប្រអប់ថា username)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ឬ Password មិនត្រឹមត្រូវឡើយ!")
        
    # បង្កើតកាតសម្គាល់ខ្លួនដោយផ្ដោតលើ User ID
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


# ៣. API LOGOUT
@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    return {"detail": "បានចាកចេញពីគណនីដោយជោគជ័យ! សូមលុប Token ចេញពី Client (Frontend)។"}
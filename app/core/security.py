from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status
# 🔄 ដូរពី passlib មកប្រើ pwdlib ដែលដើរលើគ្រប់ទម្រង់ Python ទាំង Windows 
from pwdlib import PasswordHash

SECRET_KEY = "MY_SUPER_SECRET_KEY_FOR_JWT_SECURITY_123" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# បង្កើតម៉ាស៊ីន Hash សុវត្ថិភាពជំនាន់ថ្មី
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token មិនត្រឹមត្រូវទេ")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token នេះហួសកំណត់ថ្ងៃប្រើហើយ")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token មិនត្រឹមត្រូវ ឬខូចហើយ")
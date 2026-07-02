
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_access_token
from sqlalchemy.orm import Session
from database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = verify_access_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="រកមិនឃើញគណនីនេះទេ")
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        # 🚨 ចំណុចសំខាន់៖ ត្រូវប្រាកដថាបានដាក់លក្ខខណ្ឌ "not in" បែបនេះ
        if current_user.role not in self.allowed_roles:
            raise HTTPException(                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"អ្នកជា '{current_user.role}' មិនមានសិទ្ធិឡើយ! ទាល់តែជា {self.allowed_roles} ទើបអាចធ្វើបាន។"
            )
        return current_user
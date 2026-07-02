from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from app.models.cart import CartItem
from app.models.item import Item
from app.schemas.cart_schema import CartItemCreate, CartItemUpdate, CartItemResponse

# 🔒 ហៅជំនួយការឆែក Token ដើម្បីស្គាល់ថាជា User មួយណា (ដូរផ្លូវឱ្យត្រូវតាមគម្រោងរបស់អ្នក)
from app.core.dependencies import get_current_user 

router = APIRouter(prefix="/cart", tags=["Cart"])


# 1. ADD TO CART (🔒 ថែមទំនិញចូលកន្ត្រក)
@router.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart_data: CartItemCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user) # ◀ ចាប់យក User ពី Token
):
    # ឆែកមើលថាតើមានទំនិញហ្នឹងពិតមែនអត់
    item = db.query(Item).filter(Item.id == cart_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="រកមិនឃើញទំនិញនេះទេ")

    if item.quantity < cart_data.quantity:
        raise HTTPException(status_code=400, detail="ចំនួនទំនិញក្នុងស្តុកមិនគ្រាន់គ្រាន់ឡើយ")

    # ឆែកមើលក្រែងលោ User ធ្លាប់បានថែមទំនិញហ្នឹងចូលកន្ត្រកម្តងរួចហើយ
    existing_cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id, 
        CartItem.item_id == cart_data.item_id
    ).first()

    if existing_cart_item:
        # បើមានហើយ គឺគ្រាន់តែបូកចំនួនថែម
        existing_cart_item.quantity += cart_data.quantity
        db.commit()
        db.refresh(existing_cart_item)
        return existing_cart_item
    
    # បើមិនទាន់មានទេ គឺបង្កើតជួរថ្មីក្នុងកន្ត្រក
    new_cart_item = CartItem(
        user_id=current_user.id,
        item_id=cart_data.item_id,
        quantity=cart_data.quantity
    )
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    return new_cart_item


# 2. GET MY CART (🔒 មើលរបស់របរក្នុងកន្ត្រកខ្លួនឯង)
@router.get("/", response_model=list[CartItemResponse])
def get_user_cart(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(CartItem).filter(CartItem.user_id == current_user.id).all()


# 3. UPDATE QUANTITY (🔒 កែប្រែចំនួនលេខទំនិញ ថែម/ថយ ក្នុងកន្ត្រក)
@router.put("/{cart_item_id}", response_model=CartItemResponse)
def update_cart_quantity(
    cart_item_id: int, 
    cart_data: CartItemUpdate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="មិនមានទំនិញនេះក្នុងកន្ត្រកឡើយ")

    if cart_data.quantity <= 0:
        db.delete(cart_item)
        db.commit()
        return None

    cart_item.quantity = cart_data.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


# 4. DELETE FROM CART (🔒 លុបទំនិញមួយចេញពីកន្ត្រក)
@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(cart_item_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id, CartItem.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="មិនមានទំនិញនេះក្នុងកន្ត្រកឡើយ")

    db.delete(cart_item)
    db.commit()
    return None
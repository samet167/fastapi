from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

# 1. PLACE ORDER / CHECKOUT (🔒 ដំណើរការទូទាត់ប្រាក់ និងបង្កើតវិក្កយបត្រ)
@router.post("/", status_code=status.HTTP_201_CREATED)
def checkout(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # ទាញយកទំនិញទាំងអស់ក្នុងកន្ត្រករបស់ User ម្នាក់នេះ
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="កន្ត្រកទំនិញរបស់អ្នកទទេស្អាត មិនអាច Checkout បានទេ")

    # គណនាតម្លៃសរុប
    total_price = sum(item.item.price * item.quantity for item in cart_items)

    try:
        # បង្កើតជួរវិក្កយបត្រថ្មី (Order)
        new_order = Order(user_id=current_user.id, total_price=total_price, status="paid") # ឧបមាថា paid ភ្លាមៗ
        db.add(new_order)
        db.flush() # ទាញយក Order ID មកប្រើជាមុនសិន ដោយមិនទាន់ Commit ផ្តាច់

        # បំលែងពី CartItem ទៅជា OrderItem
        for cart_item in cart_items:
            # ឆែកស្តុក និងកាត់ស្តុកទំនិញចេញ
            if cart_item.item.quantity < cart_item.quantity:
                raise HTTPException(status_code=400, detail=f"ទំនិញ {cart_item.item.name} មិនគ្រាន់គ្រាន់ក្នុងស្តុកទេ")
            
            cart_item.item.quantity -= cart_item.quantity # កាត់ស្តុក

            order_item = OrderItem(
                order_id=new_order.id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                price=cart_item.item.price
            )
            db.add(order_item)

        # សម្អាតកន្ត្រកទំនិញរបស់ User នេះចោល
        db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()

        db.commit()
        return {"message": "ការទូទាត់ប្រាក់បានជោគជ័យ! 🎉", "order_id": new_order.id, "total": total_price}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"មានបញ្ហាក្នុងការ Checkout: {str(e)}")
    
    # បន្ថែមចូលក្នុង app/routes/order_routes.py

@router.get("/{order_id}")
def get_order_invoice(order_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # ទាញរក Order តាម ID និងត្រូវជារបស់ User ដែលកំពុង Login នោះ
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="រកមិនឃើញវិក្កយបត្រនេះឡើយ")
    
    # រៀបចំទិន្នន័យបោះទៅឱ្យ Frontend
    invoice_items = []
    for oi in order.items:
        invoice_items.append({
            "item_name": oi.item.name,
            "price": oi.price,
            "quantity": oi.quantity,
            "subtotal": oi.price * oi.quantity
        })
        
    return {
        "order_id": order.id,
        "status": order.status,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
        "total_price": order.total_price,
        "customer": current_user.username,
        "items": invoice_items
    }
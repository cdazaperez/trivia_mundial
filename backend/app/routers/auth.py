from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user, get_admin_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, LoginRequest, PasswordChange, AdminPasswordReset, AdminUserUpdate

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check existing username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    # Check existing email
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario desactivado")

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/change-password")
def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 6 caracteres")

    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"detail": "Contraseña actualizada correctamente"}


@router.put("/admin/reset-password")
def admin_reset_password(
    data: AdminPasswordReset,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.is_admin:
        raise HTTPException(status_code=400, detail="No se puede resetear la contraseña de otro administrador")

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 6 caracteres")

    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"detail": f"Contraseña de {data.username} reseteada correctamente"}


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """List all non-admin users (for admin management)."""
    return db.query(User).filter(User.is_admin == False).order_by(User.username).all()


@router.put("/admin/toggle-user/{user_id}")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Block or unblock a user. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="No se puede bloquear a un administrador")

    user.is_active = not user.is_active
    db.commit()
    action = "activado" if user.is_active else "bloqueado"
    return {"detail": f"Usuario {user.username} {action}", "is_active": user.is_active}


@router.put("/admin/toggle-payment/{user_id}")
def toggle_user_payment(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Mark or unmark a user's payment. Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="No aplica para administradores")

    user.has_paid = not user.has_paid
    db.commit()
    status = "pagado" if user.has_paid else "pendiente"
    return {"detail": f"Pago de {user.username}: {status}", "has_paid": user.has_paid}


@router.put("/admin/update-user/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: int,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_admin_user),
):
    """Update a user's profile data (username, email, full_name). Admin only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.is_admin:
        raise HTTPException(status_code=400, detail="No se puede editar a un administrador desde aquí")

    if data.username is not None and data.username != user.username:
        if len(data.username.strip()) < 3:
            raise HTTPException(status_code=400, detail="El usuario debe tener al menos 3 caracteres")
        existing = db.query(User).filter(User.username == data.username, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"El usuario '{data.username}' ya existe")
        user.username = data.username.strip()

    if data.email is not None and data.email != user.email:
        existing = db.query(User).filter(User.email == data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"El email '{data.email}' ya está registrado")
        user.email = data.email.strip()

    if data.full_name is not None and data.full_name != user.full_name:
        if len(data.full_name.strip()) < 2:
            raise HTTPException(status_code=400, detail="El nombre debe tener al menos 2 caracteres")
        user.full_name = data.full_name.strip()

    db.commit()
    db.refresh(user)
    return user

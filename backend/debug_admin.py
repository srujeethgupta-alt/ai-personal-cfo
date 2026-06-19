from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from auth import verify_password
from database import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
with SessionLocal() as db:
    users = db.query(User).all()
    print('USER COUNT:', len(users))
    for u in users:
        print('id:', u.id, 'email:', u.email, 'is_active:', u.is_active, 'is_admin:', u.is_admin)
    admin = db.query(User).filter(User.email == 'admin@example.com').first()
    print('ADMIN FOUND:', bool(admin))
    if admin:
        print('Verify default password Admin@123:', verify_password('Admin@123', admin.password_hash))
        print('Verify known wrong password test123:', verify_password('test123', admin.password_hash))

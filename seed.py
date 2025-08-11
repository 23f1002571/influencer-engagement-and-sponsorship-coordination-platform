from app import app, db
from models import User

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            username='admin',
            password='admin',
            name='admin',
            is_admin=True,
            email='admin@admin.com',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

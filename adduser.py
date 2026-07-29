from app import create_app
from app.extensions import db
from app.models.admin import Admin

app = create_app()

with app.app_context():
    db.create_all()

    admin = Admin(username="colin")
    admin.set_password("colin")
    db.session.add(admin)
    db.session.commit()

    print("Admin user created.")
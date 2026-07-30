from app import create_app
from app.extensions import db
from app.models.admin import Admin

app = create_app()

with app.app_context():
    # Prevent accidental table creation on PostgreSQL
    engine = db.engine
    if not engine.url.drivername.startswith("sqlite"):
        print("✔ PostgreSQL detected — safe mode enabled (no db.create_all).")
    else:
        print("✔ SQLite detected — running db.create_all() for local dev.")
        db.create_all()

    # Check if admin already exists
    if Admin.query.filter_by(username="colin").first():
        print("✔ Admin user already exists.")
    else:
        admin = Admin(username="colin")
        admin.set_password("colin")
        db.session.add(admin)
        db.session.commit()
        print("✔ Admin user created successfully.")

from flask import Flask, render_template
from app.extensions import db
from app.routes.public import public_bp
from app.routes.admin import admin_bp
from app.models.category import Category
from config import get_config


# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(get_config())

#     # Init DB
#     db.init_app(app)

#     # Register blueprints
#     app.register_blueprint(public_bp)
#     app.register_blueprint(admin_bp, url_prefix="/admin")

#     # ---------------------------------------------------------
#     # DATABASE INITIALISATION + SAFE AUTO-SEEDING
#     # ---------------------------------------------------------
#     with app.app_context():
#         db.create_all()

#         # Only seed categories if none exist
#         if Category.query.count() == 0:
#             categories = [
#                 # MAIN TOOL CATEGORIES
#                 Category(
#                     name="Power Tools",
#                     slug="power-tools",
#                     icon="⚡",
#                     description="Cordless tools, drills, saws, sanders and professional-grade power equipment.",
#                     is_main=True
#                 ),
#                 Category(
#                     name="Hand Tools",
#                     slug="hand-tools",
#                     icon="🔧",
#                     description="Essential hand tools for woodworking, construction and home improvement.",
#                     is_main=True
#                 ),
#                 Category(
#                     name="Garden Tools",
#                     slug="garden-tools",
#                     icon="🌿",
#                     description="Lawn care tools, trimmers, hedge cutters and outdoor maintenance equipment.",
#                     is_main=True
#                 ),
#                 Category(
#                     name="Hardware Supplies",
#                     slug="hardware-supplies",
#                     icon="📦",
#                     description="Fixings, fasteners, brackets, adhesives and general hardware essentials.",
#                     is_main=True
#                 ),

#                 # CONTENT CATEGORIES
#                 Category(
#                     name="Reviews",
#                     slug="reviews",
#                     icon="⭐",
#                     description="In-depth tool reviews with images, pros/cons and buying advice.",
#                     is_main=False
#                 ),
#                 Category(
#                     name="Comparisons",
#                     slug="comparisons",
#                     icon="⚖️",
#                     description="Tool vs tool comparisons and best-of lists.",
#                     is_main=False
#                 ),
#                 Category(
#                     name="DIY Projects",
#                     slug="diy-projects",
#                     icon="🛠️",
#                     description="Step-by-step woodworking, kitchen fitting and home improvement guides.",
#                     is_main=False
#                 )
#             ]

#             db.session.add_all(categories)
#             db.session.commit()
#             print("✔ Categories created automatically (first run).")
#         else:
#             print("✔ Categories already exist — skipping auto-seed.")

#     from sqlalchemy import inspect

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    db.init_app(app)

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # ---------------------------------------------------------
    # SAFE: Only auto-create tables when using SQLite
    # ---------------------------------------------------------
    with app.app_context():
        engine = db.engine

        # Detect SQLite
        if engine.url.drivername.startswith("sqlite"):
            inspector = inspect(engine)

            # Create tables only if missing
            if 'category' not in inspector.get_table_names():
                db.create_all()

                # Seed only on fresh SQLite DB
                if Category.query.count() == 0:
                    seed_categories()
        else:
            # PostgreSQL → NEVER auto-create tables
            pass

 


    # ---------------------------------------------------------
    # ERROR HANDLERS
    # ---------------------------------------------------------

    @app.errorhandler(404)
    def not_found(e):
        return render_template(
            "errors/404.html",
            title="404 — Page Not Found",
            seo_title="404 — Page Not Found",
            seo_description="The page you requested could not be found on ToolJudge.",
            seo_keywords="404, page not found, ToolJudge"
        ), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template(
            "errors/500.html",
            title="500 — Server Error",
            seo_title="500 — Server Error",
            seo_description="A server error occurred while loading ToolJudge.",
            seo_keywords="500, server error, ToolJudge"
        ), 500

    return app

def seed_categories():
    categories = [
        Category(name="Power Tools", slug="power-tools", icon="⚡", description="Cordless tools...", is_main=True),
        Category(name="Hand Tools", slug="hand-tools", icon="🔧", description="Essential hand tools...", is_main=True),
        Category(name="Garden Tools", slug="garden-tools", icon="🌿", description="Lawn care tools...", is_main=True),
        Category(name="Hardware Supplies", slug="hardware-supplies", icon="📦", description="Fixings...", is_main=True),
        Category(name="Reviews", slug="reviews", icon="⭐", description="In-depth tool reviews...", is_main=False),
        Category(name="Comparisons", slug="comparisons", icon="⚖️", description="Tool vs tool...", is_main=False),
        Category(name="DIY Projects", slug="diy-projects", icon="🛠️", description="Step-by-step guides...", is_main=False),
    ]

    db.session.add_all(categories)
    db.session.commit()
    print("✔ Categories seeded (SQLite only).")

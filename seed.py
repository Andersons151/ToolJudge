from app import create_app
from app.extensions import db
from app.models.category import Category

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    categories = [
        # MAIN TOOL CATEGORIES
        Category(
            name="Power Tools",
            slug="power-tools",
            icon="⚡",
            description="Cordless tools, drills, saws, sanders and professional-grade power equipment.",
            is_main=True
        ),
        Category(
            name="Hand Tools",
            slug="hand-tools",
            icon="🔧",
            description="Essential hand tools for woodworking, construction and home improvement.",
            is_main=True
        ),
        Category(
            name="Garden Tools",
            slug="garden-tools",
            icon="🌿",
            description="Lawn care tools, trimmers, hedge cutters and outdoor maintenance equipment.",
            is_main=True
        ),
        Category(
            name="Hardware Supplies",
            slug="hardware-supplies",
            icon="📦",
            description="Fixings, fasteners, brackets, adhesives and general hardware essentials.",
            is_main=True
        ),

        # CONTENT CATEGORIES
        Category(
            name="Reviews",
            slug="reviews",
            icon="⭐",
            description="In-depth tool reviews with images, pros/cons and buying advice.",
            is_main=False
        ),
        Category(
            name="Comparisons",
            slug="comparisons",
            icon="⚖️",
            description="Tool vs tool comparisons and best-of lists.",
            is_main=False
        ),
        Category(
            name="DIY Projects",
            slug="diy-projects",
            icon="🛠️",
            description="Step-by-step woodworking, kitchen fitting and home improvement guides.",
            is_main=False
        )
    ]

    db.session.add_all(categories)
    db.session.commit()

    print("Database seeded successfully.")

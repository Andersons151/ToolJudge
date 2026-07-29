from app.extensions import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    slug = db.Column(db.String(255), unique=True)
    icon = db.Column(db.String(10))        # emoji or icon text
    description = db.Column(db.Text)
    image = db.Column(db.String(255))      # optional category image
    is_main = db.Column(db.Boolean, default=False)

    # Backref from Article.categories (many-to-many)
    # This is created automatically by the Article model:
    # categories = db.relationship("Category", secondary=article_categories, backref="articles")
    #
    # You do NOT need to define anything here.
    #
    # Your existing single-category relationship stays untouched:
    # Article.category -> Category.primary_articles

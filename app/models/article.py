from app.extensions import db
from datetime import datetime

# NEW: association table for many-to-many categories
article_categories = db.Table(
    'article_categories',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Core fields
    title = db.Column(db.String(255))
    slug = db.Column(db.String(255), unique=True)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    faq = db.Column(db.Text)          # JSON string
    schema = db.Column(db.Text)
    published = db.Column(db.Boolean, default=False)
    affiliate_link = db.Column(db.String(500))
    featured_image = db.Column(db.String(500))

    # Comparison article support
    comparison = db.Column(db.Text)   # JSON string containing left/right product data

    # ⭐ NEW: Product Card JSON
    product_card = db.Column(db.Text)   # <— ADD THIS LINE

    # Original single-category fields
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship("Category", backref="primary_articles")

    # Multi-category relationship
    categories = db.relationship(
        "Category",
        secondary=article_categories,
        backref="articles",
        lazy="dynamic"
    )

    # ⭐ NEW: SEO fields (safe, optional, non-breaking)
    seo_title = db.Column(db.String(255))
    seo_description = db.Column(db.String(500))
    seo_keywords = db.Column(db.String(500))
    canonical_url = db.Column(db.String(500))
    og_image = db.Column(db.String(500))
    twitter_image = db.Column(db.String(500))

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_featured = db.Column(db.Boolean, default=False)

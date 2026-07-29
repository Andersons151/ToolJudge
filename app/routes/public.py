from flask import Blueprint, render_template, request, Response
from app.models.article import Article, article_categories
from app.models.category import Category
import json
import datetime

public_bp = Blueprint("public", __name__)

# ---------------------------------------------------------
# HOMEPAGE
# ---------------------------------------------------------
@public_bp.route("/")
def index():
    categories = Category.query.filter_by(is_main=True).all()

    featured_articles = Article.query.filter_by(is_featured=True).order_by(Article.id.desc()).limit(6).all()
    articles = Article.query.filter_by(is_featured=False).order_by(Article.id.desc()).limit(9).all()

    return render_template(
        "public/index.html",
        categories=categories,
        articles=articles,
        featured_articles=featured_articles,
        title="NoFoolTools — Honest Tool Reviews & Guides",
        seo_title="NoFoolTools — Honest Tool Reviews & Guides",
        seo_description="Honest tool reviews, comparisons, buying guides and DIY projects — no fluff, no nonsense.",
        seo_keywords="tool reviews, power tools, DIY guides, buying guides, honest reviews"
    )

# ---------------------------------------------------------
# ARTICLE PAGE
# ---------------------------------------------------------
@public_bp.route("/article/<slug>")
def article_page(slug):
    article = Article.query.filter_by(slug=slug).first_or_404()

    faq_list = []
    if article.faq:
        try:
            faq_list = json.loads(article.faq)
        except Exception:
            faq_list = []

    comparison = None
    if article.comparison:
        try:
            comparison = json.loads(article.comparison)
        except Exception:
            comparison = None

    related_articles = (
        Article.query
        .join(article_categories)
        .join(Category)
        .filter(Category.id.in_([c.id for c in article.categories]))
        .filter(Article.id != article.id)
        .order_by(Article.id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "public/article.html",
        article=article,
        faq_list=faq_list,
        comparison=comparison,
        related_articles=related_articles,
        title=article.title,
        seo_title=article.seo_title,
        seo_description=article.seo_description,
        seo_keywords=article.seo_keywords,
        canonical_url=article.canonical_url,
        og_image=article.og_image,
        twitter_image=article.twitter_image,
        featured_image=article.featured_image
    )

# ---------------------------------------------------------
# CATEGORY PAGE
# ---------------------------------------------------------
@public_bp.route("/category/<slug>")
def category_page(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    filter_type = request.args.get("type")
    page = request.args.get("page", 1, type=int)

    base_query = Article.query.filter(Article.categories.contains(category))
    if filter_type:
        base_query = base_query.filter(Article.categories.any(Category.slug == filter_type))

    pagination = base_query.order_by(Article.id.desc()).paginate(page=page, per_page=12, error_out=False)
    articles = pagination.items

    seo_title = f"{category.name} — Reviews & Buying Guides"
    seo_description = f"Explore honest reviews, comparisons and buying guides for {category.name.lower()} — powered by NoFoolTools."
    seo_keywords = f"{category.slug}, {category.name}, tool reviews, DIY guides, NoFoolTools"

    return render_template(
        "public/category.html",
        category=category,
        articles=articles,
        pagination=pagination,
        filter_type=filter_type,
        title=category.name,
        seo_title=seo_title,
        seo_description=seo_description,
        seo_keywords=seo_keywords
    )

# ---------------------------------------------------------
# STATIC PAGES
# ---------------------------------------------------------
@public_bp.route("/about")
def about():
    return render_template(
        "public/about.html",
        title="About NoFoolTools",
        seo_title="About NoFoolTools",
        seo_description="Learn about NoFoolTools — honest tool reviews, comparisons and DIY guides.",
        seo_keywords="about nofooltools"
    )

@public_bp.route("/contact")
def contact():
    return render_template(
        "public/contact.html",
        title="Contact NoFoolTools",
        seo_title="Contact NoFoolTools",
        seo_description="Get in touch with NoFoolTools for enquiries, feedback or partnership opportunities.",
        seo_keywords="contact nofooltools"
    )

@public_bp.route("/privacy")
def privacy():
    return render_template(
        "public/privacy.html",
        title="Privacy Policy",
        seo_title="NoFoolTools Privacy Policy",
        seo_description="Read the NoFoolTools privacy policy and learn how we handle user data responsibly.",
        seo_keywords="privacy policy, gdpr, nofooltools"
    )

@public_bp.route("/terms")
def terms():
    return render_template(
        "public/terms.html",
        title="Terms & Conditions",
        seo_title="NoFoolTools Terms & Conditions",
        seo_description="Review the NoFoolTools terms and conditions for using our website and content.",
        seo_keywords="terms and conditions, nofooltools"
    )

@public_bp.route("/cookies")
def cookies():
    return render_template(
        "public/cookies.html",
        title="Cookie Policy",
        seo_title="NoFoolTools Cookie Policy",
        seo_description="Learn how NoFoolTools uses cookies for analytics and site functionality.",
        seo_keywords="cookie policy, cookies, nofooltools"
    )

@public_bp.route("/affiliate-disclosure")
def affiliate():
    return render_template(
        "public/affiliate.html",
        title="Affiliate Disclosure",
        seo_title="NoFoolTools Affiliate Disclosure",
        seo_description="NoFoolTools participates in affiliate programmes and may earn commissions from qualifying purchases.",
        seo_keywords="affiliate disclosure, amazon associates, nofooltools"
    )

# ---------------------------------------------------------
# SEARCH PAGE
# ---------------------------------------------------------
@public_bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    categories = Category.query.filter_by(is_main=True).all()

    if not q:
        return render_template(
            "public/search.html",
            categories=categories,
            results=[],
            q="",
            title="Search Tools",
            seo_title="Search Tools",
            seo_description="Search tool reviews, guides and comparisons.",
            seo_keywords="tool search, tool reviews"
        )

    results = Article.query.filter(
        Article.title.ilike(f"%{q}%") |
        Article.summary.ilike(f"%{q}%") |
        Article.content.ilike(f"%{q}%")
    ).all()

    return render_template(
        "public/search.html",
        categories=categories,
        results=results,
        q=q,
        title=f"Search results for '{q}'",
        seo_title=f"Search results for '{q}'",
        seo_description=f"NoFoolTools search results for '{q}'.",
        seo_keywords=f"tool search, {q}"
    )

# ---------------------------------------------------------
# SITEMAP
# ---------------------------------------------------------
@public_bp.route("/sitemap.xml")
def sitemap():
    pages = []
    static_urls = [
        ("/", "daily", "1.0"),
        ("/about", "yearly", "0.5"),
        ("/contact", "yearly", "0.5"),
        ("/privacy", "yearly", "0.5"),
        ("/terms", "yearly", "0.5"),
        ("/cookies", "yearly", "0.5"),
        ("/affiliate-disclosure", "yearly", "0.5"),
        ("/category/power-tools", "weekly", "0.9"),
        ("/category/hand-tools", "weekly", "0.9"),
        ("/category/garden-tools", "weekly", "0.9"),
        ("/category/hardware-supplies", "weekly", "0.9")
    ]

    for url, freq, priority in static_urls:
        pages.append({
            "loc": f"https://nofooltools.com{url}",
            "lastmod": datetime.date.today().isoformat(),
            "changefreq": freq,
            "priority": priority
        })

    articles = Article.query.all()
    for a in articles:
        pages.append({
            "loc": f"https://nofooltools.com/article/{a.slug}",
            "lastmod": a.created_at.date().isoformat(),
            "changefreq": "monthly",
            "priority": "0.8"
        })

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for p in pages:
        xml.append("  <url>")
        xml.append(f"    <loc>{p['loc']}</loc>")
        xml.append(f"    <lastmod>{p['lastmod']}</lastmod>")
        xml.append(f"    <changefreq>{p['changefreq']}</changefreq>")
        xml.append(f"    <priority>{p['priority']}</priority>")
        xml.append("  </url>")
    xml.append("</urlset>")

    return Response("\n".join(xml), mimetype="application/xml")

# ---------------------------------------------------------
# ROBOTS.TXT
# ---------------------------------------------------------
@public_bp.route("/robots.txt")
def robots():
    content = """User-agent: *
Allow: /

Disallow: /admin/
Disallow: /admin
Disallow: /upload/
Disallow: /api/

Allow: /static/css/
Allow: /static/js/
Allow: /static/images/

Sitemap: https://nofooltools.com/sitemap.xml
"""
    return Response(content, mimetype="text/plain")

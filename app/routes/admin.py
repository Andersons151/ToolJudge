from flask import Blueprint, render_template, request, redirect, jsonify, current_app, session, url_for, flash
from app.models.article import Article, article_categories
from app.models.category import Category
from app.models.admin import Admin
from app.extensions import db
from app.services.ai_generator import generate_article
from app.services.slugify import slugify
from werkzeug.utils import secure_filename
from app.utils.auth import admin_required
import os
import json
from bs4 import BeautifulSoup

admin_bp = Blueprint("admin", __name__)


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session["admin_logged_in"] = True
            session["admin_username"] = admin.username
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("admin/login.html")


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
@admin_bp.route("/logout")
@admin_required
def logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    flash("Logged out.", "info")
    return redirect(url_for("admin.login"))


# ---------------------------------------------------------
# FAQ EXTRACTOR (HTML → JSON)
# ---------------------------------------------------------
def extract_faq_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    faq_items = []

    for item in soup.select(".faq-item"):
        p_tags = item.find_all("p")

        if len(p_tags) >= 2:
            question = p_tags[0].get_text(strip=True).replace("Q: ", "")
            answer = p_tags[1].get_text(strip=True).replace("A: ", "")

            faq_items.append({
                "question": question,
                "answer": answer
            })

    return json.dumps(faq_items, indent=4)


# ---------------------------------------------------------
# FAQ SCHEMA GENERATOR (JSON → Schema.org)
# ---------------------------------------------------------
def generate_faq_schema(faq_json):
    try:
        faq_list = json.loads(faq_json)
    except:
        return "{}"

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }

    for item in faq_list:
        schema["mainEntity"].append({
            "@type": "Question",
            "name": item["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": item["answer"]
            }
        })

    return json.dumps(schema, indent=4)


# ---------------------------------------------------------
# COMPARISON TABLE EXTRACTOR (HTML → JSON)
# ---------------------------------------------------------
def extract_comparison_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.comparison-table")

    if not table:
        return "[]"

    rows = table.select("tbody tr")
    comparison_items = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            comparison_items.append({
                "feature": cols[0].get_text(strip=True),
                "product_a": cols[1].get_text(strip=True),
                "product_b": cols[2].get_text(strip=True)
            })

    return json.dumps(comparison_items, indent=4)


# ---------------------------------------------------------
# PRODUCT CARD EXTRACTOR (HTML → JSON)
# ---------------------------------------------------------
def extract_product_card_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    card = soup.select_one("section.product-card")

    if not card:
        return "{}"

    title_tag = card.select_one(".product-card-title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    img_tag = card.select_one(".product-card-image")
    image = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""

    summary_tag = card.select_one(".product-card-summary")
    summary = summary_tag.get_text(strip=True) if summary_tag else ""

    features = []
    for li in card.select(".product-card-features li"):
        features.append(li.get_text(strip=True).replace("✔ ", ""))

    link_tag = card.select_one(".product-card-button")
    affiliate_link = link_tag["href"] if link_tag and link_tag.has_attr("href") else ""

    product_json = {
        "title": title,
        "image": image,
        "summary": summary,
        "features": features,
        "affiliate_link": affiliate_link
    }

    return json.dumps(product_json, indent=4)


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
@admin_bp.route("/")
@admin_required
def dashboard():
    articles = Article.query.order_by(Article.id.desc()).all()
    return render_template("admin/dashboard.html", articles=articles)



    categories = Category.query.all()

    if request.method == "POST":
        topic = request.form["topic"]
        category_id = request.form["category_id"]

        generated = generate_article(topic)

        article = Article(
            title=generated["title"],
            slug=slugify(generated["title"]),
            category_id=category_id,
            summary=generated["summary"],
            content=generated["content"],
            faq=json.dumps(generated["faq"]),
            schema=json.dumps(generated["schema"]),
            published=True
        )

        db.session.add(article)
        db.session.commit()

        return redirect("/admin")

    return render_template("admin/new_article.html", categories=categories)


# ---------------------------------------------------------
# CATEGORY LIST
# ---------------------------------------------------------
@admin_bp.route("/categories")
@admin_required
def categories():
    categories = Category.query.all()
    return render_template("admin/categories.html", categories=categories)


# ---------------------------------------------------------
# MANUAL JSON IMPORT ARTICLE
# ---------------------------------------------------------
@admin_bp.route("/articles/manual", methods=["GET", "POST"])
@admin_required
def manual_article():
    categories = Category.query.all()

    if request.method == "POST":
        raw_json = request.form["json_data"]
        primary_category_id = request.form["category_id"]

        try:
            data = json.loads(raw_json)
        except Exception as e:
            return f"JSON Error: {e}", 400

        is_featured = bool(request.form.get("is_featured"))

        article = Article(
            title=data["title"],
            slug=slugify(data["title"]),
            summary=data["summary"],
            content=data["content"],
            faq=json.dumps(data.get("faq", [])),
            schema=json.dumps(data.get("schema", {})),
            category_id=primary_category_id,
            published=True,
            affiliate_link=data.get("affiliate_link"),
            featured_image=data.get("featured_image"),
            comparison=json.dumps(data.get("comparison")) if data.get("comparison") else None,
            seo_title=data.get("seo_title"),
            seo_description=data.get("seo_description"),
            seo_keywords=data.get("seo_keywords"),
            canonical_url=data.get("canonical_url"),
            og_image=data.get("og_image"),
            twitter_image=data.get("twitter_image"),
            is_featured=is_featured
        )

        db.session.add(article)
        db.session.flush()

        if "categories" in data:
            for slug in data["categories"]:
                cat = Category.query.filter_by(slug=slug).first()
                if cat:
                    article.categories.append(cat)

        db.session.commit()
        return redirect("/admin")

    return render_template("admin/manual_article.html", categories=categories)


# ---------------------------------------------------------
# DELETE ARTICLE
# ---------------------------------------------------------
@admin_bp.route("/articles/delete/<int:article_id>", methods=["GET", "POST"])
@admin_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)

    db.session.execute(
        article_categories.delete().where(article_categories.c.article_id == article.id)
    )

    db.session.delete(article)
    db.session.commit()

    return redirect("/admin")


# ---------------------------------------------------------
# EDIT ARTICLE (AUTO‑SYNC EVERYTHING)
# ---------------------------------------------------------
@admin_bp.route("/articles/edit/<int:article_id>", methods=["GET", "POST"])
@admin_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    categories = Category.query.all()

    if request.method == "POST":
        article.title = request.form["title"]
        article.slug = slugify(request.form["title"])
        article.summary = request.form["summary"]
        article.content = request.form["content"]
        article.featured_image = request.form.get("featured_image")
        article.affiliate_link = request.form.get("affiliate_link")

        article.is_featured = request.form.get("is_featured") == "1"

        article.seo_title = request.form.get("seo_title")
        article.seo_description = request.form.get("seo_description")
        article.seo_keywords = request.form.get("seo_keywords")
        article.canonical_url = request.form.get("canonical_url")
        article.og_image = request.form.get("og_image")
        article.twitter_image = request.form.get("twitter_image")

        faq_json = extract_faq_from_html(article.content)
        article.faq = faq_json

        article.schema = generate_faq_schema(faq_json)

        comparison_json = extract_comparison_from_html(article.content)
        article.comparison = comparison_json

        product_json = extract_product_card_from_html(article.content)
        article.product_card = product_json

        selected_slugs = request.form.getlist("categories")

        db.session.execute(
            article_categories.delete().where(article_categories.c.article_id == article.id)
        )

        for slug in selected_slugs:
            cat = Category.query.filter_by(slug=slug).first()
            if cat:
                article.categories.append(cat)

        db.session.commit()
        return redirect("/admin")

    faq_json = article.faq if article.faq else "[]"
    schema_json = article.schema if article.schema else "{}"
    comparison_json = article.comparison if article.comparison else "[]"
    product_card_json = article.product_card if hasattr(article, "product_card") and article.product_card else "{}"

    return render_template(
        "admin/edit_article.html",
        article=article,
        categories=categories,
        faq_json=faq_json,
        schema_json=schema_json,
        comparison_json=comparison_json,
        product_card_json=product_card_json
    )


# ---------------------------------------------------------
# FEATURE TOGGLE
# ---------------------------------------------------------
@admin_bp.route("/articles/feature/<int:article_id>", methods=["POST", "GET"])
@admin_required
def toggle_feature(article_id):
    article = Article.query.get_or_404(article_id)
    article.is_featured = not article.is_featured
    db.session.commit()
    return redirect("/admin")


# ---------------------------------------------------------
# IMAGE UPLOAD ENDPOINT (TinyMCE)
# ---------------------------------------------------------
@admin_bp.route("/upload-image", methods=["POST"])
@admin_required
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)

    upload_path = os.path.join(current_app.root_path, "static/uploads", filename)
    file.save(upload_path)

    file_url = f"/static/uploads/{filename}"

    return jsonify({"location": file_url})

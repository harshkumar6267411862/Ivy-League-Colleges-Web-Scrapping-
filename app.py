from flask import Flask, render_template, redirect, url_for, request, flash
from config import Config
from models import db, User, Opportunity, Post
from scraper import scrape_all
from incoscore import calculate_score
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Flask 3 compatible initialization
with app.app_context():
    db.create_all()
    scrape_all()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed = generate_password_hash(request.form["password"])

        user = User(
            username=request.form["username"],
            email=request.form["email"],
            password=hashed,
            domain=request.form["domain"],
        )

        user.incoscore = calculate_score(user)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    opps = Opportunity.query.filter_by(domain=current_user.domain).all()
    return render_template("dashboard.html", opps=opps)


@app.route("/refresh")
@login_required
def refresh():
    scrape_all()
    flash("Opportunities Updated Successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/leaderboard")
def leaderboard():
    users = User.query.order_by(User.incoscore.desc()).all()
    return render_template("leaderboard.html", users=users)


@app.route("/community", methods=["GET", "POST"])
@login_required
def community():
    if request.method == "POST":
        post = Post(
            content=request.form["content"],
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()

    posts = Post.query.all()
    return render_template("community.html", posts=posts)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
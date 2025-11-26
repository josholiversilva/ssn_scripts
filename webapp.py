from flask import Flask, render_template, request, redirect, url_for, session, flash
from users import Users
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random


app = Flask(__name__)
app.secret_key = "change-this-secret-for-prod"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ssn.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Seed constants (used only for initial DB population)
SEED_GROUPS = [
    {"id": 1, "name": "SSN 2025!!!", "desc": "Secret Santa With Friends for 2025", "members": Users.get_all()}
]

SEED_POSTS = {
    1: [
        {"author": "jen", "text": "I've hung the stockings!"},
        {"author": "brian", "text": "Who's bringing cookies to the party?"},
    ],
    2: [
        {"author": "eric", "text": "Movie night this Friday?"},
    ],
    3: [
        {"author": "vincent", "text": "Secret Santa signups open."},
    ],
}

SEED_WISHLISTS = {
    1: {"jen": ["mug", "scarves"], "brian": ["socks"]},
    2: {"eric": ["board game"], "ryan": ["headphones"]},
    3: {"vincent": ["coffee"], "bryan": ["wallet"]},
}


### Models
group_members = db.Table(
    "group_members",
    db.Column("group_id", db.Integer, db.ForeignKey("group.id"), primary_key=True),
    db.Column("user_name", db.String, db.ForeignKey("user.username"), primary_key=True),
)


class User(db.Model):
    username = db.Column(db.String, primary_key=True)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=True)
    members = db.relationship("User", secondary=group_members, backref="groups")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    author = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    username = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)
    item = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Add timestamp


class Pairing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)
    recipient = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)


class RandomFact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)


def seed_db():
    # create Users
    if User.query.count() == 0:
        for u in Users:
            db.session.add(User(username=u.value))
        db.session.commit()

    # create Groups and memberships
    if Group.query.count() == 0:
        for g in SEED_GROUPS:
            grp = Group(id=g["id"], name=g["name"], desc=g.get("desc"))
            for m in g.get("members", []):
                user = User.query.filter_by(username=m).first()
                if user:
                    grp.members.append(user)
            db.session.add(grp)
        db.session.commit()

    '''
    # create Posts
    for gid, posts in SEED_POSTS.items():
        for p in posts:
            exists = Post.query.filter_by(group_id=gid, author=p["author"], text=p["text"]).first()
            if not exists:
                db.session.add(Post(group_id=gid, author=p["author"], text=p["text"]))
    db.session.commit()

    # create WishlistItems
    for gid, lists in SEED_WISHLISTS.items():
        for user, items in lists.items():
            for it in items:
                exists = WishlistItem.query.filter_by(group_id=gid, username=user, item=it).first()
                if not exists:
                    db.session.add(WishlistItem(group_id=gid, username=user, item=it))
    db.session.commit()

    # create Pairings (simple deterministic cyclic pairings) if none exist
    if Pairing.query.count() == 0:
        users = [u.username for u in User.query.order_by(User.username).all()]
        if users:
            for i, u in enumerate(users):
                buyer = u
                recipient = users[(i + 1) % len(users)]
                exists = Pairing.query.filter_by(buyer=buyer).first()
                if not exists:
                    db.session.add(Pairing(buyer=buyer, recipient=recipient))
        db.session.commit()

    # add some random facts if none exist
    if RandomFact.query.count() == 0:
        facts = [
            "Candy canes were originally white and flavored with peppermint.",
            "The first artificial Christmas tree was made of dyed goose feathers.",
            "In Japan, KFC is a popular Christmas meal tradition.",
            "Rudolph the Red-Nosed Reindeer was created as a marketing campaign in 1939.",
        ]
        for f in facts:
            db.session.add(RandomFact(text=f))
        db.session.commit()
    '''


def init_app_db():
    db.create_all()
    seed_db()

# Register DB initialization in a way that's compatible across Flask versions.
# Some Flask versions may not expose `before_first_request` (AttributeError);
# try registering it, fall back to `before_serving`, and as a last resort run immediately.
try:
    app.before_first_request(init_app_db)
except Exception:
    try:
        app.before_serving(init_app_db)
    except Exception:
        # last resort: run immediately (synchronous) within an application context
        # to avoid "Working outside of application context" errors when SQLAlchemy
        # needs the current app.
        with app.app_context():
            init_app_db()


def is_valid_user(username: str) -> bool:
    if not username:
        return False
    return User.query.filter_by(username=username).first() is not None


@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        if is_valid_user(username):
            session["user"] = username
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username. Try one from the known users.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login"))
    groups = Group.query.all()
    return render_template("dashboard.html", groups=groups)


@app.route("/profile")
def profile():
    if not session.get("user"):
        return redirect(url_for("login"))
    user = session.get("user")
    # find pairing for this user
    pairing = Pairing.query.filter_by(buyer=user).first()
    recipient = pairing.recipient if pairing else None
    wishlist = []
    if recipient:
        wishlist = WishlistItem.query.filter_by(group_id=1, username=recipient).all()
    # choose a random fact
    fact_obj = RandomFact.query.order_by(db.func.random()).first() if RandomFact.query.count() > 0 else None
    fact = fact_obj.text if fact_obj else ""
    return render_template("profile.html", user=user, recipient=recipient, wishlist=wishlist, fact=fact)


@app.route("/group/<int:group_id>")
def group_page(group_id: int):
    if not session.get("user"):
        return redirect(url_for("login"))
    group = Group.query.get(group_id)
    if not group:
        flash("Group not found", "warning")
        return redirect(url_for("dashboard"))
    # convert to a simple dict for template compatibility
    g = {"id": group.id, "name": group.name, "desc": group.desc, "members": [m.username for m in group.members]}
    return render_template("group.html", group=g)


@app.route("/group/<int:group_id>/christmas")
def christmas_home(group_id: int):
    if not session.get("user"):
        return redirect(url_for("login"))
    group = Group.query.get(group_id)
    if not group:
        flash("Group not found", "warning")
        return redirect(url_for("dashboard"))
    # paginate posts for messenger-style loading (load newest 20 by default)
    limit = 20
    total = Post.query.filter_by(group_id=group_id).count()
    page_posts = Post.query.filter_by(group_id=group_id).order_by(Post.created_at.desc()).limit(limit).all()
    # reverse so chronological order (oldest first -> newest last) for display
    page_posts = list(reversed(page_posts))
    posts_list = [{"author": p.author, "text": p.text, "created_at": p.created_at.isoformat()} for p in page_posts]
    members = [m.username for m in group.members]
    wishlists = {}
    items = WishlistItem.query.filter_by(group_id=group_id).all()
    for it in items:
        wishlists.setdefault(it.username, []).append(it.item)
    g = {"id": group.id, "name": group.name}
    has_more = total > len(page_posts)
    return render_template("christmas_home.html", group=g, posts=posts_list, members=members, wishlists=wishlists, page=0, has_more=has_more)



@app.route("/group/<int:group_id>/posts")
def posts_json(group_id: int):
    # returns a page of posts as JSON; page=0 is newest (most recent) page
    try:
        page = int(request.args.get("page", "0"))
    except ValueError:
        page = 0
    try:
        limit = int(request.args.get("limit", "20"))
    except ValueError:
        limit = 20
    offset = page * limit
    q = Post.query.filter_by(group_id=group_id).order_by(Post.created_at.desc()).offset(offset).limit(limit)
    results = list(reversed(q.all()))
    posts = []
    for p in results:
        posts.append({"author": p.author, "text": p.text, "created_at": p.created_at.isoformat()})
    # indicate if more older posts exist
    total = Post.query.filter_by(group_id=group_id).count()
    more = total > (offset + len(results))
    return {"posts": posts, "page": page, "more": more}


@app.route("/group/<int:group_id>/post", methods=["POST"])
def add_post(group_id: int):
    if not session.get("user"):
        return redirect(url_for("login"))
    text = request.form.get("text", "").strip()
    if not text:
        flash("Post cannot be empty.", "danger")
        return redirect(url_for("christmas_home", group_id=group_id))
    db.session.add(Post(group_id=group_id, author=session.get("user"), text=text))
    db.session.commit()
    flash("Post added.", "success")
    return redirect(url_for("christmas_home", group_id=group_id))


@app.route("/group/<int:group_id>/wishlist", methods=["POST"])
def add_wishlist_item(group_id: int):
    if not session.get("user"):
        return redirect(url_for("login"))

    user = session.get("user")
    item = request.form.get("item", "").strip()
    if not user or not item:
        flash("User and item are required for wishlist.", "danger")
        return redirect(url_for("christmas_home", group_id=group_id))
    wi = WishlistItem(group_id=group_id, username=user, item=item, created_at=datetime.utcnow())  # Populate timestamp
    db.session.add(wi)
    # Also create a post announcing the wishlist addition with the item on a new line
    post_text = f"{user} just added to their wishlist!\n{item}"
    db.session.add(Post(group_id=group_id, author=user, text=post_text))
    db.session.commit()
    flash(f"Added wishlist item for {user}.", "success")
    return redirect(url_for("christmas_home", group_id=group_id))


if __name__ == "__main__":
    app.run(debug=True, port=5000)

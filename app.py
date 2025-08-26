from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "atm_secret"

# SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///atm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

MAX_BALANCE = 50000.0


# ------------------ Database Models -------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # password still hashed
    pin = db.Column(db.String(10), nullable=False)  # store plain 4-digit PIN
    balance = db.Column(db.Float, default=0.0)

    transactions = db.relationship("Transaction", backref="user", lazy=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # deposit, withdraw, send, receive
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(200))


# ------------------ Helpers -------------------

def parse_amount(val):
    """Safely parse amount to float, return positive float or None."""
    try:
        amt = float(val)
    except Exception:
        return None
    if amt <= 0:
        return None
    return round(amt, 2)


# ------------------ Routes -------------------

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password_raw = request.form.get("password") or ""
        pin_raw = (request.form.get("pin") or "").strip()

        if not username or not password_raw or not pin_raw:
            flash("All fields are required.", "warning")
            return redirect(url_for("signup"))

        if not pin_raw.isdigit() or len(pin_raw) != 4:
            flash("PIN must be exactly 4 digits.", "warning")
            return redirect(url_for("signup"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("signup"))

        password_hashed = generate_password_hash(password_raw)

        new_user = User(username=username, password=password_hashed, pin=pin_raw, balance=0.0)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        session.pop("user", None)
        flash("User not found. Please login again.", "danger")
        return redirect(url_for("login"))

    transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.timestamp.desc()).all()
    return render_template("dashboard.html", user=user, transactions=transactions)


# ------------------ PIN Confirmation --------------------

@app.route("/confirm_action", methods=["POST"])
def confirm_action():
    if "user" not in session:
        return redirect(url_for("login"))

    action = (request.form.get("action") or "").strip()
    amount_raw = request.form.get("amount")
    recipient_form = (request.form.get("recipient") or "").strip() or None

    amount = parse_amount(amount_raw)
    if amount is None:
        flash("Please enter a valid positive amount.", "warning")
        return redirect(url_for("dashboard"))

    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        session.pop("user", None)
        flash("Session invalid. Please login again.", "warning")
        return redirect(url_for("login"))

    recipients = []
    if action == "send":
        recipients = User.query.filter(User.id != user.id).all()

    session["pending"] = {"action": action, "amount": amount, "recipient": recipient_form}
    return render_template("confirm_pin.html", action=action, amount=amount, recipients=recipients)


@app.route("/process_action", methods=["POST"])
def process_action():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()
    if not user:
        session.pop("user", None)
        flash("User not found. Please login again.", "danger")
        return redirect(url_for("login"))

    pending = session.pop("pending", None)
    if not pending:
        flash("No action pending.", "warning")
        return redirect(url_for("dashboard"))

    action = (request.form.get("action") or pending.get("action") or "").strip()
    amount_raw = request.form.get("amount") or pending.get("amount")
    recipient_name = (request.form.get("recipient") or pending.get("recipient") or "").strip() or None
    entered_pin = (request.form.get("pin") or "").strip()

    amount = parse_amount(amount_raw)
    if amount is None:
        flash("Invalid amount.", "warning")
        return redirect(url_for("dashboard"))

    # 🔑 Check PIN directly (plain)
    if entered_pin != user.pin:
        flash("Invalid PIN! Transaction cancelled.", "danger")
        return redirect(url_for("dashboard"))

    # ---------- perform actions ----------
    if action == "deposit":
        if user.balance + amount > MAX_BALANCE:
            flash(f"Transaction exceeds account limit of ₹{MAX_BALANCE:,.2f}.", "danger")
        else:
            user.balance += amount
            db.session.add(Transaction(user_id=user.id, type="Deposit", amount=amount))
            db.session.commit()
            flash(f"Deposited ₹{amount:.2f} successfully!", "success")

    elif action == "withdraw":
        if amount > user.balance:
            flash("Insufficient balance!", "danger")
        else:
            user.balance -= amount
            db.session.add(Transaction(user_id=user.id, type="Withdraw", amount=amount))
            db.session.commit()
            flash(f"Withdrew ₹{amount:.2f} successfully!", "success")

    elif action == "send":
        if not recipient_name:
            flash("Recipient is required.", "warning")
            return redirect(url_for("dashboard"))

        recipient = User.query.filter_by(username=recipient_name).first()
        if not recipient:
            flash("Recipient does not exist!", "danger")
        elif amount > user.balance:
            flash("Insufficient balance!", "danger")
        elif recipient.balance + amount > MAX_BALANCE:
            flash("Recipient’s account cannot exceed ₹50,000!", "danger")
        else:
            user.balance -= amount
            recipient.balance += amount
            db.session.add(Transaction(user_id=user.id, type="Send", amount=amount, details=f"To {recipient.username}"))
            db.session.add(Transaction(user_id=recipient.id, type="Receive", amount=amount, details=f"From {user.username}"))
            db.session.commit()
            flash(f"Sent ₹{amount:.2f} to {recipient.username} successfully!", "success")

    else:
        flash("Unknown action.", "warning")

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

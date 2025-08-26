# ATM-Simulation
Perfect 👍 Let’s refine and polish the **README.md** text for a more professional, GitHub-ready look (edited, concise, and clean).

---

# 💳 ATM Web Application (Flask)

A lightweight **ATM simulation web application** built with **Flask, SQLAlchemy, and SQLite**.
It allows users to **sign up, log in, deposit, withdraw, send money, and track transactions** securely.

---

## ✨ Features

* 🔐 **User Accounts** – Sign up, log in, and manage sessions
* 💵 **Deposit & Withdraw** – Secure balance handling with limits
* 📤 **Money Transfer** – Send funds to other registered users
* 📜 **Transaction History** – Track all account activity
* 🔑 **PIN Verification** – Required before deposits, withdrawals, and transfers
* 📊 **Balance Cap** – Maximum allowed balance is **₹50,000**

---

## 🛠 Tech Stack

* **Backend:** Python (Flask)
* **Database:** SQLite (via SQLAlchemy ORM)
* **Frontend:** HTML, Jinja2 Templates, Bootstrap

---

## 📂 Project Structure

```
atm-app/
│── app.py                # Main Flask app
│── atm.db                # SQLite database (auto-created)
│── templates/            # Jinja2 templates
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── confirm_pin.html
│── static/               # CSS / JS assets
│── requirements.txt      # Python dependencies
│── README.md             # Documentation
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/atm-app.git
cd atm-app
```

### 2️⃣ Create a virtual environment (recommended)

```bash
python -m venv venv
# Activate:
venv\Scripts\activate      # On Windows
source venv/bin/activate   # On macOS/Linux
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` doesn’t exist, create one with:

```
Flask
Flask-SQLAlchemy
Werkzeug
```

### 4️⃣ Run the application

```bash
python app.py
```

👉 Visit: `http://127.0.0.1:5000`

---

## 🧑‍💻 How to Use

1. **Sign Up** with a username, password, and 4-digit PIN
2. **Log In** with your credentials
3. Access the **dashboard** to:

   * Deposit money
   * Withdraw money
   * Send money to other users
4. Confirm each action with your **PIN**
5. View your **transaction history** anytime

---

## 📸 Screenshots

<img width="1766" height="850" alt="image" src="https://github.com/user-attachments/assets/042b693c-d2af-4e79-8165-ed6661e6891b" />

* 🔑 Login Page
* 📝 Signup Page
* 🏦 Dashboard
* ✅ PIN Confirmation

---

## ⚠️ Security Notes

* In this demo version, **PINs are stored in plain text** for simplicity
* For production, always **hash & salt** passwords and PINs (e.g., with `Werkzeug` or `bcrypt`)

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

# 🚀 TaskFlow — Flask CRUD Application with Authentication

A modern, responsive CRUD (Create, Read, Update, Delete) web application built with **Flask**, **Flask-Login**, **Flask-SQLAlchemy**, and **Bootstrap 5**.

---

## ✨ Features

- **🔐 Authentication & Security**:
  - User Registration with form validation.
  - Secure Login & Logout with session management via `Flask-Login`.
  - Secure password hashing using `werkzeug.security`.
  - Protected routes (unauthorized users are automatically redirected to the login page).
  - User-isolated data (each user only manages their own items).

- **📝 Full CRUD Operations**:
  - **Create**: Add new items with title, description, category, status, priority, and value.
  - **Read**: Dashboard with search bar, category filtering, status filtering, and sorting (Newest, Oldest, Title, Price).
  - **Update**: Edit existing items with pre-filled forms.
  - **Delete**: Safely delete items with client-side confirmation.
  - **Quick Status Toggle**: Mark items as Pending/Completed directly with one click.

- **📊 Dashboard Statistics**:
  - Live summary counters: Total Items, Completed, In Progress/Pending, and Total Value.

- **🎨 Modern UI/UX**:
  - Clean styling with Bootstrap 5 and Bootstrap Icons.
  - Informative dismissible flash messages (Success, Warning, Danger, Info).
  - Fully responsive on mobile, tablet, and desktop.

---

## 🛠️ Project Structure

```text
CRUD/
├── app.py               # Main Flask application & routes (Auth + CRUD)
├── models.py            # SQLAlchemy database models (User, Item)
├── requirements.txt     # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css    # Custom modern stylesheet
│   └── js/
│       └── main.js      # Interactive JavaScript & confirmations
└── templates/
    ├── base.html        # Main template layout with navigation & flash alerts
    ├── login.html       # Login page
    ├── register.html    # User registration page
    ├── index.html       # Dashboard & items list (Read / Filter / Search)
    ├── create.html      # Create item form
    ├── edit.html        # Edit item form
    └── view.html        # View item details
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
Navigate to **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.
1. Click **Sign Up** to create an account.
2. Log in and start creating, viewing, editing, and deleting items.

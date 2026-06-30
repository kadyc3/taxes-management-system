# 💼 Taxes Management System

A modern desktop application developed in **Python** using **PyQt6** and **SQLite** for managing taxpayers, tax declarations, and audit logs. The application follows a layered architecture (GUI, Kernel, Infrastructure) to ensure maintainability, scalability, and clean separation of concerns.

---

## 📸 Screenshots

> Add screenshots of your application here.

### Login
<img width="280" height="355" alt="image" src="https://github.com/user-attachments/assets/923b24dd-9ac2-4ebe-9bb1-064010e52be2" />


### Dashboard
<img width="957" height="500" alt="image" src="https://github.com/user-attachments/assets/7d76d8e0-96c0-43d5-9132-3fd0a527b47a" />


### Taxpayer Management
<img width="959" height="497" alt="image" src="https://github.com/user-attachments/assets/5cb44eb6-c742-4552-aec9-449102097898" />


### Declaration Management
<img width="959" height="497" alt="image" src="https://github.com/user-attachments/assets/2ecb08a3-96c5-4dae-a649-339609aedb29" />


### Audit Logs
<img width="959" height="488" alt="image" src="https://github.com/user-attachments/assets/2d180b13-646d-4b03-8394-b533f08aed09" />


---

# ✨ Features

## Authentication

- User login
- Role-Based Access Control (RBAC)
- Administrator and Editor roles
- Session management

## Dashboard

- Total taxpayers
- Active taxpayers
- Total declarations
- Pending declarations
- Approved declarations
- Rejected declarations
- Total approved revenue
- Today's audit activity

## Taxpayer Management

- Create taxpayer
- Update taxpayer
- Delete taxpayer
- Search taxpayers
- View taxpayer information

## Declaration Management

- Create declarations
- Edit declarations
- Delete declarations
- Submit declarations
- Validate declarations
- Reject declarations
- Search declarations

## Audit Logs

- Automatic logging of operations
- User activity tracking
- Recent activity history

## Export

- Export declarations to Excel (.xlsx)

---

# 🛠 Technologies Used

| Technology | Purpose |
|------------|----------|
| Python | Programming language |
| PyQt6 | Desktop GUI |
| SQLite | Database |
| OpenPyXL | Excel export |
| Git | Version control |
| GitHub | Source code hosting |

---

# 🏗 Architecture

The project follows a layered architecture inspired by Clean Architecture principles.

```
Taxes Management System

GUI
│
├── Pages
├── Dialogs
├── Widgets
└── Windows

Kernel
│
├── Models
├── Services
├── Exceptions
└── Business Logic

Infrastructure
│
├── Database
├── Repositories
└── Connection
```

### GUI Layer

Responsible for:

- User interface
- User interactions
- Forms
- Dashboard
- Dialogs

### Kernel Layer

Responsible for:

- Business logic
- Services
- Models
- Validation
- Authentication

### Infrastructure Layer

Responsible for:

- SQLite database
- Data persistence
- Repository pattern
- Database connection

---

# 📂 Project Structure

```
taxes-management-system/

GUI/
    dialogs/
    pages/
    widgets/
    login_window.py
    dashboard_window.py

Infrastructure/
    database/
    repositories/

Kernel/
    models/
    services/
    exceptions/

main.py
requirements.txt
README.md
```

---

# 🗄 Database

The application uses **SQLite**.

Main tables:

- Users
- Taxpayers
- Declarations
- Audit Logs

Relationships:

- One taxpayer can have multiple declarations.
- Every action performed by users is stored in the audit logs.

---

# 🚀 Installation

## Clone the repository

```bash
git clone https://github.com/yourusername/taxes-management-system.git
```

## Enter the project

```bash
cd taxes-management-system
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run the application

```bash
python main.py
```

---

# 📊 Main Functionalities

✔ Authentication

✔ Dashboard

✔ Taxpayer CRUD

✔ Declaration CRUD

✔ Search

✔ Audit Logging

✔ Excel Export

✔ Modern Desktop Interface

---

# 💡 Software Engineering Concepts

This project demonstrates the following concepts:

- Object-Oriented Programming (OOP)
- Layered Architecture
- Repository Pattern
- Service Layer Pattern
- CRUD Operations
- Authentication
- Role-Based Access Control
- Exception Handling
- Database Design
- GUI Development
- Separation of Concerns
- Data Validation
- Excel Export
- Git Version Control

---

# 📈 Future Improvements

- Password hashing
- PDF export
- Data visualization charts
- Email notifications
- Automatic backups
- Multi-user sessions
- REST API integration
- PostgreSQL support
- Dark mode
- Unit testing

---

# 👨‍💻 Author

**Khadija Ayeb**

Software Engineering Student

Specialization: **Software Engineering and Information Systems**

---

# 📜 License

This project was developed for educational and portfolio purposes.

# CampusFlow 🏫

### A Web-Based Campus Complaint and Maintenance Management System

CampusFlow is a web-based platform designed to simplify campus complaint management and improve the maintenance process within educational institutions. It provides students with a centralized system to report campus-related issues and helps organize complaint records for efficient management and resolution.

---

## 📌 Problem Statement

Traditional campus complaint management often relies on manual reporting methods, which can lead to poor organization, delays, and difficulties in tracking complaints. CampusFlow aims to address these challenges by providing a structured digital platform for submitting and managing campus maintenance complaints.

## 🎯 Objectives

- Develop a centralized platform for campus complaint management.
- Simplify the process of reporting campus-related issues.
- Allow students to provide complaint details, including category, priority, and location.
- Maintain organized complaint records using a database.
- Improve the efficiency and transparency of campus maintenance operations.

## ✨ Features

- **User Registration and Login:** Provides user authentication for accessing the platform.
- **Complaint Submission:** Allows students to report campus issues through an organized form.
- **Category Selection:** Classifies complaints into Electrical, Cleanliness, Wi-Fi, Furniture, and Other.
- **Priority Assignment:** Allows complaints to be marked as Low, Medium, or High priority.
- **Complaint Management:** Provides structured complaint records for easier management.
- **Dashboard:** Offers separate dashboard interfaces for students and administrators.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| HTML | Frontend structure |
| CSS | Styling and layout |
| JavaScript | Frontend interactivity |

## ⚙️ Project Architecture

CampusFlow follows a simple three-layer architecture:

1. **Frontend:** HTML, CSS, and JavaScript handle the user interface and interactions.
2. **Backend:** Python Flask processes requests, handles application logic, and connects the frontend with the database.
3. **Database:** SQLite stores and manages user and complaint records.

### Application Workflow

Student → Frontend Interface → Flask Backend → SQLite Database → Response

## 📂 Project Structure

```text
CampusFlow/
│
├── app.py
├── database.db
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── admin_dashboard.html
│   ├── submit_complaint.html
│   └── my_complaints.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md
```

## 🚀 Installation and Setup

Follow these steps to run CampusFlow locally.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/CampusFlow.git
```

### 2. Navigate to the Project Directory

```bash
cd CampusFlow
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install flask
```

### 6. Run the Application

```bash
python app.py
```

### 7. Open in Browser

Visit:

```text
http://127.0.0.1:5000/
```

The application should now be running locally.

## 🔮 Future Scope

- Email and real-time complaint status notifications.
- Advanced complaint filtering and search functionality.
- Analytics and visual reports for administrators.
- Improved complaint tracking and resolution monitoring.
- Mobile-friendly interface and enhanced accessibility.

## 🎓 Academic Project

**Project Name:** CampusFlow  

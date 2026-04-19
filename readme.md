# 🇨🇦 Canadian Farm Data Dashboard (Django)
# 📌 Project Overview
This project is a Django-based web application that visualizes Canadian agricultural data. It allows users to analyze crop performance, compare provinces, and predict crop success.

## 🚀 Features
- Dashboard with key metrics
- Crop yield trend visualization
- Crop value comparison
- Province & crop comparison tool
- Machine learning prediction system
- Admin-restricted CSV upload feature

## 🛠 Tech Stack
- Python 3.12
- Django 4.x
- SQLite
- Pandas
- Scikit-learn
- Chart.js

## ⚙️ Setup Instructions

### 1. Clone repository
```bash
git clone <https://github.com/amardeepsingh01/Canadian-Farm-Data-Dashboard>
cd project-folder

### 2. Create virtual environment

python -m venv env
source env/bin/activate

### 3. Install dependencies
pip install django pandas scikit-learn

### 4. Run migrations
python manage.py migrate

### 5. Run server
python manage.py runserver

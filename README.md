# Assignment 10 – Weather Application (Django + MongoDB + EC2)

This project is part of Assignment 10 and demonstrates how to build a weather information application using **Django**, **MongoDB**, and **OpenWeatherMap API**, hosted on two separate **AWS EC2 instances**.

The application retrieves real-time weather data for selected cities and stores interaction logs in MongoDB.  
Django runs on a separate EC2 web server, while MongoDB is hosted on its own EC2 instance.

---

## 🚀 Project Overview

This application:

- Fetches real-time weather information using the **OpenWeatherMap API**
- Uses **Django** as the web framework
- Stores logs in **MongoDB** running on an EC2 instance
- Loads the API key securely from environment variables
- Separates backend roles:
  - **EC2 #1** → MongoDB server  
  - **EC2 #2** → Django web server

This architecture reflects real-world industry deployment models.

---

## 🛠️ Setup Instructions

### **1. Configure OpenWeatherMap API Key**

1. Sign up and obtain an API key:  
   https://home.openweathermap.org/users/sign_up

2. Create a `.env` file in your Django project root and add:
3. 3. Load the key inside your `settings.py`:
```python
import os
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

2. Starting the Django Web Server (EC2 Web Server)
	1.	SSH into your EC2 web server.
	2.	Navigate to the project directory:
cd ~/assignment10	3.	Install dependencies:
pip install -r requirements.txt
	4.	Apply migrations:
python3 manage.py migrate	5.	Start the Django server:
python3 manage.py runserver 0.0.0.0:8000
Your application will be available at:
http://<your-webserver-public-ip>:8000/
3. MongoDB Setup (Separate EC2 Instance)
	1.	SSH into your MongoDB EC2 server.
	2.	Start MongoDB:
sudo systemctl start mongod
	3.	Verify status:
sudo systemctl status mongod
4.	In Django settings, connect to MongoDB:
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'weather_db',
        'CLIENT': {
            'host': 'mongodb://<mongo-private-ip>:27017/',
        }
    }
}

# 🚀 PythonAnywhere Deployment Guide for Contactify

## Why PythonAnywhere?
✅ **100% FREE** - No credit card required  
✅ **Perfect for Django** - Built specifically for Python web apps  
✅ **Easy to use** - Beginner-friendly interface  
✅ **Always online** - Your app stays live 24/7  

---

## 📋 What You'll Need
1. GitHub account (you already have this ✅)
2. PythonAnywhere free account (we'll create this)
3. 15-20 minutes of your time

---

## 🎯 Step-by-Step Deployment

### STEP 1: Create PythonAnywhere Account (2 minutes)

1. Go to: **https://www.pythonanywhere.com/**
2. Click **"Start running Python online in less than a minute"**
3. Click **"Create a Beginner account"** (FREE)
4. Fill in:
   - Username: (choose your username, e.g., "nexus462")
   - Email: your email
   - Password: create a password
5. Click **"Register"**
6. Check your email and verify your account
7. Log in to PythonAnywhere

✅ **You're now logged in!**

---

### STEP 2: Open a Bash Console (1 minute)

1. After logging in, you'll see the **Dashboard**
2. Click on **"Consoles"** tab (at the top)
3. Under **"Start a new console"**, click **"Bash"**
4. A black terminal window will open

✅ **You now have a Linux terminal!**

---

### STEP 3: Clone Your GitHub Repository (2 minutes)

In the Bash console, type these commands **one by one**:

```bash
# Go to your home directory
cd ~

# Clone your repository from GitHub
git clone https://github.com/Nexus462/Contact-Management-System.git

# Enter the project folder
cd Contact-Management-System

# Check if files are there
ls
```

**What you should see:**
- A list of files including `manage.py`, `requirements.txt`, `db.sqlite3`, etc.

✅ **Your code is now on PythonAnywhere!**

---

### STEP 4: Create a Virtual Environment (2 minutes)

Still in the Bash console:

```bash
# Make sure you're in the project folder
cd ~/Contact-Management-System

# Create a virtual environment
mkvirtualenv --python=/usr/bin/python3.10 contactify

# The virtual environment will activate automatically
# You'll see (contactify) at the start of your command line
```

✅ **Virtual environment created!**

---

### STEP 5: Install Dependencies (3 minutes)

```bash
# Install all required packages
pip install -r requirements.txt

# This will install Django, Pillow, and reportlab
# Wait for it to finish (takes 1-2 minutes)
```

**What you'll see:**
- Lots of text scrolling by
- "Successfully installed..." messages
- No red error messages (red is bad, green/white is good)

✅ **All packages installed!**

---

### STEP 6: Run Database Migrations (1 minute)

```bash
# Create database tables
python manage.py migrate

# You should see:
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ... (many more lines)
```

✅ **Database is ready!**

---

### STEP 7: Collect Static Files (1 minute)

```bash
# Collect all CSS, JS, and image files
python manage.py collectstatic --noinput

# You should see:
# 150+ static files copied to '/home/yourusername/Contact-Management-System/staticfiles'
```

✅ **Static files collected!**

---

### STEP 8: Create Superuser (1 minute)

```bash
# Create an admin account for yourself
python manage.py createsuperuser

# It will ask you:
# Username: (type your username, e.g., admin)
# Email address: (type your email)
# Password: (type a password - you won't see it typing)
# Password (again): (type the same password)
```

✅ **Admin account created!**

---

### STEP 9: Set Up Web App (3 minutes)

1. **Go back to PythonAnywhere Dashboard**
   - Click **"Web"** tab at the top
   - Click **"Add a new web app"**

2. **Configuration Wizard:**
   - Click **"Next"** (accept free domain)
   - Your app URL will be: `http://yourusername.pythonanywhere.com`
   - Select **"Manual configuration"**
   - Select **"Python 3.10"**
   - Click **"Next"**

3. **You'll see the Web App configuration page**

✅ **Web app created!**

---

### STEP 10: Configure Virtual Environment (1 minute)

On the Web App configuration page:

1. Scroll down to **"Virtualenv"** section
2. In the **"Enter path to a virtualenv"** box, type:
   ```
   /home/yourusername/.virtualenvs/contactify
   ```
   ⚠️ **IMPORTANT:** Replace `yourusername` with your actual PythonAnywhere username!
   
3. Click the blue checkmark ✓

✅ **Virtual environment linked!**

---

### STEP 11: Configure WSGI File (2 minutes)

Still on the Web App configuration page:

1. Scroll down to **"Code"** section
2. Click on the **WSGI configuration file** link (it's blue)
   - Example: `/var/www/yourusername_pythonanywhere_com_wsgi.py`
3. A code editor will open

**Delete ALL the code** in that file and replace it with this:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/Contact-Management-System'
if path not in sys.path:
    sys.path.append(path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

⚠️ **IMPORTANT:** Replace `yourusername` with your actual PythonAnywhere username!

4. Click **"Save"** button at the top
5. Close the editor tab

✅ **WSGI configured!**

---

### STEP 12: Configure Static Files (2 minutes)

Back on the Web App configuration page:

1. Scroll down to **"Static files"** section
2. Click **"Enter URL"** and add two entries:

**First Entry (static files):**
- URL: `/static/`
- Directory: `/home/yourusername/Contact-Management-System/staticfiles/`

**Second Entry (media files):**
- URL: `/media/`
- Directory: `/home/yourusername/Contact-Management-System/media/`

⚠️ **IMPORTANT:** Replace `yourusername` with your actual PythonAnywhere username!

3. Click the green checkmarks ✓ for both

✅ **Static files configured!**

---

### STEP 13: Update Allowed Hosts (2 minutes)

1. Go back to the **Bash console**
2. Type:

```bash
# Edit settings file
nano ~/Contact-Management-System/project/settings.py
```

3. Find this line:
```python
ALLOWED_HOSTS = ['*']
```

4. Change it to:
```python
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com', 'localhost', '127.0.0.1']
```

⚠️ **IMPORTANT:** Replace `yourusername` with your actual PythonAnywhere username!

5. Save and exit:
   - Press `Ctrl + X`
   - Press `Y` (yes)
   - Press `Enter`

✅ **Security configured!**

---

### STEP 14: Reload Your Web App (1 minute)

1. Go back to the **"Web"** tab
2. At the top, there's a big green button: **"Reload yourusername.pythonanywhere.com"**
3. Click it!
4. Wait 5-10 seconds

✅ **App is deploying!**

---

### STEP 15: Test Your Live Website! 🎉

1. Click on the link: `http://yourusername.pythonanywhere.com`
2. Your website should load!
3. You should see your homepage

**Test these features:**
- ✅ Homepage loads
- ✅ Login page works
- ✅ Signup page works
- ✅ Create a test account
- ✅ Add a contact
- ✅ Upload profile picture
- ✅ Try all features!

---

## 🎊 CONGRATULATIONS! YOUR APP IS LIVE!

Your Contact Management System is now online at:
**`http://yourusername.pythonanywhere.com`**

---

## 🔧 Common Issues and Solutions

### Problem 1: "Something went wrong :("
**Solution:** 
1. Go to Web tab
2. Click "Log files" → "Error log"
3. Check what the error says
4. Usually it's a typo in the WSGI file or wrong path

### Problem 2: "Static files not loading (no CSS)"
**Solution:**
1. Check that static file paths are correct
2. Run `python manage.py collectstatic --noinput` again
3. Reload the web app

### Problem 3: "ImportError: No module named..."
**Solution:**
1. Go to Bash console
2. Activate virtual environment: `workon contactify`
3. Install missing package: `pip install package-name`
4. Reload web app

### Problem 4: "Forbidden (403)"
**Solution:**
- Check ALLOWED_HOSTS in settings.py
- Make sure it includes your PythonAnywhere URL

---

## 📱 Updating Your App Later

When you make changes and want to update your live site:

```bash
# 1. Go to Bash console
cd ~/Contact-Management-System

# 2. Pull latest changes from GitHub
git pull origin main

# 3. If you changed models, run migrations
python manage.py migrate

# 4. If you added static files
python manage.py collectstatic --noinput

# 5. Reload web app
# Go to Web tab and click "Reload"
```

---

## 🆘 Need Help?

- PythonAnywhere Help: https://help.pythonanywhere.com/
- PythonAnywhere Forums: https://www.pythonanywhere.com/forums/
- Django Documentation: https://docs.djangoproject.com/

---

## 🎯 What You've Accomplished

✅ Created a free hosting account  
✅ Deployed a full-featured Django application  
✅ Made your app accessible from anywhere in the world  
✅ Learned about web hosting and deployment  

**This is a huge achievement!** 🎉

Your Contact Management System is now:
- 🌐 Online 24/7
- 📱 Accessible from any device
- 🔒 Secure with Django's built-in security
- 🚀 Ready to share with friends and on your resume!

---

**Created by:** Kiro AI Assistant  
**For Project:** Contactify - Contact Management System  
**Deployment Date:** June 11, 2026

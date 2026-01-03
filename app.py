import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')

# Import Django and setup
import django
django.setup()

# Import the WSGI application
from clm_backend.wsgi import application

# Make the application available as 'app' for gunicorn
app = application
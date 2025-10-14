#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciphertalk.settings')
    
    # DEBUG: Check if we're running runserver command
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        print("🚀 Starting with ASGI WebSocket support...")
        # Ensure ASGI application is loaded
        from ciphertalk.asgi import application
        print("✅ ASGI application loaded successfully!")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
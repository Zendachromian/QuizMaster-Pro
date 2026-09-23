#!/usr/bin/env python
import os
from init_app import create_app
from tasks import make_celery

# Create Flask app and Celery instance
app = create_app()
celery = make_celery(app)

if __name__ == '__main__':
    with app.app_context():
        celery.start()
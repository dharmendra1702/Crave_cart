from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
import os


def create_admin(sender, **kwargs):
    if os.environ.get("CREATE_SUPERUSER") != "true":
        return

    User = get_user_model()

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            password=password,
            email=email
        )
        print("✅ Superuser created")
    else:
        print("ℹ️ Superuser already exists")

class DeliveryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'delivery'

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, **kwargs):

    if created:
        print(f"New user created: {instance.username}")

        # Example future use:
        # create calendar token space
        # create profile model
        # send onboarding email
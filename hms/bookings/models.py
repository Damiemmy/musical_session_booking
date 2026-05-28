from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class AvailabilitySlot(models.Model):

    producer= models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.producer.username} - {self.start_time}"


class Booking(models.Model):

    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.artist.username} booked {self.slot}"
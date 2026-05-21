from django import forms
from .models import AvailabilitySlot


class AvailabilitySlotForm(forms.ModelForm):

    class Meta:
        model = AvailabilitySlot

        fields = [
            "start_time",
            "end_time"
        ]

        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),

            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }
from django import forms
from .models import AvailabilitySlot


class AvailabilitySlotForm(forms.ModelForm):

    class Meta:
        model = AvailabilitySlot
        fields = ["start_time", "end_time"]

        widgets = {
            "start_time": forms.DateTimeInput(attrs={
                "type": "datetime-local",
                "class": "w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white focus:ring-2 focus:ring-purple-500 outline-none shadow-sm"
            }),

            "end_time": forms.DateTimeInput(attrs={
                "type": "datetime-local",
                "class": "w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white focus:ring-2 focus:ring-purple-500 outline-none shadow-sm"
            }),
        }
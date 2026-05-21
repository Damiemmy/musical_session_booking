from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import AvailabilitySlotForm
from .models import AvailabilitySlot

from accounts.decorators import doctor_required

from django.db import transaction
from django.utils import timezone
from .models import AvailabilitySlot, Booking
from django.contrib.auth import get_user_model
from accounts.decorators import patient_required

from accounts.utils import trigger_email


from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from allauth.socialaccount.models import SocialToken

User=get_user_model()


@login_required
@doctor_required
def create_slot_view(request):

    if request.method == "POST":

        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():

            slot = form.save(commit=False)

            slot.doctor = request.user

            slot.save()

            return redirect("doctor_slots")

    else:
        form = AvailabilitySlotForm()

    return render(request, "bookings/create_slot.html", {
        "form": form
    })


@login_required
@doctor_required
def doctor_slots_view(request):

    slots = AvailabilitySlot.objects.filter(
        doctor=request.user
    ).order_by("start_time")

    return render(request, "bookings/doctor_slots.html", {
        "slots": slots
    })


@login_required
@patient_required
def doctors_list_view(request):

    doctors = User.objects.filter(
        role="doctor"
    )

    return render(request, "bookings/doctors_list.html", {
        "doctors": doctors
    })


@login_required
@patient_required
def doctor_available_slots_view(request, doctor_id):

    doctor = User.objects.get(id=doctor_id)

    slots = AvailabilitySlot.objects.filter(
        doctor=doctor,
        is_booked=False,
        start_time__gt=timezone.now()
    ).order_by("start_time")

    return render(request, "bookings/available_slots.html", {
        "doctor": doctor,
        "slots": slots
    })


@login_required
@patient_required
@transaction.atomic
def book_slot_view(request, slot_id):

    slot = AvailabilitySlot.objects.select_for_update().get(
        id=slot_id
    )

    if slot.is_booked:

        return render(request, "bookings/booking_failed.html")

    slot.is_booked = True

    slot.save()

    Booking.objects.create(
        patient=request.user,
        slot=slot
    )

    trigger_email(
        trigger="BOOKING_CONFIRMATION",
        email=request.user.email,
        username=request.user.username
    )

    # create event for patient

    create_google_calendar_event(
        user=request.user,
        slot=slot,
        title=f"Appointment with Dr. {slot.doctor.username}"
    )

    # create event for doctor

    create_google_calendar_event(
        user=slot.doctor,
        slot=slot,
        title=f"Appointment with {request.user.username}"
    )

    return render(request, "bookings/booking_success.html", {
        "slot": slot
    })

def create_google_calendar_event(user, slot, title):

    social_token = SocialToken.objects.get(
        account__user=user,
        account__provider="google"
    )

    credentials = Credentials(
        token=social_token.token
    )

    service = build(
        "calendar",
        "v3",
        credentials=credentials
    )

    event = {
        "summary": title,

        "description": "Hospital Appointment",

        "start": {
            "dateTime": slot.start_time.isoformat(),
            "timeZone": "UTC",
        },

        "end": {
            "dateTime": slot.end_time.isoformat(),
            "timeZone": "UTC",
        },
    }

    service.events().insert(
        calendarId="primary",
        body=event
    ).execute()
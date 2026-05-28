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

from django.template.loader import render_to_string


from django.shortcuts import render, get_object_or_404, redirect

from accounts.utils import trigger_email
from django.core.mail import EmailMessage
from django.conf import settings


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

            slot.producer = request.user

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
        producer=request.user
    ).order_by("start_time")

    return render(request, "bookings/doctor_slots.html", {
        "slots": slots
    })


@login_required
@patient_required
def doctors_list_view(request):

    producer = User.objects.filter(
        role="producer"
    )

    return render(request, "bookings/doctors_list.html", {
        "producers": producer
    })


@login_required
@patient_required
def doctor_available_slots_view(request, producer_id):
    producer = User.objects.get(id=producer_id)
    slots = AvailabilitySlot.objects.filter(
        producer=producer,
        is_booked=False,
        start_time__gt=timezone.now()
    ).order_by("start_time")

    return render(request, "bookings/available_slots.html", {
        "producer": producer,
        "slots": slots
    })


@login_required
@patient_required
@transaction.atomic
def book_slot_view(request, slot_id):

    slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)

    # 1. prevent double booking
    if slot.is_booked:
        return render(request, "bookings/booking_failed.html")

    # 2. mark slot as booked
    slot.is_booked = True
    slot.save()

    # 3. ALWAYS create booking (core system)
    booking = Booking.objects.create(
        artist=request.user,
        slot=slot
    )

    # =========================
    # 🎧 ARTIST EMAIL (CONFIRMATION)
    # =========================
    try:
        artist_html = render_to_string("emails/artist_booking_confirmation.html", {
            "user": request.user,
            "slot": slot,
            "producer": slot.producer,
        })

        artist_email = EmailMessage(
            subject="🎧 Booking Confirmed - Johnsonix Studio",
            body=artist_html,
            from_email=settings.EMAIL_HOST_USER,
            to=[request.user.email],
        )
        artist_email.content_subtype = "html"
        artist_email.send(fail_silently=True)

    except Exception as e:
        print("Artist email failed:", e)

    # =========================
    # 🚨 PRODUCER EMAIL (NEW BOOKING ALERT)
    # =========================
    try:
        producer_html = render_to_string("emails/producer_new_booking.html", {
            "producer": slot.producer,
            "artist": request.user,
            "slot": slot,
        })

        producer_email = EmailMessage(
            subject="🚨 New Booking on Your Slot - Johnsonix",
            body=producer_html,
            from_email=settings.EMAIL_HOST_USER,
            to=[slot.producer.email],
        )
        producer_email.content_subtype = "html"
        producer_email.send(fail_silently=True)

    except Exception as e:
        print("Producer email failed:", e)

    # =========================
    # 📅 GOOGLE CALENDAR (ARTIST)
    # =========================
    try:
        create_google_calendar_event(
            user=request.user,
            slot=slot,
            title=f"Appointment with Prod. {slot.producer.username}"
        )
    except Exception as e:
        print("Artist calendar sync failed:", e)

    # =========================
    # 📅 GOOGLE CALENDAR (PRODUCER)
    # =========================
    try:
        create_google_calendar_event(
            user=slot.producer,
            slot=slot,
            title=f"Session with {request.user.username}"
        )
    except Exception as e:
        print("Producer calendar sync failed:", e)

    # 7. success response (booking is ALWAYS successful)
    return render(request, "bookings/booking_success.html", {
        "slot": slot
    })

@login_required
def edit_slot(request, slot_id):
    slot = AvailabilitySlot.objects.get(id=slot_id)

    if request.method == "POST":
        form = AvailabilitySlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            return redirect("doctor_slots")
    else:
        form = AvailabilitySlotForm(instance=slot)

    return render(request, "bookings/edit_slot.html", {"form": form})


@login_required
def delete_slot(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot, id=slot_id)

    # 🔒 only owner can delete
    if slot.producer != request.user:
        return redirect("doctor_slots")

    if request.method == "POST":
        slot.delete()
        return redirect("doctor_slots")

    return render(request, "bookings/delete_slot_confirm.html", {
        "slot": slot
    })



def create_google_calendar_event(user, slot, title):

    social_token = SocialToken.objects.filter(
        account__user=user,
        account__provider="google"
    ).first()
    print("TOKEN EXISTS:", bool(social_token))  # 👈 PART 3 DEBUG LINE

    # OPTION B: safe fallback
    if not social_token:
        print("Google Calendar not connected for user:", user.username)
        return  # IMPORTANT: do not crash

    credentials = Credentials(
        token=social_token.token
    )

    service = build("calendar", "v3", credentials=credentials)

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

@login_required
@patient_required
def my_bookings_view(request):

    bookings = Booking.objects.select_related(
        "slot",
        "slot__producer"
    ).filter(
        artist=request.user
    ).order_by("-id")

    return render(request, "bookings/my_bookings.html", {
        "bookings": bookings
    })
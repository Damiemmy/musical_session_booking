from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from .utils import trigger_email
from django.core.mail import EmailMessage
from django.conf import settings

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.contrib import messages

from django.utils.encoding import force_bytes, force_str
from bookings.models import AvailabilitySlot,Booking

User=get_user_model()

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()

            login_url = request.build_absolute_uri("/login/")

            # =========================
            # USER WELCOME EMAIL
            # =========================
            user_email_html = render_to_string("emails/signup_welcome.html", {
                "username": user.username,
                "login_url": login_url,
            })

            user_email = EmailMessage(
                subject="Welcome to Johnsonix 🎧",
                body=user_email_html,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )
            user_email.content_subtype = "html"
            user_email.send(fail_silently=False)

            # =========================
            # ADMIN NOTIFICATION EMAIL
            # =========================
            admin_email_html = render_to_string("emails/admin_new_user.html", {
                "username": user.username,
                "email": user.email,
            })

            admin_email = EmailMessage(
                subject="🚨 New User Registered - Johnsonix",
                body=admin_email_html,
                from_email=settings.EMAIL_HOST_USER,
                to=["damisaemmanuel778@gmail.com"],
            )
            admin_email.content_subtype = "html"
            admin_email.send(fail_silently=False)

            return redirect("login")

    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})

    
@login_required
def dashboard_view(request):

    if request.user.role == "producer":
        user = request.user

        booked_by_users = AvailabilitySlot.objects.filter(
            producer=user,
            is_booked=True
        ).count()
        available_for_users = AvailabilitySlot.objects.filter(
            producer=user,
            is_booked=False
        ).count()

        return render(request, "accounts/doctor_dashboard.html",{'booked_by_users': booked_by_users,'available_for_users':available_for_users})
        
    user = request.user
    booked_by_users = Booking.objects.filter(
        artist=user
    ).count()
    
    return render(request, "accounts/patient_dashboard.html",{'booked_by_users': booked_by_users})







# =========================
# FORGOT PASSWORD VIEW
# =========================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal user existence (security best practice)
            return redirect("password_reset_sent")

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = request.build_absolute_uri(
            f"/reset-password/{uid}/{token}/"
        )

        # Render HTML email
        subject = "Johnsonix Password Reset 🎧"
        html_message = render_to_string("emails/password_reset_email.html", {
            "user": user,
            "reset_link": reset_link,
        })

        email_message = EmailMessage(
            subject=subject,
            body=html_message,
            to=[user.email],
        )
        email_message.content_subtype = "html"
        email_message.send()

        return redirect("password_reset_sent")

    return render(request, "accounts/forgot_password.html")


# =========================
# PASSWORD RESET SENT PAGE
# =========================
def password_reset_sent(request):
    return render(request, "accounts/password_reset_sent.html")


# =========================
# RESET PASSWORD VIEW
# =========================
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired reset link.")
        return redirect("forgot_password")

    if request.method == "POST":
        password1 = request.POST.get("new_password1")
        password2 = request.POST.get("new_password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/reset_password.html")

        user.set_password(password1)
        user.save()

        messages.success(request, "Password reset successful. You can now log in.")
        return redirect("login")

    return render(request, "accounts/reset_password.html")




# def signup_view(request):

#     if request.method == "POST":
#         form = SignupForm(request.POST)

#         if form.is_valid():
#             user = form.save()
#             trigger_email(
#                 trigger="SIGNUP_WELCOME",
#                 email=user.email,
#                 username=user.username
#             )
#             login(request, user,backend='django.contrib.auth.backends.ModelBackend')

#             return redirect("dashboard")

#     else:
#         form = SignupForm()

#     return render(request, "accounts/signup.html", {
#         "form": form
#     })
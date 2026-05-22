from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from .utils import trigger_email



def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()

            trigger_email(
                trigger="SIGNUP_WELCOME",
                email=user.email,
                username=user.username
            )

            return redirect("login")  # or dashboard after login

    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})

    
@login_required
def dashboard_view(request):

    if request.user.role == "doctor":
        return render(request, "accounts/doctor_dashboard.html")

    return render(request, "accounts/patient_dashboard.html")




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
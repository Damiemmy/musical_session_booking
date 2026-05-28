from django.shortcuts import redirect


def doctor_required(view_func):

    def wrapper(request, *args, **kwargs):

        if request.user.role != "producer":
            return redirect("dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper

def patient_required(view_func):

    def wrapper(request, *args, **kwargs):

        if request.user.role != "artist":
            return redirect("dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper
from django.urls import path
from .views import (
    create_slot_view,
    doctor_slots_view
)
from .views import (
    create_slot_view,
    doctor_slots_view,
    doctors_list_view,
    doctor_available_slots_view,
    book_slot_view,
    edit_slot,
    delete_slot,
    my_bookings_view,
)


urlpatterns = [
    path("create-slot/",create_slot_view,name="create_slot"),
    path("my-slots/",doctor_slots_view,name="doctor_slots"),
    path("doctors/",doctors_list_view,name="doctors_list"),
    path("doctor/<int:producer_id>/slots/",doctor_available_slots_view,name="doctor_slots_available"),
    path("book/<int:slot_id>/",book_slot_view,name="book_slot"),
    path("slot/edit/<int:slot_id>/",edit_slot, name="edit_slot"),
    path("slot/delete/<int:slot_id>/", delete_slot, name="delete_slot"),
    path("my-bookings/",my_bookings_view, name="my_bookings"),
    
]
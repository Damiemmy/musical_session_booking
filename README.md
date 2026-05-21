# Mini Hospital Management System (HMS)

## Setup and Run

### Clone Repository

```bash
git clone <repo-url>
cd hms-project
```

### Backend Setup

```bash
cd hms

python3 -m venv env

source env/bin/activate

pip install -r ../requirements.txt
```

### Database Setup

Update PostgreSQL credentials inside settings.py.

Run migrations:

```bash
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

Run Django server:

```bash
python manage.py runserver
```

### Serverless Email Service

```bash
cd email-service

npm install

serverless offline
```

Serverless service runs locally at:

```text
http://localhost:3000
```

---

## System Architecture

The project consists of two systems:

1. Django Hospital Management System backend
2. Python serverless email notification service

### Django Backend

The Django application handles:

- Authentication
- Doctor and patient role management
- Doctor availability slot management
- Appointment booking
- Google OAuth login
- Google Calendar event creation

### Role-Based Access

A custom User model with a role field was used:

- doctor
- patient

Custom decorators restrict access to doctor-only and patient-only views.

### Booking and Race Condition Handling

To prevent double booking:

- transaction.atomic
- select_for_update()

were used during booking.

This locks the selected slot row during booking and prevents simultaneous booking requests.

A OneToOneField between Booking and AvailabilitySlot was also used as an additional database-level protection.

### Google Calendar Integration

Google OAuth was implemented using django-allauth.

When a booking is confirmed:
- an event is created in the patient’s Google Calendar
- an event is created in the doctor’s Google Calendar

### Serverless Email Service

The email notification service runs separately using:
- Serverless Framework
- serverless-offline

Django communicates with the service through HTTP requests.

Supported triggers:
- SIGNUP_WELCOME
- BOOKING_CONFIRMATION

---

## The Design Decision

One major design decision was how to handle appointment slot booking safely under concurrent requests.

### Problem

Two patients could attempt to book the same appointment slot simultaneously.

### Option 1

Use a normal check:

```python
if not slot.is_booked:
```

This approach is simple but unsafe because two requests could read the slot before either request updates it.

### Option 2 (Chosen)

Use:
- transaction.atomic
- select_for_update()

This locks the selected database row during the transaction.

### Why I Chose This

I chose database-level locking because consistency was more important than simplicity in the booking flow.

This prevents concurrent requests from booking the same slot and keeps the system reliable.

---

## Limitations

This project was designed for local demonstration purposes and not production deployment.

Current limitations include:

- Limited OAuth token refresh handling
- No asynchronous task queue
- Minimal UI styling
- No Docker/containerization
- Limited automated testing
- Local-only serverless configuration

If productionizing the system, the first improvement would be implementing asynchronous background task processing using Celery and Redis.
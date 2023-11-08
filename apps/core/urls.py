from django.urls import path

from . import views

urlpatterns = [
    path("doctor/", views.DoctorSignUpView.as_view(), name="create-doctor"),
    path("patient/", views.CreatePatient.as_view(), name="create-patient"),
    path("patient/appointment/", views.PatientBookAppointmentView.as_view(), name="patient-book-appointment"),
    path("patient/appointment/", views.PatientAppointmentListView.as_view(), name="patient-appointment-list"),
    path("doctor/appointment/", views.DoctorAppointmentListView.as_view(), name="doctor-appointment-list"),
    path("doctor/login", views.LoginDoctorView.as_view(), name="login_doctor")
]

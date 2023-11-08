from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Doctor, Patient, Appointment
from .serializers import AppointmentSerializer


# Create doctor

class DoctorSignUpView(APIView):

    def post(self, request):
        data = request.data

        username = data["username"]
        email = data["email"]

        password1 = data["password1"]
        password2 = data["password2"]

        full_name = data["full_name"]

        if password1 != password2:
            return Response({"message": "passwords did not match"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=username).first()

        if user is not None:
            return Response({"message": "a user with this username already exists"})

        user = User.objects.create_user(username=username, email=email, password=password1)

        doctor = Doctor.objects.create(user=user, full_name=full_name)

        doctor.save()

        token = Token.objects.create(user=user)

        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class LoginDoctorView(APIView):

    def post(self, request):
        data = request.data
        username = data["username"]
        password = data["password"]

        user = authenticate(username=username, password=password)

        if user:
            doctor = Doctor.objects.filter(user=user).first()
            if len(doctor) != 0:
                token = Token.objects.get_or_create(user=user)
                return Response({"token": token}, status=status.HTTP_200_OK)

            return Response({"message": "invalid user credentials"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "invalid user credentials"}, status=status.HTTP_400_BAD_REQUEST)


class CreatePatient(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        username = data["username"]
        email = data["email"]

        password1 = data["password1"]
        password2 = data["password2"]

        full_name = data["full_name"]

        if password1 != password2:
            return Response({"message": "passwords did not match"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(username=username)

        if user is not None:
            return Response({"message": "a user with this username already exists"})

        user = User.objects.create_user(username=username, email=email, password=password1)

        patient = Patient.objects.create(user=user, full_name=full_name)

        patient.save()

        token = Token.objects.create(user=user)

        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class PatientBookAppointmentView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        doctor_id = data["doctor"]
        appointment_time = data["appointment_time"]

        # make sure the user is a patient
        user = request.user
        patient = Patient.objects.get(user=user)

        if patient is None:
            return Response({"message": "only authenticated patients can book appointments"},
                            status=status.HTTP_403_FORBIDDEN)

        # check that doctor is available at said time
        appointment_time_in_date_time = datetime.strptime(appointment_time, '%H:%M:%S').time()

        # filter available appointments for said time

        l = Appointment.objects.filter(appointment_time=appointment_time_in_date_time, doctor__pk=doctor_id)

        if len(l) != 0:
            return Response({"message": "This doctor is already booked at this time"},
                            status=status.HTTP_400_BAD_REQUEST)

        appointment = Appointment.objects.create(doctor=doctor_id, patient=patient,
                                                 appointment_time=appointment_time_in_date_time)

        appointment_serializer = AppointmentSerializer(appointment)

        return Response(appointment_serializer.data, status=status.HTTP_201_CREATED)


class DoctorAppointmentListView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        doctor = Doctor.objects.get(user=user)
        queryset = Appointment.objects.filter(doctor=doctor)

        return queryset


class PatientAppointmentListView(ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        patient = Patient.objects.get(user=user)
        queryset = Appointment.objects.filter(doctor=patient)
        return queryset

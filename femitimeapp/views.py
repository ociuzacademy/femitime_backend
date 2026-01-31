from urllib import response
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer

class LoginView(APIView):
    """
    Login endpoint for:
    - Hospital Doctor
    - Normal User 
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        

        # --- Hospital Doctor Login ---
        hospital_doc = tbl_hospital_doctor_register.objects.filter(email=email, password=password).first()
        if hospital_doc:
            if hospital_doc.status != 'approved':
                return Response(
                    {'message': 'Hospital doctor account not approved yet. Please wait for admin approval.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response({
                'id': hospital_doc.id,
                'name': hospital_doc.name,
                'email': hospital_doc.email,
                'phone': hospital_doc.hospital_phone,
                'role': hospital_doc.role,
                'password': hospital_doc.password,
            }, status=status.HTTP_200_OK)

        # --- Normal User Login ---
        user = Register.objects.filter(email=email, password=password).first()
        if user:
            return Response({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'password': user.password,
                'phone':user.phone,
                'role': user.role
            }, status=status.HTTP_200_OK)

        # --- Invalid Credentials ---
        return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


#  Hospital Doctor ViewSet
class HospitalDoctorRegisterViewSet(viewsets.ModelViewSet):
    queryset = tbl_hospital_doctor_register.objects.all()
    serializer_class = HospitalDoctorRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    

import google.generativeai as genai
import os
from dotenv import load_dotenv
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import google.generativeai as genai
import os
from dotenv import load_dotenv
from django.conf import settings

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env file")

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Create model instance
gemini_model = genai.GenerativeModel('gemini-2.5-flash')


# PCOD-related keywords (for filtering)
PCOD_KEYWORDS = [
    "pcod", "pcos", "ovarian cyst", "cysts", "hormonal imbalance",
    "irregular periods", "missed period", "period delay", "fertility",
    "infertility", "ovulation", "insulin resistance", "testosterone",
    "estrogen", "weight gain", "acne", "hair loss", "hair growth",
    "belly fat", "obesity", "thyroid", "metformin", "follicles",
    "ultrasound", "polycystic", "cycle", "pimples", "skin darkening",
    "pelvic pain", "pcod symptoms", "pcod treatment", "pcod cure",
    "exercise", "diet", "nutrition", "healthy food"
]

# Greeting keywords
GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]


class PCODChatbotAPIView(APIView):
    def post(self, request):
        user_message = request.data.get("message", "").lower().strip()

        if not user_message:
            return Response({
                "type": "error",
                "reply": "Message is empty"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Greeting check
        if any(greet in user_message for greet in GREETINGS):
            return Response({
                "type": "greeting",
                "reply": "Hello! 😊 I'm PCO-Assist, your PCOD health companion. Ask me anything about PCOD symptoms, diet, treatment, or recovery."
            })

        # Check PCOD relevance
        if not any(keyword in user_message for keyword in PCOD_KEYWORDS):
            return Response({
                "type": "not_related",
                "reply": "I can only answer questions related to PCOD/PCOS, hormonal imbalance, symptoms, treatment, or lifestyle tips."
            })

        try:
            # Focus Gemini on PCOD-only conversation
            response = gemini_model.generate_content(
                f"You are a women's health assistant specialized in PCOD/PCOS. "
                f"Give medical-safe, supportive, simple replies. "
                f"Do NOT answer outside PCOD. User asked: {user_message}"
            )
            return Response({
                "type": "pcod_info",
                "reply": response.text
            })
        
            
        except Exception as e:
            return Response({
                "type": "error",
                "reply": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






# from .models import Register, TblPredictionResult
# from .ml_assets.ml_utils import (
#     encode_blood_group,
#     map_cycle,
#     map_fast_food,
#     map_severity,
#     prepare_final_df,
#     extract_medical_values,
#     scaler,
#     model
# )


# class PCODPredictionAPI(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request):
#         try:
#             # -------------------------
#             # Validate User
#             # -------------------------
#             user_id = request.data.get("user_id")
#             user = Register.objects.get(id=user_id)

#             # -------------------------
#             # User Inputs (Strings)
#             # -------------------------
#             age = float(request.data.get("age"))
#             weight = float(request.data.get("weight"))
#             height = float(request.data.get("height"))
#             bmi = float(request.data.get("bmi"))

#             fast_food = request.data.get("fast_food")            # Never
#             blood_group = request.data.get("blood_group")        # O+
#             pulse = float(request.data.get("pulse"))             # 78
#             cycle = request.data.get("cycle")                    # Regular
#             mood = request.data.get("mood_swings")
#             skin = request.data.get("skin_darkening")
#             hair = request.data.get("hair")
#             acne = request.data.get("acne")
#                     # Mild

#             # -------------------------
#             # Convert Strings → ML Values
#             # -------------------------
#             user_input = {
#                 "Age": age,
#                 "Weight": weight,
#                 "Height": height,
#                 "BMI": bmi,
#                 "Fast_Food_Consumption": map_fast_food(fast_food),
#                 "Blood_Group": encode_blood_group(blood_group),
#                 "Pulse_Rate": pulse,
#                 "Cycle_Regularity": map_cycle(cycle),
#                 "Hair_Growth": map_severity(hair),
#                 "Acne": map_severity(acne),
#                 "Mood_Swings": map_severity(mood),
#                 "Skin_Darkening": map_severity(skin)
#             }

#             # -------------------------
#             # Save PDF + User Inputs
#             # -------------------------
#             pdf_file = request.FILES["pdf"]

#             saved_obj = TblPredictionResult.objects.create(
#                 user=user,
#                 age=age,
#                 weight=weight,
#                 height=height,
#                 bmi=bmi,
#                 fast_food_consumption=fast_food,
#                 blood_group=blood_group,
#                 pulse_rate=pulse,
#                 cycle_regularity=cycle,
#                 hair_growth=hair,
#                 acne=acne,
#                 mood_swings=mood,
#                 skin_darkening=skin,
#                 pdf_file=pdf_file
#             )

#             # -------------------------
#             # Extract PDF Medical Values
#             # -------------------------
#             pdf_values = extract_medical_values(saved_obj.pdf_file.path)

#             # -------------------------
#             # Prepare ML Input
#             # -------------------------
#             df = prepare_final_df(user_input, pdf_values)
#             df_scaled = scaler.transform(df)
#             prediction = model.predict(df_scaled)[0]

#             mapping = {0: "Likely", 1: "Unlikely", 2: "Highly Risk"}
#             result_label = mapping[int(prediction)]

#             # -------------------------
#             # Save Backend Result
#             # -------------------------
#             saved_obj.result = result_label
#             saved_obj.extracted_data = pdf_values
#             saved_obj.save()

#             # -------------------------
#             # API Success Response
#             # -------------------------
#             return Response({
#                 "status": "success",
#                 "user_id": user.id,
#                 "user_name": user.name,
#                 "result": result_label,
#                 "extracted_pdf_values": pdf_values,
#                 "prediction_id": saved_obj.id,
#                 "age": age,
#                 "weight": weight,
#                 "height": height,
#                 "bmi": bmi,
#                 "fast_food_consumption": fast_food,
#                 "blood_group": blood_group,
#                 "pulse_rate": pulse,
#                 "cycle_regularity": cycle,
#                 "hair_growth": hair,
#                 "acne": acne,
#                 "mood_swings": mood,
#                 "skin_darkening": skin
#             })

#         except Exception as e:
#             return Response({"error": str(e)}, status=400)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import Register, TblPredictionResult
from femitimeapp.ml_assets.ml_utils import (
    model, scaler, pcod_label_encoder,
    map_fast_food, encode_blood_group,
    map_cycle, map_severity,
    extract_medical_values, prepare_final_df
)


class PCODPredictionAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            user = Register.objects.get(id=request.data.get("user_id"))

            # -----------------------------
            # BASIC INPUTS
            # -----------------------------
            age = float(request.data.get("age"))
            weight = float(request.data.get("weight"))
            height = float(request.data.get("height"))
            bmi = float(request.data.get("bmi"))

            fast_food = request.data.get("fast_food")
            blood_group = request.data.get("blood_group")
            cycle = request.data.get("cycle")

            hair = request.data.get("hair")
            acne = request.data.get("acne")
            mood = request.data.get("mood_swings")
            skin = request.data.get("skin_darkening")

            # -----------------------------
            # ML INPUT
            # -----------------------------
            user_input = {
                "Age": age,
                "Weight": weight,
                "Height": height,
                "BMI": bmi,
                "Fast_Food_Consumption": map_fast_food(fast_food),
                "Blood_Group": encode_blood_group(blood_group),
                "Cycle_Regularity": map_cycle(cycle),
                "Hair_Growth": map_severity(hair),
                "Acne": map_severity(acne),
                "Mood_Swings": map_severity(mood),
                "Skin_Darkening": map_severity(skin),
            }

            # -----------------------------
            # SAVE INPUT + PDF
            # -----------------------------
            pdf_file = request.FILES["pdf"]

            saved_obj = TblPredictionResult.objects.create(
                user=user,
                age=age,
                weight=weight,
                height=height,
                bmi=bmi,
                fast_food_consumption=fast_food,
                blood_group=blood_group,
                cycle_regularity=cycle,
                hair_growth=hair,
                acne=acne,
                mood_swings=mood,
                skin_darkening=skin,
                pdf_file=pdf_file
            )

            # -----------------------------
            # PDF EXTRACTION
            # -----------------------------
            pdf_values = extract_medical_values(saved_obj.pdf_file.path)

            # -----------------------------
            # PREPARE + SCALE
            # -----------------------------
            df = prepare_final_df(user_input, pdf_values)
            df_scaled = scaler.transform(df)

            # -----------------------------
            # PROBABILITY-BASED PREDICTION
            # -----------------------------
            proba = model.predict_proba(df_scaled)[0]
            classes = pcod_label_encoder.classes_
            prob_map = dict(zip(classes, proba))

            if prob_map.get("High Risk", 0) >= 0.6:
                result_label = "High Risk"
            elif prob_map.get("Likely", 0) >= 0.12:
                result_label = "Likely"
            else:
                result_label = "Unlikely"

            # -----------------------------
            # SAVE RESULT
            # -----------------------------
            saved_obj.result = result_label
            saved_obj.extracted_data = {
                "pdf_values": pdf_values,
                "probabilities": prob_map
            }
            saved_obj.save()

            return Response({
                "status": "success",
                "message": "PCOD prediction generated successfully",
                "prediction_id": saved_obj.id,
                "result": result_label,
                "probabilities": prob_map,
                "user_inputs": user_input,
                "extracted_pdf_values": pdf_values
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

from adminapp.models import Book
from femitimeapp.serializers import BookSerializer
class UserViewBook(APIView):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import HospitalBooking
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import HospitalBooking, Register


class UserCancelBookingAPI(APIView):
    def post(self, request, booking_id, user_id):
        try:
            booking = HospitalBooking.objects.get(id=booking_id)
            user = Register.objects.get(id=user_id)

            # 🔒 Ensure booking belongs to this user
            if booking.user != user:
                return Response(
                    {"error": "You are not authorized to cancel this booking"},
                    status=status.HTTP_403_FORBIDDEN
                )

            if booking.status.startswith("cancelled"):
                return Response(
                    {"message": "Booking already cancelled"},
                    status=status.HTTP_200_OK
                )

            booking.status = "cancelled_by_user"
            booking.is_booked = False
            booking.save()

            return Response({
                "status": "success",
                "message": "Booking cancelled by user",
                "booking_id": booking.id,
                "date": booking.date,
                "time": booking.time
            }, status=status.HTTP_200_OK)

        except HospitalBooking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Register.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )







#Doctor


@api_view(['GET'])
def view_hospital_doctor_profile(request, doctor_id):
    try:
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
    except tbl_hospital_doctor_register.DoesNotExist:
        return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = HospitalDoctorRegisterSerializer(doctor)
    return Response(serializer.data, status=status.HTTP_200_OK)




class HospitalDoctorProfileViewSet(viewsets.ViewSet):
    """
    A ViewSet for updating hospital doctor profiles (partial or full updates).
    """

    def partial_update(self, request, pk=None):
        try:
            doctor = tbl_hospital_doctor_register.objects.get(pk=pk)
        except tbl_hospital_doctor_register.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HospitalDoctorProfileUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework import viewsets
from .models import HospitalDoctorTimeSlotGroup
from .serializers import HospitalDoctorTimeSlotGroupSerializer

class HospitalDoctorTimeSlotGroupViewSet(viewsets.ModelViewSet):
    queryset = HospitalDoctorTimeSlotGroup.objects.all().order_by('-date')
    serializer_class = HospitalDoctorTimeSlotGroupSerializer







# ✅ View all available hospital doctor time slots
@api_view(['GET'])
def view_hospital_doctor_timeslots(request, doctor_id):
    """
    Get all time slot groups for a hospital doctor with booking info.
    """
    try:
        groups = HospitalDoctorTimeSlotGroup.objects.filter(doctor_id=doctor_id).order_by('date')

        if not groups.exists():
            return Response({"message": "No time slots found for this doctor."}, status=status.HTTP_404_NOT_FOUND)

        result = []
        for group in groups:
            # ✅ Already booked times for that date
            booked_times = list(
                HospitalBooking.objects.filter(
                    doctor_id=doctor_id,
                    date=group.date
                ).values_list('time', flat=True)
            )

            # Normalize booked times (e.g. "10:00:00" → "10:00")
            booked_times = [t[:5] for t in booked_times]

            result.append({
                "id": group.id,
                "doctor": group.doctor.id,
                "doctor_name": group.doctor.name,
                "date": group.date,
                "start_time": group.start_time.strftime("%H:%M:%S"),
                "end_time": group.end_time.strftime("%H:%M:%S"),
                "timeslots": [
                    {"time": t, "is_booked": t in booked_times}
                    for t in group.timeslots
                ],
            })

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







@api_view(['POST'])
def update_hospital_doctor_availability(request, doctor_id):
    try:
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
    except tbl_hospital_doctor_register.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
    
    available = request.data.get('available')

    if available is None:
        return Response({"error": "Availability value required (true/false)"}, status=status.HTTP_400_BAD_REQUEST)

    # Convert to boolean
    if isinstance(available, str):
        available = available.lower() in ['true', '1', 'yes']

    doctor.available = available
    doctor.save()

    return Response({
        "message": "Availability updated successfully",
        "doctor_id": doctor.id,
        "available": doctor.available
    }, status=status.HTTP_200_OK)




@api_view(['GET'])
def view_nearby_hospital_doctors(request, user_id):
    """
    Get all approved and available hospital doctors 
    who are in the same place as the user.
    """
    try:
        user = Register.objects.get(id=user_id)
    except Register.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if not user.place:
        return Response({"error": "User place not available"}, status=400)

    # ✅ Only approved & available doctors in the same place
    doctors = tbl_hospital_doctor_register.objects.filter(
        status='approved', available=True, place__iexact=user.place
    )

    if not doctors.exists():
        return Response({"message": "No nearby hospital doctors found in your area."}, status=200)

    nearby_doctors = []
    for doctor in doctors:
        nearby_doctors.append({
            "id": doctor.id,
            "name": doctor.name,
            "qualification": doctor.qualification,
            "specialization": doctor.specialization,
            "experience": doctor.experience,
            "phone": doctor.hospital_phone,
            "hospital_name": doctor.hospital_name,
            "hospital_address": doctor.hospital_address,
            "place": doctor.place,
            "available": doctor.available,
            "image": doctor.image.url if doctor.image else None,
            "status": doctor.status,
        })

    return Response({"nearby_hospital_doctors": nearby_doctors})




# ✅ Book a hospital doctor time slot (same logic as clinic)
@api_view(['POST'])
def book_hospital_doctor_slot(request):
    """
    Book a specific time slot for a hospital doctor.

    Expected JSON:
    {
        "user": 1,
        "doctor": 3,
        "timeslot_group": 5,
        "date": "2025-11-01",
        "time": "09:30"
    }
    """
    data = request.data

    try:
        user = Register.objects.get(id=data['user'])
        doctor = tbl_hospital_doctor_register.objects.get(id=data['doctor'])
        timeslot_group = HospitalDoctorTimeSlotGroup.objects.get(id=data['timeslot_group'])
    except (Register.DoesNotExist, tbl_hospital_doctor_register.DoesNotExist, HospitalDoctorTimeSlotGroup.DoesNotExist):
        return Response({"error": "Invalid doctor, user, or timeslot group."}, status=404)

    # ✅ Check if time is in available slots
    timeslots = timeslot_group.timeslots
    if data['time'] not in timeslots:
        return Response({"error": "Invalid time slot."}, status=400)

    # ✅ Check if already booked
    if HospitalBooking.objects.filter(
        doctor=doctor,
        date=data['date'],
        time=data['time'],
        is_booked=True
    ).exists():
        return Response({"error": "This time slot is already booked."}, status=400)

    # ✅ Create booking
    booking = HospitalBooking.objects.create(
        user=user,
        doctor=doctor,
        timeslot_group=timeslot_group,
        date=data['date'],
        time=data['time'],
        is_booked=True
    )

    return Response({
        "message": "Slot booked successfully!",
        "booking_id": booking.id,
        "doctor": doctor.name,
        "date": data['date'],
        "time": data['time']
    }, status=201)



# 🧠 User Adds Feedback
@api_view(['POST'])
def add_hospital_doctor_feedback(request):
    user_id = request.data.get('user')
    doctor_id = request.data.get('doctor')
    rating = request.data.get('rating')
    comments = request.data.get('comments', '')

    try:
        user = Register.objects.get(id=user_id)
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
    except (Register.DoesNotExist, tbl_hospital_doctor_register.DoesNotExist):
        return Response({'error': 'Invalid user or doctor ID'}, status=status.HTTP_404_NOT_FOUND)

    feedback = HospitalDoctorFeedback.objects.create(
        user=user, doctor=doctor, rating=rating, comments=comments
    )
    serializer = HospitalDoctorFeedbackSerializer(feedback)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 🧠 Doctor Views Feedback
@api_view(['GET'])
def view_hospital_doctor_feedback(request, doctor_id):
    feedbacks = HospitalDoctorFeedback.objects.filter(doctor_id=doctor_id).order_by('-created_at')
    serializer = HospitalDoctorFeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import HospitalDoctorFeedback
from .serializers import HospitalDoctorFeedbackSerializer


class GetDoctorFeedbackAPI(APIView):
    def get(self, request, doctor_id):
        try:
            feedbacks = HospitalDoctorFeedback.objects.filter(doctor_id=doctor_id)

            if not feedbacks.exists():
                return Response({"message": "No feedback found for this doctor."}, status=404)

            serializer = HospitalDoctorFeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)




from rest_framework import viewsets
from .models import CycleInput
from .serializers import CycleInputSerializer

class CycleInputViewSet(viewsets.ModelViewSet):
    queryset = CycleInput.objects.all()
    serializer_class = CycleInputSerializer



class user_view_booking_hospital(APIView):
    def get(self, request, user_id):
        bookings = HospitalBooking.objects.filter(user_id=user_id)
        data = []
        for booking in bookings:
            data.append({
                "id": booking.id,
                "doctor": booking.doctor.id if booking.doctor else None,
                "doctor_name": booking.doctor.name if booking.doctor else "Doctor removed",
                "patient": booking.user.id,
                "patient_name": booking.user.name if booking.user else "User removed",
                "date": booking.date,
                "time": booking.time,
                "place": booking.doctor.place if booking.doctor else None,
                "hospital_name": booking.doctor.hospital_name if booking.doctor else None,
                # "booked_at": getattr(booking, 'created_at', None),
            })
        return Response(data, status=status.HTTP_200_OK)


class doctor_view_booking_hospital(APIView):
    def get(self, request, doctor_id):
        bookings = HospitalBooking.objects.filter(doctor_id=doctor_id)
        data = []
        for booking in bookings:
            data.append({
                "id": booking.id,
                "user": booking.user.id,
                "user_name": booking.user.name,
                "date": booking.date,
                "time": booking.time,
                "status": booking.status,
                # "booked_at": booking.created_at,
            })
        return Response(data, status=status.HTTP_200_OK)
    



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CycleInput
from .serializers import CycleInputSerializer


class GetCycleInputsByUser(APIView):
    def get(self, request, user_id):
        try:
            cycle_inputs = CycleInput.objects.filter(user_id=user_id).order_by('-created_at')

            if not cycle_inputs.exists():
                return Response(
                    {"message": "No cycle data found for this user."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CycleInputSerializer(cycle_inputs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class ViewPredictionResultsByUser(APIView):
    def get(self, request, user_id):
        try:
            results = TblPredictionResult.objects.filter(user_id=user_id).order_by('-created_at')

            if not results.exists():
                return Response(
                    {"message": "No prediction results found for this user."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = PredictionSerializer(results, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import HospitalBooking, tbl_hospital_doctor_register
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import HospitalBooking, tbl_hospital_doctor_register


class DoctorCancelBookingAPI(APIView):
    def post(self, request, booking_id, doctor_id):
        try:
            booking = HospitalBooking.objects.get(id=booking_id)
            doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)

            # 🔒 Ensure only assigned doctor can cancel
            if booking.doctor != doctor:
                return Response(
                    {"error": "You are not authorized to cancel this booking"},
                    status=status.HTTP_403_FORBIDDEN
                )

            if booking.status.startswith("cancelled"):
                return Response(
                    {"message": "Booking already cancelled"},
                    status=status.HTTP_200_OK
                )

            booking.status = "cancelled_by_doctor"
            booking.is_booked = False
            booking.save()

            return Response({
                "status": "success",
                "message": "Booking cancelled by doctor",
                "booking_id": booking.id,
                "patient_name": booking.user.name,
                "date": booking.date,
                "time": booking.time
            }, status=status.HTTP_200_OK)

        except HospitalBooking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except tbl_hospital_doctor_register.DoesNotExist:
            return Response(
                {"error": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND
            )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import HospitalBooking, Register


class UserDoctorCancelledBookingsAPI(APIView):
    def get(self, request, user_id):
        try:
            user = Register.objects.get(id=user_id)

            bookings = HospitalBooking.objects.filter(
                user=user,
                status="cancelled_by_doctor"
            ).select_related("doctor", "timeslot_group")

            if not bookings.exists():
                return Response({
                    "status": "success",
                    "message": "No doctor-cancelled bookings found",
                    "data": []
                }, status=status.HTTP_200_OK)

            data = []
            for booking in bookings:
                data.append({
                    "booking_id": booking.id,
                    "doctor_name": booking.doctor.name if booking.doctor else None,
                    "date": booking.date,
                    "time": booking.time,
                    "status": booking.status,
                    "is_booked": booking.is_booked
                })

            return Response({
                "status": "success",
                "user_id": user.id,
                "user_name": user.name,
                "doctor_cancelled_bookings": data
            }, status=status.HTTP_200_OK)

        except Register.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import HospitalBooking, tbl_hospital_doctor_register


class DoctorCompleteBookingAPI(APIView):
    def post(self, request, booking_id, doctor_id):
        try:
            booking = HospitalBooking.objects.get(id=booking_id)
            doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)

            #  Only assigned doctor can complete
            if booking.doctor != doctor:
                return Response(
                    {"error": "You are not authorized to complete this booking"},
                    status=status.HTTP_403_FORBIDDEN
                )

            #  Cannot complete cancelled bookings
            if booking.status.startswith("cancelled"):
                return Response(
                    {"error": "Cancelled booking cannot be completed"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Already completed
            if booking.status == "completed":
                return Response(
                    {"message": "Booking already completed"},
                    status=status.HTTP_200_OK
                )

            #  Mark as completed
            booking.status = "completed"
            booking.is_booked = False
            booking.save()

            return Response({
                "status": "success",
                "message": "Booking marked as completed",
                "booking_id": booking.id,
                "patient_name": booking.user.name,
                "date": booking.date,
                "time": booking.time
            }, status=status.HTTP_200_OK)

        except HospitalBooking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except tbl_hospital_doctor_register.DoesNotExist:
            return Response(
                {"error": "Doctor not found"},
                status=status.HTTP_404_NOT_FOUND
            )

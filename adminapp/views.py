from django.shortcuts import get_object_or_404, render

# Create your views here.

from django.shortcuts import render, redirect
from django.http import HttpResponse

from femitimeapp.models import Register
from .models import Admin

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            admin = Admin.objects.get(username=username, password=password)
            # Store admin in session
            request.session["admin_id"] = admin.id
            request.session["admin_username"] = admin.username
            return redirect("index")  # redirect after login
        except Admin.DoesNotExist:
            return render(request, "login.html", {"error": "Invalid email or password"})

    return render(request, "login.html")

def index(request):
    return render(request, "index.html")

def view_users(request):
    users = Register.objects.all()
    return render(request, 'view_users.html', {'users': users})

def delete_user(request, user_id):
    user = get_object_or_404(Register, id=user_id)
    user.delete()
    return redirect('view_users')



from django.shortcuts import render
from femitimeapp.models import  tbl_hospital_doctor_register
from django.shortcuts import render, redirect, get_object_or_404

# ✅ View all pending doctors
def view_pending_doctors(request):
    hospital_pending = tbl_hospital_doctor_register.objects.filter(status='pending')
    return render(request, 'pending_doctors.html', {
        'hospital_pending': hospital_pending
    })



# ✅ Approve hospital doctor
def approve_hospital_doctor(request, doctor_id):
    doctor = get_object_or_404(tbl_hospital_doctor_register, id=doctor_id)
    doctor.status = 'approved'
    doctor.save()
    return redirect('view_pending_doctors')


# ✅ Reject hospital doctor
def reject_hospital_doctor(request, doctor_id):
    doctor = get_object_or_404(tbl_hospital_doctor_register, id=doctor_id)
    doctor.status = 'rejected'
    doctor.save()
    return redirect('view_pending_doctors')



def view_approved_doctors(request):
   
    hospital_approved = tbl_hospital_doctor_register.objects.filter(status='approved')
    return render(request, 'approved_doctors.html', {
        
        'hospital_approved': hospital_approved
    })


def view_rejected_doctors(request):
    hospital_rejected = tbl_hospital_doctor_register.objects.filter(status='rejected')
    return render(request, 'rejected_doctors.html', {
        'hospital_rejected': hospital_rejected
    })





from django.shortcuts import render, redirect, get_object_or_404
from .models import Book

# 📘 Add Book
def add_book(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        description = request.POST.get("description")
        category = request.POST.get("category")
        publisher = request.POST.get("publisher")
        publication_date = request.POST.get("publication_date")
        cover_image = request.FILES.get("cover_image")

        Book.objects.create(
            title=title,
            author=author,
            description=description,
            category=category,
            publisher=publisher,
            publication_date=publication_date if publication_date else None,
            cover_image=cover_image
        )
        return redirect("view_books")
    return render(request, "add_book.html")


# 📚 List Books
def view_books(request):
    books = Book.objects.all().order_by("created_at")
    return render(request, "view_books.html", {"books": books})


# ✏️ Edit Book
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.title = request.POST.get("title")
        book.author = request.POST.get("author")
        book.description = request.POST.get("description")
        book.category = request.POST.get("category")
        book.publisher = request.POST.get("publisher")
        book.publication_date = request.POST.get("publication_date")
        if request.FILES.get("cover_image"):
            book.cover_image = request.FILES.get("cover_image")
        book.save()
        return redirect("view_books")
    return render(request, "edit_book.html", {"book": book})


# 🗑️ Delete Book
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect("view_books")






from django.shortcuts import render
from femitimeapp.models import  HospitalBooking

from django.shortcuts import render
from femitimeapp.models import HospitalBooking

def admin_view_hospital_bookings(request):
    hospital_bookings = (
        HospitalBooking.objects
        .select_related('user', 'doctor')
        
        .order_by('-date', '-id')
    )

    return render(request, 'view_all_bookings.html', {
        'hospital_bookings': hospital_bookings
    })

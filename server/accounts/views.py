import json
from datetime import datetime, date
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.http import JsonResponse


def user_signup(request):
    if request.user.is_authenticated:
        return redirect("user_home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            messages.error(request, "Username or Email already exists!")
            return redirect("user_signup")

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("user_signup")

        phone = request.POST.get("phone")
        # we no longer ask for country code during signup, keep default on model
        # collect optional personal details if provided
        dob = request.POST.get("date_of_birth") or None
        gender = request.POST.get("gender") or None
        age_val = None
        if dob:
            try:
                dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
                # simple age calculation
                today = date.today()
                age_val = today.year - dob_date.year - (
                    (today.month, today.day) < (dob_date.month, dob_date.day)
                )
            except Exception:
                age_val = None

        # Create user
        try:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            Profile.objects.create(
                phone=phone,
                date_of_birth=dob,
                age=age_val,
                gender=gender,
                user=user,
            )

            messages.success(request, "Account created successfully! Please login.")
            return redirect("user_login")

        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect("user_signup")

    return render(request, "account/signup.html")


def user_login(request):
    if request.user.is_authenticated:
        return redirect("user_profile")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("user_profile")

        messages.error(request, "Invalid username or password!")
        return redirect("user_login")

    return render(request, "account/login.html")

@login_required
def user_profile(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")

        user = request.user
        profile = user.profile

        # Validate username
        if User.objects.exclude(id=user.id).filter(username=username).exists():
            return JsonResponse({"error": "Username already taken!"}, status=400)

        # Validate email
        if User.objects.exclude(id=user.id).filter(email=email).exists():
            return JsonResponse({"error": "Email already taken!"}, status=400)

        phone = data.get("phone")
        dob = data.get("date_of_birth")
        age = data.get("age")
        gender = data.get("gender")

        # Save user
        user.username = username
        user.email = email
        user.save()

        # Save profile fields (country code untouched)
        if phone is not None:
            profile.phone = phone
        if dob:
            profile.date_of_birth = dob
            # recalc age if dob changed
            try:
                dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
                today = date.today()
                profile.age = today.year - dob_date.year - (
                    (today.month, today.day) < (dob_date.month, dob_date.day)
                )
            except Exception:
                pass
        if age and not dob:
            # user supplied explicit age without changing dob
            try:
                profile.age = int(age)
            except (ValueError, TypeError):
                pass
        if gender is not None:
            profile.gender = gender
        profile.save()

        # RETURN JSON ✔️
        return JsonResponse({
            "message": "Profile updated successfully!",
            "username": user.username,
            "email": user.email,
            "phone": profile.phone,
            "date_of_birth": profile.date_of_birth,
            "age": profile.age,
            "gender": profile.gender,
        }, status=200)

    return render(request, "account/profile.html", {"user": request.user})


@login_required
def user_logout(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect("user_login")
    return redirect("user_profile")

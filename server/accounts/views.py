import json
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
        country_code = request.POST.get("country_code")

        # Create user
        try:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            Profile.objects.create(phone=phone, country_code=country_code, user=user)

            messages.success(request, "Account created successfully! Please login.")
            return redirect("user_login")

        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect("user_signup")

    return render(request, "account/signup.html")


def user_login(request):
    if request.user.is_authenticated:
        return redirect("user_home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("user_home")

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

        country_code = data.get("country_code")
        phone = data.get("phone")

        # Save user
        user.username = username
        user.email = email
        user.save()

        # Save profile
        profile.country_code = country_code
        profile.phone = phone
        profile.save()

        # RETURN JSON ✔️
        return JsonResponse({
            "message": "Profile updated successfully!",
            "username": user.username,
            "email": user.email,
            "country_code": profile.country_code,
            "phone": profile.phone
        }, status=200)

    return render(request, "account/profile.html", {"user": request.user})


def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("user_login")

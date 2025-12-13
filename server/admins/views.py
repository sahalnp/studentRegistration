from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from accounts.models import Profile
from products.models import Products, Category, ProductImage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


@login_required(login_url="admin_login")
def admin_home(request):
    users = Profile.objects.all()
    deletedUser = Profile.objects.filter(is_deleted=True).count()
    totalProduct = Products.objects.filter(active=True).count()
    deletedProduct = Products.objects.filter(active=False).count()
    return render(
        request,
        "home.html",
        {
            "users": users,
            "deletedUser": deletedUser,
            "totalProduct": totalProduct,
            "deletedProduct": deletedProduct,
            "totalUsers": users.count(),
            
        },
    )


@login_required(login_url="admin_login")
def add_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")
        country_code = request.POST.get("country_code")

        try:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )

            Profile.objects.create(phone=phone, country_code=country_code, user=user)

            messages.success(request, "User created successfully!")
            return redirect("home")  # 🔥 redirect to admin home

        except Exception as e:
            messages.error(request, f"Failed to create user: {str(e)}")
            return redirect("home")


@login_required(login_url="admin_login")
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile

        user.is_active = False
        user.save()

        profile.is_deleted = True
        profile.save()

        messages.success(request, "User deleted successfully!")
        return redirect("home")

    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect("home")

    except Exception as e:
        messages.error(request, f"Error deleting user: {str(e)}")
        return redirect("home")


@login_required(login_url="admin_login")
def edit_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile

        if request.method == "POST":
            username = request.POST.get("username")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            country_code = request.POST.get("country_code")

            # Check for duplicate username
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                messages.error(request, "Username already exists!")
                return redirect("home")

            # Check for duplicate email
            if User.objects.filter(email=email).exclude(id=user_id).exists():
                messages.error(request, "Email already registered!")
                return redirect("home")

            # Update user
            user.username = username
            user.email = email
            user.save()

            # Update profile
            profile.phone = phone
            profile.country_code = country_code
            profile.save()

            messages.success(request, "User updated successfully!")
            return redirect("home")

        return render(
            request, "admin/edit_user.html", {"user": user, "profile": profile}
        )

    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect("home")

    except Exception as e:
        messages.error(request, f"Error updating user: {str(e)}")
        return redirect("home")


@login_required(login_url="admin_login")
def admin_products(request):
    products = Products.objects.filter(active=True)
    return render(
        request,
        "product.html",
        {"products": products},
    )


@login_required(login_url="admin_login")
def admin_add_product(request):
    if request.method == "POST":
        try:
            category_name = request.POST.get("category")
            name = request.POST.get("name")
            price = request.POST.get("price")

            main_image = request.FILES.get("main_image")
            image_side = request.FILES.get("image_side")
            image_back = request.FILES.get("image_back")
            image_up = request.FILES.get("image_up")

            add_category, created = Category.objects.get_or_create(name=category_name)

            product = Products.objects.create(
                name=name, price=price, category=add_category
            )

            ProductImage.objects.create(
                product=product,
                main_image=main_image,
                image_back=image_back,
                image_side=image_side,
                image_up=image_up,
            )

            messages.success(request, "Product added successfully!")
            return redirect("product")

        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")
            return redirect("product")


@login_required(login_url="admin_login")
def admin_edit_product(request, id):
    try:
        product = Products.objects.get(id=id)
        product_images = ProductImage.objects.get(product=product)

        if request.method == "POST":
            category_name = request.POST.get("category")
            name = request.POST.get("name")
            price = request.POST.get("price")

            if category_name:
                category, created = Category.objects.get_or_create(name=category_name)
                product.category = category

            if name:
                product.name = name

            if price:
                product.price = price

            product.save()

            main_image = request.FILES.get("main_image")
            image_side = request.FILES.get("image_side")
            image_back = request.FILES.get("image_back")
            image_up = request.FILES.get("image_up")

            if main_image:
                product_images.main_image = main_image
            if image_side:
                product_images.image_side = image_side
            if image_back:
                product_images.image_back = image_back
            if image_up:
                product_images.image_up = image_up

            product_images.save()

            messages.success(request, "Product updated successfully!")
            return redirect("product")

        return render(
            request,
            "admin/edit_product.html",
            {"product": product, "images": product_images},
        )

    except Exception as e:
        messages.error(request, f"Error editing product: {str(e)}")
        return redirect("product")


@login_required(login_url="admin_login")
def admin_delete_product(request, id):
    try:
        Products.objects.filter(id=id).update(active=False)
        messages.success(request, "Product deleted successfully!")
        return redirect("product")
    except Exception as e:
        messages.error(request, f"Error deleting product: {str(e)}")
        return redirect("product")


def admin_logout(request):
    logout(request)
    return redirect(login)


def admin_login(request):
    if request.user.is_authenticated:
        return redirect("admins_home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("admins_home")

        messages.error(request, "Invalid username or password!")
        return redirect("admins_login")
    return render(request, "login.html")
@login_required(login_url="admins_login")
def user_profile(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        user = request.user
        profile = user.profile

        # Validate username
        if User.objects.exclude(id=user.id).filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect("user_profile")

        # Validate email
        if User.objects.exclude(id=user.id).filter(email=email).exists():
            messages.error(request, "Email already taken!")
            return redirect("user_profile")

        country_code = request.POST.get("country_code")
        phone = request.POST.get("phone")

        # Save user
        user.username = username
        user.email = email
        user.save()

        # Save profile
        profile.country_code = country_code
        profile.phone = phone
        profile.save()

        # Use messages with values
        success_message = f"Profile updated successfully! Username: {user.username}, Email: {user.email}, Phone: {phone}, Country Code: {country_code}"
        messages.success(request, success_message)
        return redirect("user_profile")

    return render(request, "account.html", {"user": request.user})
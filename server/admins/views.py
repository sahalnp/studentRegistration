import profile
from datetime import datetime, date
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from accounts.models import Profile
from products.models import Products, Category, ProductImage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError


@login_required(login_url="admins_login")
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


@login_required(login_url="admins_login")
def add_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = "0000"
        phone = request.POST.get("phone")
        country_code = request.POST.get("country_code")
        print(username, email, password, phone, country_code, "sfiodsfsdjfls")
        try:
            if Profile.objects.filter(phone=phone, country_code=country_code).exists():
                messages.error(request, "Phone number already exists")
                return redirect("admins_home")
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return redirect("admins_home")

            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )

                # Create profile
                Profile.objects.create(
                    user=user, phone=phone, country_code=country_code
                )

            messages.success(request, "User created successfully")
            return redirect("admins_home")

        except IntegrityError:
            messages.error(request, "Phone number already exists")
            return redirect("admins_home")
        except Exception as e:
            print("❌ ERROR CREATING USER:", repr(e))
            messages.error(request, str(e))
            return redirect("admins_home")


@login_required(login_url="admins_login")
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile

        user.is_active = False
        user.save()

        profile.is_deleted = True
        profile.save()

        messages.success(request, "User deleted successfully!")
        return redirect("admins_home")

    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect("admins_home")
    except Exception as e:
        messages.error(request, f"Error deleting user: {str(e)}")
        return redirect("admins_home")


@login_required(login_url="admins_login")
def edit_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile

        if request.method == "POST":
            username = request.POST.get("username")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            country_code = request.POST.get("country_code")

            # Duplicate username
            if User.objects.filter(username=username).exclude(id=user_id).exists():
                messages.error(request, "Username already exists!")
                return redirect("admins_home")

            # Duplicate email
            if User.objects.filter(email=email).exclude(id=user_id).exists():
                messages.error(request, "Email already registered!")
                return redirect("admins_home")

            try:
                with transaction.atomic():
                    user.username = username
                    user.email = email
                    user.save()

                    profile.phone = phone
                    profile.country_code = country_code
                    profile.save()

                messages.success(request, "User updated successfully!")

            except IntegrityError:
                messages.error(request, "Phone number already exists!")

            return redirect("admins_home")

        # ✅ IMPORTANT: HANDLE GET REQUEST
        return redirect("admins_home")

    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect("admins_home")

    except Exception as e:
        messages.error(request, f"Error updating user: {str(e)}")
    return redirect("admins_home")


@login_required(login_url="admin_login")
def admin_products(request):
    products = Products.objects.all()
    print(products, "=================products=================")
    return render(
        request,
        "product.html",
        {"products": products},
    )


@login_required(login_url="admin_login")
def admin_add_product(request):
    if request.method == "POST":
        try:
            category_name = request.POST.get("category", "").upper()
            name = request.POST.get("name")
            price = request.POST.get("price")
            main_image = request.FILES.get("main_image")
            image_side = request.FILES.get("image_side")
            image_back = request.FILES.get("image_back")
            image_up = request.FILES.get("image_up")
            print(
                category_name, name, price, main_image, image_side, image_back, image_up
            )
            add_category, created = Category.objects.get_or_create(
                category_name=category_name
            )

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
            return redirect("admins_products")

        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")
            return redirect("admins_products")


@login_required(login_url="admin_login")
def admin_edit_product(request, id):
    print(id, "=================edit product id=================")
    try:
        product = Products.objects.get(uid=id)
        product_images = ProductImage.objects.get(product=product)
        print(product, product_images, "================      hdhdhdhdh=edit product=================")
        if request.method == "POST":
            category_name = request.POST.get("category", "").upper()
            name = request.POST.get("name")
            price = request.POST.get("price")
            active = request.POST.get("active", "true") == "true"

            if category_name:
                category, created = Category.objects.get_or_create(category_name=category_name)
                product.category = category

            if name:
                product.name = name

            if price:
                product.price = price

            product.active = active
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
            return redirect("admins_products")

        return redirect("admins_products")

    except Exception as e:
        messages.error(request, f"Error editing product: {str(e)}")
        return redirect("admins_products")


@login_required(login_url="admin_login")
def admin_delete_product(request, id):
    try:
        Products.objects.filter(uid=id).update(active=False)
        messages.success(request, "Product deleted successfully!")
        return redirect("admins_products")
    except Exception as e:
        messages.error(request, f"Error deleting product: {str(e)}")
        return redirect("admins_products")


def admin_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


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
def admin_profile(request):
    user = request.user
    profile = user.profile  # ✅ FIXED

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        country_code = request.POST.get("country_code")
        phone = request.POST.get("phone")
        dob = request.POST.get("date_of_birth")
        age = request.POST.get("age")
        gender = request.POST.get("gender")

        if User.objects.exclude(id=user.id).filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("admins_account")

        if User.objects.exclude(id=user.id).filter(email=email).exists():
            messages.error(request, "Email already taken")
            return redirect("admins_account")
        if (
            Profile.objects.exclude(user=user)
            .filter(phone=phone, country_code=country_code)
            .exists()
        ):
            messages.error(request, "Phone already exists")
            return redirect("admins_account")

        user.username = username
        user.email = email
        user.save()

        profile.country_code = country_code
        profile.phone = phone
        if dob:
            profile.date_of_birth = dob
            # recalc age if needed
            try:
                dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
                today = date.today()
                profile.age = today.year - dob_date.year - (
                    (today.month, today.day) < (dob_date.month, dob_date.day)
                )
            except Exception:
                pass
        if age and not dob:
            try:
                profile.age = int(age)
            except (ValueError, TypeError):
                pass
        if gender:
            profile.gender = gender
        profile.save()

        messages.success(request, "Profile updated successfully")
        return redirect("admins_account")

    return render(request, "account.html", {"admin": user})


@login_required(login_url="admins_login")
def admin_detail_products(request, id):
    try:
        product = Products.objects.get(uid=id)
        product_images = ProductImage.objects.get(product=product)
        return render(
            request,
            "productDetails.html",
            {"product": product, "product_images": product_images},
        )
    except Products.DoesNotExist:
        messages.error(request, "Product not found!")
        return redirect("admins_products")
    except Exception as e:
        messages.error(request, f"Error retrieving product details: {str(e)}")
        return redirect("admins_products")
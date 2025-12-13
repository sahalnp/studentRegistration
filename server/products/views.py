from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Products, Category
from django.core.paginator import Paginator


@login_required
def home(request):
    latest = Products.objects.all()[:5]
    return render(request, "nav_page/home.html", {"latest": latest})


@login_required
def user_products(request):
    products = Products.objects.filter(active=True)
    categories = Category.objects.filter(active=True)
    paginator = Paginator(products, 12) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "nav_page/productPage.html",
        {"page_obj": page_obj, "categories": categories},
    )


@login_required
def filter_products(request):
    min_price = float(request.GET.get("min") or 0)
    max_price = request.GET.get("max")
    category_id = request.GET.get("category")
    products = Products.objects.filter(
        price__lte=float(max_price), price__gte=min_price, category__id=category_id
    )

    return render(request, "nav_page/productPage.html", {"products": products})

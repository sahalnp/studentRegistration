from django.db import models
from base.models import Base
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)


class Products(Base):
    name = models.CharField(max_length=100)
    main_image = models.ImageField(upload_to="product_images")
    slug = models.SlugField(unique=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("name", "category")
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.OneToOneField(Products, on_delete=models.CASCADE)
    image_side = models.ImageField(upload_to="product_images")
    image_back = models.ImageField(upload_to="product_images")
    image_up = models.ImageField(upload_to="product_images")


@receiver(post_save, sender=ProductImage)
def resize_images(sender, instance, created, **kwargs):
    if not created:
        return

    TARGET_SIZE = (840, 840)

    image_fields = [
        ("main_image", instance.product.main_image),
        ("image_side", instance.image_side),
        ("image_back", instance.image_back),
        ("image_up", instance.image_up),
    ]

    for field_name, image_field in image_fields:
        try:
            if not image_field or not image_field.path:
                continue

            img = Image.open(image_field.path)

            if img.size[0] > TARGET_SIZE[0] or img.size[1] > TARGET_SIZE[1]:
                img = img.resize(TARGET_SIZE, Image.LANCZOS)
                img.save(image_field.path)
                print(f"{field_name} resized successfully.")

        except Exception as e:
            print(f"Error resizing {field_name}: {e}")

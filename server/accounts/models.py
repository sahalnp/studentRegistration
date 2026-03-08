from django.db import models
import uuid
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils.text import slugify


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    # country code is still stored but not shown on profile page anymore
    country_code = models.CharField(default="91", max_length=4)

    from django.core.validators import RegexValidator

    phone = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(r"^\d{10}$", message="Enter a valid 10-digit phone number")
        ],
    )

    # new personal information fields
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    is_deleted = models.BooleanField(default=False, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return f"{self.user.username}"

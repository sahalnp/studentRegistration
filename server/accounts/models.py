from django.db import models
import uuid
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    country_code=models.CharField(default=91,max_length=2)
    phone = models.CharField(max_length=10, validators=[RegexValidator(r"^\d{10}$")])
    is_deleted = models.BooleanField(default=False, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")    

    def __str__(self):
        return f"{self.user.first_name}"
    class Meta:
         ordering = ['-created_at']
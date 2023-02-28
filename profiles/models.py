from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class UserAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=254, null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)
    town_or_city = models.CharField(max_length=254, null=True, blank=True)
    county = models.CharField(max_length=254, null=True, blank=True)
    country = CountryField(blank_label='Country', null=True, blank=False)

    def __str__(self):
        return self.user.username
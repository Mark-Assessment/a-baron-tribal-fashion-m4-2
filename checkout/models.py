import uuid
from django.db import models
from django.db.models import Sum
from django_countries.fields import CountryField
from django.conf import settings
from products.models import Product
from profiles.models import UserAccount


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    street_address1 = models.CharField(max_length=254, null=False, blank=False)
    street_address2 = models.CharField(max_length=254, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=False, blank=False)
    town_or_city = models.CharField(max_length=100, null=False, blank=False)
    county = models.CharField(max_length=100, null=True, blank=True)
    country = CountryField(blank_label='Country', null=True, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6,
                                        decimal_places=2,
                                        null=False, default=0)
    total_cost = models.DecimalField(max_digits=10,
                                     decimal_places=2, null=False, default=0)
    overall_total = models.DecimalField(max_digits=10,
                                        decimal_places=2,
                                        null=False, default=0)
    user_account = models.CharField(max_length=254, null=True, blank=True)
    stripe_pid = models.CharField(max_length=254, null=False,
                                  blank=False, default='')
    cancel_request = models.BooleanField(null=False, default=False)

    def _generate_order_number(self):
        return uuid.uuid4().hex.upper()

    def update_total(self):
        self.total_cost = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0
        if self.total_cost < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = (
                self.total_cost * settings.DELIVERY_PERCENTAGE / 100)
        else:
            self.delivery_cost = 0
        self.overall_total = self.total_cost + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False,
                              on_delete=models.CASCADE,
                              related_name='lineitems')
    product = models.ForeignKey(Product, null=False, blank=False,
                                on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    product_seller = models.CharField(max_length=254, null=False, default='',
                                      blank=False, editable=False)
    lineitem_total = models.DecimalField(max_digits=6,
                                         decimal_places=2, null=False,
                                         default=0, editable=False)

    def save(self, *args, **kwargs):
        self.lineitem_total = self.product.price * self.quantity
        self.product_seller = self.product.seller
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU: {self.product.sku}\
             on order number {self.order.order_number}'


class ShippingDetails(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    street_address1 = models.CharField(max_length=254, null=False, blank=False)
    street_address2 = models.CharField(max_length=254, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=False, blank=False)
    town_or_city = models.CharField(max_length=100, null=False, blank=False)
    county = models.CharField(max_length=100, null=True, blank=True)
    country = CountryField(blank_label='Country', null=True, blank=False)

    def __str__(self):
        return self.user.user.username

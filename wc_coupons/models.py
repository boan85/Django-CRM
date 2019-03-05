from django.db import models

from wc_orders.models import Order


class Coupon(models.Model):
    coupon_code = models.PositiveIntegerField(("Coupon code"), unique=True)
    description = models.TextField(("Description"), null=True, blank=True)

    PERCENTAGE_DISCOUNT = 'PD'
    FIXED_CARD_DISCOUNT = 'FC'
    FIXED_PRODUCT_DISCOUNT = 'FP'
    BOOKING_PERSON_DISCOUNT = 'BP'

    DISCOUNT_TYPE_CHOICE = (
        (PERCENTAGE_DISCOUNT, 'Percentage discount'),
        (FIXED_CARD_DISCOUNT, 'Fixed card discount'),
        (FIXED_PRODUCT_DISCOUNT, 'Fixed product discount'),
        (BOOKING_PERSON_DISCOUNT, 'Booking person discount'),
    )

    discount_type = models.CharField(
        ("Discount type"),
        max_length=2,
        choices=DISCOUNT_TYPE_CHOICE,
        default=PERCENTAGE_DISCOUNT
    )

    free_shipping = models.BooleanField(("Allow free shipping"), default=False)
    expiry_date = models.DateField(("Coupon expiry date"), db_index=True)

    # Usage restriction
    minimum_spend = models.PositiveIntegerField(("Minimum spend"), null=True, blank=True)
    maximum_spend = models.PositiveIntegerField(("Maximum spend"), null=True, blank=True)
    individual_use_only = models.BooleanField(("Individual use only"), default=False)
    exclude_sale_items = models.BooleanField(("Exlude sale items"), default=False)

    # Products
    # Exclude products
    # Product categoriesUncategorized
    # Exclude categoriesUncategorized
    # Allowed emails

    # Usage limits
    usage_limit_per_coupon = models.PositiveIntegerField(("Usage limit per coupon"), null=True, blank=True)
    usage_limit_per_user = models.PositiveIntegerField(("Usage limit per user"), null=True, blank=True)

    order = models.ForeignKey(Order, related_name='Orders', on_delete=models.CASCADE, blank=True, null=True)

    total = models.FloatField(("Total"), default=0.0)

    class Meta:
        app_label = 'wc_coupons'

    def __str__(self):
        return "%s" % self.coupon_code



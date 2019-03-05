from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


class OrderShipping(models.Model):
    first_name = models.CharField("First_name", max_length=255, blank=True, null=True)
    last_name = models.CharField("Last_name", max_length=255, blank=True, null=True)
    company = models.CharField("Company", max_length=20, blank=True, null=True)
    address_line_one = models.CharField("Address line 1", max_length=255, blank=True, null=True)
    address_line_two = models.CharField("Address line 2", max_length=255, blank=True, null=True)
    city = models.CharField("City", max_length=255, blank=True, null=True)
    post_code = models.PositiveIntegerField("Post code / ZIP", null=True)
    country = models.CharField("Country", max_length=20, blank=True, null=True)
    state_or_country = models.CharField("State / Country", max_length=20, blank=True, null=True)
    customer_provided_note = models.TextField(("Customer provided note"), blank=True, null=True)


class OrderBilling(models.Model):
    first_name = models.CharField("First_name", max_length=255, blank=True, null=True)
    last_name = models.CharField("Last_name", max_length=255, blank=True, null=True)
    company = models.CharField("Company", max_length=20, blank=True, null=True)
    address_line_one = models.CharField("Address line 1", max_length=255, blank=True, null=True)
    address_line_two = models.CharField("Address line 2", max_length=255, blank=True, null=True)
    city = models.CharField("City", max_length=255, blank=True, null=True)
    post_code = models.PositiveIntegerField("Post code / ZIP", blank=True, null=True)
    country = models.CharField("Country", max_length=20, blank=True, null=True)
    state_or_country = models.CharField("State / Country", max_length=20, blank=True, null=True)
    email_address = models.EmailField()
    phone = PhoneNumberField()

    NA = 'NA'
    CHECK_BOOKING_AVAILABILITY = 'CA'
    OTHER = 'OT'

    ORDER_BILLING_CHOICE = (
        (NA, 'N/A'),
        (CHECK_BOOKING_AVAILABILITY, 'Check booking availability'),
        (OTHER, 'Other'),
    )

    payment_method = models.CharField(
        ("Payment method"),
        max_length=2,
        choices=ORDER_BILLING_CHOICE,
        default=NA
    )

    transaction_id = models.PositiveIntegerField(null=True, blank=True)


class Order(models.Model):
    date_created = models.DateField(("Date created"), auto_now_add=True)
    order_number = models.PositiveIntegerField(("Order number"), default=0)

    PENDING_PAYMENT = 'PP'
    PROCESSING = 'PR'
    ON_HOLD = 'OH'
    COMPLETED = 'CP'
    CANCELLED = 'CL'
    REFUNDED = 'RF'
    FAILED = 'FA'

    ORDER_TYPE_CHOICE = (
        (PENDING_PAYMENT, 'Pending payment'),
        (PROCESSING, 'Processing'),
        (ON_HOLD, 'On hold'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (REFUNDED, 'Refaunded'),
        (FAILED, 'Failed'),
    )

    order_type = models.CharField(
        ("Order type"),
        max_length=2,
        choices=ORDER_TYPE_CHOICE,
        default=PENDING_PAYMENT
    )

    # now it is just char field, we have not customer model in project
    customer = models.CharField(("Customer"), max_length=255, blank=True, null=True)

    billing = models.OneToOneField(OrderBilling, null=True, blank=True, on_delete=models.CASCADE)
    shipping = models.OneToOneField(OrderShipping, null=True, blank=True, on_delete=models.CASCADE)

    EMAIL_INVOICE = 'Email invoice / order details to customer'
    RESEND_NEW_ORDER_NOTIFICATION = 'Resend new order notification'
    REGENERATE_DOWNLOAD_PERMISSIONS = 'Regenerate download permissions'

    ACTION_TYPE_CHOICE = (
        (EMAIL_INVOICE, 'Email invoice / order details to customer'),
        (RESEND_NEW_ORDER_NOTIFICATION, 'Resend new order notification'),
        (REGENERATE_DOWNLOAD_PERMISSIONS, 'Regenerate download permissions'),
    )

    order_actions = models.CharField(
        ("Order actions"),
        max_length=100,
        choices=ACTION_TYPE_CHOICE,
        default=EMAIL_INVOICE,
        blank=True,
        null=True
    )

    # for now it is just char field, because we have not downloadable product permissions in project
    downloadable_product_permission = models.CharField("Downloadable product permissions", max_length=255, null=True,
                                                       blank=True)

    def copy_billing_address_to_shipping(self):
        if self.billing:
            self.shipping.first_name = self.billing.first_name
            self.shipping.last_name_name = self.billing.last_name
            self.shipping.company = self.billing.company
            self.shipping.address_line_one = self.billing.address_line_one
            self.shipping.address_line_two = self.billing.address_line_two
            self.shipping.city = self.billing.city
            self.shipping.post_code = self.billing.post_code
            self.shipping.country = self.billing.country
            self.shipping.state_or_country = self.billing.state_or_country
            self.shipping.save()


class CustomFields(models.Model):
    ALLOW_RETRIES = 'allow_retries'
    ANSWERS = 'answers'
    ANSWERS_SELECTED = 'answers_selected'
    ASSESSABLE = 'assessable'
    CAPTION_CUSTOM_TEXT = 'caption_custom_text'
    CAPTION_FIELD = 'caption_field'
    COUPON_AMOUNT = 'coupon_amount'
    COURSE_SETTINGS = 'course_setting'
    COURSE_START_DATE = 'course_start_date'
    CP_ALLOW_DISCUSSION = 'cp_allow_discussion'
    CP_ALLOW_GRADES = 'cp_allow_grades'
    CP_ALLOW_WORK_BOOK = 'cp_allow_workbook'
    CP_BASIC_CERTIFICATE = 'cp_basic_certificate'
    CP_BASIC_CERTIFICATE_LAYOUT = 'cp_basic_certificate_layout'
    CP_CERTIFICATE_BACKGROUND = 'cp_certificate_background'
    CP_CERTIFICATE_LOGO = 'cp_certificate_logo'
    CP_CERT_MARGIN = 'cp_cert_margin'
    CP_CERT_TEXT_COLOR = 'cp_cert_text_color'
    CP_CLASS_LIMITED = 'cp_class_limited'
    CP_CLASS_SIZE = 'cp_class_size'
    CP_COURSE_COMPLETION_CONTENT = 'cp_course_completion_content'
    CP_COURSE_COMPLETION_TITLE = 'cp_course_completion_title'
    CP_COURSE_END_DATE = 'cp_course_end_date'
    CP_COURSE_FAILED_CONTENT = 'cp_course_failed_content'
    CP_COURSE_FAILED_TITLE = 'cp_course_failed_title'
    CP_COURSE_LANGUAGE = 'cp_course_language'
    CP_COURSE_OPEN_ENDED = 'cp_course_open_ended'
    CP_COURSE_START_DATE = 'cp_course_start_date'
    CP_COURSE_VIEW = 'cp_course_view'
    CP_ENROLLMENT_END_DATE = 'cp_enrollment_end_date'

    CUSTOM_FIELD_NAME_CHOICE = (
        (ALLOW_RETRIES, 'allow_retries'),
        (ANSWERS, 'answers'),
        (ANSWERS_SELECTED, 'answers_selected'),
        (ASSESSABLE, 'allow_retries'),
        (CAPTION_CUSTOM_TEXT, 'caption_custom_text'),
        (CAPTION_FIELD, 'caption_field'),
        (COUPON_AMOUNT, 'coupon_amount'),
        (COURSE_SETTINGS, 'course_setting'),
        (COURSE_START_DATE, 'course_start_date'),
        (CP_ALLOW_DISCUSSION, 'cp_allow_discussion'),
        (CP_ALLOW_GRADES, 'cp_allow_grades'),
        (CP_ALLOW_WORK_BOOK, 'cp_allow_workbook'),
        (CP_BASIC_CERTIFICATE, 'cp_basic_certificate'),
        (CP_BASIC_CERTIFICATE_LAYOUT, 'cp_basic_certificate_layout'),
        (CP_CERTIFICATE_BACKGROUND, 'cp_certificate_background'),
        (CP_CERTIFICATE_LOGO, 'cp_certificate_background'),
        (CP_CERT_MARGIN, 'cp_cert_margin'),
        (CP_CERT_TEXT_COLOR, 'cp_cert_text_color'),
        (CP_CLASS_LIMITED, 'cp_class_limited'),
        (CP_CLASS_SIZE, 'cp_class_size'),
        (CP_COURSE_COMPLETION_CONTENT, 'cp_course_completion_content'),
        (CP_COURSE_COMPLETION_TITLE, 'cp_course_completion_title'),
        (CP_COURSE_END_DATE, 'cp_course_end_date'),
        (CP_COURSE_FAILED_CONTENT, 'cp_course_failed_content'),
        (CP_COURSE_FAILED_TITLE, 'cp_course_failed_title'),
        (CP_COURSE_LANGUAGE, 'cp_course_language'),
        (CP_COURSE_OPEN_ENDED, 'cp_course_open_ended'),
        (CP_COURSE_START_DATE, 'cp_course_start_date'),
        (CP_COURSE_VIEW, 'cp_course_view'),
        (CP_ENROLLMENT_END_DATE, 'cp_enrollment_end_date'),
    )

    name = models.CharField(("Name"), choices=CUSTOM_FIELD_NAME_CHOICE, max_length=100)
    value = models.TextField(("Value"))
    order = models.ForeignKey(Order, related_name='orders_custom_field', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "%s" % self.name


class OrderNote(models.Model):
    PRIVATE_NOTE = 'PN'
    NOTE_TO_CUSTOMER = 'NC'

    NOTE_TYPE_CHOICE = (
        (PRIVATE_NOTE, 'Private note'),
        (NOTE_TO_CUSTOMER, 'Note to customer'),
    )

    note_type = models.CharField(("Note type"), max_length=2, choices=NOTE_TYPE_CHOICE, default=PRIVATE_NOTE)
    note_text = models.TextField("Note", default='')
    order = models.ForeignKey(Order, related_name='orders_note', on_delete=models.CASCADE)
    date_created = models.DateField(("Date created"), auto_now=True, null=True)

    def __str__(self):
        return "%s" % self.note_text
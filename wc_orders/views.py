import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, DetailView, UpdateView

from wc_coupons.models import Coupon
from wc_orders.forms import OrderForm
from wc_orders.models import Order, CustomFields, OrderNote
from pprint import pprint


class GetOrdersView(LoginRequiredMixin, TemplateView):
    context_object_name = "order_obj"
    template_name = "orders.html"

    def get(self, request, *args, **kwargs):
        orders = Order.objects.all()
        return render(request, "orders.html", {'orders': orders})


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = "order_record"
    template_name = "view_orders.html"

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        coupons = Coupon.objects.filter(order=context.get('order_record'))
        custom_fields = CustomFields.objects.filter(order=context.get('order_record'))
        order_notes = OrderNote.objects.filter(order=context.get('order_record'))

        order_action_choices = [Order.EMAIL_INVOICE, Order.RESEND_NEW_ORDER_NOTIFICATION,
                                Order.REGENERATE_DOWNLOAD_PERMISSIONS]
        context['order_notes'] = order_notes
        context['custom_fields'] = custom_fields
        context['coupons'] = coupons

        context['order_actions_choices'] = order_action_choices
        context['custom_fields_choices'] = CustomFields.CUSTOM_FIELD_NAME_CHOICE
        context['order_statuses'] = Order.ORDER_TYPE_CHOICE
        return context


class OrderEditDetailView(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = "order_record"
    template_name = "edit_order.html"

    def get_context_data(self, **kwargs):
        context = super(OrderEditDetailView, self).get_context_data(**kwargs)
        coupons = Coupon.objects.filter(order=context.get('order_record'))
        custom_fields = CustomFields.objects.filter(order=context.get('order_record'))
        order_notes = OrderNote.objects.filter(order=context.get('order_record'))

        order_action_choices = [Order.EMAIL_INVOICE, Order.RESEND_NEW_ORDER_NOTIFICATION,
                                Order.REGENERATE_DOWNLOAD_PERMISSIONS]
        context['order_notes'] = order_notes
        context['custom_fields'] = custom_fields
        context['coupons'] = coupons

        context['order_actions_choices'] = order_action_choices
        context['custom_fields_choices'] = CustomFields.CUSTOM_FIELD_NAME_CHOICE
        context['order_statuses'] = Order.ORDER_TYPE_CHOICE
        return context


class OrderEditView(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = "order_record"
    template_name = "edit_order.html"

    def post(self, request, *args, **kwargs):
        new_order_date = request.POST.get('new_order_date')
        new_order_customer = request.POST.get('new_order_customer')
        new_order_status = request.POST.get('new_order_status')
        order = Order.objects.get(id=kwargs.get('pk'))
        if new_order_date != '':
            new_date = datetime.datetime.strptime(new_order_date, '%Y-%m-%d')
            order.date_created = new_date
        if new_order_customer != '':
            order.customer = new_order_customer
        if new_order_status != '':
            if new_order_status == 'Pending payment':
                order.order_type = 'PP'
            if new_order_status == 'Processing':
                order.order_type = 'PR'
            if new_order_status == 'On hold':
                order.order_type = 'OH'
            if new_order_status == 'Completed':
                order.order_type = 'CP'
            if new_order_status == 'Cancelled':
                order.order_type = 'CL'
            if new_order_status == 'Refaunded':
                order.order_type = 'RF'
            if new_order_status == 'Failed':
                order.order_type = 'FA'
        order.save()
        redirect_url = '/orders/{}/edit/'.format(kwargs.get('pk'))
        return HttpResponseRedirect(redirect_url)


class OrderEditActionView(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = "order_record"
    template_name = "edit_order.html"

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs.get('pk'))
        if request.POST.get('order_action'):
            if request.POST.get('order_action') == Order.EMAIL_INVOICE:
                order.order_actions = Order.EMAIL_INVOICE
            if request.POST.get('order_action') == Order.RESEND_NEW_ORDER_NOTIFICATION:
                order.order_actions = Order.RESEND_NEW_ORDER_NOTIFICATION
            if request.POST.get('order_action') == Order.REGENERATE_DOWNLOAD_PERMISSIONS:
                order.order_actions = Order.REGENERATE_DOWNLOAD_PERMISSIONS
        order.save()
        redirect_url = '/orders/{}/edit/'.format(kwargs.get('pk'))
        return HttpResponseRedirect(redirect_url)


class OrderBillingEditView(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = "order_record"
    template_name = "edit_order.html"

    def post(self, request, *args, **kwargs):
        pprint(request.POST)
        billing_address_line_one = request.POST.get('billing_address_line_one')
        billing_address_line_two = request.POST.get('billing_address_line_two')
        billing_city = request.POST.get('billing_city')
        billing_company = request.POST.get('billing_company')
        billing_country = request.POST.get('billing_country')
        billing_email_address = request.POST.get('billing_email_address')
        billing_first_name = request.POST.get('billing_first_name')
        billing_last_name = request.POST.get('billing_last_name')
        billing_phone = request.POST.get('billing_phone')
        billing_post_code = request.POST.get('billing_post_code')
        billing_state_or_country = request.POST.get('billing_state_or_country')

        order = Order.objects.get(id=kwargs.get('pk'))
        order.billing.address_line_one = billing_address_line_one
        order.billing.address_line_two = billing_address_line_two
        order.billing.city = billing_city
        order.billing.company = billing_company
        order.billing.country = billing_country
        order.billing.email_address = billing_email_address
        order.billing.first_name = billing_first_name
        order.billing.last_name = billing_last_name
        order.billing.phone = billing_phone
        order.billing.post_code = int(billing_post_code)
        order.billing.state_or_country = billing_state_or_country
        order.save()
        order.billing.save()

        redirect_url = '/orders/{}/edit/'.format(kwargs.get('pk'))
        return HttpResponseRedirect(redirect_url)


class OrderShippingEditView(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = "order_record"
    template_name = "edit_order.html"

    def post(self, request, *args, **kwargs):
        shipping_address_line_one = request.POST.get('shipping_address_line_one')
        shipping_address_line_two = request.POST.get('shipping_address_line_two')
        shipping_city = request.POST.get('shipping_city')
        shipping_company = request.POST.get('shipping_company')
        shipping_country = request.POST.get('shipping_country')
        shipping_customer_provided_note = request.POST.get('shipping_customer_provided_note')
        shipping_first_name = request.POST.get('shipping_first_name')
        shipping_last_name = request.POST.get('shipping_last_name')
        shipping_post_code = request.POST.get('shipping_post_code')
        shipping_state_or_country = request.POST.get('shipping_state_or_country')

        order = Order.objects.get(id=kwargs.get('pk'))

        order.shipping.address_line_one = shipping_address_line_one
        order.shipping.address_line_two = shipping_address_line_two
        order.shipping.city = shipping_city
        order.shipping.company = shipping_company
        order.shipping.country = shipping_country
        order.shipping.customer_provided_note = shipping_customer_provided_note
        order.shipping.first_name = shipping_first_name
        order.shipping.last_name = shipping_last_name
        order.shipping.post_code = int(shipping_post_code)
        order.shipping.state_or_country = shipping_state_or_country
        order.shipping.save()
        order.save()

        redirect_url = '/orders/{}/edit/'.format(kwargs.get('pk'))
        return HttpResponseRedirect(redirect_url)


class OrderNoteAdd(LoginRequiredMixin, UpdateView):
    model = OrderNote

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs.get('pk', int))
        print(request.POST)
        note_text = request.POST.get('create_order_note_text')
        note_type = request.POST.get('create_order_note')
        new_order_note = OrderNote.objects.create(note_text=note_text, order=order, date_created=datetime.datetime.now())
        if note_type == OrderNote.PRIVATE_NOTE:
            new_order_note.note_type = OrderNote.PRIVATE_NOTE
        if note_type == OrderNote.NOTE_TO_CUSTOMER:
            new_order_note.note_type = OrderNote.NOTE_TO_CUSTOMER
        new_order_note.save()

        redirect_url = '/orders/{}/edit/'.format(order.id)
        return HttpResponseRedirect(redirect_url)


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    context_object_name = "order_record"
    template_name = "view_orders.html"

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs.get('pk', int))
        if self.check_form(order):
            # I know that it is always True, later will fix this.
            redirect_url = '/orders/{}/view/'.format(order.id)
            return HttpResponseRedirect(redirect_url)

    def check_form(self, order):
        if self.request.POST.get('order_action'):
            if self.request.POST.get('order_action') == Order.EMAIL_INVOICE:
                order.order_actions = Order.EMAIL_INVOICE
            if self.request.POST.get('order_action') == Order.RESEND_NEW_ORDER_NOTIFICATION:
                order.order_actions = Order.RESEND_NEW_ORDER_NOTIFICATION
            if self.request.POST.get('order_action') == Order.REGENERATE_DOWNLOAD_PERMISSIONS:
                order.order_actions = Order.REGENERATE_DOWNLOAD_PERMISSIONS
        order.save()
        return True


class OrderNoteCreate(LoginRequiredMixin, UpdateView):
    model = OrderNote

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs.get('pk', int))
        note_text = request.POST.get('create_order_note_text')
        note_type = request.POST.get('create_order_note')
        new_order_note = OrderNote.objects.create(note_text=note_text, order=order, date_created=datetime.datetime.now())
        if note_type == OrderNote.PRIVATE_NOTE:
            new_order_note.note_type = OrderNote.PRIVATE_NOTE
        if note_type == OrderNote.NOTE_TO_CUSTOMER:
            new_order_note.note_type = OrderNote.NOTE_TO_CUSTOMER
        new_order_note.save()

        redirect_url = '/orders/{}/view/'.format(order.id)
        return HttpResponseRedirect(redirect_url)


class OrderNoteDelete(LoginRequiredMixin, UpdateView):
    model = OrderNote

    def post(self, request, *args, **kwargs):
        print(kwargs)
        note = OrderNote.objects.get(id=kwargs.get('note')).delete()
        redirect_url = '/orders/{}/edit/'.format(kwargs.get('order'))
        return HttpResponseRedirect(redirect_url)


class CustomFieldAdd(LoginRequiredMixin, UpdateView):
    model = CustomFields

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs.get('pk', int))
        field_name = request.POST.get('custom_fields_names')
        field_value = request.POST.get('new_custom_field_value')
        new_custom_field = CustomFields.objects.create(order=order, name=field_name, value=field_value)
        new_custom_field.save()
        redirect_url = '/orders/{}/edit/'.format(order.id)
        return HttpResponseRedirect(redirect_url)


class CustomFieldCreate(LoginRequiredMixin, UpdateView):
    model = CustomFields

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs.get('pk', int))
        field_name = request.POST.get('custom_fields_names')
        field_value = request.POST.get('new_custom_field_value')
        new_custom_field = CustomFields.objects.create(order=order, name=field_name, value=field_value)
        new_custom_field.save()
        redirect_url = '/orders/{}/view/'.format(order.id)
        return HttpResponseRedirect(redirect_url)


class OrderCouponDelete(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        coupon = Coupon.objects.get(id=kwargs.get('coupon')).delete()
        redirect_url = '/orders/{}/edit/'.format(kwargs.get('order'))
        return HttpResponseRedirect(redirect_url)


class OrderCustomFieldUpdate(LoginRequiredMixin, UpdateView):
    model = CustomFields

    def post(self, request, *args, **kwargs):
        print(request.POST)
        redirect_url = '/orders/{}/edit/'.format(1)
        # redirect_url = '/orders/{}/edit/'.format(kwargs.get('order'))
        return HttpResponseRedirect(redirect_url)


class OrderCustomFieldDelete(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        custom_field = CustomFields.objects.get(id=kwargs.get('cf')).delete()
        redirect_url = '/orders/{}/edit/'.format(kwargs.get('order'))
        return HttpResponseRedirect(redirect_url)
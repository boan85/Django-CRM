import json
from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, render_to_response

# Create your views here.
from django.views import View
from django.views.generic import TemplateView

from wc_utils.wc_utils import get_orders_list


class GetOrdersView(LoginRequiredMixin, TemplateView):
    context_object_name = "order_obj"
    template_name = "orders.html"

    def get(self, request, *args, **kwargs):
        orders = get_orders_list()
        pprint(orders)
        # return HttpResponse(json.dumps(orders))
        return render(request, "orders.html", {'orders': orders})
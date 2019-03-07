from django.conf.urls import url

from wc_orders.forms import OrderForm
from wc_orders.views import OrderDetailView, OrderUpdateView, OrderNoteCreate, CustomFieldCreate, OrderEditView, \
    OrderEditDetailView, OrderNoteDelete, OrderCouponDelete, OrderCustomFieldDelete, OrderBillingEditView, \
    OrderShippingEditView, OrderEditActionView, OrderNoteAdd, CustomFieldAdd, GetOrdersFromAPI
from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

app_name = 'gravity_forms'

urlpatterns = [
    path('list/', views.GravityFormsList.as_view(), name="gravity_forms_list"),
    path('update-gravity-forms/', views.UpdateRedis.as_view(), name="update_gravity_forms"),
    path('<int:pk>/view/', views.GravityFormView.as_view(), name="gravity_forms_view"),
]
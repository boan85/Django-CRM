from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'emails'

urlpatterns = [
    url(r'^list/', views.GetOrdersView.as_view(), name="orders_list"),
]
from django.contrib.auth import views
from django.urls import include, path
from common.views import handler404, handler500

app_name = 'crm'

urlpatterns = [
    path('', include('common.urls', namespace="common")),
    path('', include('django.contrib.auth.urls')),
    path('companies/', include('accounts.urls', namespace="accounts")),
    path('leads/', include('leads.urls', namespace="leads")),
    path('contacts/', include('contacts.urls', namespace="contacts")),
    path('opportunities/', include('opportunity.urls', namespace="opportunities")),
    path('cases/', include('cases.urls', namespace="cases")),
    path('emails/', include('emails.urls', namespace="emails")),
    path('orders/', include('wc_orders.urls', namespace="wc_orders")),
    path('gravity-forms/', include('wc_gravity_forms.urls', namespace="wc_gravity_forms")),
    # path('planner/', include('planner.urls', namespace="planner")),
    path('logout/', views.LogoutView, {'next_page': '/login/'}, name="logout"),
]

handler404 = handler404
handler500 = handler500

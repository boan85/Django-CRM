from django.conf.urls import url

from wc_orders.forms import OrderForm
from wc_orders.views import OrderDetailView, OrderUpdateView, OrderNoteCreate, CustomFieldCreate, OrderEditView, \
    OrderEditDetailView, OrderNoteDelete, OrderCouponDelete, OrderCustomFieldDelete, OrderBillingEditView, \
    OrderShippingEditView, OrderEditActionView, OrderNoteAdd, CustomFieldAdd, GetOrdersFromAPI
from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

app_name = 'emails'

urlpatterns = [
    path('list/', views.GetOrdersView.as_view(), name="orders_list"),
    path('<int:pk>/view/', OrderDetailView.as_view(), name="view_order"),
    path('<int:pk>/edit/', OrderEditDetailView.as_view(), name="edit_order"),
    path('<int:pk>/edit/post/', OrderEditView.as_view(), name="edit_order_post"),
    path('<int:pk>/edit/post/billing/', OrderBillingEditView.as_view(), name="edit_order_post_billing"),
    path('<int:pk>/edit/post/action/', OrderEditActionView.as_view(), name="edit_order_post_action"),
    path('<int:pk>/edit/post/shipping/', OrderShippingEditView.as_view(), name="edit_order_post_shipping"),
    path('<int:pk>/edit/post/note/', OrderNoteAdd.as_view(), name="edit_order_post_note"),
    path('<int:pk>/update', OrderUpdateView.as_view(), name='update_view'),
    path('<int:pk>/create-order-note', OrderNoteCreate.as_view(), name='order_note_create'),
    path('<int:note>/<int:order>/delete-order-note', OrderNoteDelete.as_view(), name='order_note_delete'),
    path('<int:coupon>/<int:order>/delete-order-coupon', OrderCouponDelete.as_view(), name='order_coupon_delete'),
    path('<int:cf>/<int:order>/delete-order-cf', OrderCustomFieldDelete.as_view(), name='order_cf_delete'),
    path('<int:pk>/create-custom-field', CustomFieldCreate.as_view(), name='order_custom_field_create'),
    path('<int:pk>/add-custom-field', CustomFieldAdd.as_view(), name='order_custom_field_add'),

    path('update-orders-api/', GetOrdersFromAPI.as_view(), name='update_orders_api')
]
from django.urls import path


from .views import *

app_name = 'core'

urlpatterns = [
    path('', home_view, name='index'),
    path('product/<int:pk>', item_view, name='product'),
    path('product/<int:pk>/contact_seller', contact_seller_item_view, name='contact-seller-item-page'),
    path('accounts/order_history/details/<int:pk>/contact_seller', contact_seller_order_view, name='contact-seller-order-page'),
    path('profile/<int:pk>', profile_public, name='profile'),
    path('grading', GradingView.as_view(), name='grading'),
    path('terms_and_conditions', TAndCView.as_view(), name="terms_conditions"),
    path('privacy_policy', PrivacyView.as_view(), name="privacy"),
    path('accounts/order_history', profile_page_order_history, name='profile_page_order_history'),
    path('accounts/order_history/details/<int:pk>', profile_page_order_details_buyer, name='profile_page_order_details_buyer'),
    path('accounts/sales_history/details/<int:pk>', profile_page_order_details_seller, name='profile_page_order_details_seller'),
    path('accounts/sales_history/details/<int:pk>/update', order_update, name='order_update'),
    path('accounts/sales_history/details/<int:pk>/cancel', cancel_order, name='cancel_order'),
    path('accounts/login/success', redirect_to_home, name='redirect'),
    path('accounts/account_details', account_details,
         name='account_details'),
    path('accounts/account_details/my_products/add_item',
         ItemCreateView.as_view(),
         name="item_add"),
    path('accounts/sales_history', profile_page_sales_history, name='profile_page_sales_history'),
    path('accounts/profile-page-edit', UserUpdateView.as_view(), name='profile_page_edit'),
    path('accounts/account_details/my_products', my_products,
         name="my_products"),
    # path('product/<int:pk>/edit', ItemUpdateView.as_view(), name="item-edit")
    path('accounts/account_details/my_products/edit/<int:pk>',
         ItemUpdateView.as_view(), name="item-edit"),
    path('accounts/account_details/my_products/delete/<int:pk>',
         ItemDeleteView.as_view(), name="delete_confirmation"),
    path('product/<int:pk>/add_to_cart', add_to_cart, name="test_go_back"),
    path('empty_cart', empty_cart, name="empty_cart"),
    path('remove_from_cart/<int:oi_id>', remove_from_cart, name="remove_from_cart"),
    path('contact_us', ContactUsView.as_view(), name="contact_us"),
    path('check_out', checkout, name="checkout"),
    path('search', search, name="search"),
    path('success', purchase_success, name='success'),
    path('category/<int:pk>', category_view, name='category_view'),
    path('team-page', team_page_view, name='team_page')
]

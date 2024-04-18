from django.urls import path
from . import views

urlpatterns = [
    ####Admin URLS####
    path('pharmacy/login/', views.AdminLoginView, name='admin_login'),
    path('', views.Index, name='index'),
    path('logout/', views.LogoutView, name='logout'),
    path('home/', views.Home, name='home'),
    path('orders/', views.OrdersView, name='orders'),
    path('patient/home/', views.PatientHome, name='patient'),
    path('register/', views.RegisterView, name='register'),
    path('patient/register/', views.PatientRegisterView, name='patient_register'),
    path('add/patient/', views.AddPatientView, name='add_patient'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('add_medication/', views.add_medication, name='medication'),
    path('medications/', views.MedicationsView, name='medications'),
    path('users/', views.UsersView, name='users'),
    path('invoices/', views.InvoicesView, name='invoices'),
    path('api/profile/', views.UserProfileListView.as_view(), name='profile-list'),
     path('medications/edit/<int:medication_id>/', views.edit_medication, name='edit_medication'),

    ####APP URLS######

    path('login/', views.LoginView, name='login'),
    path('api/logout/', views.LogoutAPI.as_view(), name='api_logout'),
    path('api/register/', views.registerApi, name='register_api'),
    path('api/admin/home/', views.homeApi, name='home_api'),
    path('api/orders/', views.user_orders, name='user_orders'),
    path('api/invoice/<int:order_id>/', views.generate_invoice_pdf, name='invoice_api'),
    path('medication_list/', views.medication_list, name='medication_list'),
    path('medication_details/<int:medication_id>/', views.medication_details, name='medication_details'),
    path('api/submit_order/', views.submit_orderApi, name='submit_order_api'),#new
    path('profile/', views.user_profile, name='user_profile'),
    path('csrf_token/', views.csrf_token, name='csrf_token'),
]

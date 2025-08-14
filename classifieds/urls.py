from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.home, name='home'),

    # Auth
    #path('login/', views.login_view, name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/', LogoutView.as_view(), name='logout'),
    

    # Property routes
    path('properties/', views.property_list, name='property_list'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),

    # Car routes 
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),

    # Job routes
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),

    # Car routes
    path('api/cars/', views.car_list_json, name='car_list_json'),

    # Webhook calls
    path('webhook/', views.car_models, name='webhook'),
    path('property/', views.property_models, name='property'),
    path('job/', views.job_models, name='job'),

   
    path('listings/', views.listings_view, name='listings'),
    path('upload/', views.upload_listing, name='upload_listing'),

    path('my-adverts/', views.my_adverts, name='my_adverts'),
    path('edit/property/<int:pk>/', views.edit_property, name='edit_property'),

    path('my-adverts/', views.my_adverts, name='my_adverts'),
    path('edit/car/<int:pk>/', views.edit_car, name='edit_car'),

    path('my-adverts/', views.my_adverts, name='my_adverts'),
    path('edit/job/<int:pk>/', views.edit_job, name='edit_job'),

    path('delete/property/<int:pk>/', views.delete_property, name='delete_property'),
    path('delete/car/<int:pk>/', views.delete_car, name='delete_car'),
    path('delete/job/<int:pk>/', views.delete_job, name='delete_job'),

    path('toggle/property/<int:pk>/', views.toggle_visibility_property, name='toggle_visibility_property'),
    path('toggle/car/<int:pk>/', views.toggle_visibility_car, name='toggle_visibility_car'),
    path('toggle/job/<int:pk>/', views.toggle_visibility_job, name='toggle_visibility_job'),

    path('contact-seller/<int:property_id>/', views.contact_seller, name='contact_seller'),
    path('contact-car-seller/<int:pk>/', views.contact_car_seller, name='contact_car_seller'),
    path('contact-job-advertiser/<int:pk>/', views.contact_job_advertiser, name='contact_job_advertiser'),

    path('chatbot/', views.chatbot_view, name='chatbot_view'),
    


    
]

from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('about/', views.about, name='about'),
    path('testimonials/', views.testimonials, name='testimonials'),  # Add this
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    
    # Admin dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mark-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
    path('api/check-new-messages/', views.check_new_messages, name='check_new_messages'),
    path('testimonials/submit/', views.submit_testimonial, name='submit_testimonial'),
]
"""
URL configuration for the library app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Book URLs
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/new/', views.book_create, name='book_create'),
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('books/<int:pk>/availability/', views.book_availability, name='book_availability'),
    
    # Member URLs
    path('members/', views.member_list, name='member_list'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/new/', views.member_create, name='member_create'),
    path('members/<int:pk>/edit/', views.member_update, name='member_update'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),
    
    # Loan URLs
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/new/', views.loan_create, name='loan_create'),
    path('loans/<int:pk>/return/', views.loan_return, name='loan_return'),
]
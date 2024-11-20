from django.urls import path
from . import views

urlpatterns = [
    path('',views.user_login, name='login'),
    path('logout/',views.user_logout, name='logout'),
    path('admins/home/', views.adminhome, name='adminhome'),
    path('admins/destinations/', views.allpackcat, name='allpackcat'),
    path('admins/packages/', views.allpac, name='allpac'),
    path('admins/add/destination/', views.addpackcat, name='addpackcat'),
    path('edit-package-category/<int:id>/', views.edit_package_category, name='edit-package-category'),
    path('delete-package-category/<int:id>/', views.delete_package_category, name='delete-package-category'),
    path('admins/add/package/', views.addnewpack, name='addnewpack'),
    path('package/edit/<int:pk>/', views.package_edit, name='package_edit'),
    path('package/delete/<int:pk>/', views.package_delete, name='package_delete'),
    path('booking/<int:package_id>/create/', views.booking_create, name='booking_create'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('booking/confirm/', views.booking_confirm, name='booking_confirm'),
]

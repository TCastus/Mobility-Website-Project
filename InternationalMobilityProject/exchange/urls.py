from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
   
    path('search', views.search, name='search'),
    path('add-department/<int:univ>', views.addDepartment, name='add-department'),
    path('edit-department/<int:dep>', views.editDepartment, name='edit-department'),
    path('home', views.home),
    path('university/<int:idUni>', views.university),
    path('review-exchange', views.reviewExchange, name='review-exchange'),
    path('continent/<str:continent>', views.countries, name='countries'),
    path('country/<int:country>', views.cities, name='cities'),
    path('city/<int:city>', views.universities, name='universities'),
    path('edit/<int:univ>', views.edit, name='edit'), #universite/<int:univ>/informations-personnelles
    path('edit-department-student/<int:univ>/<int:stud>', views.editDepartmentStudent, name='edit-department-student'), #universite/<int:univ>/<int:stud>/departement
    path('edit-exchange/<int:univ>/<int:stud>', views.editExchange, name='edit-exchange'), #universite/<int:univ>/<int:stud>/echange
    path('edit-financial/<int:univ>/<int:exch>', views.editFinancial, name='edit-financial'), #universite/<int:univ>/<int:exch>/bourses
    path('login', views.exchangeLogin, name='exchange-login'),
    path('logout', views.exchangeLogout, name='exchange-logout'),
    path('rapport', views.rapport),
    path('base', views.base),
    path('user', views.user),
    path('review', views.review)
]
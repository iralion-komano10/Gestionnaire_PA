from django.urls import path
from . import views

app_name = 'pa'

urlpatterns = [
    # Authentification
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Pages protégées
    path('', views.accueil, name='accueil'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('plans/', views.liste_plans, name='liste_plans'),
    path('plans/ajouter/', views.ajouter_plan, name='ajouter_plan'),
    path('plans/<int:pk>/', views.detail_plan, name='detail_plan'),
    path('plans/<int:pk>/modifier/', views.modifier_plan, name='modifier_plan'),
    path('plans/<int:pk>/supprimer/', views.supprimer_plan, name='supprimer_plan'),
    # URLs d'export
    path('export/csv/', views.export_plans_csv, name='export_csv'),
    path('export/excel/', views.export_plans_excel, name='export_excel'),
    path('plans/<int:pk>/annuler/', views.annuler_plan, name='annuler_plan'),
    path('plans/<int:pk>/relancer/', views.relancer_plan, name='relancer_plan'),
    
]

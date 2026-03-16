from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('DEDI/', admin.site.urls),
    path('', include('pa.urls')),  # Seulement vos URLs personnalisées
]
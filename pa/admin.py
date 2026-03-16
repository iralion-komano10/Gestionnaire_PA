from django.contrib import admin
from .models import PlanAction  # Enlevez Direction de l'import

@admin.register(PlanAction)
class PlanActionAdmin(admin.ModelAdmin):
    list_display = ('description', 'direction', 'porteur', 'echeance', 'progression', 'statut', 'date_creation')
    list_filter = ('statut', 'direction', 'date_creation')
    search_fields = ('description', 'direction', 'porteur')
    readonly_fields = ('statut', 'date_creation', 'date_modification')
    
    # Optionnel : organisez les champs dans l'interface d'admin
    fieldsets = (
        ('Informations générales', {
            'fields': ('description', 'direction', 'porteur', 'indicateur')
        }),
        ('Dates', {
            'fields': ('date_debut', 'date_fin', 'echeance')
        }),
        ('Avancement', {
            'fields': ('progression', 'statut')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class PlanAction(models.Model):
    STATUT_CHOIX = [
        ('en_attente', '⏳ En attente'),
        ('en_cours', '🔄 En cours'),
        ('termine', '✅ Terminé'),
        ('annule', '❌ Annulé'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plans_action')
    
    description = models.TextField(verbose_name="Description")
    direction = models.CharField(max_length=200, verbose_name="Direction")
    porteur = models.CharField(max_length=200, verbose_name="Porteur")
    indicateur = models.CharField(max_length=200, verbose_name="Indicateur")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    echeance = models.DateField(verbose_name="Échéance")
    
    progression = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Progression (%)"
    )
    
    # Statut avec valeur par défaut
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOIX,
        default='en_attente',
        verbose_name="Statut"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Plan d'action"
        verbose_name_plural = "Plans d'action"

    def __str__(self):
        return f"{self.description[:50]} - {self.direction}"

    def mettre_a_jour_statut(self):
        """
        Met à jour le statut selon les règles métier:
        - Si progression = 100% → terminé
        - Si date actuelle >= date_debut → en cours
        - Si date actuelle < date_debut → en attente
        - Le statut 'annulé' est géré manuellement
        """
        today = date.today()
        
        # Ne pas modifier si le statut est 'annulé' (géré manuellement)
        if self.statut == 'annule':
            return self.statut
        
        # Règle 1: Si progression = 100% → terminé
        if self.progression >= 100:
            self.statut = 'termine'
        
        # Règle 2: Si date actuelle >= date_debut → en cours
        elif today >= self.date_debut:
            self.statut = 'en_cours'
        
        # Règle 3: Si date actuelle < date_debut → en attente
        elif today < self.date_debut:
            self.statut = 'en_attente'
        
        return self.statut

    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour mettre à jour le statut 
        automatiquement avant la sauvegarde, sauf si c'est 'annulé'
        """
        # Mettre à jour le statut automatiquement (sauf si annulé)
        if self.statut != 'annule':
            self.mettre_a_jour_statut()
        
        super().save(*args, **kwargs)

    def annuler(self):
        """Méthode pour annuler manuellement un plan"""
        self.statut = 'annule'
        self.save()

    def relancer(self):
        """Méthode pour relancer un plan annulé"""
        self.statut = 'en_attente'
        self.mettre_a_jour_statut()
        self.save()

    @property
    def jours_restants(self):
        return (self.echeance - date.today()).days

    @property
    def couleur_statut(self):
        couleurs = {
            'termine': 'success',
            'en_cours': 'primary',
            'en_attente': 'secondary',
            'annule': 'danger',
        }
        return couleurs.get(self.statut, 'secondary')

    @property
    def icone_statut(self):
        icones = {
            'termine': 'fa-check-circle',
            'en_cours': 'fa-sync-alt',
            'en_attente': 'fa-clock',
            'annule': 'fa-times-circle',
        }
        return icones.get(self.statut, 'fa-question-circle')

    @property
    def est_annule(self):
        return self.statut == 'annule'
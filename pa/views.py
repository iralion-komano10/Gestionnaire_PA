from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from datetime import date, timedelta, datetime
from django.db.models import Count, Avg
from .models import PlanAction
from .forms import PlanActionForm, UserRegistrationForm

import csv
import xlwt
from django.http import HttpResponse


# Page de connexion
def login_view(request):
    if request.user.is_authenticated:
        return redirect('pa:accueil')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {username} !')
            return redirect('pa:accueil')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'registration/login.html')

# Page d'inscription
def register_view(request):
    if request.user.is_authenticated:
        return redirect('pa:accueil')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.username}! Votre compte a été créé avec succès.')
            return redirect('pa:accueil')
        else:
            print(form.errors)
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

# Déconnexion
def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('pa:login')

# Page d'accueil - Protégée
@login_required(login_url='pa:login')
def accueil(request):
    # Filtrer les plans par utilisateur connecté
    plans = PlanAction.objects.filter(user=request.user)
    
    stats = {
        'termine': plans.filter(statut='termine').count(),
        'en_cours': plans.filter(statut='en_cours').count(),
        'en_attente': plans.filter(statut='en_attente').count(),
        'annule': plans.filter(statut='annule').count(),
    }
    
    plans_recents = plans.order_by('-date_creation')[:5]
    
    context = {
        'total_plans': plans.count(),
        'stats': stats,
        'plans_recents': plans_recents,
    }
    return render(request, 'pa/accueil.html', context)

# Dashboard - Protégé
@login_required(login_url='pa:login')
def dashboard(request):
    # Filtrer les plans par utilisateur connecté
    plans = PlanAction.objects.filter(user=request.user)
    
    stats = {
        'termine': plans.filter(statut='termine').count(),
        'en_cours': plans.filter(statut='en_cours').count(),
        'en_attente': plans.filter(statut='en_attente').count(),
        'annule': plans.filter(statut='annule').count(),
    }
    
    today = date.today()
    alertes = []
    for plan in plans.filter(statut__in=['en_cours', 'en_attente']):
        jours_restants = (plan.echeance - today).days
        if 0 <= jours_restants <= 7:
            alertes.append(plan)
    
    directions = plans.values('direction').annotate(
        total=Count('id'),
        progression_moyenne=Avg('progression')
    ).order_by('-total')
    
    plans_recents = plans.order_by('-date_creation')[:10]
    
    debut_mois = date(today.year, today.month, 1)
    nouveaux_plans = plans.filter(date_creation__gte=debut_mois).count()
    
    progression_moyenne = plans.filter(statut='en_cours').aggregate(Avg('progression'))['progression__avg'] or 0
    
    context = {
        'total_plans': plans.count(),
        'stats': stats,
        'alertes': alertes,
        'stats_directions': directions,
        'plans_recents': plans_recents,
        'nouveaux_plans': nouveaux_plans,
        'progression_moyenne': round(progression_moyenne, 1),
        'pourcentage_termines': round((stats['termine'] / plans.count() * 100) if plans.count() > 0 else 0, 1),
    }
    return render(request, 'pa/dashboard.html', context)

# Ajouter un plan - Protégé
@login_required(login_url='pa:login')
def ajouter_plan(request):
    if request.method == 'POST':
        form = PlanActionForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan d\'action créé avec succès!')
            return redirect('pa:dashboard')
        else:
            # Afficher les erreurs dans la console pour déboguer
            print("=" * 50)
            print("ERREURS DU FORMULAIRE:")
            print(form.errors)
            print("=" * 50)
            # Afficher aussi les données reçues
            print("DONNÉES REÇUES:")
            print(request.POST)
            print("=" * 50)
            
            # Ajouter un message d'erreur pour l'utilisateur
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PlanActionForm(user=request.user)
    
    return render(request, 'pa/ajouter_plan.html', {'form': form})


# Liste des plans - Protégé (filtré par utilisateur)
@login_required(login_url='pa:login')
def liste_plans(request):
    plans = PlanAction.objects.filter(user=request.user).order_by('-date_creation')
    
    statut = request.GET.get('statut')
    direction = request.GET.get('direction')
    
    if statut:
        plans = plans.filter(statut=statut)
    if direction:
        plans = plans.filter(direction__icontains=direction)
    
    context = {
        'plans': plans,
        'statut_actuel': statut,
        'direction_filtre': direction,
    }
    return render(request, 'pa/liste_plans.html', context)

# Détail d'un plan - Protégé (vérifie que le plan appartient à l'utilisateur)
@login_required(login_url='pa:login')
def detail_plan(request, pk):
    plan = get_object_or_404(PlanAction, pk=pk, user=request.user)
    context = {'plan': plan}
    return render(request, 'pa/detail_plan.html', context)

# Modifier un plan - Protégé (vérifie que le plan appartient à l'utilisateur)
@login_required(login_url='pa:login')
def modifier_plan(request, pk):
    plan = get_object_or_404(PlanAction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PlanActionForm(request.POST, instance=plan, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan modifié avec succès!')
            return redirect('pa:detail_plan', pk=plan.pk)
    else:
        form = PlanActionForm(instance=plan, user=request.user)
    
    return render(request, 'pa/modifier_plan.html', {'form': form, 'plan': plan})

# Supprimer un plan - Protégé (vérifie que le plan appartient à l'utilisateur)
@login_required(login_url='pa:login')
def supprimer_plan(request, pk):
    plan = get_object_or_404(PlanAction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Plan supprimé avec succès!')
        return redirect('pa:dashboard')
    
    return render(request, 'pa/supprimer_plan.html', {'plan': plan})



@login_required(login_url='pa:login')
def export_plans_csv(request):
    plans = PlanAction.objects.filter(user=request.user).order_by('-date_creation')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plans_action.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Description', 'Direction', 'Porteur', 'Indicateur', 
                     'Date début', 'Date fin', 'Échéance', 'Progression', 'Statut'])
    
    for plan in plans:
        writer.writerow([
            plan.description,
            plan.direction,
            plan.porteur,
            plan.indicateur,
            plan.date_debut.strftime('%d/%m/%Y'),
            plan.date_fin.strftime('%d/%m/%Y'),
            plan.echeance.strftime('%d/%m/%Y'),
            f"{plan.progression}%",
            plan.get_statut_display()
        ])
    
    return response

@login_required(login_url='pa:login')
def export_plans_excel(request):
    plans = PlanAction.objects.filter(user=request.user).order_by('-date_creation')
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Plans d\'action')
    
    # Style pour l'en-tête
    header_style = xlwt.XFStyle()
    header_style.font.bold = True
    header_style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    header_style.pattern.pattern_fore_colour = xlwt.Style.colour_map['orange']
    
    # En-têtes
    headers = ['Description', 'Direction', 'Porteur', 'Indicateur', 
               'Date début', 'Date fin', 'Échéance', 'Progression', 'Statut']
    
    for col, header in enumerate(headers):
        ws.write(0, col, header, header_style)
        # Ajuster la largeur des colonnes
        ws.col(col).width = 5000
    
    # Style pour les dates
    date_style = xlwt.XFStyle()
    date_style.num_format_str = 'DD/MM/YYYY'
    
    # Écrire les données
    for row, plan in enumerate(plans, start=1):
        ws.write(row, 0, plan.description)
        ws.write(row, 1, plan.direction)
        ws.write(row, 2, plan.porteur)
        ws.write(row, 3, plan.indicateur)
        ws.write(row, 4, plan.date_debut, date_style)
        ws.write(row, 5, plan.date_fin, date_style)
        ws.write(row, 6, plan.echeance, date_style)
        ws.write(row, 7, f"{plan.progression}%")
        
        # Style pour le statut - CORRECTION ICI
        status_style = xlwt.XFStyle()
        if plan.statut == 'termine':
            status_style.font.colour_index = xlwt.Style.colour_map['green']
        elif plan.statut == 'en_cours':
            status_style.font.colour_index = xlwt.Style.colour_map['orange']
        elif plan.statut == 'annule':
            status_style.font.colour_index = xlwt.Style.colour_map['red']
        else:  # en_attente
            status_style.font.colour_index = xlwt.Style.colour_map['grey25']  # CHANGÉ: 'gray' -> 'grey25'
        
        ws.write(row, 8, plan.get_statut_display(), status_style)
    
    # Ajouter une feuille de statistiques
    ws_stats = wb.add_sheet('Statistiques')
    stats_style = xlwt.XFStyle()
    stats_style.font.bold = True
    stats_style.font.height = 300
    
    ws_stats.write(0, 0, 'Statistiques', stats_style)
    ws_stats.write(2, 0, 'Total des plans:')
    ws_stats.write(2, 1, plans.count())
    ws_stats.write(3, 0, 'Terminés:')
    ws_stats.write(3, 1, plans.filter(statut='termine').count())
    ws_stats.write(4, 0, 'En cours:')
    ws_stats.write(4, 1, plans.filter(statut='en_cours').count())
    ws_stats.write(5, 0, 'En attente:')
    ws_stats.write(5, 1, plans.filter(statut='en_attente').count())
    ws_stats.write(6, 0, 'Annulés:')
    ws_stats.write(6, 1, plans.filter(statut='annule').count())
    
    # Date d'export
    from datetime import datetime
    ws_stats.write(8, 0, 'Export généré le:')
    ws_stats.write(8, 1, datetime.now().strftime('%d/%m/%Y %H:%M'))
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="plans_action.xls"'
    wb.save(response)
    
    return response


@login_required(login_url='pa:login')
def annuler_plan(request, pk):
    """Vue pour annuler un plan"""
    plan = get_object_or_404(PlanAction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        plan.annuler()
        messages.success(request, f'Le plan "{plan.description[:50]}..." a été annulé.')
        return redirect('pa:detail_plan', pk=plan.pk)
    
    return render(request, 'pa/annuler_plan.html', {'plan': plan})

@login_required(login_url='pa:login')
def relancer_plan(request, pk):
    """Vue pour relancer un plan annulé"""
    plan = get_object_or_404(PlanAction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        plan.relancer()
        messages.success(request, f'Le plan "{plan.description[:50]}..." a été relancé.')
        return redirect('pa:detail_plan', pk=plan.pk)
    
    return render(request, 'pa/relancer_plan.html', {'plan': plan})
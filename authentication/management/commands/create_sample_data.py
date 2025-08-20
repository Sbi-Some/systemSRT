from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from intelligence.models import ThreatCategory, HostileGroup, IntelligenceReport, GeographicZone
from analysis.models import Alert
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée des données d\'exemple pour le système SRT'

    def handle(self, *args, **options):
        self.stdout.write('Création des données d\'exemple...')
        
        # Créer des catégories de menaces
        categories = [
            ('Terrorisme', 'TERRORIST', 'Activités terroristes et extrémistes', '#dc2626'),
            ('Criminalité Organisée', 'CRIMINAL', 'Réseaux criminels organisés', '#ea580c'),
            ('Cybermenaces', 'CYBER', 'Attaques informatiques et cyber-espionnage', '#3b82f6'),
            ('Espionnage', 'ESPIONAGE', 'Activités d\'espionnage étatique', '#7c3aed'),
            ('Sabotage', 'SABOTAGE', 'Actes de sabotage d\'infrastructures', '#f59e0b'),
            ('Trafic', 'TRAFFICKING', 'Trafic de drogues, armes, personnes', '#ef4444'),
        ]
        
        for name, cat_type, desc, color in categories:
            category, created = ThreatCategory.objects.get_or_create(
                name=name,
                defaults={
                    'category_type': cat_type,
                    'description': desc,
                    'color_code': color,
                    'priority_weight': random.randint(1, 10)
                }
            )
            if created:
                self.stdout.write(f'Catégorie créée: {name}')

        # Créer des groupes hostiles
        groups = [
            ('Cellule Alpha', ['Terrorisme urbain', 'Groupe Alpha'], 'TERRORIST', 'ACTIVE', 'HIGH'),
            ('Réseau Crimson', ['Red Network', 'Crimson'], 'CRIMINAL', 'ACTIVE', 'MEDIUM'),
            ('Ghost Hackers', ['Phantom Group'], 'CYBER', 'ACTIVE', 'CRITICAL'),
            ('Organisation Omega', ['Omega Cell'], 'ESPIONAGE', 'INACTIVE', 'LOW'),
        ]
        
        for name, aliases, threat_type, status, level in groups:
            group, created = HostileGroup.objects.get_or_create(
                name=name,
                defaults={
                    'aliases': aliases,
                    'description': f'Groupe hostile de type {threat_type}',
                    'estimated_members': random.randint(5, 50),
                    'activity_status': status,
                    'threat_level': level,
                    'known_locations': ['Zone urbaine', 'Périphérie']
                }
            )
            if created:
                self.stdout.write(f'Groupe hostile créé: {name}')

        # Créer des zones géographiques
        zones = [
            ('Zone Urbaine Centre', 'CITY', 'MEDIUM'),
            ('Frontière Est', 'BORDER', 'HIGH'),
            ('Installation Critique A', 'FACILITY', 'CRITICAL'),
            ('Axe Routier Principal', 'ROUTE', 'LOW'),
        ]
        
        for name, zone_type, risk in zones:
            zone, created = GeographicZone.objects.get_or_create(
                name=name,
                defaults={
                    'zone_type': zone_type,
                    'description': f'Zone surveillée de type {zone_type}',
                    'risk_level': risk,
                    'coordinates': {
                        "type": "Polygon",
                        "coordinates": [[[2.0, 46.0], [2.1, 46.0], [2.1, 46.1], [2.0, 46.1], [2.0, 46.0]]]
                    },
                    'is_monitored': True
                }
            )
            if created:
                self.stdout.write(f'Zone géographique créée: {name}')

        # Créer des rapports d'exemple
        agents = User.objects.filter(is_field_agent=True)
        if agents.exists():
            report_types = ['HUMINT', 'SIGINT', 'IMINT', 'OSINT']
            threat_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            
            for i in range(20):
                agent = random.choice(agents)
                report = IntelligenceReport.objects.create(
                    title=f'Rapport de terrain #{i+1:03d}',
                    description=f'Observation d\'activité suspecte dans la zone {random.randint(1, 5)}. '
                               f'Présence de {random.randint(2, 8)} individus non identifiés.',
                    report_type=random.choice(report_types),
                    classification_level=random.choice(['RESTRICTED', 'CONFIDENTIAL', 'SECRET']),
                    source_agent=agent,
                    source_type='FIELD_AGENT',
                    latitude=46.0 + random.uniform(-0.5, 0.5),
                    longitude=2.0 + random.uniform(-0.5, 0.5),
                    location_description=f'Secteur {random.randint(1, 10)}',
                    threat_level=random.choice(threat_levels),
                    confidence_level=random.randint(60, 95),
                    priority=random.randint(1, 5),
                    report_date=timezone.now() - timedelta(days=random.randint(0, 30)),
                    tags=['surveillance', 'terrain', f'zone-{random.randint(1, 5)}']
                )
                
                # Associer des catégories aléatoires
                categories = ThreatCategory.objects.all()
                if categories.exists():
                    report.threat_categories.add(random.choice(categories))
                
                self.stdout.write(f'Rapport créé: {report.title}')

        # Créer des alertes
        users = User.objects.filter(rank__in=['SUPERVISOR', 'MANAGER', 'DIRECTOR'])
        if users.exists():
            alert_levels = ['INFO', 'WARNING', 'CRITICAL', 'EMERGENCY']
            alert_types = ['THREAT_ESCALATION', 'NEW_INTELLIGENCE', 'PATTERN_DETECTED']
            
            for i in range(10):
                alert = Alert.objects.create(
                    title=f'Alerte #{i+1:03d}',
                    message=f'Détection d\'activité anormale nécessitant une attention immédiate.',
                    alert_level=random.choice(alert_levels),
                    alert_type=random.choice(alert_types),
                    created_by=random.choice(users),
                    is_active=random.choice([True, True, True, False])  # 75% actives
                )
                self.stdout.write(f'Alerte créée: {alert.title}')

        self.stdout.write(
            self.style.SUCCESS('\n=== DONNÉES D\'EXEMPLE CRÉÉES ===')
        )
        self.stdout.write('- Catégories de menaces')
        self.stdout.write('- Groupes hostiles')
        self.stdout.write('- Zones géographiques')
        self.stdout.write('- Rapports de renseignement')
        self.stdout.write('- Alertes système')
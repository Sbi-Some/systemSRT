from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée des utilisateurs de test pour le système SRT'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Créer le superutilisateur admin
            if not User.objects.filter(username='admin').exists():
                admin = User.objects.create_superuser(
                    username='admin',
                    email='admin@srt.local',
                    password='admin123',
                    employee_id='AD000001',
                    first_name='Administrateur',
                    last_name='Système',
                    security_clearance='TOP_SECRET',
                    rank='ADMINISTRATOR',
                    department='Administration Système',
                    phone_number='+33123456789',
                    is_field_agent=False
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Superutilisateur créé: {admin.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Superutilisateur admin existe déjà')
                )

            # Créer un directeur
            if not User.objects.filter(username='director').exists():
                director = User.objects.create_user(
                    username='director',
                    email='director@srt.local',
                    password='director123',
                    employee_id='DR000001',
                    first_name='Jean',
                    last_name='Directeur',
                    security_clearance='TOP_SECRET',
                    rank='DIRECTOR',
                    department='Direction Générale',
                    phone_number='+33123456790',
                    is_field_agent=False,
                    is_staff=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Directeur créé: {director.username}')
                )

            # Créer un manager
            if not User.objects.filter(username='manager').exists():
                manager = User.objects.create_user(
                    username='manager',
                    email='manager@srt.local',
                    password='manager123',
                    employee_id='MG000001',
                    first_name='Marie',
                    last_name='Manager',
                    security_clearance='SECRET',
                    rank='MANAGER',
                    department='Opérations',
                    phone_number='+33123456791',
                    is_field_agent=False
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Manager créé: {manager.username}')
                )

            # Créer un superviseur
            if not User.objects.filter(username='supervisor').exists():
                supervisor = User.objects.create_user(
                    username='supervisor',
                    email='supervisor@srt.local',
                    password='supervisor123',
                    employee_id='SV000001',
                    first_name='Pierre',
                    last_name='Superviseur',
                    security_clearance='SECRET',
                    rank='SUPERVISOR',
                    department='Analyse',
                    phone_number='+33123456792',
                    is_field_agent=False
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Superviseur créé: {supervisor.username}')
                )

            # Créer un analyste
            if not User.objects.filter(username='analyst1').exists():
                analyst = User.objects.create_user(
                    username='analyst1',
                    email='analyst1@srt.local',
                    password='analyst123',
                    employee_id='AN000001',
                    first_name='Sophie',
                    last_name='Analyste',
                    security_clearance='CONFIDENTIAL',
                    rank='SENIOR_AGENT',
                    department='Analyse',
                    phone_number='+33123456793',
                    is_field_agent=False
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Analyste créé: {analyst.username}')
                )

            # Créer un agent de terrain
            if not User.objects.filter(username='agent1').exists():
                agent = User.objects.create_user(
                    username='agent1',
                    email='agent1@srt.local',
                    password='agent123',
                    employee_id='AG000001',
                    first_name='Marc',
                    last_name='Agent',
                    security_clearance='RESTRICTED',
                    rank='AGENT',
                    department='Terrain',
                    phone_number='+33123456794',
                    is_field_agent=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Agent de terrain créé: {agent.username}')
                )

            # Créer un agent senior
            if not User.objects.filter(username='agent2').exists():
                agent2 = User.objects.create_user(
                    username='agent2',
                    email='agent2@srt.local',
                    password='agent123',
                    employee_id='AG000002',
                    first_name='Julie',
                    last_name='Agent Senior',
                    security_clearance='CONFIDENTIAL',
                    rank='SENIOR_AGENT',
                    department='Terrain',
                    phone_number='+33123456795',
                    is_field_agent=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Agent senior créé: {agent2.username}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n=== UTILISATEURS DE TEST CRÉÉS ===')
        )
        self.stdout.write('Administrateur: admin / admin123')
        self.stdout.write('Directeur: director / director123')
        self.stdout.write('Manager: manager / manager123')
        self.stdout.write('Superviseur: supervisor / supervisor123')
        self.stdout.write('Analyste: analyst1 / analyst123')
        self.stdout.write('Agent terrain: agent1 / agent123')
        self.stdout.write('Agent senior: agent2 / agent123')
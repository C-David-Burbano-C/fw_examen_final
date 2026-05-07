from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from gestion_proyectos.roles import ROLE_DOCENTE, ROLE_ESTUDIANTE


class Command(BaseCommand):
    help = 'Crea o actualiza los usuarios base del parcial.'

    def handle(self, *args, **options):
        User = get_user_model()

        estudiante_group, _ = Group.objects.get_or_create(name=ROLE_ESTUDIANTE)
        docente_group, _ = Group.objects.get_or_create(name=ROLE_DOCENTE)

        admin = self.upsert_user(
            User,
            username='admin',
            password='Admin12345*',
            is_staff=True,
            is_superuser=True,
            email='admin@example.com',
        )

        docente = self.upsert_user(
            User,
            username='docente',
            password='Docente12345*',
            is_staff=True,
            email='docente@example.com',
        )
        docente.groups.set([docente_group])

        estudiante = self.upsert_user(
            User,
            username='estudiante',
            password='Estudiante12345*',
            email='estudiante@example.com',
        )
        estudiante.groups.set([estudiante_group])

        self.stdout.write(self.style.SUCCESS('Usuarios demo creados o actualizados correctamente.'))
        self.stdout.write('admin / Admin12345*')
        self.stdout.write('docente / Docente12345*')
        self.stdout.write('estudiante / Estudiante12345*')

    def upsert_user(self, User, username, password, **defaults):
        user, _ = User.objects.get_or_create(username=username, defaults=defaults)

        changed = False
        for field, value in defaults.items():
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed = True

        user.set_password(password)
        user.save()

        return user

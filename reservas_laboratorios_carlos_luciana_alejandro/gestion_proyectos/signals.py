from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.mail import send_mail
from django.db.models.signals import post_migrate, post_save

from .roles import DEFAULT_ROLES, ROLE_DOCENTE, ROLE_ESTUDIANTE


def ensure_default_groups(sender, **kwargs):
    estudiante_group, _ = Group.objects.get_or_create(name=ROLE_ESTUDIANTE)
    docente_group, _ = Group.objects.get_or_create(name=ROLE_DOCENTE)

    estudiante_permissions = Permission.objects.filter(
        content_type__app_label='gestion_proyectos',
        codename__in=[
            'add_proyecto',
            'change_proyecto',
            'delete_proyecto',
            'view_proyecto',
            'add_comentario',
            'view_comentario',
        ],
    )
    docente_permissions = Permission.objects.filter(
        content_type__app_label='gestion_proyectos',
        codename__in=[
            'change_proyecto',
            'view_proyecto',
            'add_comentario',
            'view_comentario',
            'revisar_proyecto',
        ],
    )

    estudiante_group.permissions.add(*estudiante_permissions)
    docente_group.permissions.add(*docente_permissions)


def notify_student_on_comment(sender, instance, created, **kwargs):
    if not created or not instance.proyecto.estudiante.email:
        return

    send_mail(
        subject=f'Nuevo comentario en el proyecto: {instance.proyecto.titulo}',
        message=(
            f'{instance.usuario.get_username()} agrego un comentario al proyecto '
            f'"{instance.proyecto.titulo}":\n\n{instance.texto}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[instance.proyecto.estudiante.email],
        fail_silently=True,
    )


def create_default_groups(app_config):
    post_migrate.connect(
        ensure_default_groups,
        sender=app_config,
        dispatch_uid='gestion_proyectos.ensure_default_groups',
    )
    post_save.connect(
        notify_student_on_comment,
        sender=app_config.get_model('Comentario'),
        dispatch_uid='gestion_proyectos.notify_student_on_comment',
    )

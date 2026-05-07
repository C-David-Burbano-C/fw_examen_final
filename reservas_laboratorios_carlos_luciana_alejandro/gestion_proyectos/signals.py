from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate

from .roles import DEFAULT_ROLES


def ensure_default_groups(sender, **kwargs):
    for role_name in DEFAULT_ROLES:
        Group.objects.get_or_create(name=role_name)


def create_default_groups(app_config):
    post_migrate.connect(
        ensure_default_groups,
        sender=app_config,
        dispatch_uid='gestion_proyectos.ensure_default_groups',
    )

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied


ROLE_ESTUDIANTE = 'Estudiante'
ROLE_DOCENTE = 'Docente'
DEFAULT_ROLES = (ROLE_ESTUDIANTE, ROLE_DOCENTE)


def user_has_role(user, role_name):
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name=role_name).exists()


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Protect class-based views by Django group."""

    role_name = None
    raise_exception = True

    def test_func(self):
        if not self.role_name:
            raise ImproperlyConfigured('RoleRequiredMixin requires role_name.')
        return user_has_role(self.request.user, self.role_name)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            self.raise_exception = False
            return super().handle_no_permission()
        raise PermissionDenied(self.get_permission_denied_message())

    def get_permission_denied_message(self):
        return f'Necesitas el rol {self.role_name} para acceder a esta seccion.'

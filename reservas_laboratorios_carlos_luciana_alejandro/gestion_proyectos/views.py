from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .roles import RoleRequiredMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'gestion_proyectos/dashboard.html'


class EstudiantePanelView(RoleRequiredMixin, TemplateView):
    role_name = 'Estudiante'
    template_name = 'gestion_proyectos/estudiante_panel.html'


class DocentePanelView(RoleRequiredMixin, TemplateView):
    role_name = 'Docente'
    template_name = 'gestion_proyectos/docente_panel.html'

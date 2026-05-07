import csv

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import ComentarioForm, ProyectoDocenteForm, ProyectoEstudianteForm
from .models import Comentario, Proyecto
from .roles import ROLE_DOCENTE, ROLE_ESTUDIANTE, RoleRequiredMixin, is_docente, is_estudiante


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'gestion_proyectos/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = proyecto_queryset_for_user(self.request.user)
        context['total_proyectos'] = queryset.count()
        context['proyectos_enviados'] = queryset.filter(estado=Proyecto.ESTADO_ENVIADO).count()
        context['proyectos_revision'] = queryset.filter(estado=Proyecto.ESTADO_REVISION).count()
        context['proyectos_aprobados'] = queryset.filter(estado=Proyecto.ESTADO_APROBADO).count()
        return context


class EstudiantePanelView(RoleRequiredMixin, TemplateView):
    role_name = ROLE_ESTUDIANTE
    template_name = 'gestion_proyectos/estudiante_panel.html'


class DocentePanelView(RoleRequiredMixin, TemplateView):
    role_name = ROLE_DOCENTE
    template_name = 'gestion_proyectos/docente_panel.html'


def proyecto_queryset_for_user(user):
    if is_docente(user):
        return Proyecto.objects.select_related('estudiante').prefetch_related('comentarios')
    return Proyecto.objects.filter(estudiante=user).select_related('estudiante').prefetch_related('comentarios')


class ProyectoAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            self.raise_exception = False
            return super().handle_no_permission()
        raise PermissionDenied('No tienes permiso para acceder a este proyecto.')


class ProyectoListView(LoginRequiredMixin, ListView):
    model = Proyecto
    template_name = 'gestion_proyectos/proyecto_list.html'
    context_object_name = 'proyectos'

    def get_queryset(self):
        queryset = proyecto_queryset_for_user(self.request.user)

        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)

        estudiante = self.request.GET.get('estudiante')
        if estudiante and is_docente(self.request.user):
            queryset = queryset.filter(estudiante_id=estudiante)

        return queryset

    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'csv':
            return self.export_csv()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        context['estado_choices'] = Proyecto.ESTADO_CHOICES
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['estudiante_filtro'] = self.request.GET.get('estudiante', '')
        context['es_docente'] = is_docente(self.request.user)
        context['es_estudiante'] = is_estudiante(self.request.user)
        context['estudiantes'] = User.objects.filter(proyectos__isnull=False).distinct().order_by('username')
        return context

    def export_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="proyectos.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Titulo',
            'Estudiante',
            'Estado',
            'Fecha envio',
            'Fecha revision',
            'Calificacion',
        ])

        for proyecto in self.get_queryset():
            writer.writerow([
                proyecto.titulo,
                proyecto.estudiante.get_username(),
                proyecto.get_estado_display(),
                proyecto.fecha_envio,
                proyecto.fecha_revision or '',
                proyecto.calificacion or '',
            ])

        return response


class ProyectoDetailView(ProyectoAccessMixin, DetailView):
    model = Proyecto
    template_name = 'gestion_proyectos/proyecto_detail.html'
    context_object_name = 'proyecto'

    def get_queryset(self):
        return proyecto_queryset_for_user(self.request.user)

    def test_func(self):
        return self.get_queryset().filter(pk=self.kwargs['pk']).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comentario_form'] = ComentarioForm()
        context['puede_comentar'] = not self.object.esta_aprobado
        context['es_docente'] = is_docente(self.request.user)
        return context


class ProyectoCreateView(RoleRequiredMixin, CreateView):
    role_name = ROLE_ESTUDIANTE
    model = Proyecto
    form_class = ProyectoEstudianteForm
    template_name = 'gestion_proyectos/proyecto_form.html'
    success_url = reverse_lazy('gestion_proyectos:proyecto_list')

    def form_valid(self, form):
        form.instance.estudiante = self.request.user
        messages.success(self.request, 'Proyecto creado correctamente.')
        return super().form_valid(form)


class ProyectoUpdateView(ProyectoAccessMixin, UpdateView):
    model = Proyecto
    form_class = ProyectoEstudianteForm
    template_name = 'gestion_proyectos/proyecto_form.html'
    success_url = reverse_lazy('gestion_proyectos:proyecto_list')

    def get_queryset(self):
        return Proyecto.objects.filter(estudiante=self.request.user)

    def test_func(self):
        return is_estudiante(self.request.user) and self.get_queryset().filter(pk=self.kwargs['pk']).exists()

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto actualizado correctamente.')
        return super().form_valid(form)


class ProyectoDeleteView(ProyectoAccessMixin, DeleteView):
    model = Proyecto
    template_name = 'gestion_proyectos/proyecto_confirm_delete.html'
    success_url = reverse_lazy('gestion_proyectos:proyecto_list')

    def get_queryset(self):
        return Proyecto.objects.filter(estudiante=self.request.user)

    def test_func(self):
        return is_estudiante(self.request.user) and self.get_queryset().filter(pk=self.kwargs['pk']).exists()

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto eliminado correctamente.')
        return super().form_valid(form)


class ProyectoRevisionView(RoleRequiredMixin, UpdateView):
    role_name = ROLE_DOCENTE
    model = Proyecto
    form_class = ProyectoDocenteForm
    template_name = 'gestion_proyectos/proyecto_revision_form.html'
    success_url = reverse_lazy('gestion_proyectos:proyecto_list')

    def form_valid(self, form):
        form.instance.fecha_revision = timezone.now()
        messages.success(self.request, 'Revision guardada correctamente.')
        return super().form_valid(form)


class ComentarioCreateView(LoginRequiredMixin, CreateView):
    model = Comentario
    form_class = ComentarioForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.proyecto = get_object_or_404(proyecto_queryset_for_user(request.user), pk=kwargs['pk'])
        if self.proyecto.esta_aprobado:
            messages.error(request, 'No se pueden agregar comentarios a un proyecto aprobado.')
            return redirect('gestion_proyectos:proyecto_detail', pk=self.proyecto.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.proyecto = self.proyecto
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Comentario agregado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('gestion_proyectos:proyecto_detail', kwargs={'pk': self.proyecto.pk})

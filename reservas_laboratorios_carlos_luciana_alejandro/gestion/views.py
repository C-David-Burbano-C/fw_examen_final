from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q, Count
from django.http import HttpResponse
from django.views.generic.detail import SingleObjectMixin
import csv
from .models import Reserva, Proyecto, Comentario
from .forms import ReservaForm, ProyectoEstudianteForm, ProyectoDocenteForm, ComentarioForm

# --- Vistas para Reserva ---

class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'gestion/reserva_list.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        queryset = Reserva.objects.all()
        
        # Filtro por fecha
        fecha = self.request.GET.get('fecha')
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        
        # Filtro por laboratorio
        laboratorio = self.request.GET.get('laboratorio')
        if laboratorio:
            queryset = queryset.filter(laboratorio=laboratorio)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener laboratorios únicos para el filtro
        context['laboratorios'] = Reserva.objects.values_list('laboratorio', flat=True).distinct()
        
        # Filtros aplicados
        context['fecha_filtro'] = self.request.GET.get('fecha', '')
        context['laboratorio_filtro'] = self.request.GET.get('laboratorio', '')
        
        # Estadísticas agregadas por laboratorio
        reservas = self.get_queryset()
        stats = reservas.values('laboratorio').annotate(count=Count('id')).order_by('-count')
        context['stats'] = stats
        
        return context

    def get(self, request, *args, **kwargs):
        # Exportar a CSV si se pasa el parámetro
        if request.GET.get('export') == 'csv':
            return self.export_csv()
        return super().get(request, *args, **kwargs)

    def export_csv(self):
        reservas = self.get_queryset()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reservas.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Laboratorio', 'Fecha', 'Hora Inicio', 'Hora Fin', 'Usuario'])
        
        for reserva in reservas:
            writer.writerow([reserva.laboratorio, reserva.fecha, reserva.hora_inicio, reserva.hora_fin, reserva.usuario.username])
        
        return response

class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'gestion/reserva_form.html'
    success_url = reverse_lazy('reserva_list')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class ReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'gestion/reserva_form.html'
    success_url = reverse_lazy('reserva_list')

    def test_func(self):
        reserva = self.get_object()
        return reserva.usuario == self.request.user

class ReservaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reserva
    template_name = 'gestion/reserva_confirm_delete.html'
    success_url = reverse_lazy('reserva_list')

    def test_func(self):
        reserva = self.get_object()
        return reserva.usuario == self.request.user


# --- Vistas para Proyecto ---

class ProyectoListView(LoginRequiredMixin, ListView):
    model = Proyecto
    template_name = 'gestion/proyecto_list.html'
    context_object_name = 'proyectos'

    def get_queryset(self):
        user = self.request.user
        
        # Base queryset
        if user.groups.filter(name='Docente').exists() or user.is_staff:
            queryset = Proyecto.objects.all()
        else:
            queryset = Proyecto.objects.filter(estudiante=user)
        
        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtro por estudiante (solo para docentes/staff)
        if user.groups.filter(name='Docente').exists() or user.is_staff:
            estudiante = self.request.GET.get('estudiante')
            if estudiante:
                queryset = queryset.filter(estudiante__username=estudiante)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Filtros aplicados
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['estudiante_filtro'] = self.request.GET.get('estudiante', '')
        context['es_docente'] = user.groups.filter(name='Docente').exists() or user.is_staff
        
        # Estudiantes disponibles para docentes
        if context['es_docente']:
            context['estudiantes'] = Proyecto.objects.values_list('estudiante__username', flat=True).distinct()
        
        # Estadísticas agregadas por estado
        proyectos = self.get_queryset()
        stats = proyectos.values('estado').annotate(count=Count('id')).order_by('estado')
        context['stats'] = stats
        
        return context

    def get(self, request, *args, **kwargs):
        # Exportar a CSV si se pasa el parámetro
        if request.GET.get('export') == 'csv':
            return self.export_csv()
        return super().get(request, *args, **kwargs)

    def export_csv(self):
        proyectos = self.get_queryset()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="proyectos.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Título', 'Estudiante', 'Docente', 'Estado', 'Calificación'])
        
        for proyecto in proyectos:
            docente = proyecto.docente.username if proyecto.docente else 'N/A'
            calificacion = proyecto.calificacion if proyecto.calificacion else 'N/A'
            writer.writerow([proyecto.titulo, proyecto.estudiante.username, docente, proyecto.estado, calificacion])
        
        return response

class ProyectoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Proyecto
    form_class = ProyectoEstudianteForm
    template_name = 'gestion/proyecto_form.html'
    success_url = reverse_lazy('proyecto_list')

    def test_func(self):
        # Docentes no crean proyectos
        user = self.request.user
        return not (user.groups.filter(name='Docente').exists() or user.is_staff)

    def form_valid(self, form):
        form.instance.estudiante = self.request.user
        return super().form_valid(form)

class ProyectoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Proyecto
    template_name = 'gestion/proyecto_form.html'
    success_url = reverse_lazy('proyecto_list')

    def get_form_class(self):
        user = self.request.user
        if user.groups.filter(name='Docente').exists() or user.is_staff:
            return ProyectoDocenteForm
        return ProyectoEstudianteForm

    def test_func(self):
        proyecto = self.get_object()
        user = self.request.user
        if user.groups.filter(name='Docente').exists() or user.is_staff:
            return True
        return proyecto.estudiante == user

    def form_valid(self, form):
        user = self.request.user
        if user.groups.filter(name='Docente').exists() or user.is_staff:
            form.instance.docente = user
        return super().form_valid(form)

class ProyectoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Proyecto
    template_name = 'gestion/proyecto_confirm_delete.html'
    success_url = reverse_lazy('proyecto_list')

    def test_func(self):
        proyecto = self.get_object()
        user = self.request.user
        return proyecto.estudiante == user


# --- Vistas para Comentario ---

class ComentarioCreateView(LoginRequiredMixin, CreateView):
    model = Comentario
    form_class = ComentarioForm
    template_name = 'gestion/comentario_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.proyecto = get_object_or_404(Proyecto, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.autor = self.request.user
        form.instance.proyecto = self.proyecto
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('proyecto_list')

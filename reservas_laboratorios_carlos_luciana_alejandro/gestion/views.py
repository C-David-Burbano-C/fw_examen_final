from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from .models import Reserva, Proyecto
from .forms import ReservaForm, ProyectoEstudianteForm, ProyectoDocenteForm

# --- Vistas para Reserva ---

class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'gestion/reserva_list.html'
    context_object_name = 'reservas'

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
        # Se asume que el docente es superuser/staff o pertenece a un grupo "Docente"
        if user.groups.filter(name='Docente').exists() or user.is_staff:
            return Proyecto.objects.all()
        return Proyecto.objects.filter(estudiante=user)

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

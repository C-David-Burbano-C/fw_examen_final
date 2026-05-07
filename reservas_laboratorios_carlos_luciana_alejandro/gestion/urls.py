from django.urls import path
from .views import (
    ReservaListView, ReservaCreateView, ReservaUpdateView, ReservaDeleteView,
    ProyectoListView, ProyectoCreateView, ProyectoUpdateView, ProyectoDeleteView,
    ComentarioCreateView
)

urlpatterns = [
    path('reservas/', ReservaListView.as_view(), name='reserva_list'),
    path('reservas/nueva/', ReservaCreateView.as_view(), name='reserva_create'),
    path('reservas/<int:pk>/editar/', ReservaUpdateView.as_view(), name='reserva_update'),
    path('reservas/<int:pk>/eliminar/', ReservaDeleteView.as_view(), name='reserva_delete'),
    
    path('proyectos/', ProyectoListView.as_view(), name='proyecto_list'),
    path('proyectos/nuevo/', ProyectoCreateView.as_view(), name='proyecto_create'),
    path('proyectos/<int:pk>/editar/', ProyectoUpdateView.as_view(), name='proyecto_update'),
    path('proyectos/<int:pk>/eliminar/', ProyectoDeleteView.as_view(), name='proyecto_delete'),
    path('proyectos/<int:pk>/comentar/', ComentarioCreateView.as_view(), name='proyecto_comentar'),
]

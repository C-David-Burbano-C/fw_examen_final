from django.urls import path

from .views import (
    ComentarioCreateView,
    DashboardView,
    DocentePanelView,
    EstudiantePanelView,
    ProyectoCreateView,
    ProyectoDeleteView,
    ProyectoDetailView,
    ProyectoListView,
    ProyectoRevisionView,
    ProyectoUpdateView,
)

app_name = 'gestion_proyectos'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('estudiante/', EstudiantePanelView.as_view(), name='estudiante_panel'),
    path('docente/', DocentePanelView.as_view(), name='docente_panel'),
    path('proyectos/', ProyectoListView.as_view(), name='proyecto_list'),
    path('proyectos/nuevo/', ProyectoCreateView.as_view(), name='proyecto_create'),
    path('proyectos/<int:pk>/', ProyectoDetailView.as_view(), name='proyecto_detail'),
    path('proyectos/<int:pk>/editar/', ProyectoUpdateView.as_view(), name='proyecto_update'),
    path('proyectos/<int:pk>/eliminar/', ProyectoDeleteView.as_view(), name='proyecto_delete'),
    path('proyectos/<int:pk>/revision/', ProyectoRevisionView.as_view(), name='proyecto_revision'),
    path('proyectos/<int:pk>/comentarios/nuevo/', ComentarioCreateView.as_view(), name='comentario_create'),
]

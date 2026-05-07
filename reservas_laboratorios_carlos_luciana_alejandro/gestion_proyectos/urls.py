from django.urls import path

from .views import DashboardView, DocentePanelView, EstudiantePanelView

app_name = 'gestion_proyectos'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('estudiante/', EstudiantePanelView.as_view(), name='estudiante_panel'),
    path('docente/', DocentePanelView.as_view(), name='docente_panel'),
]

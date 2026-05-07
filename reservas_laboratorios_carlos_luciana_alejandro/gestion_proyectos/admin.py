from django.contrib import admin

from .models import Comentario, Proyecto


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ['usuario', 'fecha']


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'estudiante', 'estado', 'calificacion', 'fecha_envio', 'fecha_revision']
    list_filter = ['estado', 'estudiante']
    search_fields = ['titulo', 'descripcion', 'estudiante__username']
    readonly_fields = ['fecha_envio']
    inlines = [ComentarioInline]


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['proyecto', 'usuario', 'fecha']
    list_filter = ['fecha', 'usuario']
    search_fields = ['proyecto__titulo', 'usuario__username', 'texto']

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Categoria, Producto, Venta, DetalleVenta, MovimientoStock, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    list_display = (
        'username',
        'email',
        'rol',
        'is_active',
        'is_staff',
        'is_superuser'
    )

    list_filter = (
        'rol',
        'is_active',
        'is_staff'
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rol',)
        }),
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'fecha_creacion')
    search_fields = ('nombre',)
    list_filter = ('activa',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sku', 'categoria', 'precio_venta', 'stock', 'activo')
    search_fields = ('nombre', 'sku')
    list_filter = ('categoria', 'activo')


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero_venta', 'vendedor', 'total', 'cantidad_items', 'estado', 'fecha_venta')
    list_filter = ('estado', 'fecha_venta')
    search_fields = ('numero_venta',)
    inlines = [DetalleVentaInline]


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('producto__nombre',)
from django.contrib import admin
from django.utils.html import format_html
from .models import Usuario, Categoria, Producto, Venta, DetalleVenta, MovimientoStock

# ========================
# USUARIO
# ========================
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'get_nombre_completo', 'rol', 'email', 'es_activo', 'fecha_creacion')
    list_filter = ('rol', 'es_activo', 'fecha_creacion')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = (
        ('Información Personal', {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password')
        }),
        ('Datos de Sistema', {
            'fields': ('rol', 'documento', 'telefono')
        }),
        ('Permisos', {
            'fields': ('is_staff', 'is_superuser', 'es_activo', 'groups', 'user_permissions')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'last_login')
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username
    get_nombre_completo.short_description = 'Nombre Completo'


# ========================
# CATEGORÍA
# ========================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'mostrar_imagen', 'obtener_total_stock', 'activa')
    list_editable = ('activa',)
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'descripcion')
        }),
        ('Imagen y Diseño', {
            'fields': ('imagen', 'color_hex')
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
    )
    
    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;" />',
                obj.imagen.url
            )
        return '—'
    mostrar_imagen.short_description = 'Vista Previa'


# ========================
# PRODUCTO
# ========================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 
        'sku', 
        'categoria', 
        'precio_venta', 
        'stock',
        'mostrar_estado', 
        'margen_ganancia_display'
    )
    list_filter = ('categoria', 'activo', 'fecha_ingreso')
    search_fields = ('nombre', 'sku', 'descripcion')
    readonly_fields = ('fecha_ingreso', 'fecha_actualizacion', 'margen_ganancia_display')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'sku', 'categoria', 'descripcion')
        }),
        ('Precios', {
            'fields': ('precio_costo', 'precio_venta', 'margen_ganancia_display')
        }),
        ('Inventario', {
            'fields': ('stock', 'stock_minimo', 'mostrar_estado')
        }),
        ('Media', {
            'fields': ('imagen',)
        }),
        ('Sistema', {
            'fields': ('activo', 'fecha_ingreso', 'fecha_actualizacion')
        }),
    )
    
    def mostrar_estado(self, obj):
        colores = {
            'disponible': '#28a745',
            'bajo_stock': '#ffc107',
            'agotado': '#dc3545'
        }
        estado_texto = dict(obj.ESTADO_CHOICES)
        return format_html(
            '<span style="color: white; background: {}; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colores.get(obj.estado, '#000'),
            estado_texto.get(obj.estado, obj.estado)
        )
    mostrar_estado.short_description = 'Estado'
    
    def margen_ganancia_display(self, obj):
        return f"{obj.margen_ganancia:.1f}%"
    margen_ganancia_display.short_description = 'Margen (%)'


# ========================
# VENTA Y DETALLES
# ========================
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero_venta', 'vendedor', 'fecha_venta', 'cantidad_items', 'total', 'estado')
    list_filter = ('estado', 'fecha_venta', 'vendedor')
    search_fields = ('numero_venta',)
    readonly_fields = ('fecha_venta',)
    inlines = [DetalleVentaInline]


# ========================
# MOVIMIENTO DE STOCK
# ========================
@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'fecha')
    list_filter = ('tipo', 'fecha', 'usuario')
    search_fields = ('producto__nombre',)
    readonly_fields = ('fecha',)
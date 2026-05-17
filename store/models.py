from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils.text import slugify

# ========================
# 1. USUARIO PERSONALIZADO
# ========================
class Usuario(AbstractUser):
    """Usuario del sistema con roles diferenciados"""
    ROLES = [
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('almacenero', 'Almacenero'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='vendedor')
    telefono = models.CharField(max_length=15, blank=True)
    documento = models.CharField(max_length=20, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    es_activo = models.BooleanField(default=True)
    
    # ⚠️ Agregar related_name personalizados
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='store_usuario_groups',  # ← AGREGAR ESTO
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='store_usuario_permissions',  # ← AGREGAR ESTO
        blank=True
    )
    
    class Meta:
        db_table = 'usuarios'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

# ========================
# 2. CATEGORÍA (CON IMAGEN)
# ========================
class Categoria(models.Model):
    """Categorías de productos con imágenes"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(
        upload_to='categorias/',
        blank=True,
        null=True,
        help_text="Imagen representativa de la categoría"
    )
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    color_hex = models.CharField(
        max_length=7, 
        default='#003366',
        help_text="Color de tema para la categoría (ej: #003366)"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categorias'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre
    
    def obtener_total_stock(self):
        """Retorna el stock total de productos en esta categoría"""
        return sum(p.stock for p in self.productos.filter(activo=True))


# ========================
# 3. PRODUCTO
# ========================
class Producto(models.Model):
    """Productos del inventario"""
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('bajo_stock', 'Bajo Stock'),
        ('agotado', 'Agotado'),
    ]
    
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True)
    sku = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="SKU",
        help_text="Código único del producto"
    )
    precio_costo = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Precio de Costo"
    )
    precio_venta = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Precio de Venta"
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='productos'
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    stock_minimo = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        help_text="Nivel de stock que activa alerta"
    )
    imagen = models.ImageField(
        upload_to='productos/%Y/%m/',
        blank=True,
        null=True
    )
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'productos'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_ingreso']
        indexes = [
            models.Index(fields=['categoria', 'activo']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return f"{self.nombre} (SKU: {self.sku})"
    
    @property
    def estado(self):
        """Estado dinámico del producto"""
        if self.stock == 0:
            return 'agotado'
        elif self.stock <= self.stock_minimo:
            return 'bajo_stock'
        return 'disponible'
    
    @property
    def margen_ganancia(self):
        """Calcula margen de ganancia en porcentaje"""
        if self.precio_costo == 0:
            return 0
        return ((self.precio_venta - self.precio_costo) / self.precio_costo) * 100
    
    def esta_disponible(self):
        return self.stock > 0 and self.activo


# ========================
# 4. VENTA
# ========================
class Venta(models.Model):
    """Registro de ventas del sistema"""
    numero_venta = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name="Número de Venta"
    )
    vendedor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ventas'
    )
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cantidad_items = models.IntegerField(default=0)
    estado = models.CharField(
        max_length=20,
        choices=[('completada', 'Completada'), ('cancelada', 'Cancelada')],
        default='completada'
    )
    notas = models.TextField(blank=True)
    
    class Meta:
        db_table = 'ventas'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta {self.numero_venta} - ${self.total}"


# ========================
# 5. DETALLE DE VENTA
# ========================
class DetalleVenta(models.Model):
    """Items individuales de cada venta"""
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        related_name='detalles_venta'
    )
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'detalles_venta'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"


# ========================
# 6. MOVIMIENTO DE STOCK
# ========================
class MovimientoStock(models.Model):
    """Log de todos los movimientos de stock"""
    TIPO_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('venta', 'Venta'),
    ]
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='movimientos'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    stock_anterior = models.IntegerField()
    stock_nuevo = models.IntegerField()
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(blank=True)
    
    class Meta:
        db_table = 'movimientos_stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad})"
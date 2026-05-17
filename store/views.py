from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Q, Count, F
from django.utils import timezone
from datetime import timedelta
from .models import Categoria, Producto, Venta, DetalleVenta, MovimientoStock, Usuario
import json
from decimal import Decimal


def requiere_rol(roles_permitidos):
    def decorator(func):
        from functools import wraps
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.rol in roles_permitidos:
                return func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso para acceder aquí.")
        return wrapper
    return decorator

@login_required(login_url='store:login')
def eliminar_categoria(request, pk):

    if request.method == 'POST':

        categoria = get_object_or_404(Categoria, pk=pk)

        categoria.delete()

        messages.success(
            request,
            'Categoría eliminada correctamente.'
        )

    return redirect('store:categorias')

@login_required(login_url='store:login')  
def dashboard(request):
    """Dashboard principal del sistema"""
    total_productos = Producto.objects.filter(activo=True).count()
    productos_bajo_stock = Producto.objects.filter(
        Q(stock__lte=F('stock_minimo')) & Q(activo=True)
    ).count()
    
    hoy = timezone.localdate()
    ventas_hoy = Venta.objects.filter(
        fecha_venta__date=hoy
    ).aggregate(total=Sum('total'))['total'] or 0
    
    total_categorias = Categoria.objects.filter(activa=True).count()
    ultimas_ventas = Venta.objects.all()[:5]
    productos_top = Producto.objects.annotate(
        total_vendido=Count('detalles_venta')
    ).order_by('-total_vendido')[:5]
    
    context = {
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'ventas_hoy': ventas_hoy,
        'total_categorias': total_categorias,
        'ultimas_ventas': ultimas_ventas,
        'productos_top': productos_top,
    }
    return render(request, 'dashboard.html', context)



@login_required(login_url='store:login')  
def inventario(request):
    """Lista completa del inventario con filtros"""
    productos = Producto.objects.select_related('categoria').filter(activo=True)
    
    categoria_id = request.GET.get('categoria')
    estado = request.GET.get('estado')
    busqueda = request.GET.get('busqueda')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if estado:
        if estado == 'bajo_stock':
            productos = productos.filter(stock__lte=F('stock_minimo'))
        elif estado == 'agotado':
            productos = productos.filter(stock=0)
    
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(sku__icontains=busqueda)
        )
    
    categorias = Categoria.objects.filter(activa=True)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'estado_seleccionado': estado,
        'busqueda': busqueda,
    }
    return render(request, 'inventario.html', context)



@login_required(login_url='store:login')  
@require_http_methods(["GET", "POST"])
def crear_producto(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        try:
            producto = Producto.objects.create(
                nombre=request.POST['nombre'],
                sku=request.POST['sku'],
                descripcion=request.POST.get('descripcion', ''),
                precio_costo=request.POST['precio_costo'],
                precio_venta=request.POST['precio_venta'],
                categoria_id=request.POST['categoria'],
                stock=request.POST['stock'],
                stock_minimo=request.POST.get('stock_minimo', 5),
                imagen=request.FILES.get('imagen'),
            )
            return redirect('store:inventario')
        except Exception as e:
            context = {
                'categorias': Categoria.objects.filter(activa=True),
                'error': str(e)
            }
            return render(request, 'crear_producto.html', context)
    
    context = {
        'categorias': Categoria.objects.filter(activa=True),
    }
    return render(request, 'crear_producto.html', context)


@login_required(login_url='store:login') 
def editar_producto(request, pk):
    """Editar producto existente"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.sku = request.POST['sku']
        producto.descripcion = request.POST.get('descripcion', '')
        producto.precio_costo = request.POST['precio_costo']
        producto.precio_venta = request.POST['precio_venta']
        producto.stock = int(request.POST.get('stock', 0))
        producto.categoria_id = request.POST['categoria']
        producto.stock_minimo = request.POST.get('stock_minimo', 5)
        if request.FILES.get('imagen'):
            producto.imagen = request.FILES['imagen']
        producto.save()

        messages.success(
            request,
            f'Producto "{producto.nombre}" actualizado correctamente.'
        )
        
        return redirect('store:inventario')
    
    context = {
        'producto': producto,
        'categorias': Categoria.objects.filter(activa=True),
    }
    return render(request, 'editar_producto.html', context)


@login_required(login_url='store:login')
def eliminar_producto(request, pk):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=pk)
        producto.activo = False
        producto.save()

        messages.success(request, f'Producto "{producto.nombre}" eliminado correctamente.')

    return redirect('store:inventario')



@login_required(login_url='store:login')  
def categorias(request):
    """Listar categorías"""
    todas_categorias = Categoria.objects.all()
    context = {'categorias': todas_categorias}
    return render(request, 'categorias.html', context)


@login_required(login_url='store:login')  
def crear_categoria(request):
    """Crear categoría"""
    if request.method == 'POST':
        categoria = Categoria.objects.create(
            nombre=request.POST['nombre'],
            descripcion=request.POST.get('descripcion', ''),
            imagen=request.FILES.get('imagen'),
            color_hex=request.POST.get('color_hex', '#003366'),
        )
        return redirect('store:categorias')
    
    return render(request, 'crear_categoria.html')


@login_required(login_url='store:login')
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        categoria.nombre = request.POST['nombre']
        categoria.descripcion = request.POST.get('descripcion', '')
        categoria.color_hex = request.POST.get('color_hex', categoria.color_hex)

        if request.FILES.get('imagen'):
            categoria.imagen = request.FILES['imagen']

        categoria.save()

        messages.success(
            request,
            f'Categoría "{categoria.nombre}" actualizada correctamente.'
        )

        return redirect('store:categorias')

    context = {'categoria': categoria}
    return render(request, 'editar_categoria.html', context)



@login_required(login_url='store:login')  
def ventas(request):
    """Listar todas las ventas"""
    todas_ventas = Venta.objects.prefetch_related('detalles').order_by('-fecha_venta')
    context = {'ventas': todas_ventas}
    return render(request, 'ventas.html', context)


@login_required(login_url='store:login')
def crear_venta(request):
    """Crear nueva venta y descontar stock."""

    productos = Producto.objects.filter(
        activo=True,
        stock__gt=0
    ).select_related('categoria')

    if request.method == 'POST':
        try:
            carrito = json.loads(request.POST.get('carrito', '[]'))

            if not carrito:
                messages.error(request, 'Agrega al menos un producto a la venta.')
                return render(request, 'crear_venta.html', {
                    'productos': productos
                })

            subtotal_general = Decimal('0')
            detalles_temporales = []

            for item in carrito:
                producto = get_object_or_404(
                    Producto,
                    id=item['id'],
                    activo=True
                )

                cantidad = int(item['cantidad'])

                if cantidad <= 0:
                    raise ValueError('La cantidad debe ser mayor a cero.')

                if producto.stock < cantidad:
                    raise ValueError(
                        f'Stock insuficiente para {producto.nombre}. '
                        f'Disponible: {producto.stock}'
                    )

                precio = producto.precio_venta
                subtotal = precio * cantidad

                subtotal_general += subtotal

                detalles_temporales.append(
                    (producto, cantidad, precio, subtotal)
                )

            numero = f"V-{timezone.now().strftime('%Y%m%d%H%M%S')}"

            venta = Venta.objects.create(
                numero_venta=numero,
                vendedor=request.user,
                total=subtotal_general,
                cantidad_items=sum(
                    cantidad for _, cantidad, _, _ in detalles_temporales
                ),
                estado='completada'
            )

            for producto, cantidad, precio, subtotal in detalles_temporales:

                stock_anterior = producto.stock

                producto.stock -= cantidad

                producto.save(
                    update_fields=[
                        'stock',
                        'fecha_actualizacion'
                    ]
                )

                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=subtotal
                )

                MovimientoStock.objects.create(
                    producto=producto,
                    tipo='venta',
                    cantidad=-cantidad,
                    stock_anterior=stock_anterior,
                    stock_nuevo=producto.stock,
                    usuario=request.user,
                    motivo=f'Venta {numero}'
                )

            messages.success(
                request,
                f'Venta {venta.numero_venta} registrada correctamente.'
            )

            return redirect('store:crear_venta')

        except Exception as e:
            messages.error(request, str(e))

    context = {
        'productos': productos
    }

    return render(request, 'crear_venta.html', context)


@login_required(login_url='store:login')
def productos(request):
    productos_qs = Producto.objects.filter(activo=True).select_related('categoria')
    categoria_slug = request.GET.get('categoria')
    if categoria_slug:
        productos_qs = productos_qs.filter(categoria__slug=categoria_slug)
    categorias_qs = Categoria.objects.filter(activa=True)
    return render(request, 'productos.html', {'productos': productos_qs, 'categorias': categorias_qs})


@login_required(login_url='store:login')
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto.objects.select_related('categoria'), pk=pk, activo=True)
    relacionados = Producto.objects.filter(categoria=producto.categoria, activo=True).exclude(pk=pk)[:4]
    return render(request, 'detalle_producto.html', {'producto': producto, 'relacionados': relacionados})


@login_required(login_url='store:login')
def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')


@login_required(login_url='store:login')
def contacto(request):
    return render(request, 'contacto.html')


@login_required(login_url='store:login')
@requiere_rol(['admin'])
def usuarios(request):
    usuarios_sistema = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'usuarios.html', {'usuarios': usuarios_sistema})


@login_required(login_url='store:login')
@requiere_rol(['admin'])
@require_http_methods(["GET", "POST"])
def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST.get('email', '').strip()
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        rol = request.POST.get('rol', 'vendedor')

        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'crear_usuario.html')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'Ese usuario ya existe.')
            return render(request, 'crear_usuario.html')

        usuario = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            rol=rol,
            is_staff=(rol == 'admin'),
            is_superuser=False,
        )
        usuario.es_activo = True
        usuario.save()

        messages.success(request, 'Usuario creado correctamente.')
        return redirect('store:usuarios')

    return render(request, 'crear_usuario.html')


def register(request):
    """Registro público deshabilitado: los usuarios se crean desde el sistema."""
    messages.error(request, 'El registro público está deshabilitado. Solicita acceso a un administrador.')
    return redirect('store:login')

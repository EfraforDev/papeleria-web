from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'store'

urlpatterns = [
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='store:login'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Productos públicos internos
    path('productos/', views.productos, name='productos'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('contacto/', views.contacto, name='contacto'),

    # Inventario
    path('inventario/', views.inventario, name='inventario'),
    path('producto/crear/', views.crear_producto, name='crear_producto'),
    path('producto/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    
    # Categorías
    path('categorias/', views.categorias, name='categorias'),
    path('categoria/crear/', views.crear_categoria, name='crear_categoria'),
    path('categoria/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    
    # Ventas
    path('ventas/', views.ventas, name='ventas'),
    path('venta/crear/', views.crear_venta, name='crear_venta'),

    # Usuarios internos
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),

    # Eliminar categoria. 
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='eliminar_categoria'),

    # Eliminar producto
    path('producto/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
]
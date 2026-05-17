// ===========================
// CARRITO DE COMPRAS (localStorage)
// ===========================

class CarritoCompras {
    constructor() {
        this.items = this.cargarCarrito();
    }
    
    agregar(id, nombre, precio) {
        const existente = this.items.find(item => item.id === id);
        
        if (existente) {
            existente.cantidad++;
        } else {
            this.items.push({ id, nombre, precio, cantidad: 1 });
        }
        
        this.guardarCarrito();
        this.mostrarNotificacion(`"${nombre}" agregado al carrito ✓`);
    }
    
    obtenerTotal() {
        return this.items.reduce((total, item) => total + (item.precio * item.cantidad), 0);
    }
    
    guardarCarrito() {
        localStorage.setItem('carrito', JSON.stringify(this.items));
    }
    
    cargarCarrito() {
        return JSON.parse(localStorage.getItem('carrito')) || [];
    }
    
    mostrarNotificacion(mensaje) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alert.style.top = '80px';
        alert.style.right = '20px';
        alert.style.zIndex = '1050';
        alert.style.minWidth = '300px';
        alert.innerHTML = `
            <i class="fas fa-check-circle"></i> ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        
        setTimeout(() => alert.remove(), 3000);
    }
}

// Se eliminó la instancia global para evitar conflicto con crear_venta.html

// ===========================
// VALIDACIÓN DE FORMULARIOS
// ===========================

document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// ===========================
// EFFECTS Y UTILIDADES
// ===========================

// Smooth scroll para enlaces
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Animación de scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.card').forEach(el => observer.observe(el));
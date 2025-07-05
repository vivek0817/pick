// Main JavaScript file for Pickles Store

document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to all links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add loading animation to buttons
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            this.disabled = true;
        });
    });

    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Add to cart animation
    const addToCartButtons = document.querySelectorAll('a[href*="add_to_cart"]');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add a small delay to show the animation
            setTimeout(() => {
                // You can add custom animation here
                console.log('Product added to cart!');
            }, 100);
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });

    // Success page animation
    const successElement = document.querySelector('.text-success');
    if (successElement) {
        successElement.classList.add('success-animation');
    }
});

// Utility function to format currency
function formatCurrency(amount) {
    return '₹' + amount.toFixed(2);
}

// Utility function to update cart count
function updateCartCount(count) {
    const cartBadge = document.querySelector('.badge');
    if (cartBadge) {
        cartBadge.textContent = count;
    }
} 
// Initialize tooltips and delete confirmations
document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Delete confirmation handler
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const itemName = form.getAttribute('data-item-name') || 'this item';
            if (!confirm(`Are you sure you want to delete "${itemName}"? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });
});

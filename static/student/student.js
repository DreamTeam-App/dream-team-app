document.addEventListener('DOMContentLoaded', function() {
    // User Menu Toggle
    const userMenuButton = document.getElementById('userMenuButton');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuButton && userDropdown) {
        userMenuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (userDropdown.classList.contains('show') && !userDropdown.contains(e.target) && e.target !== userMenuButton) {
                userDropdown.classList.remove('show');
            }
        });
    }
    
    // Join Class Modal
    const joinClassBtn = document.getElementById('joinClassBtn');
    const joinClassModal = document.getElementById('joinClassModal');
    const closeModal = document.querySelector('.close-modal');
    const cancelJoinClass = document.getElementById('cancelJoinClass');
    
    if (joinClassBtn && joinClassModal) {
        joinClassBtn.addEventListener('click', function() {
            joinClassModal.classList.add('show');
        });
        
        // Close modal with X button
        if (closeModal) {
            closeModal.addEventListener('click', function() {
                joinClassModal.classList.remove('show');
            });
        }
        
        // Close modal with Cancel button
        if (cancelJoinClass) {
            cancelJoinClass.addEventListener('click', function() {
                joinClassModal.classList.remove('show');
            });
        }
        
        // Close modal when clicking outside
        joinClassModal.addEventListener('click', function(e) {
            if (e.target === joinClassModal) {
                joinClassModal.classList.remove('show');
            }
        });
    }
    
    // Logout functionality
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', function(e) {
            e.preventDefault();
            // Aquí iría la lógica para cerrar sesión
            alert('Cerrando sesión...');
            // Redireccionar a la página de login o home después de cerrar sesión
            // window.location.href = '/login';
        });
    }
});
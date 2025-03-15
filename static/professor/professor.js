document.addEventListener('DOMContentLoaded', function() {
    // Class selector dropdown
    const classSelectorBtn = document.getElementById('class-selector-btn');
    const classDropdown = document.getElementById('class-dropdown');
    
    if (classSelectorBtn && classDropdown) {
        classSelectorBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            classDropdown.style.display = classDropdown.style.display === 'block' ? 'none' : 'block';
        });
        
        document.addEventListener('click', function() {
            classDropdown.style.display = 'none';
        });
        
        classDropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // Mobile menu
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const tabs = document.querySelector('.tabs');
    
    if (mobileMenuBtn && tabs) {
        mobileMenuBtn.addEventListener('click', function() {
            tabs.style.display = tabs.style.display === 'grid' ? 'none' : 'grid';
        });
    }
    
    // Mobile class selector
    const mobileClassSelectorBtn = document.getElementById('mobile-class-selector-btn');
    const mobileClassModal = document.getElementById('mobile-class-modal');
    const closeModal = document.getElementById('close-modal');
    
    if (mobileClassSelectorBtn && mobileClassModal) {
        mobileClassSelectorBtn.addEventListener('click', function() {
            mobileClassModal.classList.add('open');
        });
    }
    
    if (closeModal && mobileClassModal) {
        closeModal.addEventListener('click', function() {
            mobileClassModal.classList.remove('open');
        });
        
        mobileClassModal.addEventListener('click', function(e) {
            if (e.target === mobileClassModal) {
                mobileClassModal.classList.remove('open');
            }
        });
    }
    
    // Create placeholder image for demo
    const placeholderImage = document.createElement('img');
    placeholderImage.src = 'data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%2240%22%20height%3D%2240%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2040%2040%22%20preserveAspectRatio%3D%22none%22%3E%3Cdefs%3E%3Cstyle%20type%3D%22text%2Fcss%22%3E%23holder_1%20text%20%7B%20fill%3A%23999%3Bfont-weight%3Anormal%3Bfont-family%3AArial%2C%20Helvetica%2C%20Open%20Sans%2C%20sans-serif%2C%20monospace%3Bfont-size%3A10pt%20%7D%20%3C%2Fstyle%3E%3C%2Fdefs%3E%3Cg%20id%3D%22holder_1%22%3E%3Crect%20width%3D%2240%22%20height%3D%2240%22%20fill%3D%22%23eee%22%3E%3C%2Frect%3E%3Cg%3E%3Ctext%20x%3D%2214.5%22%20y%3D%2220%22%3E%3C%2Ftext%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E';
    placeholderImage.alt = 'Placeholder';
    
    // Replace missing images with placeholder
    document.querySelectorAll('img').forEach(img => {
        img.onerror = function() {
            this.src = placeholderImage.src;
        };
    });
    
    // Team row expansion
    const teamRows = document.querySelectorAll('.team-row');
    teamRows.forEach(row => {
        row.addEventListener('click', function() {
            const teamId = this.getAttribute('data-team-id');
            const detailsRow = document.getElementById('details-' + teamId);
            
            if (detailsRow) {
                if (detailsRow.classList.contains('expanded')) {
                    detailsRow.classList.remove('expanded');
                } else {
                    // Close any open details first
                    document.querySelectorAll('.team-details-row.expanded').forEach(el => {
                        el.classList.remove('expanded');
                    });
                    detailsRow.classList.add('expanded');
                }
            }
        });
    });
});

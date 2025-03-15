document.addEventListener('DOMContentLoaded', function() {
    // Team row click handler
    const teamRows = document.querySelectorAll('.team-row');
    teamRows.forEach(row => {
        row.addEventListener('click', function() {
            const teamId = this.getAttribute('data-team-id');
            const detailsRow = document.getElementById('details-' + teamId);
            
            // Toggle details visibility
            if (detailsRow.classList.contains('expanded')) {
                detailsRow.classList.remove('expanded');
            } else {
                // Close any open details first
                document.querySelectorAll('.team-details-row.expanded').forEach(el => {
                    el.classList.remove('expanded');
                });
                detailsRow.classList.add('expanded');
            }
        });
    });
});
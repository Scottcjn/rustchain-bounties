document.addEventListener('DOMContentLoaded', function() {
    // Add click handlers to machine entries
    const machineEntries = document.querySelectorAll('.machine-entry');
    
    machineEntries.forEach(entry => {
        entry.style.cursor = 'pointer';
        
        entry.addEventListener('click', function() {
            const fingerprintHash = this.dataset.fingerprintHash;
            if (fingerprintHash) {
                window.location.href = `/machine-detail?fingerprint_hash=${fingerprintHash}`;
            }
        });
        
        // Add hover effect
        entry.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
        });
        
        entry.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
});
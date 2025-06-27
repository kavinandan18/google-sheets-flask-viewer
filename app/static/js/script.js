// Show loading spinner
function showLoadingSpinner() {
    document.getElementById('loading-spinner').classList.remove('hidden');
}

// Hide loading spinner when page loads
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('loading-spinner').classList.add('hidden');
});

// Ensure sticky header adjusts to window resize
window.addEventListener('resize', function() {
    const thead = document.querySelector('thead.sticky');
    if (thead) {
        thead.style.top = `${document.querySelector('header').offsetHeight}px`;
    }
});
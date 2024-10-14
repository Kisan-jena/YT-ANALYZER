document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.body.classList.add(currentTheme + '-mode');
    themeToggle.className = currentTheme === 'light' ? 'ri-moon-fill' : 'ri-sun-fill';

    themeToggle.addEventListener('click', function() {
        const newTheme = document.body.classList.contains('light-mode') ? 'dark' : 'light';
        document.body.classList.toggle('light-mode');
        document.body.classList.toggle('dark-mode');
        themeToggle.className = newTheme === 'light' ? 'ri-moon-fill' : 'ri-sun-fill';
        localStorage.setItem('theme', newTheme);
    });

    // Flash messages auto-hide
    const flashMessages = document.querySelectorAll('#flash-container .flash');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'fade-out 0.5s ease-in-out';
            setTimeout(() => {
                message.remove();
            }, 500); // Match the duration of the fade-out animation
        }, 3000); // Display flash messages for 3 seconds
    });

    // Logout confirmation
    const logoutButton = document.getElementById('logout');
    if (logoutButton) {
        logoutButton.addEventListener('click', function(event) {
            const confirmLogout = confirm('Are you sure you want to logout?');
            if (!confirmLogout) {
                event.preventDefault();  // Prevent logout if the user cancels
            }
        });
    }
});
let counter = 1;
setInterval(() => {
    document.getElementById('radio' + counter).checked = true;
    counter++;
    if (counter > 4) {
        counter = 1;
    }
}, 5000); // 5000ms = 5 seconds


document.addEventListener("DOMContentLoaded", function() {
    // Function to enable dark mode
    function enableDarkMode() {
        document.body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'enabled');
    }

    // Function to disable dark mode
    function disableDarkMode() {
        document.body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'disabled');
    }

    // Check for saved dark mode preference in localStorage on page load
    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'enabled') {
        enableDarkMode();  // Apply dark mode if it's enabled
    }

    // Toggle dark mode when the switch is clicked
    const darkModeToggle = document.getElementById('mode-changer');
    darkModeToggle.addEventListener('click', () => {
        const darkMode = localStorage.getItem('darkMode');
        if (darkMode !== 'enabled') {
            enableDarkMode();  // Enable dark mode and save preference
        } else {
            disableDarkMode();  // Disable dark mode and save preference
        }
    });

    // Features menu toggle
    const featuresLink = document.querySelector("#features > a");
    const subMenu = document.querySelector("#features .sub-menu");
    featuresLink.addEventListener("click", function(event) {
        event.preventDefault();
        subMenu.classList.toggle("show");
    });
});




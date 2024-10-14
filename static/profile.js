// Function to enable editing of fields
function enableEditing(fieldId) {
    document.getElementById(fieldId).removeAttribute('readonly');
    document.getElementById(fieldId).focus();
}

// Function to handle image upload and save to MySQL
document.getElementById('uploadImage').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            const imgData = event.target.result;
            document.getElementById('profileImage').src = imgData;
            saveImageToDB(imgData); // Save image to MySQL
        };
        reader.readAsDataURL(file);
    }
});

// Function to save image to MySQL
function saveImageToDB(imgData) {
    fetch('/save-profile-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imgData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Image saved successfully!');
        } else {
            alert('Failed to save image.');
        }
    });
}

// Function to save profile data to the server and local storage
document.querySelector('.save-button').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent default form submission

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const imageInput = document.getElementById('uploadImage');
    const imageFile = imageInput.files[0];

    // Prepare FormData to handle image upload
    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);
    if (imageFile) {
        formData.append('profile_image', imageFile);
    }

    // Send data to server
    fetch('/profile', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Save data in local storage
            localStorage.setItem('profileName', name);
            localStorage.setItem('profileEmail', email);
            if (imageFile) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    localStorage.setItem('profileImage', event.target.result);
                    document.getElementById('profileImage').src = event.target.result; // Update image preview
                };
                reader.readAsDataURL(imageFile);
            }

            // Show success message
            showFlashMessage('Profile updated successfully!', 'success');
        } else {
            showFlashMessage('Failed to update profile. Please try again.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred. Please try again later.', 'danger');
    });
});

// Function to display flash messages
function showFlashMessage(message, category) {
    const flashContainer = document.createElement('div');
    flashContainer.className = `flash-message ${category}`;
    flashContainer.textContent = message;

    // Append flash message to the body
    document.body.appendChild(flashContainer);

    // Automatically hide the flash message after 3 seconds
    setTimeout(() => {
        flashContainer.style.opacity = '0';
        setTimeout(() => {
            flashContainer.remove();
        }, 500); // Delay for smooth transition
    }, 3000);
}
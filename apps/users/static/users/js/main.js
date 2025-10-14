// Main JavaScript for CipherTalk
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('input[required]');
            let valid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('error');
                    valid = false;
                } else {
                    input.classList.remove('error');
                }
            });

            if (!valid) {
                e.preventDefault();
                // Show error message
                if (!this.querySelector('.form-error')) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-error form-error';
                    errorDiv.innerHTML = `
                        <span class="alert-icon"><i class="fas fa-exclamation-circle"></i></span>
                        <span class="alert-text">Please fill in all required fields.</span>
                    `;
                    this.insertBefore(errorDiv, this.firstChild);
                }
            }
        });
    });

    // Real-time input validation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('error');
            }
        });

        input.addEventListener('blur', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.classList.add('error');
            }
        });
    });

    // Password strength indicator (for registration)
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updatePasswordStrengthIndicator(this, strength);
        });
    });
});

function calculatePasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[!@#$%^&*(),.?":{}|<>]+/)) strength++;
    return strength;
}

function updatePasswordStrengthIndicator(input, strength) {
    let existingIndicator = input.parentNode.querySelector('.password-strength');
    if (!existingIndicator) {
        existingIndicator = document.createElement('div');
        existingIndicator.className = 'password-strength';
        input.parentNode.appendChild(existingIndicator);
    }

    const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
    const strengthColors = ['#ef4444', '#f59e0b', '#f59e0b', '#10b981', '#10b981', '#10b981'];
    
    existingIndicator.innerHTML = `
        <div class="strength-bar">
            <div class="strength-fill" style="width: ${(strength / 5) * 100}%; background: ${strengthColors[strength]}"></div>
        </div>
        <span class="strength-text" style="color: ${strengthColors[strength]}">${strengthText[strength]}</span>
    `;
}
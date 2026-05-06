// Main JavaScript for Medical Platform

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('is-invalid');
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// TC Kimlik Validation
function validateTCKimlik(tc) {
    if (!/^\d{11}$/.test(tc)) return false;

    const digits = tc.split('').map(Number);

    // İlk rakam 0 olamaz
    if (digits[0] === 0) return false;

    // 10. hane kontrolü
    let sum1 = 0;
    for (let i = 0; i < 9; i += 2) sum1 += digits[i];
    sum1 *= 7;

    let sum2 = 0;
    for (let i = 1; i < 9; i += 2) sum2 += digits[i];

    if ((sum1 - sum2) % 10 !== digits[9]) return false;

    // 11. hane kontrolü
    let sum3 = 0;
    for (let i = 0; i < 10; i++) sum3 += digits[i];

    if (sum3 % 10 !== digits[10]) return false;

    return true;
}

// TC Kimlik input için real-time validation
document.addEventListener('DOMContentLoaded', function () {
    const tcInput = document.getElementById('tc_kimlik');
    if (tcInput) {
        tcInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 11);
        });
    }

    // Telefon input için format
    const phoneInput = document.getElementById('telefon');
    if (phoneInput) {
        phoneInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 11);
        });
    }

    // Password confirmation
    const password = document.getElementById('password');
    const passwordConfirm = document.getElementById('password_confirm');

    if (password && passwordConfirm) {
        passwordConfirm.addEventListener('input', function () {
            if (this.value && this.value !== password.value) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }

    // File upload preview
    const fileInput = document.getElementById('xray_image');
    const fileLabel = document.querySelector('.file-upload-label');

    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 16 * 1024 * 1024) {
                    showAlert('Dosya boyutu 16MB\'dan küçük olmalıdır', 'danger');
                    this.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = function (e) {
                    const preview = document.getElementById('imagePreview');
                    if (preview) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }

                    fileLabel.innerHTML = `
                        <div class="file-upload-icon">✅</div>
                        <h3>${file.name}</h3>
                        <p>Dosya yüklendi - Analiz için hazır</p>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Drag and drop
    const dropZone = document.querySelector('.file-upload-label');
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, function () {
                this.style.borderColor = 'var(--primary-color)';
                this.style.background = 'rgba(79, 70, 229, 0.1)';
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, function () {
                this.style.borderColor = '';
                this.style.background = '';
            });
        });

        dropZone.addEventListener('drop', function (e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    }

    // Auto dismiss alerts
    setTimeout(function () {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);
});

// Show custom alert
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.innerHTML = `
        <span>${getAlertIcon(type)}</span>
        <span>${message}</span>
    `;

    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);

        setTimeout(() => {
            alertDiv.style.opacity = '0';
            setTimeout(() => alertDiv.remove(), 500);
        }, 5000);
    }
}

function getAlertIcon(type) {
    const icons = {
        'success': '✅',
        'danger': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    return icons[type] || 'ℹ️';
}

// Loading overlay
function showLoading() {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    overlay.innerHTML = `
        <div style="text-align: center;">
            <div class="spinner"></div>
            <p style="color: white; margin-top: 1rem; font-size: 1.2rem;">Analiz ediliyor...</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.remove();
}

// Form submit with loading
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form.id === 'analyzeForm') {
            form.addEventListener('submit', function () {
                showLoading();
            });
        }
    });
});

// Confirmation dialogs
function confirmDelete(message) {
    return confirm(message || 'Bu işlemi gerçekleştirmek istediğinizden emin misiniz?');
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add fade-in animation to elements
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function (entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.card, .model-card').forEach(el => {
        observer.observe(el);
    });
});


// ===== PROFILE DROPDOWN =====
document.addEventListener('DOMContentLoaded', () => {
    const profileBtn = document.getElementById('profileDropdownBtn');
    const profileMenu = document.getElementById('profileDropdownMenu');

    if (profileBtn && profileMenu) {
        // Toggle dropdown on button click
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            profileMenu.classList.toggle('active');
            profileBtn.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!profileBtn.contains(e.target) && !profileMenu.contains(e.target)) {
                profileMenu.classList.remove('active');
                profileBtn.classList.remove('active');
            }
        });

        // Prevent dropdown from closing when clicking inside
        profileMenu.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
});


// ===== DELETE ACCOUNT CONFIRMATION =====
function confirmDeleteAccount(event) {
    event.preventDefault();

    if (confirm('UYARI: Hesabinizi silmek istediginizden emin misiniz? Bu islem geri alinamaz ve TUM analizleriniz silinecektir!')) {
        const password = prompt('Onaylamak icin sifrenizi girin:');

        if (password) {
            // Create a form and submit
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/profile/delete';

            const passwordInput = document.createElement('input');
            passwordInput.type = 'hidden';
            passwordInput.name = 'password';
            passwordInput.value = password;

            form.appendChild(passwordInput);
            document.body.appendChild(form);
            form.submit();
        }
    }
}

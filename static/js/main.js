// Alpha Nex - Main JavaScript File
// Handles interactive features and form validation
// Enhanced with modern ES6+ features and improved performance
// Last updated: 2025

(function() {
    'use strict';

    // Global app object
    window.AlphaNex = {
        // Configuration
        config: {
            maxFileSize: 500 * 1024 * 1024, // 500MB
            allowedExtensions: ['pdf', 'mp4', 'mp3', 'wav', 'txt', 'py', 'js', 'html', 'css', 'jpg', 'jpeg', 'png', 'gif'],
            refreshInterval: 30000, // 30 seconds
            animationDuration: 300
        },
        
        // Initialize app
        init: function() {
            this.setupEventListeners();
            this.initializeComponents();
            this.startPeriodicUpdates();
            console.log('Alpha Nex initialized');
        },
        
        // Setup global event listeners
        setupEventListeners: function() {
            // Handle flash message dismissal
            this.handleFlashMessages();
            
            // Handle form submissions
            this.handleFormValidation();
            
            // Handle file uploads
            this.handleFileUploads();
            
            // Handle keyboard shortcuts
            this.handleKeyboardShortcuts();
            
            // Handle responsive navigation
            this.handleNavigation();
        },
        
        // Initialize components
        initializeComponents: function() {
            // Initialize tooltips if Bootstrap is available
            if (typeof bootstrap !== 'undefined') {
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(function(tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });
            }
            
            // Initialize countdown timers
            this.initCountdownTimers();
            
            // Initialize progress bars
            this.initProgressBars();
            
            // Initialize character counters
            this.initCharacterCounters();
        },
        
        // Handle flash messages
        handleFlashMessages: function() {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                // Auto-dismiss success messages after 5 seconds
                if (alert.classList.contains('alert-success')) {
                    setTimeout(() => {
                        this.fadeOut(alert);
                    }, 5000);
                }
            });
        },
        
        // Handle form validation
        handleFormValidation: function() {
            const forms = document.querySelectorAll('form');
            
            forms.forEach(form => {
                form.addEventListener('submit', (e) => {
                    if (!this.validateForm(form)) {
                        e.preventDefault();
                        this.showValidationErrors(form);
                    }
                });
                
                // Real-time validation
                const inputs = form.querySelectorAll('input, textarea, select');
                inputs.forEach(input => {
                    input.addEventListener('blur', () => {
                        this.validateField(input);
                    });
                    
                    input.addEventListener('input', () => {
                        this.clearFieldError(input);
                    });
                });
            });
        },
        
        // Handle file uploads
        handleFileUploads: function() {
            const fileInputs = document.querySelectorAll('input[type="file"]');
            
            fileInputs.forEach(input => {
                input.addEventListener('change', (e) => {
                    this.handleFileSelection(e.target);
                });
            });
            
            // Drag and drop functionality
            const dropZones = document.querySelectorAll('.upload-zone, #dropZone');
            dropZones.forEach(zone => {
                this.setupDragAndDrop(zone);
            });
        },
        
        // Setup drag and drop
        setupDragAndDrop: function(zone) {
            const fileInput = zone.querySelector('input[type="file"]') || 
                            document.querySelector('input[type="file"]');
            
            if (!fileInput) return;
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                zone.addEventListener(eventName, this.preventDefaults);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                zone.addEventListener(eventName, () => {
                    zone.classList.add('drag-over');
                });
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                zone.addEventListener(eventName, () => {
                    zone.classList.remove('drag-over');
                });
            });
            
            zone.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    this.handleFileSelection(fileInput);
                }
            });
        },
        
        // Prevent default drag behaviors
        preventDefaults: function(e) {
            e.preventDefault();
            e.stopPropagation();
        },
        
        // Handle file selection
        handleFileSelection: function(input) {
            const file = input.files[0];
            if (!file) return;
            
            // Validate file
            const validation = this.validateFile(file);
            if (!validation.valid) {
                this.showFileError(input, validation.message);
                input.value = '';
                return;
            }
            
            // Update UI
            this.updateFileDisplay(file);
            this.clearFileError(input);
        },
        
        // Validate file
        validateFile: function(file) {
            // Check file size
            if (file.size > this.config.maxFileSize) {
                return {
                    valid: false,
                    message: `File size exceeds 500MB limit. Selected file is ${this.formatFileSize(file.size)}.`
                };
            }
            
            // Check file extension
            const extension = file.name.split('.').pop().toLowerCase();
            if (!this.config.allowedExtensions.includes(extension)) {
                return {
                    valid: false,
                    message: `File type not allowed. Allowed types: ${this.config.allowedExtensions.join(', ')}`
                };
            }
            
            return { valid: true };
        },
        
        // Update file display
        updateFileDisplay: function(file) {
            const fileName = document.getElementById('fileName');
            const fileSize = document.getElementById('fileSize');
            const fileInfo = document.getElementById('fileInfo');
            
            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
            if (fileInfo) fileInfo.classList.remove('d-none');
        },
        
        // Format file size
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
        },
        
        // Show file error
        showFileError: function(input, message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'text-danger small mt-1 file-error';
            errorDiv.textContent = message;
            
            // Remove existing error
            this.clearFileError(input);
            
            // Add new error
            input.parentNode.appendChild(errorDiv);
        },
        
        // Clear file error
        clearFileError: function(input) {
            const existingError = input.parentNode.querySelector('.file-error');
            if (existingError) {
                existingError.remove();
            }
        },
        
        // Handle keyboard shortcuts
        handleKeyboardShortcuts: function() {
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + K for search (if implemented)
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    const searchInput = document.querySelector('input[type="search"]');
                    if (searchInput) searchInput.focus();
                }
                
                // Escape to close modals
                if (e.key === 'Escape') {
                    const modals = document.querySelectorAll('.modal.show');
                    modals.forEach(modal => {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        if (modalInstance) modalInstance.hide();
                    });
                }
            });
        },
        
        // Handle navigation
        handleNavigation: function() {
            // Add active class to current page nav link
            const currentPath = window.location.pathname;
            const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
            
            navLinks.forEach(link => {
                if (link.getAttribute('href') === currentPath) {
                    link.classList.add('active');
                }
            });
            
            // Handle mobile menu
            const navbarToggler = document.querySelector('.navbar-toggler');
            if (navbarToggler) {
                navbarToggler.addEventListener('click', () => {
                    const navbar = document.querySelector('.navbar-collapse');
                    navbar.classList.toggle('show');
                });
            }
        },
        
        // Initialize countdown timers
        initCountdownTimers: function() {
            const timers = document.querySelectorAll('[data-countdown]');
            timers.forEach(timer => {
                const endTime = new Date(timer.dataset.countdown).getTime();
                this.startCountdown(timer, endTime);
            });
        },
        
        // Start countdown
        startCountdown: function(element, endTime) {
            const updateTimer = () => {
                const now = new Date().getTime();
                const distance = endTime - now;
                
                if (distance < 0) {
                    element.textContent = 'Expired';
                    element.classList.add('text-danger');
                    return;
                }
                
                const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((distance % (1000 * 60)) / 1000);
                
                element.textContent = `${hours}h ${minutes}m ${seconds}s`;
            };
            
            updateTimer();
            setInterval(updateTimer, 1000);
        },
        
        // Initialize progress bars
        initProgressBars: function() {
            const progressBars = document.querySelectorAll('.progress-bar[data-target]');
            progressBars.forEach(bar => {
                const target = parseInt(bar.dataset.target);
                this.animateProgressBar(bar, target);
            });
        },
        
        // Animate progress bar
        animateProgressBar: function(bar, target) {
            let current = 0;
            const increment = target / 50; // 50 steps
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                bar.style.width = current + '%';
                bar.setAttribute('aria-valuenow', current);
            }, this.config.animationDuration / 50);
        },
        
        // Initialize character counters
        initCharacterCounters: function() {
            const textareas = document.querySelectorAll('textarea[maxlength]');
            textareas.forEach(textarea => {
                this.setupCharacterCounter(textarea);
            });
        },
        
        // Setup character counter
        setupCharacterCounter: function(textarea) {
            const maxLength = parseInt(textarea.getAttribute('maxlength'));
            const counterId = textarea.id + 'Count';
            let counter = document.getElementById(counterId);
            
            if (!counter) {
                counter = document.createElement('small');
                counter.id = counterId;
                counter.className = 'text-muted';
                textarea.parentNode.appendChild(counter);
            }
            
            const updateCounter = () => {
                const current = textarea.value.length;
                counter.textContent = `${current}/${maxLength}`;
                
                if (current > maxLength * 0.9) {
                    counter.className = 'text-warning';
                } else if (current === maxLength) {
                    counter.className = 'text-danger';
                } else {
                    counter.className = 'text-muted';
                }
            };
            
            textarea.addEventListener('input', updateCounter);
            updateCounter(); // Initial update
        },
        
        // Form validation
        validateForm: function(form) {
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!this.validateField(input)) {
                    isValid = false;
                }
            });
            
            return isValid;
        },
        
        // Validate individual field
        validateField: function(field) {
            const value = field.value.trim();
            let isValid = true;
            let message = '';
            
            // Required validation
            if (field.hasAttribute('required') && !value) {
                isValid = false;
                message = 'This field is required.';
            }
            
            // Email validation
            if (field.type === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    isValid = false;
                    message = 'Please enter a valid email address.';
                }
            }
            
            // Minimum length validation
            const minLength = field.getAttribute('minlength');
            if (minLength && value.length < parseInt(minLength)) {
                isValid = false;
                message = `Minimum ${minLength} characters required.`;
            }
            
            // Password confirmation
            if (field.name === 'confirm_password') {
                const password = field.form.querySelector('input[name="password"]');
                if (password && value !== password.value) {
                    isValid = false;
                    message = 'Passwords do not match.';
                }
            }
            
            // Update field appearance
            if (isValid) {
                this.clearFieldError(field);
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            } else {
                this.showFieldError(field, message);
                field.classList.remove('is-valid');
                field.classList.add('is-invalid');
            }
            
            return isValid;
        },
        
        // Show field error
        showFieldError: function(field, message) {
            this.clearFieldError(field);
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = message;
            
            field.parentNode.appendChild(errorDiv);
        },
        
        // Clear field error
        clearFieldError: function(field) {
            const existingError = field.parentNode.querySelector('.invalid-feedback');
            if (existingError) {
                existingError.remove();
            }
        },
        
        // Show validation errors
        showValidationErrors: function(form) {
            const firstInvalidField = form.querySelector('.is-invalid');
            if (firstInvalidField) {
                firstInvalidField.focus();
                firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        },
        
        // Start periodic updates
        startPeriodicUpdates: function() {
            // Update upload status every 30 seconds if on dashboard
            if (window.location.pathname === '/dashboard') {
                setInterval(() => {
                    this.updateUploadStatuses();
                }, this.config.refreshInterval);
            }
        },
        
        // Update upload statuses
        updateUploadStatuses: function() {
            const uploadRows = document.querySelectorAll('[data-upload-id]');
            uploadRows.forEach(row => {
                const uploadId = row.dataset.uploadId;
                this.checkUploadStatus(uploadId);
            });
        },
        
        // Check upload status
        checkUploadStatus: function(uploadId) {
            fetch(`/api/upload_status/${uploadId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error('Status check error:', data.error);
                        return;
                    }
                    
                    // Update UI based on status
                    this.updateUploadStatusUI(uploadId, data);
                })
                .catch(error => {
                    console.error('Status check failed:', error);
                });
        },
        
        // Update upload status UI
        updateUploadStatusUI: function(uploadId, data) {
            const row = document.querySelector(`[data-upload-id="${uploadId}"]`);
            if (!row) return;
            
            // Update countdown timer
            const countdownEl = row.querySelector('.countdown');
            if (countdownEl) {
                if (data.hours_remaining > 0) {
                    const hours = Math.floor(data.hours_remaining);
                    const minutes = Math.floor((data.hours_remaining - hours) * 60);
                    countdownEl.textContent = `${hours}h ${minutes}m remaining`;
                    countdownEl.className = 'text-success small';
                } else {
                    countdownEl.textContent = `${data.penalty} XP penalty`;
                    countdownEl.className = 'text-warning small';
                }
            }
        },
        
        // Utility functions
        fadeOut: function(element) {
            element.style.transition = 'opacity 0.3s';
            element.style.opacity = '0';
            setTimeout(() => {
                if (element.parentNode) {
                    element.parentNode.removeChild(element);
                }
            }, 300);
        },
        
        fadeIn: function(element) {
            element.style.opacity = '0';
            element.style.display = 'block';
            element.style.transition = 'opacity 0.3s';
            
            setTimeout(() => {
                element.style.opacity = '1';
            }, 10);
        },
        
        // Show notification
        showNotification: function(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} alert-dismissible fade show`;
            notification.style.position = 'fixed';
            notification.style.top = '20px';
            notification.style.right = '20px';
            notification.style.zIndex = '9999';
            notification.style.minWidth = '300px';
            
            notification.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
            `;
            
            document.body.appendChild(notification);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    this.fadeOut(notification);
                }
            }, 5000);
        },
        
        // Copy to clipboard
        copyToClipboard: function(text) {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    this.showNotification('Copied to clipboard!', 'success');
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    this.showNotification('Copied to clipboard!', 'success');
                } catch (err) {
                    console.error('Copy failed:', err);
                }
                document.body.removeChild(textArea);
            }
        },
        
        // Loading states
        showLoading: function(element, text = 'Loading...') {
            element.disabled = true;
            element.classList.add('loading');
            const originalText = element.textContent;
            element.textContent = text;
            element.dataset.originalText = originalText;
        },
        
        hideLoading: function(element) {
            element.disabled = false;
            element.classList.remove('loading');
            if (element.dataset.originalText) {
                element.textContent = element.dataset.originalText;
                delete element.dataset.originalText;
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            AlphaNex.init();
        });
    } else {
        AlphaNex.init();
    }

})();

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AlphaNex;
}

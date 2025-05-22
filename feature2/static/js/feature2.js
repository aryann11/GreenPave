document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    const loading = document.querySelector('.loading');
    const resultCard = document.querySelector('.result-card');
    const predictionText = document.getElementById('prediction');
    const numericInputs = form.querySelectorAll('input[type="number"]');
    const sliders = form.querySelectorAll('.range-slider');
    
    // Initialize sliders and sync with number inputs
    initializeInputsAndSliders();
    
    // Input validation
    function validateInput(input) {
        const value = parseFloat(input.value);
        const min = parseFloat(input.min);
        const max = parseFloat(input.max);
        
        if (input.value === '') {
            input.classList.add('invalid');
            return false;
        }
        
        if (value < min || value > max) {
            input.classList.add('invalid');
            showNotification(`Please enter a value between ${min} and ${max} for ${input.previousElementSibling.textContent}`);
            return false;
        }
        
        input.classList.remove('invalid');
        return true;
    }

    // Show notification instead of alert
    function showNotification(message) {
        // Check if notification exists already
        let notification = document.querySelector('.notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'notification';
            document.body.appendChild(notification);
        }
        
        notification.textContent = message;
        notification.style.display = 'block';
        notification.style.opacity = '1';
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 300);
        }, 3000);
    }

    // Initialize all inputs and sliders
    function initializeInputsAndSliders() {
        // For each numeric input, set up the slider connection
        numericInputs.forEach(input => {
            const sliderId = `${input.id}-slider`;
            const valueId = `${input.id}-value`;
            const slider = document.getElementById(sliderId);
            const valueDisplay = document.getElementById(valueId);
            
            if (slider && valueDisplay) {
                // Set initial values
                const initialValue = parseFloat(slider.value);
                input.value = initialValue;
                updateValueDisplay(valueDisplay, initialValue, input);
                
                // When slider changes, update input and display
                slider.addEventListener('input', (e) => {
                    const value = parseFloat(e.target.value);
                    input.value = value;
                    updateValueDisplay(valueDisplay, value, input);
                    input.classList.remove('invalid');
                });
                
                // When input changes, update slider and display
                input.addEventListener('input', (e) => {
                    let value = parseFloat(e.target.value);
                    
                    // Ensure value is within range
                    const min = parseFloat(input.min);
                    const max = parseFloat(input.max);
                    
                    if (!isNaN(value)) {
                        if (value < min) value = min;
                        if (value > max) value = max;
                        
                        slider.value = value;
                        updateValueDisplay(valueDisplay, value, input);
                        input.classList.remove('invalid');
                    }
                });
            }
        });
    }
    
    // Update value display with appropriate formatting
    function updateValueDisplay(element, value, input) {
        // Format based on input type
        let formattedValue;
        
        if (input.id === 'ph') {
            formattedValue = parseFloat(value).toFixed(1);
        } else if (input.id === 'temperature' || input.id === 'humidity' || input.id === 'rainfall') {
            formattedValue = `${parseFloat(value).toFixed(1)} ${input.nextElementSibling.textContent.trim()}`;
        } else {
            formattedValue = `${Math.round(value)} ${input.nextElementSibling.textContent.trim()}`;
        }
        
        element.textContent = formattedValue;
    }

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validate all inputs
        let isValid = true;
        numericInputs.forEach(input => {
            if (!validateInput(input)) {
                isValid = false;
            }
        });

        if (!isValid) {
            return;
        }

        // Show loading animation with smooth transition
        loading.style.display = 'block';
        resultCard.style.display = 'none';
        
        // Smooth scroll to loading indicator
        loading.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Collect form data
        const data = {
            N: document.getElementById('N').value,
            P: document.getElementById('P').value,
            K: document.getElementById('K').value,
            temperature: document.getElementById('temperature').value,
            humidity: document.getElementById('humidity').value,
            ph: document.getElementById('ph').value,
            rainfall: document.getElementById('rainfall').value
        };
        
        try {
            const response = await fetch('/feature2/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Add a small delay for a smoother transition
                setTimeout(() => {
                    predictionText.textContent = result.prediction;
                    resultCard.style.display = 'block';
                    
                    // Smooth scroll to result
                    resultCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    // Add animation class
                    resultCard.classList.add('fadeIn');
                    
                    // Remove animation class after animation completes
                    setTimeout(() => {
                        resultCard.classList.remove('fadeIn');
                    }, 500);
                }, 500);
            } else {
                showNotification('Error: ' + result.error);
            }
        } catch (error) {
            showNotification('Error: ' + error.message);
        } finally {
            setTimeout(() => {
                loading.style.display = 'none';
            }, 500);
        }
    });

    // Add keyboard navigation
    numericInputs.forEach((input, index) => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (index < numericInputs.length - 1) {
                    numericInputs[index + 1].focus();
                } else {
                    form.dispatchEvent(new Event('submit'));
                }
            }
        });
    });

    // Add smooth scrolling for any anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add notification styles dynamically
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: rgba(220, 53, 69, 0.9);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 1000;
            display: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            max-width: 350px;
            font-weight: 500;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fadeIn {
            animation: fadeIn 0.5s ease;
        }
    `;
    document.head.appendChild(style);
});
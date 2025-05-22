async function searchNurseries() {
    const locationInput = document.getElementById('location');
    const loadingElement = document.getElementById('loading');
    const resultsContainer = document.getElementById('results');
    
    if (!locationInput.value.trim()) {
        alert('Please enter a location');
        return;
    }

    // Show loading state
    loadingElement.classList.remove('hidden');
    resultsContainer.innerHTML = '';

    try {
        const response = await fetch('/feature4/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location: locationInput.value.trim()
            })
        });

        const data = await response.json();

        if (data.success) {
            // Parse the response from Groq
            const nurseries = JSON.parse(data.data);
            displayResults(nurseries);
        } else {
            throw new Error(data.error || 'Failed to fetch nurseries');
        }
    } catch (error) {
        resultsContainer.innerHTML = `
            <div class="error-message">
                <p>Error: ${error.message}</p>
            </div>
        `;
    } finally {
        loadingElement.classList.add('hidden');
    }
}

function displayResults(nurseries) {
    const resultsContainer = document.getElementById('results');
    
    if (!Array.isArray(nurseries) || nurseries.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <p>No nurseries found in this location. Try searching for a different area.</p>
            </div>
        `;
        return;
    }

    const nurseryCards = nurseries.map(nursery => `
        <div class="nursery-card">
            <h3>${nursery.name}</h3>
            <p class="phone">📞 ${nursery.phone}</p>
            <p>📍 ${nursery.address}</p>
            <p>${nursery.description}</p>
        </div>
    `).join('');

    resultsContainer.innerHTML = nurseryCards;
}

// Add event listener for Enter key
document.getElementById('location').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchNurseries();
    }
}); 
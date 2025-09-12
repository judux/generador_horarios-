document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const materiasContainer = document.getElementById('materias-container');
    const loadingMessage = document.getElementById('loading-message');

    const apiUrlBase = 'http://127.0.0.1:8000';
    let materiasCargadas = []; // Store the last loaded subjects

    /**
     * Renders a list of materias into the container.
     * @param {Array} materias - The list of materia objects to display.
     */
    const displayMaterias = (materias) => {
        materiasContainer.innerHTML = '';
        if (!materias || materias.length === 0) {
            materiasContainer.innerHTML = '<p id="error-message">No se encontraron materias.</p>';
            return;
        }
        materias.forEach(materia => {
            const card = document.createElement('div');
            card.className = 'materia-card';
            card.dataset.codigo = materia.codigo; // Store codigo for modal
            card.innerHTML = `
                <h2>${materia.nombre}</h2>
                <p>Código: <span class="codigo">${materia.codigo}</span></p>
                <p>Créditos: ${materia.creditos}</p>
            `;
            materiasContainer.appendChild(card);
        });
    };

    /**
     * Fetches and displays all materias.
     */
    const fetchAndDisplayAllMaterias = () => {
        loadingMessage.textContent = 'Cargando materias...';
        loadingMessage.classList.remove('hidden');
        materiasContainer.innerHTML = '';

        const url = `${apiUrlBase}/materias`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                loadingMessage.classList.add('hidden');
                materiasCargadas = data; // Save the loaded subjects
                displayMaterias(materiasCargadas);
            })
            .catch(error => {
                console.error("Error al cargar materias:", error);
                loadingMessage.innerHTML = '<p id="error-message">Error al conectar con la API.</p>';
            });
    };

    // --- Initial Load ---
    fetchAndDisplayAllMaterias();
});
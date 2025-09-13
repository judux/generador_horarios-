document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const materiasContainer = document.getElementById('materias-container');
    const loadingMessage = document.getElementById('loading-message');
    const modalOverlay = document.getElementById('modal-overlay');
    const modalBody = document.getElementById('modal-body');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const horarioGrid = document.getElementById('horario-grid');

    const apiUrlBase = 'http://127.0.0.1:8000';
    const HORAS = Array.from({ length: 16 }, (_, i) => i + 7); // 7am to 10pm (22h)
    const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];

    let materiasCargadas = [];
    let coloresMaterias = {};

    // --- Modal Logic ---
    const hideModal = () => modalOverlay.classList.add('hidden');
    const showModal = () => modalOverlay.classList.remove('hidden');

    const displayMateriaDetails = (materia) => {
        modalBody.innerHTML = '';
        const title = document.createElement('h2');
        title.textContent = materia.nombre;
        modalBody.appendChild(title);

        if (!materia.grupos || materia.grupos.length === 0) {
            modalBody.innerHTML += '<p>No hay grupos disponibles para esta materia.</p>';
            return;
        }

        materia.grupos.forEach(grupo => {
            const grupoDiv = document.createElement('div');
            grupoDiv.className = 'grupo-info';
            let grupoHTML = `<h3>Grupo ${grupo.nombre}</h3>`;
            if (grupo.docente) grupoHTML += `<p><strong>Docente:</strong> ${grupo.docente}</p>`;
            if (grupo.cupos) grupoHTML += `<p><strong>Cupos:</strong> ${grupo.cupos}</p>`;
            
            if (grupo.sesiones && grupo.sesiones.length > 0) {
                grupo.sesiones.forEach(sesion => {
                    grupoHTML += `
                        <div class="sesion-info">
                            <p><strong>Día:</strong> ${sesion.dia}</p>
                            <p><strong>Hora:</strong> ${sesion.hora_inicio} - ${sesion.hora_fin}</p>
                            <p><strong>Salón:</strong> ${sesion.salon}</p>
                        </div>
                    `;
                });
            } else {
                grupoHTML += '<p>No hay sesiones programadas para este grupo.</p>';
            }
            grupoDiv.innerHTML = grupoHTML;
            modalBody.appendChild(grupoDiv);
        });
    };

    const fetchMateriaDetails = (codigoMateria) => {
        const url = `${apiUrlBase}/materias/${codigoMateria}`;
        modalBody.innerHTML = '<p>Cargando detalles...</p>';
        showModal();
        fetch(url)
            .then(response => response.ok ? response.json() : Promise.reject(response.status))
            .then(displayMateriaDetails)
            .catch(error => {
                console.error("Error al cargar detalles de la materia:", error);
                modalBody.innerHTML = '<p class="error-message">No se pudieron cargar los detalles.</p>';
            });
    };

    // --- Horario Grid Logic ---
    const generarHorarioGrid = () => {
        horarioGrid.innerHTML = '';

        const formatHour12 = (hour) => {
            const ampm = hour >= 12 ? 'PM' : 'AM';
            const h = hour % 12 || 12; // Convert 0 to 12
            return `${h}:00 ${ampm}`;
        };

        // Empty cell for top-left corner
        horarioGrid.appendChild(document.createElement('div'));
        // Day headers
        DIAS.forEach(dia => {
            const header = document.createElement('div');
            header.className = 'grid-header';
            header.textContent = dia;
            horarioGrid.appendChild(header);
        });
        // Time slots and cells
        HORAS.forEach(hora => {
            const timeCell = document.createElement('div');
            timeCell.className = 'grid-time';
            timeCell.textContent = formatHour12(hora);
            horarioGrid.appendChild(timeCell);
            DIAS.forEach(dia => {
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                cell.dataset.dia = dia;
                cell.dataset.hora = hora;
                horarioGrid.appendChild(cell);
            });
        });
    };

    const getColorParaMateria = (codigoMateria) => {
        if (coloresMaterias[codigoMateria]) {
            return coloresMaterias[codigoMateria];
        }
        // Simple hash function to get a color
        let hash = 0;
        for (let i = 0; i < codigoMateria.length; i++) {
            hash = codigoMateria.charCodeAt(i) + ((hash << 5) - hash);
        }
        const h = hash % 360;
        const color = `hsl(${h}, 70%, 80%)`; // Lighter colors
        coloresMaterias[codigoMateria] = color;
        return color;
    };

    const agregarMateriaAlHorario = (materia) => {
        if (!materia.grupos || materia.grupos.length === 0) {
            alert(`La materia ${materia.nombre} no tiene grupos para agregar.`);
            return;
        }

        const grupo = materia.grupos[0]; // Add the first group by default
        const color = getColorParaMateria(materia.codigo);

        grupo.sesiones.forEach(sesion => {
            const diaIndex = DIAS.indexOf(sesion.dia);
            if (diaIndex === -1) return;

            const [horaInicio] = sesion.hora_inicio.split(':').map(Number);
            const [horaFin] = sesion.hora_fin.split(':').map(Number);
            const duracion = Math.max(1, horaFin - horaInicio);

            const cell = horarioGrid.querySelector(`[data-dia='${sesion.dia}'][data-hora='${horaInicio}']`);
            if (!cell) return;

            const materiaDiv = document.createElement('div');
            materiaDiv.className = 'horario-materia';
            materiaDiv.style.backgroundColor = color;
            materiaDiv.style.height = `${duracion * 40 - 4}px`; // -4 for padding/gap
            materiaDiv.innerHTML = `<strong>${materia.nombre}</strong> (G${grupo.nombre})`;

            cell.appendChild(materiaDiv);
        });
    };

    // --- Materias List Logic ---
    const toTitleCase = (str) => {
        if (!str || str === 'N/A') return str;
        return str.toLowerCase().replace(/\b\w/g, char => char.toUpperCase());
    };

    const displayMaterias = (materias) => {
        materiasContainer.innerHTML = '';
        if (!materias || materias.length === 0) {
            materiasContainer.innerHTML = '<p id="error-message">No se encontraron materias.</p>';
            return;
        }
        materias.forEach(materia => {
            const card = document.createElement('div');
            card.className = 'materia-card';
            card.dataset.codigo = materia.codigo;
            card.innerHTML = `
                <h2>${materia.nombre}</h2>
                <div class="materia-info">
                    <div class="info-line">
                        <span class="info-label">Docente:</span>
                        <span class="info-value">${toTitleCase(materia.docente)}</span>
                    </div>
                    <div class="info-line">
                        <span class="info-label">Créditos:</span>
                        <span class="info-value">${materia.creditos}</span>
                    </div>
                </div>
            `;
            materiasContainer.appendChild(card);
        });
    };

    const fetchAndDisplayAllMaterias = () => {
        loadingMessage.textContent = 'Cargando materias...';
        loadingMessage.classList.remove('hidden');
        materiasContainer.innerHTML = '';
        fetch(`${apiUrlBase}/materias`)
            .then(response => response.json())
            .then(data => {
                loadingMessage.classList.add('hidden');
                materiasCargadas = data;
                displayMaterias(materiasCargadas);
            })
            .catch(error => {
                console.error("Error al cargar materias:", error);
                loadingMessage.innerHTML = '<p id="error-message">Error al conectar con la API.</p>';
            });
    };

    // --- Event Listeners ---
    materiasContainer.addEventListener('click', (event) => {
        const card = event.target.closest('.materia-card');
        if (card && card.dataset.codigo) {
            const materia = materiasCargadas.find(m => m.codigo === card.dataset.codigo);
            if (materia) {
                fetch(`${apiUrlBase}/materias/${materia.codigo}`)
                    .then(res => res.json())
                    .then(agregarMateriaAlHorario)
                    .catch(err => console.error("Could not fetch details to add to schedule", err));
            }
        }
    });

    // modalCloseBtn.addEventListener('click', hideModal);
    // modalOverlay.addEventListener('click', (event) => {
    //     if (event.target === modalOverlay) hideModal();
    // });

    // --- Initial Load ---
    generarHorarioGrid();
    fetchAndDisplayAllMaterias();
});
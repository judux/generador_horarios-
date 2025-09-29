document.addEventListener('DOMContentLoaded', () => {

    // --- CONFIG & STATE ---
    const API_URL = 'http://127.0.0.1:8000';
    const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    const HORA_INICIO = 7;
    const HORA_FIN = 22;
    const PALETA_PASTEL = ['#D1E7DD', '#FEF3D1', '#D1E9FE', '#F8D7DA', '#E9D5FF'];

    let materiasCargadas = []; // Contendrá todas las materias, cargadas una sola vez
    let materiasMostradas = []; // Las materias que se muestran tras aplicar filtros
    let materiasAgregadas = new Map();
    let horario = {};
    let colorIndex = 0;

    // --- DOM ELEMENTS ---
    const materiasContainer = document.getElementById('materias-container');
    const searchInput = document.getElementById('search-input');
    const periodFilter = document.getElementById('period-filter');
    const semesterFilter = document.getElementById('semester-filter');
    const electiveFilter = document.getElementById('elective-filter');
    const programasSelect = document.getElementById('programas-select');
    const horarioGrid = document.getElementById('horario-grid');
    const clearScheduleBtn = document.getElementById('clear-schedule-btn');
    const allFilters = [searchInput, periodFilter, semesterFilter, electiveFilter, programasSelect];

    // --- API CALLS ---
    const fetchApi = async (url) => {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error("API Fetch Error: ", error);
            return null;
        }
    };

    // --- UI RENDERING ---
    const toTitleCase = (str) => str && str !== 'N/A' ? str.toLowerCase().replace(/\b\w/g, char => char.toUpperCase()) : 'No asignado';

    const renderMaterias = () => {
        materiasContainer.innerHTML = '';
        if (materiasMostradas.length === 0) {
            // Mensaje diferente si no hay resultados vs. si no se ha seleccionado el programa correcto
            if (programasSelect.value !== 'all' && programasSelect.value !== 'PROGRAMA DE LICENCIATURA EN INFORMATICA') {
                materiasContainer.innerHTML = '<p class="info-message">No hay materias para este programa en la versión actual.</p>';
            } else {
                materiasContainer.innerHTML = '<p class="info-message">No se encontraron materias para los filtros seleccionados.</p>';
            }
            return;
        }

        materiasMostradas.forEach(materia => {
            const isAdded = materiasAgregadas.has(materia.codigo);
            const card = document.createElement('div');
            card.className = `materia-card ${isAdded ? 'added' : ''}`;
            card.dataset.codigo = materia.codigo;
            card.innerHTML = `
                <h3>${toTitleCase(materia.nombre)}</h3>
                <div class="materia-details">
                    <span><i class="bi bi-person-fill"></i> ${toTitleCase(materia.docente)}</span>
                    <span><i class="bi bi-book-fill"></i> ${materia.creditos} créditos</span>
                </div>
                <button class="add-btn" ${isAdded ? 'disabled' : ''}>
                    <span class="add-text"><i class="bi bi-plus-lg"></i> Agregar</span>
                    <span class="added-text"><i class="bi bi-check-lg"></i> Agregado</span>
                </button>
            `;
            materiasContainer.appendChild(card);
        });
    };

    const renderHorarioGrid = () => {
        horarioGrid.innerHTML = '';
        DIAS.forEach((dia, index) => {
            const headerCell = document.createElement('div');
            headerCell.className = 'grid-header';
            headerCell.textContent = dia;
            headerCell.style.gridRow = '1';
            headerCell.style.gridColumn = `${index + 2}`;
            horarioGrid.appendChild(headerCell);
        });
        for (let hora = HORA_INICIO; hora < HORA_FIN; hora++) {
            const timeCell = document.createElement('div');
            timeCell.className = 'grid-time';
            timeCell.textContent = `${hora}:00`;
            const rowStart = (hora - HORA_INICIO) * 2 + 2;
            timeCell.style.gridRow = `${rowStart} / ${rowStart + 2}`;
            timeCell.style.gridColumn = '1';
            horarioGrid.appendChild(timeCell);
        }
        for (let row = 2; row <= (HORA_FIN - HORA_INICIO) * 2 + 1; row++) {
            for (let col = 2; col <= DIAS.length + 1; col++) {
                const bgCell = document.createElement('div');
                bgCell.className = 'grid-background-cell';
                bgCell.style.gridRow = `${row}`;
                bgCell.style.gridColumn = `${col}`;
                bgCell.style.borderBottom = (row - 2) % 2 === 0 ? '1px solid var(--color-gris-suave)' : '1px dotted var(--color-gris-suave)';
                horarioGrid.appendChild(bgCell);
            }
        }
    };

    // --- CORE LOGIC ---
    const getMateriaColor = (codigo) => {
        if (!materiasAgregadas.has(codigo) || !materiasAgregadas.get(codigo).color) {
            const color = PALETA_PASTEL[colorIndex % PALETA_PASTEL.length];
            colorIndex++;
            return color;
        }
        return materiasAgregadas.get(codigo).color;
    };

    const addMateriaToSchedule = (materia, grupo) => {
        for (const sesion of grupo.sesiones) {
            const [startHour, startMinute] = sesion.hora_inicio.split(':').map(Number);
            const [endHour, endMinute] = sesion.hora_fin.split(':').map(Number);
            let current = startHour * 60 + startMinute;
            const end = endHour * 60 + endMinute;
            while (current < end) {
                const h = Math.floor(current / 60);
                const m = current % 60;
                if (horario[`${sesion.dia}-${h}-${m}`]) {
                    alert(`Conflicto de horario: El espacio de ${sesion.dia} a las ${h}:${m === 0 ? '00' : m} ya está ocupado.`);
                    return false;
                }
                current += 30;
            }
        }
        const color = getMateriaColor(materia.codigo);
        materia.color = color;
        materiasAgregadas.set(materia.codigo, materia);
        grupo.sesiones.forEach(sesion => {
            const diaIndex = DIAS.indexOf(sesion.dia);
            if (diaIndex === -1) return;
            const [startHour, startMinute] = sesion.hora_inicio.split(':').map(Number);
            const [endHour, endMinute] = sesion.hora_fin.split(':').map(Number);
            const rowStart = (startHour - HORA_INICIO) * 2 + (startMinute / 30) + 2;
            const rowEnd = (endHour - HORA_INICIO) * 2 + (endMinute / 30) + 2;
            const colStart = diaIndex + 2;
            const block = document.createElement('div');
            block.className = 'class-block';
            block.dataset.codigo = materia.codigo;
            block.style.backgroundColor = color;
            block.style.gridColumn = `${colStart}`;
            block.style.gridRow = `${rowStart} / ${rowEnd}`;
            block.innerHTML = `
                <strong>${toTitleCase(materia.nombre)}</strong>
                <div class="class-details">${toTitleCase(grupo.docente)}</div>
                <div class="class-details">Gpo: ${grupo.nombre}</div>
                <button class="remove-class-btn" data-codigo="${materia.codigo}"><i class="bi bi-x"></i></button>
            `;
            horarioGrid.appendChild(block);
            let current = startHour * 60 + startMinute;
            const end = endHour * 60 + endMinute;
            while (current < end) {
                const h = Math.floor(current / 60);
                const m = current % 60;
                horario[`${sesion.dia}-${h}-${m}`] = materia.codigo;
                current += 30;
            }
        });
        return true;
    };

    const removeMateriaFromSchedule = (codigo) => {
        document.querySelectorAll(`.class-block[data-codigo="${codigo}"]`).forEach(el => el.remove());
        materiasAgregadas.delete(codigo);
        for (const key in horario) {
            if (horario[key] === codigo) delete horario[key];
        }
        renderMaterias();
    };

    // --- EVENT HANDLERS ---
    const handleAddClick = async (e) => {
        const addBtn = e.target.closest('.add-btn');
        if (!addBtn) return;
        const card = addBtn.closest('.materia-card');
        const codigo = card.dataset.codigo;
        if (materiasAgregadas.has(codigo)) return;
        const materiaDetails = await fetchApi(`${API_URL}/materias/${codigo}`);
        if (!materiaDetails || !materiaDetails.grupos || materiaDetails.grupos.length === 0) {
            alert('Esta materia no tiene grupos disponibles.');
            return;
        }
        if (addMateriaToSchedule(materiaDetails, materiaDetails.grupos[0])) {
            card.classList.add('added');
            addBtn.disabled = true;
        }
    };

    const handleRemoveClick = (e) => {
        const removeBtn = e.target.closest('.remove-class-btn');
        if (removeBtn) {
            removeMateriaFromSchedule(removeBtn.dataset.codigo);
        }
    };

    const applyFilters = () => {
        const searchTerm = searchInput.value.toLowerCase();
        const period = periodFilter.value;
        const semester = semesterFilter.value;
        const onlyElectives = electiveFilter.checked;
        const selectedProgram = programasSelect.value;

        // Lógica de filtrado en el cliente
        let materiasFiltradas = [];
        if (selectedProgram === 'PROGRAMA DE LICENCIATURA EN INFORMATICA') {
            materiasFiltradas = materiasCargadas.filter(m => {
                const searchMatch = searchTerm === '' ||
                    (m.nombre && m.nombre.toLowerCase().includes(searchTerm)) ||
                    (m.docente && m.docente.toLowerCase().includes(searchTerm));
                const semesterMatch = semester === 'all' || m.semestre == semester;
                const periodMatch = period === 'all' || m.periodo == period;
                const electiveMatch = !onlyElectives || m.es_electiva;
                return searchMatch && semesterMatch && periodMatch && electiveMatch;
            });
        }
        
        materiasMostradas = materiasFiltradas;
        renderMaterias();
    };

    const handleClear = () => {
        document.querySelectorAll('.class-block').forEach(el => el.remove());
        horario = {};
        materiasAgregadas.clear();
        colorIndex = 0;
        renderMaterias();
    };

    // --- INITIALIZATION ---
    const init = async () => {
        // --- Theme Switch Logic ---
        const themeCheckbox = document.getElementById('theme-checkbox');
        const applyTheme = (theme) => {
            document.body.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            themeCheckbox.checked = theme === 'dark';
        };
        themeCheckbox.addEventListener('change', (e) => applyTheme(e.target.checked ? 'dark' : 'light'));
        const savedTheme = localStorage.getItem('theme') || 'light';
        applyTheme(savedTheme);

        // --- App Initialization ---
        renderHorarioGrid();
        materiasContainer.innerHTML = '<div class="spinner-container"><div class="spinner"></div></div>';
        allFilters.forEach(el => el.disabled = true);

        const fetchedMaterias = await fetchApi(`${API_URL}/materias`);
        
        allFilters.forEach(el => el.disabled = false);

        if (fetchedMaterias) {
            materiasCargadas = fetchedMaterias;
            materiasContainer.innerHTML = '<p class="info-message">Seleccione un programa para buscar materias.</p>';
        } else {
            materiasContainer.innerHTML = '<p class="info-message">Error al cargar las materias. Intente de nuevo más tarde.</p>';
        }

        // Event listeners
        materiasContainer.addEventListener('click', handleAddClick);
        horarioGrid.addEventListener('click', handleRemoveClick);
        clearScheduleBtn.addEventListener('click', handleClear);
        allFilters.forEach(el => {
            const eventType = (el.tagName === 'INPUT' && el.type === 'text') ? 'input' : 'change';
            el.addEventListener(eventType, applyFilters);
        });
        
        const exportScheduleToPDF = () => {
            const { jsPDF } = window.jspdf;
            const scheduleContainer = document.getElementById('horario-grid-container');
            html2canvas(scheduleContainer, { scale: 2, useCORS: true, backgroundColor: getComputedStyle(document.body).getPropertyValue('--color-fondo') })
                .then(canvas => {
                    const imgData = canvas.toDataURL('image/png');
                    const pdf = new jsPDF({ orientation: 'landscape', unit: 'pt', format: 'letter' });
                    const pdfWidth = pdf.internal.pageSize.getWidth();
                    const pdfHeight = pdf.internal.pageSize.getHeight();
                    const ratio = canvas.width / canvas.height;
                    let newCanvasWidth = pdfWidth - 40;
                    let newCanvasHeight = newCanvasWidth / ratio;
                    if (newCanvasHeight > pdfHeight - 60) {
                        newCanvasHeight = pdfHeight - 60;
                        newCanvasWidth = newCanvasHeight * ratio;
                    }
                    const x = (pdfWidth - newCanvasWidth) / 2;
                    const y = 40;
                    pdf.setFontSize(18);
                    pdf.text('Mi Horario', pdfWidth / 2, 25, { align: 'center' });
                    pdf.addImage(imgData, 'PNG', x, y, newCanvasWidth, newCanvasHeight);
                    pdf.save('horario.pdf');
                });
        };

        document.getElementById('export-pdf-btn').addEventListener('click', exportScheduleToPDF);
        document.getElementById('export-ics-btn').addEventListener('click', () => alert('Función de exportar a .ics no implementada.'));
    };

    init();
});
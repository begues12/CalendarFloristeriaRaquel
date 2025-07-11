/**
 * API Cliente JavaScript para el Calendario
 * ==========================================
 * 
 * Este archivo proporciona funciones JavaScript para interactuar
 * con la API de notas del calendario desde el frontend.
 */

class CalendarAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
    }

    /**
     * Realizar petición HTTP con manejo de errores
     */
    async request(url, options = {}) {
        try {
            const response = await fetch(this.baseUrl + url, {
                ...options,
                headers: {
                    ...this.headers,
                    ...options.headers
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Añadir una nueva nota al calendario
     */
    async addNote(dateStr, noteData) {
        const data = {
            date_for: dateStr,
            title: noteData.title,
            content: noteData.content || '',
            color: noteData.color || '#ffc107',
            priority: noteData.priority || 'normal',
            is_private: noteData.isPrivate || false,
            is_reminder: noteData.isReminder || false,
            reminder_time: noteData.reminderTime || null
        };

        return await this.request('/api/notes', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * Añadir una nota rápida al calendario
     */
    async addQuickNote(dateStr, text, color = '#ffc107') {
        return await this.request(`/api/calendar/${dateStr}/quick-note`, {
            method: 'POST',
            body: JSON.stringify({
                text: text,
                color: color
            })
        });
    }

    /**
     * Obtener todas las notas de una fecha
     */
    async getNotesForDate(dateStr) {
        return await this.request(`/api/notes/${dateStr}`);
    }

    /**
     * Actualizar una nota existente
     */
    async updateNote(noteId, updates) {
        return await this.request(`/api/notes/${noteId}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
    }

    /**
     * Eliminar una nota
     */
    async deleteNote(noteId) {
        return await this.request(`/api/notes/${noteId}`, {
            method: 'DELETE'
        });
    }

    /**
     * Verificar si una fecha tiene notas
     */
    async checkDateHasNotes(dateStr) {
        return await this.request(`/api/calendar/${dateStr}/has-notes`);
    }
}

/**
 * Utilidades para el calendario
 */
class CalendarUtils {
    /**
     * Formatear fecha para la API (YYYY-MM-DD)
     */
    static formatDateForAPI(date) {
        if (typeof date === 'string') return date;
        if (date instanceof Date) {
            return date.toISOString().split('T')[0];
        }
        return null;
    }

    /**
     * Mostrar notificación de éxito
     */
    static showSuccess(message) {
        if (typeof toastr !== 'undefined') {
            toastr.success(message);
        } else {
            alert('✅ ' + message);
        }
    }

    /**
     * Mostrar notificación de error
     */
    static showError(message) {
        if (typeof toastr !== 'undefined') {
            toastr.error(message);
        } else {
            alert('❌ ' + message);
        }
    }

    /**
     * Obtener colores predefinidos para notas
     */
    static getColorOptions() {
        return {
            yellow: '#ffc107',    // Amarillo - Normal
            blue: '#007bff',      // Azul - Información
            green: '#28a745',     // Verde - Éxito/Completado
            orange: '#fd7e14',    // Naranja - Advertencia
            red: '#dc3545',       // Rojo - Urgente/Importante
            purple: '#6f42c1',    // Morado - Especial
            gray: '#6c757d'       // Gris - Menor prioridad
        };
    }

    /**
     * Obtener opciones de prioridad
     */
    static getPriorityOptions() {
        return {
            low: 'Baja',
            normal: 'Normal',
            high: 'Alta',
            urgent: 'Urgente'
        };
    }
}

/**
 * Manejador de eventos para el calendario
 */
class CalendarEventHandler {
    constructor() {
        this.api = new CalendarAPI();
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        // Evento al hacer clic en una fecha del calendario
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('calendar-date')) {
                this.handleDateClick(e.target);
            }
        });

        // Evento para formularios de notas rápidas
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('quick-note-form')) {
                e.preventDefault();
                this.handleQuickNoteSubmit(e.target);
            }
        });
    }

    /**
     * Manejar clic en fecha del calendario
     */
    async handleDateClick(dateElement) {
        const dateStr = dateElement.dataset.date;
        if (!dateStr) return;

        try {
            const result = await this.api.getNotesForDate(dateStr);
            this.displayNotesForDate(dateStr, result.notes);
        } catch (error) {
            CalendarUtils.showError('Error al cargar notas: ' + error.message);
        }
    }

    /**
     * Manejar envío de formulario de nota rápida
     */
    async handleQuickNoteSubmit(form) {
        const formData = new FormData(form);
        const dateStr = formData.get('date');
        const text = formData.get('text');
        const color = formData.get('color') || '#ffc107';

        if (!text.trim()) {
            CalendarUtils.showError('El texto de la nota no puede estar vacío');
            return;
        }

        try {
            const result = await this.api.addQuickNote(dateStr, text, color);
            CalendarUtils.showSuccess('Nota añadida al calendario');
            
            // Limpiar formulario
            form.reset();
            
            // Actualizar vista si es necesario
            this.refreshCalendarDate(dateStr);
        } catch (error) {
            CalendarUtils.showError('Error al añadir nota: ' + error.message);
        }
    }

    /**
     * Mostrar notas para una fecha
     */
    displayNotesForDate(dateStr, notes) {
        const modal = document.getElementById('notesModal');
        if (!modal) {
            console.warn('Modal de notas no encontrado');
            return;
        }

        const modalBody = modal.querySelector('.modal-body');
        const modalTitle = modal.querySelector('.modal-title');

        modalTitle.textContent = `Notas para ${dateStr}`;

        if (notes.length === 0) {
            modalBody.innerHTML = `
                <p class="text-muted">No hay notas para esta fecha.</p>
                <button class="btn btn-primary" onclick="calendarHandler.showAddNoteForm('${dateStr}')">
                    Añadir Nota
                </button>
            `;
        } else {
            modalBody.innerHTML = notes.map(note => `
                <div class="note-item mb-3 p-3 border-left" style="border-left-color: ${note.color};">
                    <h6 class="note-title">${note.title}</h6>
                    ${note.content ? `<p class="note-content">${note.content}</p>` : ''}
                    <small class="text-muted">
                        Prioridad: ${note.priority} | 
                        Por: ${note.creator} |
                        ${new Date(note.created_at).toLocaleString()}
                    </small>
                    <div class="note-actions mt-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="calendarHandler.editNote(${note.id})">
                            Editar
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="calendarHandler.deleteNote(${note.id}, '${dateStr}')">
                            Eliminar
                        </button>
                    </div>
                </div>
            `).join('');
        }

        // Mostrar modal (Bootstrap)
        if (typeof bootstrap !== 'undefined') {
            new bootstrap.Modal(modal).show();
        } else {
            modal.style.display = 'block';
        }
    }

    /**
     * Mostrar formulario para añadir nota
     */
    showAddNoteForm(dateStr) {
        const form = `
            <form class="add-note-form" onsubmit="calendarHandler.handleAddNoteSubmit(event, '${dateStr}')">
                <div class="mb-3">
                    <label class="form-label">Título *</label>
                    <input type="text" class="form-control" name="title" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Contenido</label>
                    <textarea class="form-control" name="content" rows="3"></textarea>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label class="form-label">Color</label>
                        <select class="form-control" name="color">
                            <option value="#ffc107">Amarillo</option>
                            <option value="#007bff">Azul</option>
                            <option value="#28a745">Verde</option>
                            <option value="#fd7e14">Naranja</option>
                            <option value="#dc3545">Rojo</option>
                            <option value="#6f42c1">Morado</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label">Prioridad</label>
                        <select class="form-control" name="priority">
                            <option value="normal">Normal</option>
                            <option value="low">Baja</option>
                            <option value="high">Alta</option>
                            <option value="urgent">Urgente</option>
                        </select>
                    </div>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="is_private">
                        <label class="form-check-label">Nota privada</label>
                    </div>
                </div>
                <div class="text-end">
                    <button type="button" class="btn btn-secondary" onclick="calendarHandler.handleDateClick(document.querySelector('[data-date=\\'${dateStr}\\']'))">
                        Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary">Guardar Nota</button>
                </div>
            </form>
        `;

        const modal = document.getElementById('notesModal');
        const modalBody = modal.querySelector('.modal-body');
        modalBody.innerHTML = form;
    }

    /**
     * Manejar envío de formulario de nueva nota
     */
    async handleAddNoteSubmit(event, dateStr) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);

        const noteData = {
            title: formData.get('title'),
            content: formData.get('content'),
            color: formData.get('color'),
            priority: formData.get('priority'),
            isPrivate: formData.has('is_private')
        };

        try {
            await this.api.addNote(dateStr, noteData);
            CalendarUtils.showSuccess('Nota creada correctamente');
            
            // Recargar notas para la fecha
            const result = await this.api.getNotesForDate(dateStr);
            this.displayNotesForDate(dateStr, result.notes);
            
            // Actualizar calendario
            this.refreshCalendarDate(dateStr);
        } catch (error) {
            CalendarUtils.showError('Error al crear nota: ' + error.message);
        }
    }

    /**
     * Eliminar una nota
     */
    async deleteNote(noteId, dateStr) {
        if (!confirm('¿Estás seguro de que quieres eliminar esta nota?')) {
            return;
        }

        try {
            await this.api.deleteNote(noteId);
            CalendarUtils.showSuccess('Nota eliminada');
            
            // Recargar notas para la fecha
            const result = await this.api.getNotesForDate(dateStr);
            this.displayNotesForDate(dateStr, result.notes);
            
            // Actualizar calendario
            this.refreshCalendarDate(dateStr);
        } catch (error) {
            CalendarUtils.showError('Error al eliminar nota: ' + error.message);
        }
    }

    /**
     * Actualizar indicador visual en el calendario para una fecha
     */
    async refreshCalendarDate(dateStr) {
        try {
            const result = await this.api.checkDateHasNotes(dateStr);
            const dateElement = document.querySelector(`[data-date="${dateStr}"]`);
            
            if (dateElement) {
                if (result.has_notes) {
                    dateElement.classList.add('has-notes');
                    // Añadir badge con número de notas
                    let badge = dateElement.querySelector('.note-count');
                    if (!badge) {
                        badge = document.createElement('span');
                        badge.className = 'note-count badge badge-primary';
                        dateElement.appendChild(badge);
                    }
                    badge.textContent = result.note_count;
                } else {
                    dateElement.classList.remove('has-notes');
                    const badge = dateElement.querySelector('.note-count');
                    if (badge) {
                        badge.remove();
                    }
                }
            }
        } catch (error) {
            console.error('Error al actualizar fecha del calendario:', error);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.calendarHandler = new CalendarEventHandler();
    console.log('🚀 Calendar API client iniciado');
});

// Exportar para uso modular
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CalendarAPI, CalendarUtils, CalendarEventHandler };
}

// Estado global de la aplicación
let generatedUrls = [];
let isGenerating = false;

// Elementos del DOM
const elements = {
    numCodes: document.getElementById('numCodes'),
    promoTypeRadios: document.querySelectorAll('input[name="promoType"]'),
    emailOptionRadios: document.querySelectorAll('input[name="emailOption"]'),
    customEmailInput: document.getElementById('customEmail'),
    customEmailContainer: document.getElementById('customEmailContainer'),
    generateBtn: document.getElementById('generateBtn'),
    btnLoader: document.getElementById('btnLoader'),
    statusMessage: document.getElementById('statusMessage'),
    progressContainer: document.getElementById('progressContainer'),
    progressFill: document.getElementById('progressFill'),
    progressText: document.getElementById('progressText'),
    urlList: document.getElementById('urlList'),
    noResultsMessage: document.getElementById('noResultsMessage'),
    copyAllBtn: document.getElementById('copyAllBtn'),
    downloadBtn: document.getElementById('downloadBtn'),
    summaryStats: document.getElementById('summaryStats'),
    toast: document.getElementById('toast')
};

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    updateEmailFieldVisibility();
});

// Configurar todos los event listeners
function initializeEventListeners() {
    // Cambio en opción de email
    elements.emailOptionRadios.forEach(radio => {
        radio.addEventListener('change', updateEmailFieldVisibility);
    });

    // Botón generar
    elements.generateBtn.addEventListener('click', handleGenerate);

    // Botones de acción
    elements.copyAllBtn.addEventListener('click', copyAllUrls);
    elements.downloadBtn.addEventListener('click', downloadUrls);

    // Validación en tiempo real del número de códigos
    elements.numCodes.addEventListener('input', validateNumCodes);

    // Validación del email personalizado
    elements.customEmailInput.addEventListener('input', validateCustomEmail);
}

// Mostrar/ocultar campo de email personalizado
function updateEmailFieldVisibility() {
    const isCustomEmail = document.querySelector('input[name="emailOption"]:checked').value === 'custom';
    
    if (isCustomEmail) {
        elements.customEmailContainer.classList.add('active');
        elements.customEmailInput.disabled = false;
        elements.customEmailInput.required = true;
    } else {
        elements.customEmailContainer.classList.remove('active');
        elements.customEmailInput.disabled = true;
        elements.customEmailInput.required = false;
        elements.customEmailInput.value = '';
    }
}

// Validar número de códigos
function validateNumCodes() {
    const value = parseInt(elements.numCodes.value);
    if (isNaN(value) || value < 1) {
        elements.numCodes.value = 1;
    } else if (value > 50) {
        elements.numCodes.value = 50;
        showToast('Máximo 50 códigos por solicitud', 'error');
    }
}

// Validar email personalizado
function validateCustomEmail() {
    const email = elements.customEmailInput.value.trim();
    const isValid = email === '' || isValidEmail(email);
    
    if (!isValid) {
        elements.customEmailInput.style.borderColor = 'var(--error-color)';
    } else {
        elements.customEmailInput.style.borderColor = 'var(--border)';
    }
}

// Validar formato de email
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Manejar la generación de códigos
async function handleGenerate() {
    if (isGenerating) return;

    const formData = getFormData();
    if (!validateFormData(formData)) return;

    try {
        isGenerating = true;
        setGeneratingState(true);
        resetResults();

        if (formData.numCodes === 1) {
            await generateSingleCode(formData);
        } else {
            await generateMultipleCodes(formData);
        }

    } catch (error) {
        console.error('Error durante la generación:', error);
        showStatus('Error de conexión. Por favor, inténtalo de nuevo.', 'error');
    } finally {
        isGenerating = false;
        setGeneratingState(false);
    }
}

// Obtener datos del formulario
function getFormData() {
    return {
        numCodes: parseInt(elements.numCodes.value),
        promoType: document.querySelector('input[name="promoType"]:checked').value,
        emailOption: document.querySelector('input[name="emailOption"]:checked').value,
        customEmail: elements.customEmailInput.value.trim()
    };
}

// Validar datos del formulario
function validateFormData(data) {
    if (isNaN(data.numCodes) || data.numCodes < 1 || data.numCodes > 50) {
        showStatus('Número de códigos inválido (1-50).', 'error');
        return false;
    }

    if (data.emailOption === 'custom' && !isValidEmail(data.customEmail)) {
        showStatus('Por favor, introduce un correo electrónico válido.', 'error');
        elements.customEmailInput.focus();
        return false;
    }

    return true;
}

// Generar un código individual
async function generateSingleCode(formData) {
    showStatus('Generando código...', 'info');
    showProgress(0);

    try {
        const response = await fetch('/api/generate_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            generatedUrls = [data.url];
            addUrlToList(data.code, data.url, 1);
            showStatus('¡Código generado exitosamente!', 'success');
            updateResultsVisibility();
            showToast('Código generado correctamente', 'success');
        } else {
            showStatus(`Error: ${data.error}`, 'error');
        }

    } catch (error) {
        showStatus('Error de conexión al generar código.', 'error');
        throw error;
    } finally {
        hideProgress();
    }
}

// Generar múltiples códigos
async function generateMultipleCodes(formData) {
    showStatus(`Generando ${formData.numCodes} códigos...`, 'info');
    showProgress(0);

    try {
        const response = await fetch('/api/generate_multiple_codes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            generatedUrls = data.results.map(result => result.url);
            
            // Mostrar resultados exitosos
            data.results.forEach(result => {
                addUrlToList(result.code, result.url, result.index);
            });

            // Mostrar errores si los hay
            if (data.errors.length > 0) {
                console.warn('Errores durante la generación:', data.errors);
            }

            const successMessage = `Generación completada: ${data.total_generated}/${data.total_requested} códigos generados`;
            showStatus(successMessage, data.total_failed > 0 ? 'warning' : 'success');
            
            updateResultsVisibility();
            updateSummaryStats(data);
            
            const toastMessage = data.total_failed > 0 
                ? `${data.total_generated} códigos generados, ${data.total_failed} fallaron`
                : `${data.total_generated} códigos generados correctamente`;
            showToast(toastMessage, data.total_failed > 0 ? 'error' : 'success');

        } else {
            showStatus(`Error: ${data.error}`, 'error');
        }

    } catch (error) {
        showStatus('Error de conexión al generar códigos.', 'error');
        throw error;
    } finally {
        hideProgress();
    }
}

// Agregar URL a la lista visual
function addUrlToList(code, url, index) {
    const urlItem = document.createElement('div');
    urlItem.className = 'url-item';
    urlItem.innerHTML = `
        <div class="url-item-header">
            <span class="url-item-code">#${index} - ${code}</span>
            <button class="url-item-copy" onclick="copyUrl('${url}')">
                <i class="fas fa-copy"></i> Copiar
            </button>
        </div>
        <div class="url-item-url">${url}</div>
    `;
    
    elements.urlList.appendChild(urlItem);
}

// Copiar URL individual
async function copyUrl(url) {
    try {
        await navigator.clipboard.writeText(url);
        showToast('URL copiada al portapapeles', 'success');
    } catch (error) {
        console.error('Error al copiar URL:', error);
        showToast('Error al copiar URL', 'error');
    }
}

// Copiar todas las URLs
async function copyAllUrls() {
    if (generatedUrls.length === 0) return;

    try {
        const allUrlsText = generatedUrls.join('\n');
        await navigator.clipboard.writeText(allUrlsText);
        showToast(`${generatedUrls.length} URLs copiadas al portapapeles`, 'success');
    } catch (error) {
        console.error('Error al copiar URLs:', error);
        showToast('Error al copiar URLs', 'error');
    }
}

// Descargar URLs como archivo .txt
function downloadUrls() {
    if (generatedUrls.length === 0) return;

    try {
        const allUrlsText = generatedUrls.join('\n');
        const blob = new Blob([allUrlsText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `playmo_urls_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('Archivo descargado correctamente', 'success');
    } catch (error) {
        console.error('Error al descargar archivo:', error);
        showToast('Error al descargar archivo', 'error');
    }
}

// Mostrar mensaje de estado
function showStatus(message, type = 'info') {
    elements.statusMessage.textContent = message;
    elements.statusMessage.className = `status-message show ${type}`;
}

// Ocultar mensaje de estado
function hideStatus() {
    elements.statusMessage.classList.remove('show');
}

// Mostrar barra de progreso
function showProgress(percentage) {
    elements.progressContainer.classList.add('show');
    elements.progressFill.style.width = `${percentage}%`;
    elements.progressText.textContent = `${Math.round(percentage)}%`;
}

// Ocultar barra de progreso
function hideProgress() {
    elements.progressContainer.classList.remove('show');
}

// Establecer estado de generación
function setGeneratingState(generating) {
    elements.generateBtn.disabled = generating;
    
    if (generating) {
        elements.generateBtn.classList.add('loading');
    } else {
        elements.generateBtn.classList.remove('loading');
    }
}

// Resetear resultados
function resetResults() {
    generatedUrls = [];
    elements.urlList.innerHTML = '';
    elements.summaryStats.classList.remove('show');
    updateResultsVisibility();
}

// Actualizar visibilidad de la sección de resultados
function updateResultsVisibility() {
    const hasResults = generatedUrls.length > 0;
    
    if (hasResults) {
        elements.noResultsMessage.style.display = 'none';
        elements.urlList.classList.add('show');
        elements.copyAllBtn.disabled = false;
        elements.downloadBtn.disabled = false;
    } else {
        elements.noResultsMessage.style.display = 'block';
        elements.urlList.classList.remove('show');
        elements.copyAllBtn.disabled = true;
        elements.downloadBtn.disabled = true;
    }
}

// Actualizar estadísticas de resumen
function updateSummaryStats(data) {
    const statsHtml = `
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">${data.total_requested}</div>
                <div class="stat-label">Solicitados</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${data.total_generated}</div>
                <div class="stat-label">Generados</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${data.total_failed}</div>
                <div class="stat-label">Fallidos</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${Math.round((data.total_generated / data.total_requested) * 100)}%</div>
                <div class="stat-label">Éxito</div>
            </div>
        </div>
    `;
    
    elements.summaryStats.innerHTML = statsHtml;
    elements.summaryStats.classList.add('show');
}

// Mostrar notificación toast
function showToast(message, type = 'success') {
    const toastIcon = elements.toast.querySelector('.toast-icon');
    const toastMessage = elements.toast.querySelector('.toast-message');
    
    // Configurar icono según el tipo
    if (type === 'success') {
        toastIcon.className = 'toast-icon fas fa-check-circle';
    } else if (type === 'error') {
        toastIcon.className = 'toast-icon fas fa-exclamation-circle';
    } else {
        toastIcon.className = 'toast-icon fas fa-info-circle';
    }
    
    toastMessage.textContent = message;
    elements.toast.className = `toast show ${type}`;
    
    // Ocultar después de 3 segundos
    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}

// Función global para copiar URLs (llamada desde HTML)
window.copyUrl = copyUrl;


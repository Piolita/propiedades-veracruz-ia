// Espera a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log('search_modals.js se está ejecutando (versión final y corregida).');

    // ##################################################################
    // INICIO: Referencias a elementos del DOM y variables de estado
    // ##################################################################

    // Referencias a los modales de Bootstrap
    const searchModalVentaElement = document.getElementById('searchModalVenta');
    const searchModalRentaElement = document.getElementById('searchModalRenta');
    const validationModalElement = document.getElementById('validationModal');
    const deleteConfirmationModalElement = document.getElementById('deleteConfirmationModal');

    // Instancias de Bootstrap Modal (creadas solo si el elemento existe)
    const searchModalVenta = searchModalVentaElement ? new bootstrap.Modal(searchModalVentaElement) : null;
    const searchModalRenta = searchModalRentaElement ? new bootstrap.Modal(searchModalRentaElement) : null;
    const validationModal = validationModalElement ? new bootstrap.Modal(validationModalElement) : null;

    let propertyIdToDelete = null; // Variable para almacenar el ID de la propiedad a eliminar

    // Referencias a los botones "Buscar" dentro de cada modal de búsqueda
    const submitSearchVentaBtn = document.getElementById('submitSearchVenta');
    const submitSearchRentaBtn = document.getElementById('submitSearchRenta');

    // Referencia al botón flotante de WhatsApp
    const whatsappFloatBtn = document.getElementById('whatsapp-float-btn');

    // ##################################################################
    // FIN: Referencias a elementos del DOM y variables de estado
    // ##################################################################


    // ##################################################################
    // INICIO: Funciones de Búsqueda y Validación
    // ##################################################################

    /**
     * Muestra el modal de validación con un mensaje específico.
     * @param {string} message - El mensaje a mostrar en el modal.
     */
    function showValidationMessage(message) {
        const validationMessageElement = document.getElementById('validationMessage');
        if (validationMessageElement && validationModal) {
            validationMessageElement.textContent = message;
            validationModal.show();
        } else {
            console.error("Error: Elementos del modal de validación no encontrados.");
            alert(message); // Fallback
        }
    }

    /**
     * Obtiene los parámetros del formulario de búsqueda y redirige.
     * @param {string} formId - El ID del formulario (ej. 'searchFormVenta' o 'searchFormRenta').
     * @param {object} modalInstance - La instancia del modal de Bootstrap a cerrar.
     */
    function performSearch(formId, modalInstance) {
        const form = document.getElementById(formId);
        if (!form) {
            console.error(`Formulario con ID ${formId} no encontrado.`);
            return;
        }
        const queryParams = new URLSearchParams();

        // Obtener valores de los campos específicos del formulario
        const operationElement = form.querySelector('input[name="operation"]');
        const propertyTypeElement = form.querySelector('select[name="property_type"]');
        const locationElement = form.querySelector('select[name="location"]');
        const minBedroomsElement = form.querySelector('input[name="min_bedrooms"]');
        const maxBedroomsElement = form.querySelector('input[name="max_bedrooms"]');
        const priceRangeElement = form.querySelector('select[name="price_range"]');

        const operation = operationElement ? operationElement.value : '';
        const propertyType = propertyTypeElement ? propertyTypeElement.value : '';
        const location = locationElement ? locationElement.value : '';
        const minBedrooms = minBedroomsElement ? minBedroomsElement.value : '';
        const maxBedrooms = maxBedroomsElement ? maxBedroomsElement.value : '';
        const priceRange = priceRangeElement ? priceRangeElement.value : '';

        // Validar que al menos un campo de búsqueda esté lleno o que se haya seleccionado algo
        if (!propertyType && !location && !minBedrooms && !maxBedrooms && !priceRange) {
            if (modalInstance) {
                modalInstance.hide(); // Oculta el modal actual antes de mostrar el de validación
            }
            showValidationMessage('Por favor, selecciona al menos un criterio de búsqueda para refinar tu búsqueda.');
            return;
        }

        // Añadir parámetros a la URL si tienen valor
        if (operation) queryParams.append('operation', operation);
        if (propertyType) queryParams.append('property_type', propertyType);
        if (location) queryParams.append('location', location);
        if (minBedrooms) queryParams.append('min_bedrooms', minBedrooms);
        if (maxBedrooms) queryParams.append('max_bedrooms', maxBedrooms);
        if (priceRange) queryParams.append('price_range', priceRange);

        // Redirige a la página principal con los parámetros de búsqueda
        window.location.href = `/?${queryParams.toString()}`;
    }

    /**
     * Maneja la eliminación de una propiedad después de la confirmación del modal.
     */
    function handleDeleteConfirmation() {
        if (propertyIdToDelete) {
            console.log("handleDeleteConfirmation: Iniciando eliminación para ID:", propertyIdToDelete); // Debugging
            // Crea un formulario dinámico para enviar la solicitud POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/delete_property/${propertyIdToDelete}`;
            document.body.appendChild(form);
            form.submit();
        } else {
            console.error("handleDeleteConfirmation: No hay ID de propiedad para eliminar.");
        }
    }

    // ##################################################################
    // FIN: Funciones de Búsqueda y Validación
    // ##################################################################


    // ##################################################################
    // INICIO: Lógica del Botón Flotante de WhatsApp
    // ##################################################################

    function updateWhatsAppLink() {
        if (!whatsappFloatBtn) {
            console.warn("Botón flotante de WhatsApp no encontrado.");
            return;
        }

        const currentPath = window.location.pathname;
        let message = "Hola, me interesa saber más sobre Propiedades Veracruz IA.";
        let phoneNumber = "522293019294"; // ¡NÚMERO DE TELÉFONO CORREGIDO!

        // Detectar si estamos en la página de detalle de una propiedad
        const propertyDetailMatch = currentPath.match(/\/property\/(\d+)/);
        if (propertyDetailMatch) {
            const propertyId = propertyDetailMatch[1];
            message = `Hola, me interesa la propiedad con ID ${propertyId}. ¿Podrías darme más información?`;
        }

        const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;
        whatsappFloatBtn.href = whatsappUrl;
    }

    // Llamar a la función al cargar la página
    updateWhatsAppLink();

    // ##################################################################
    // FIN: Lógica del Botón Flotante de WhatsApp
    // ##################################################################


    // ##################################################################
    // INICIO: Event Listeners (Controladores de Eventos)
    // ##################################################################

    // Event listener para el botón "Buscar" del modal de Venta
    if (submitSearchVentaBtn) {
        submitSearchVentaBtn.addEventListener('click', function() {
            console.log("Click en Buscar Venta"); // Debugging
            performSearch('searchFormVenta', searchModalVenta);
        });
    }

    // Event listener para el botón "Buscar" del modal de Renta
    if (submitSearchRentaBtn) {
        submitSearchRentaBtn.addEventListener('click', function() {
            console.log("Click en Buscar Renta"); // Debugging
            performSearch('searchFormRenta', searchModalRenta);
        });
    }

    // Event listener para abrir el modal de confirmación de eliminación
    // Delegamos el evento al documento para capturar clics en botones de eliminación dinámicos
    document.addEventListener('click', function(event) {
        if (event.target && event.target.matches('button[data-bs-target="#deleteConfirmationModal"]')) {
            propertyIdToDelete = event.target.dataset.propertyId; // Captura el ID de la propiedad
            console.log("Botón Eliminar clicado. propertyIdToDelete:", propertyIdToDelete); // Debugging

            if (deleteConfirmationModalElement) {
                const deleteConfirmationModalInstance = new bootstrap.Modal(deleteConfirmationModalElement);
                deleteConfirmationModalInstance.show(); // Muestra el modal de confirmación

                const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
                if (confirmDeleteBtn) {
                    confirmDeleteBtn.removeEventListener('click', handleDeleteConfirmation);
                    confirmDeleteBtn.addEventListener('click', handleDeleteConfirmation);
                    console.log("Listener adjuntado a confirmDeleteBtn."); // Debugging
                }
            } else {
                console.error("Elemento del modal de confirmación de eliminación no encontrado. Asegúrate de que el modal esté en el DOM.");
            }
        }
    });

    // ##################################################################
    // FIN: Event Listeners
    // ##################################################################

}); // Cierre de DOMContentLoaded

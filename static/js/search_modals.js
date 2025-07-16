// Espera a que el DOM esté completamente cargado (más fiable que window.onload para elementos dinámicos)
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
    // La instancia de deleteConfirmationModal se creará más tarde, bajo demanda.

    let propertyIdToDelete = null; // Variable para almacenar el ID de la propiedad a eliminar

    // Referencias a los botones "Buscar" dentro de cada modal de búsqueda
    const submitSearchVentaBtn = document.getElementById('submitSearchVenta');
    const submitSearchRentaBtn = document.getElementById('submitSearchRenta');

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
        // Asegúrate de que el elemento clicado sea el botón "Eliminar Propiedad"
        // y que tenga los atributos data-bs-toggle y data-property-id
        if (event.target && event.target.matches('button[data-bs-target="#deleteConfirmationModal"]')) {
            propertyIdToDelete = event.target.dataset.propertyId; // Captura el ID de la propiedad
            console.log("Botón Eliminar clicado. propertyIdToDelete:", propertyIdToDelete); // Debugging

            // Crea la instancia del modal aquí, justo antes de mostrarlo
            if (deleteConfirmationModalElement) {
                const deleteConfirmationModalInstance = new bootstrap.Modal(deleteConfirmationModalElement);
                deleteConfirmationModalInstance.show(); // Muestra el modal de confirmación

                // Adjunta el listener al botón de confirmación *dentro del modal*
                // Esto asegura que el botón existe cuando se intenta adjuntar el listener
                const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
                if (confirmDeleteBtn) {
                    // Eliminar cualquier listener previo para evitar duplicados
                    confirmDeleteBtn.removeEventListener('click', handleDeleteConfirmation);
                    confirmDeleteBtn.addEventListener('click', handleDeleteConfirmation);
                    console.log("Listener adjuntado a confirmDeleteBtn."); // Debugging
                }
                // No necesitamos el 'else' aquí porque la advertencia ya no es relevante.
            } else {
                console.error("Elemento del modal de confirmación de eliminación no encontrado. Asegúrate de que el modal esté en el DOM.");
            }
        }
    });

    // Eliminamos la advertencia que causaba confusión, ya que el listener se adjunta correctamente al abrir el modal.
    // if (confirmDeleteBtn) { // Esta sección se ha movido al listener 'shown.bs.modal'
    //     confirmDeleteBtn.addEventListener('click', function() {
    //         console.log("Botón Confirmar Eliminar clicado."); // Debugging
    //         handleDeleteConfirmation();
    //     });
    // } else {
    //     console.warn("Botón 'confirmDeleteBtn' no encontrado. Asegúrate de que el ID sea correcto."); // Debugging
    // }

    // ##################################################################
    // FIN: Event Listeners
    // ##################################################################

}); // Cierre de DOMContentLoaded

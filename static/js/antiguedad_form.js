document.addEventListener('DOMContentLoaded', function() {
    // Función para manejar la visibilidad del campo de años
    function toggleAntiguedadYears(optionSelectId, yearsFieldId) {
        const antiguedadOption = document.getElementById(optionSelectId);
        const antiguedadYearsField = document.getElementById(yearsFieldId);

        if (antiguedadOption && antiguedadYearsField) { // Asegura que los elementos existen
            if (antiguedadOption.value === 'years') {
                antiguedadYearsField.style.display = 'block'; // Muestra el campo
            } else {
                antiguedadYearsField.style.display = 'none'; // Oculta el campo
            }
        }
    }

    // Para add_property.html
    // Llama a la función al cargar la página para establecer el estado inicial
    toggleAntiguedadYears('antiguedad_option', 'antiguedad_years_field');

    // Agrega un escuchador de eventos para cuando cambie la selección en add_property.html
    const addAntiguedadOption = document.getElementById('antiguedad_option');
    if (addAntiguedadOption) {
        addAntiguedadOption.addEventListener('change', function() {
            toggleAntiguedadYears('antiguedad_option', 'antiguedad_years_field');
        });
    }

    // Para edit_property.html
    // Llama a la función al cargar la página para establecer el estado inicial
    toggleAntiguedadYears('antiguedad_option', 'antiguedad_years_field_edit');

    // Agrega un escuchador de eventos para cuando cambie la selección en edit_property.html
    const editAntiguedadOption = document.getElementById('antiguedad_option');
    if (editAntiguedadOption) {
         editAntiguedadOption.addEventListener('change', function() {
            toggleAntiguedadYears('antiguedad_option', 'antiguedad_years_field_edit');
        });
    }
});
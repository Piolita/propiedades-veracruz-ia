// Espera a que el DOM esté completamente cargado antes de ejecutar el script
document.addEventListener('DOMContentLoaded', function() {
    // Obtiene el contenedor principal del carrusel
    const carouselContainer = document.querySelector('.carousel-container');

    // Si no hay un contenedor de carrusel en la página, no hagas nada
    if (!carouselContainer) {
        return;
    }

    // Obtiene todas las imágenes dentro del carrusel
    const images = carouselContainer.querySelectorAll('.carousel-image');
    // Obtiene los botones de navegación
    const prevButton = carouselContainer.querySelector('.carousel-button.prev');
    const nextButton = carouselContainer.querySelector('.carousel-button.next');
    // Obtiene el contenedor para los puntos indicadores
    const dotsContainer = carouselContainer.querySelector('.carousel-dots');

    // Variable para llevar el seguimiento de la imagen actual mostrada
    let currentIndex = 0;

    // Función para mostrar una imagen específica
    function showImage(index) {
        // Asegura que el índice esté dentro de los límites de las imágenes
        if (index >= images.length) {
            currentIndex = 0; // Vuelve a la primera imagen si se pasa del final
        } else if (index < 0) {
            currentIndex = images.length - 1; // Va a la última imagen si se pasa del principio
        } else {
            currentIndex = index; // Establece el índice actual
        }

        // Calcula cuánto debe moverse el contenedor de imágenes para mostrar la imagen actual
        // La transformación mueve el contenedor horizontalmente
        carouselContainer.querySelector('.carousel-images').style.transform = `translateX(${-currentIndex * 100}%)`;

        // Actualiza las clases 'active' para las imágenes
        images.forEach((img, i) => {
            if (i === currentIndex) {
                img.classList.add('active'); // Añade la clase 'active' a la imagen actual
            } else {
                img.classList.remove('active'); // Elimina la clase 'active' de las otras imágenes
            }
        });

        // Actualiza los puntos indicadores
        updateDots();
    }

    // Función para ir a la imagen anterior
    function goToPrevImage() {
        showImage(currentIndex - 1);
    }

    // Función para ir a la imagen siguiente
    function goToNextImage() {
        showImage(currentIndex + 1);
    }

    // Función para crear y actualizar los puntos indicadores
    function updateDots() {
        dotsContainer.innerHTML = ''; // Limpia los puntos existentes
        images.forEach((_, i) => {
            const dot = document.createElement('span'); // Crea un elemento span para cada punto
            dot.classList.add('dot'); // Añade la clase 'dot'
            if (i === currentIndex) {
                dot.classList.add('active'); // Marca el punto activo
            }
            // Añade un evento de clic a cada punto para ir a la imagen correspondiente
            dot.addEventListener('click', () => showImage(i));
            dotsContainer.appendChild(dot); // Añade el punto al contenedor
        });
    }

    // Añade los eventos de clic a los botones de navegación
    if (prevButton) {
        prevButton.addEventListener('click', goToPrevImage);
    }
    if (nextButton) {
        nextButton.addEventListener('click', goToNextImage);
    }

    // Inicializa el carrusel mostrando la primera imagen y creando los puntos
    showImage(currentIndex);
});

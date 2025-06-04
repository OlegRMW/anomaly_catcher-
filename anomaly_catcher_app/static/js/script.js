"use strict";
document.querySelector('.search-filter').addEventListener('submit', function(event) {
    event.preventDefault(); // Предотвращаем стандартное поведение отправки формы

    const formData = new FormData(this);

    fetch('/wheels', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // или response.text() в зависимости от ответа сервера
    })
    .then(data => {
        console.log('Success:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});





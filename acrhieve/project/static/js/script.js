const socket = io();

document.getElementById('optimization-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Отправляем данные на сервер
    socket.emit('start_optimization', data);
});

// Обработка обновлений итераций
socket.on('iteration_update', function (data) {
    console.log('Received iteration data:', data);  // Логирование данных
    const canvas = document.getElementById('topology-canvas');
    const ctx = canvas.getContext('2d');
    const topology = data.topology;

    // Убедитесь, что canvas имеет размеры
    canvas.width = topology[0].length;  // Ширина canvas = количество столбцов
    canvas.height = topology.length;    // Высота canvas = количество строк

    // Очистка canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Отрисовка топологии
    const cellSize = Math.min(canvas.width / topology[0].length, canvas.height / topology.length);
    for (let i = 0; i < topology.length; i++) {
        for (let j = 0; j < topology[i].length; j++) {
            const value = topology[i][j];
            ctx.fillStyle = value > 0.5 ? '#000' : '#FFF';  // Черный для материала, белый для пустоты
            ctx.fillRect(j * cellSize, i * cellSize, cellSize, cellSize);
        }
    }

    // Отображение номера итерации
    document.getElementById('iteration-info').textContent = `Итерация: ${data.iteration}`;
});


document.getElementById('optimization-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Отправляем данные на сервер
    fetch('/.netlify/functions/optimize', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: { 'Content-Type': 'application/json' },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // Обработка ответа
    });
});

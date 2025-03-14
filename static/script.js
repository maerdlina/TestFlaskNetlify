const socket = io();

document.getElementById('optimization-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Отправляем данные на сервер
    socket.emit('start_optimization', data);

    // Вызов функции для отрисовки балки сразу после отправки формы
    drawInitialBeam(data.nelx, data.nely, data.loadValue); // Pass load value from form
});

// Обработка обновлений итераций
socket.on('iteration_update', function (data) {
    console.log('Received iteration data:', data); // Логирование данных
    const canvas = document.getElementById('topology-canvas');
    const ctx = canvas.getContext('2d');

    const nelx = parseInt(document.getElementById('nelx').value);
    const nely = parseInt(document.getElementById('nely').value);

    // Убедитесь, что canvas имеет размеры
    const cellSize = 5; // Размер ячейки
    canvas.width = nelx * cellSize; // Ширина canvas
    canvas.height = nely * cellSize; // Высота canvas

    // Очистка canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Отрисовка топологии
    const topology = data.topology;
    for (let i = 0; i < topology.length; i++) {
        for (let j = 0; j < topology[i].length; j++) {
            const value = topology[i][j];
            ctx.fillStyle = value > 0.5 ? '#000' : '#FFF'; // Черный для материала, белый для пустоты
            ctx.fillRect(j * cellSize, i * cellSize, cellSize, cellSize);
        }
    }

    // Отрисовка сетки
    ctx.strokeStyle = "#ccc"; // Цвет сетки
    for (let i = 0; i <= nelx; i++) {
        ctx.moveTo(i * cellSize, 0);
        ctx.lineTo(i * cellSize, canvas.height);
    }
    for (let j = 0; j <= nely; j++) {
        ctx.moveTo(0, j * cellSize);
        ctx.lineTo(canvas.width, j * cellSize);
    }
    ctx.stroke();

    // Отображение номера итерации
    document.getElementById('iteration-info').textContent = `Итерация: ${data.iteration}`;

    // Вызов функции для отрисовки балки
    drawBeam(nelx, nely, data.loadValue); // Pass load value from data
});

// Функция для отрисовки начальной балки и нагрузки
// Функция для отрисовки начальной балки и нагрузки
function drawInitialBeam(nelx, nely, loadValue) {
    const beamCanvas = document.getElementById('initial-beam-canvas');
    const beamCtx = beamCanvas.getContext('2d');

    // Рассчитываем размеры балки на основе введенных пользователем данных
    const beamLength = nelx * 3; // Умножаем количество элементов по X на коэффициент для масштабирования
    const beamWidth = nely * 3; // Умножаем количество элементов по Y на коэффициент для масштабирования

    // Установим размеры канваса на основе размеров балки
    beamCanvas.width = beamLength + 100; // Добавляем отступы для стрелки нагрузки
    beamCanvas.height = beamWidth + 100; // Добавляем отступы для стрелки нагрузки

    // Очистка канваса
    beamCtx.clearRect(0, 0, beamCanvas.width, beamCanvas.height);

    // Параметры балки
    const beamPositionY = beamCanvas.height / 2; // Позиция балки по Y (центрированная)

    // Отрисовка балки
    beamCtx.fillStyle = '#000'; // Цвет балки
    beamCtx.fillRect(50, beamPositionY - beamWidth / 2, beamLength, beamWidth); // Параметры: x, y, width, height

    // Определение направления нагрузки
    const arrowStartX = 50 + beamLength; // Начальная точка стрелки по X (на правом краю балки)
    const arrowStartY = beamPositionY + beamWidth / 2; // Начальная точка стрелки по Y (центр балки)

    // Отрисовка стрелки
    beamCtx.beginPath();
    beamCtx.moveTo(arrowStartX, arrowStartY); // Начальная точка стрелки

    // Если нагрузка -1, стрелка направлена вниз
    if (loadValue < 0) {
        beamCtx.lineTo(arrowStartX + 10, arrowStartY + 20); // Конечная точка стрелки (стрелка вниз)
        beamCtx.lineTo(arrowStartX - 10, arrowStartY + 20); // Конечная точка стрелки (стрелка вниз)
    } else {
        // Если нагрузка положительная, стрелка направлена вверх
        beamCtx.lineTo(arrowStartX + 10, arrowStartY - 20); // Конечная точка стрелки (стрелка вверх)
        beamCtx.lineTo(arrowStartX - 10, arrowStartY - 20); // Конечная точка стрелки (стрелка вверх)
    }

    beamCtx.fillStyle = 'red'; // Цвет стрелки
    beamCtx.fill(); // Заливка стрелки
    beamCtx.closePath();
}

// Вызов функции при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
    const nelx = parseInt(document.getElementById('nelx').value);
    const nely = parseInt(document.getElementById('nely').value);
    const loadValue = -1; // Значение нагрузки по умолчанию
    drawInitialBeam(nelx, nely, loadValue);
});

// Вызов функции при изменении параметров
document.getElementById('optimization-form').addEventListener('input', function () {
    const nelx = parseInt(document.getElementById('nelx').value);
    const nely = parseInt(document.getElementById('nely').value);
    const loadValue = -1; // Значение нагрузки по умолчанию
    drawInitialBeam(nelx, nely, loadValue);
});

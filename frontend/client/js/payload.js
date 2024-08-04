document.addEventListener("DOMContentLoaded", () => {
    let measurementEl = document.querySelector('[data-id=Measurements]');

    let template = document.querySelector('[data-id=data-template]');
    let socket = io.connect(window.socketString);

    socket.on('weather_update', (data) => {
        let fragment = document.createDocumentFragment();

        for (let key in data) {
            let clone = template.content.cloneNode(true);
            let locationEl = clone.querySelector('[data-id=Location]');
            let fahrenheitEl = clone.querySelector('[data-id=Fahrenheit]');
            let humidityEl = clone.querySelector('[data-id=Humidity]');

            locationEl.textContent = data[key].Room;
            fahrenheitEl.textContent = data[key].Temp;
            humidityEl.textContent = data[key].H20;

            fragment.appendChild(clone);
        }

        measurementEl.innerHTML = '';
        measurementEl.appendChild(fragment);
    });
});
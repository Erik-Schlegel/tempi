document.addEventListener("DOMContentLoaded", () => {
    let measurementEl = document.querySelector('[data-id=Measurements]');
    let template = document.querySelector('[data-id=data-template]');
    let socket = io.connect(window.socketString);

    socket.on('weather_update', (data) => {
        let fragment = document.createDocumentFragment();

        for (let key in data) {
            let clone = template.content.cloneNode(true);
            let h2 = clone.querySelector('h2');
            let temp = clone.querySelector('p:nth-child(2) span');
            let h20 = clone.querySelector('p:nth-child(3) span');

            h2.textContent = data[key].Room;
            temp.textContent = data[key].Temp;
            h20.textContent = data[key].H20;

            fragment.appendChild(clone);
        }

        measurementEl.innerHTML = '';
        measurementEl.appendChild(fragment);
    });
});

const getTimeRoundedToInterval = (timestr, interval=15) => {
    const [hours, minutes] = timestr.split(':').map(Number);
    const minutesRounded = String(Math.round(minutes/interval)*interval).padStart(2, '0');
    return `${hours}:${minutesRounded}${timestr.slice(-2)}`;
}


const getSunriseSunset = async(latitude, longitude, timeZoneId) =>
{
    let response = await fetch(`https://api.sunrise-sunset.org/json?lat=${latitude}&lng=${longitude}&date=today&tzid=${timeZoneId}`);
    response = await response.json();

    if (response.status !== "OK")
    {
        console.error("Error fetching sunrise and sunset times");
        return [null, null];
    }

    return [
        getTimeRoundedToInterval(response.results.sunrise),
        getTimeRoundedToInterval(response.results.sunset)
    ];
}



document.addEventListener("DOMContentLoaded",
  async ()=>
    {
        let measurementEl = document.querySelector('[data-id=Measurements]');
        let chartEl = document.querySelector('[data-id=Chart]');
        let chartInstance = null;

        let template = document.querySelector('[data-id=data-template]');
        let socket = io.connect(window.apiUrl);
        let riseSet = await getSunriseSunset(window.latitude, window.longitude, window.timeZoneId);

        socket.on('weather_update', data=> {
            let fragment = document.createDocumentFragment();

            for (let key in data) {
                let clone = template.content.cloneNode(true);
                let locationEl = clone.querySelector('[data-id=Location]');
                let fahrenheitEl = clone.querySelector('[data-id=Fahrenheit]');
                let humidityEl = clone.querySelector('[data-id=Humidity]');

                locationEl.textContent = data[key].Location;
                fahrenheitEl.textContent = data[key].Temp;
                humidityEl.textContent = data[key].H20;

                fragment.appendChild(clone);
            }

            measurementEl.innerHTML = '';
            measurementEl.appendChild(fragment);
        }
    );


    socket.on('historical_temps', receivedData=>
    {
      const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const dFormat = "dd h:mmA";

      // console.log(receivedData);

      let datapoints = [];
      let labelpoints = [];

      for(let i=0, len=receivedData.length; i<len; i++)
      {
        datapoints[i] = [];
        labelpoints = [];
        for(let j=0, len2 = receivedData[i].temps.length; j<len2; j++)
        {
          datapoints[i].push(receivedData[i].temps[j].fahrenheit);
          labelpoints.push(moment.tz(receivedData[i].temps[j].datetime, "GMT").tz(browserTimezone).format(dFormat));
        }

      }



      const data = {
        labels: labelpoints,
        datasets: [
          {
            label: 'Living Room',
            data: datapoints[0],
            borderColor: 'rgba(94, 90, 102, .8)',
            borderWidth: 1
          },
          {
            label: 'Outside',
            data: datapoints[1],
            borderColor: 'rgba(255, 90, 102, .8)',
            borderWidth: 1
          },
        ]
      };

      const config = {
          type: 'line',
          data,
          options: {
            responsive: true,
            plugins: {
              annotation: {
                  annotations: {
                    line1: {
                      type: 'line',
                      xMin: riseSet[0],
                      xMax: riseSet[0],
                      borderColor: 'rgba(255, 100, 100, .25)',
                      borderWidth: 2,
                    },
                    line2: {
                      type: 'line',
                      xMin: riseSet[1],
                      xMax: riseSet[1],
                      borderColor: 'rgba(100, 100, 255, .25)',
                      borderWidth: 2,
                    }
                  }
              },
              legend: {
                position: 'top',
              },
            }
          }
        };


        chartInstance && chartInstance.destroy();
        chartInstance = new Chart(chartEl, config);
    });


    socket.emit('request_historical_temps', {channels: [2, 5]});
    setInterval(
        ()=>socket.emit('request_historical_temps'),
        5*60*1000 // 5 minutes
    );


});
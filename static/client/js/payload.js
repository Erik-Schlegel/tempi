

const getFormattedDate = (datestr) =>
{
  const dFormat = "dd hh:mmA";
  return moment(datestr).format(dFormat);
}


const getLocalizedDatetime = (datestr) =>
{
  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  return getFormattedDate(moment.tz(datestr, "GMT").tz(browserTimezone))
}


const getTimeRoundedToInterval = (timestr, interval=15) =>
{
    // Round time to nearest interval. If time is 12:07 and interval is 15, return 12:00. If time is 12:08, return 12:15
    let time = moment(timestr, "dd hh:mm A");
    let minutes = time.minutes();
    let remainder = minutes % interval;
    let roundedTime = moment(time).subtract(remainder, 'minutes');
    return roundedTime.format("dd hh:mmA");
}


const isTimeEarlier = (time1, time2) =>
{
  //TODO: auto-detect format, or accept formats as parameters
  //time1 is iso8601, time2 is hh:mm:ss A
  return moment(time1).isBefore(moment(time2, "hh:mm:ss A"));
}


const getRiseSetRequestString = (latitude, longitude, timeZoneId, day) =>
{
  return `https://api.sunrise-sunset.org/json?lat=${latitude}&lng=${longitude}&date=${day}&tzid=${timeZoneId}`
}


const getRiseSet = async(currentTime, latitude, longitude, timeZoneId) =>
{
  let todayAbbrev = moment().format('dd');
  let yesterdayAbbrev = moment().subtract(1, 'days').format('dd');

  let riseSet = await Promise.all(
    [
      fetch(getRiseSetRequestString(latitude, longitude, timeZoneId, 'yesterday')).then(response=>response.json()),
      fetch(getRiseSetRequestString(latitude, longitude, timeZoneId, 'today')).then(response=>response.json())
    ]
  )

  /* riseSet includes:
  [
    {
      //yesterday
      "results": {
          "sunrise": "6:17:08 AM",
          "sunset": "7:59:30 PM",
      },
    },
    {
      //today
      "results": {
          "sunrise": "6:18:00 AM",
          "sunset": "7:58:15 PM",
      },
    }
  ]
  */

  return [
    getTimeRoundedToInterval(
      (
        isTimeEarlier(currentTime, riseSet[1].results.sunrise) ?
          `${yesterdayAbbrev} ${riseSet[0].results.sunrise}` :
          `${todayAbbrev} ${riseSet[1].results.sunrise}`
      )
    ),
    getTimeRoundedToInterval(
      (
        isTimeEarlier(currentTime, riseSet[1].results.sunset) ?
          `${yesterdayAbbrev} ${riseSet[0].results.sunset}` :
          `${todayAbbrev} ${riseSet[1].results.sunset}`
      )
    )
  ];

}


const makeChart = (chartEl, chartInstance, receivedData, riseSet) =>
{
  let datapoints = [];
  let labelpoints = null;

  for(let i=0, len=receivedData.length; i<len; i++)
  {
    datapoints[i] = [];
    labelpoints = [];
    for(let j=0, len2 = receivedData[i].temps.length; j<len2; j++)
    {
      datapoints[i].push(receivedData[i].temps[j].fahrenheit);
      labelpoints.push(getLocalizedDatetime(receivedData[i].temps[j].interval_start));
    }

  }

  const data = {
    labels: labelpoints,
    datasets: [
      {
        label: window.channels[window.lowTempDesiredChannel],
        data: datapoints[0],
        borderColor: 'rgba(94, 90, 102, .8)',
        borderWidth: 1
      },
      {
        label: window.channels[window.highTempExpectedChannel],
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
    return new Chart(chartEl, config);
}


document.addEventListener("DOMContentLoaded",
  async ()=>
    {
    let measurementEl = document.querySelector('[data-id=Measurements]');
    let chartEl = document.querySelector('[data-id=Chart]');
    let chartInstance = null;
    let currentTime = null;

    let template = document.querySelector('[data-id=data-template]');
    let socket = io.connect(window.apiUrl);
    let riseSet = null;

    socket.on('weather_update', async(data)=>
    {
      currentTime = data.current_time;
      let fragment = document.createDocumentFragment();

      for (let key in data)
      {
        //if key is not a number, skip it
        //TODO: nankey is a hack. refactor the received data (which is built in tempi.py) to have a channels array, and a separate data structure.
        if(isNaN(key)) continue;
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
    });


    socket.on('historical_temps', async (receivedData)=>
    {
      riseSet =  await getRiseSet(currentTime, window.latitude, window.longitude, window.timeZoneId);
      chartInstance = makeChart(chartEl, chartInstance, receivedData, riseSet);
    });


    socket.emit('request_historical_temps', {channels: [window.lowTempDesiredChannel, window.highTempExpectedChannel]});
    setInterval(
        ()=>socket.emit('request_historical_temps',  {channels: [window.lowTempDesiredChannel, window.highTempExpectedChannel]}),
        5*60*1000 // 5 minutes
    );

});
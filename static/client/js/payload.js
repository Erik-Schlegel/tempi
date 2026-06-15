

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


const channelPalette = [
  'rgba(255, 90, 102, .5)',
  'rgba(255, 208, 0, .5)',
  'rgba(108, 142, 42, .5)',
  'rgba(27, 86, 250, .5)'
];


const getChannelColor = (channelId) =>
{
  const sortedChannelIds = Object.keys(window.channels)
    .map(Number)
    .sort((a, b) => a - b);
  const paletteIndex = sortedChannelIds.indexOf(Number(channelId));
  if(paletteIndex < 0)
  {
    return channelPalette[0];
  }

  return channelPalette[paletteIndex % channelPalette.length];
}


const makeChart = (chartEl, chartInstance, receivedData, riseSet) =>
{
  const allIntervalStarts = Array.from(
    new Set(
      receivedData.flatMap((channelData) =>
        channelData.temps.map((entry) => entry.interval_start)
      )
    )
  ).sort((left, right) => moment(left).valueOf() - moment(right).valueOf());

  const labelpoints = allIntervalStarts.map((intervalStart) => getLocalizedDatetime(intervalStart));

  const datasets = receivedData.map((channelData) =>
  {
    const tempByInterval = new Map(
      channelData.temps.map((entry) => [entry.interval_start, entry.fahrenheit])
    );

    return {
      label: window.channels[channelData.channel] || `Channel ${channelData.channel}`,
      data: allIntervalStarts.map((intervalStart) =>
        tempByInterval.has(intervalStart) ? tempByInterval.get(intervalStart) : null
      ),
      borderColor: getChannelColor(channelData.channel),
      borderWidth: 1
    };
  });

  const data = {
    labels: labelpoints,
    datasets
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
            display: false,
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
    const selectedChannelsStorageKey = 'tempi:selectedChannels';
    const allChannels = Object.keys(window.channels)
      .map(Number)
      .filter((channelId) => Number.isFinite(channelId));
    const sanitizeChannels = (channels) =>
      channels
        .map(Number)
        .filter((channelId) => allChannels.includes(channelId));
    const defaultChannels = [
      Number(window.lowTempDesiredChannel),
      Number(window.highTempExpectedChannel)
    ];
    const defaultSelectedChannels = sanitizeChannels(defaultChannels);
    const getSavedSelectedChannels = () =>
    {
      try
      {
        const raw = localStorage.getItem(selectedChannelsStorageKey);
        if(!raw)
        {
          return null;
        }

        const parsed = JSON.parse(raw);
        if(!Array.isArray(parsed))
        {
          return null;
        }

        return sanitizeChannels(parsed);
      }
      catch(_error)
      {
        return null;
      }
    };

    const saveSelectedChannels = (channels) =>
    {
      try
      {
        localStorage.setItem(selectedChannelsStorageKey, JSON.stringify(Array.from(channels)));
      }
      catch(_error)
      {
        // Ignore localStorage write errors and keep runtime behavior.
      }
    };

    const savedSelectedChannels = getSavedSelectedChannels();
    let selectedChannels = new Set(
      savedSelectedChannels !== null ?
        savedSelectedChannels :
        (defaultSelectedChannels.length > 0 ? defaultSelectedChannels : allChannels)
    );

    saveSelectedChannels(selectedChannels);

    const requestHistoricalTemps = () =>
    {
      socket.emit('request_historical_temps', {channels: Array.from(selectedChannels)});
    };

    const updateMeasurementStyles = () =>
    {
      const defaultBorderColor = '#5e5a66';
      const cards = measurementEl.querySelectorAll('[data-id=MeasurementCard]');
      cards.forEach((card) =>
      {
        const channel = Number(card.dataset.channel);
        const isSelected = selectedChannels.has(channel);
        card.classList.toggle('is-selected', isSelected);
        card.setAttribute('aria-pressed', String(isSelected));
        card.style.borderColor = isSelected ? getChannelColor(channel) : defaultBorderColor;
      });
    };

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
        let cardEl = clone.querySelector('[data-id=MeasurementCard]');
        let locationEl = clone.querySelector('[data-id=Location]');
        let fahrenheitEl = clone.querySelector('[data-id=Fahrenheit]');
        let humidityEl = clone.querySelector('[data-id=Humidity]');
        let channelId = Number(key);

        cardEl.dataset.channel = String(channelId);
        cardEl.style.cursor = 'pointer';
        cardEl.setAttribute('role', 'button');
        cardEl.setAttribute('tabindex', '0');

        const toggleChannel = () =>
        {
          if(selectedChannels.has(channelId))
          {
            selectedChannels.delete(channelId);
          }
          else
          {
            selectedChannels.add(channelId);
          }

          updateMeasurementStyles();
          saveSelectedChannels(selectedChannels);
          requestHistoricalTemps();
        };

        cardEl.addEventListener('click', toggleChannel);
        cardEl.addEventListener('keydown', (event) =>
        {
          if(event.key === 'Enter' || event.key === ' ')
          {
            event.preventDefault();
            toggleChannel();
          }
        });

        locationEl.textContent = data[key].Location;
        fahrenheitEl.textContent = data[key].Temp;
        humidityEl.textContent = data[key].H20;

        fragment.appendChild(clone);
      }

      measurementEl.innerHTML = '';
      measurementEl.appendChild(fragment);
      updateMeasurementStyles();
    });


    socket.on('historical_temps', async (receivedData)=>
    {
      if(!currentTime)
      {
        return;
      }

      riseSet =  await getRiseSet(currentTime, window.latitude, window.longitude, window.timeZoneId);
      chartInstance = makeChart(chartEl, chartInstance, receivedData, riseSet);
    });


    requestHistoricalTemps();
    setInterval(
        requestHistoricalTemps,
        5*60*1000 // 5 minutes
    );

});
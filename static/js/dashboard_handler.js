// const
let heatLayer = null
const socket = new WebSocket('ws://' + window.location.host + '/ws/sensor/');
const siteGeoJsonURL = '/api/site_geo_json'
// function
setInfoToTable = (infoObj) => {
    const latitude = document.getElementById('latitude')
    latitude.textContent = parseFloat(infoObj.latitude.toFixed(2))

    const longitude = document.getElementById('longitude')
    longitude.textContent = parseFloat(infoObj.longitude.toFixed(2))

    const totalSensorsInSite = document.getElementById('totalSensorsInSite')
    totalSensorsInSite.textContent = infoObj.totalSensorsInSite

    const defaultZoom = document.getElementById('defaultZoom')
    defaultZoom.textContent = infoObj.defaultZoom
}
addSatelliteMap = () => {
    const token = 'pk.eyJ1IjoicmFlZC1hbHNpbmFuaSIsImEiOiJjbG56bHY4OGkwMjJlMmpueWZodTNyZ2xrIn0.41hPSEJp9e7e64_XBsAvrA'
    // L.tileLayer(tile_url, {
    //     attribution: 'Mapbox attribution',
    //     name: 'satellite map',
    //     control: true,
    // }).addTo(map)

    return 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=' + token
}
getSiteInfo = async () => {
    const response = await fetch('/api/site-info')
    const data = await response.json()
    setInfoToTable(data)
    const openstreetmap = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    })


    const responseSiteGeoJson = await fetch(siteGeoJsonURL)
    const {polygon,point} = await responseSiteGeoJson.json()

    const polygonJson = L.geoJSON(polygon)
    const pointJson = L.geoJSON(point)
    const mapbox = L.tileLayer(addSatelliteMap(), {
        attribution: 'Mapbox attribution'
    })
    let map = L.map('map', {
        layers: [openstreetmap, mapbox]
    }).setView([data.latitude, data.longitude], data.defaultZoom);
    const baseMaps = {
        openstreetmap,
        mapbox,
    }
    const overlayMaps = {
        "Polygon": polygonJson,
        "Point": pointJson
    };


    L.control.layers(baseMaps, overlayMaps).addTo(map)
    const responseLocation = await fetch('/api/locations')
    const dataLocation = await responseLocation.json()

    for (let location of dataLocation) {
        L.circleMarker(
            [location['lat'], location['lon']], {
                radius: 5,
                fill: false,
                color: "darkgray",
                fill_color: 'aliceblue',
            }
        ).addTo(map)
    }


    // Change default options
    const heatData = await getHeatDataFn(document.getElementById('selected_sensor').value)
    heatLayer = L.heatLayer(heatData, {
        radius: 25,
        gradient: {
            0.0: 'blue',
            0.3: 'cyan',
            0.5: 'lime',
            0.8: 'yellow',
            1.0: 'red'
        }
    }).addTo(map);


}
convertDataToHeat = async (data, sensorType) => {
    let heatData = []
    let tmp_row = []
    await Promise.all(data.map(async (row) => {
        tmp_row = [row.lat, row.lon, row[sensorType]]
        heatData.push(tmp_row)
    }))
    return heatData
}
getHeatDataFn = async (sensorType) => {

    const response = await fetch('/api/real-time-sensors-data')
    const data = await response.json()
    return await convertDataToHeat(data, sensorType)


}
// socket

socket.addEventListener('open', function (event) {
    getSiteInfo().then(() => console.log("WebSocket connection opened."))

});
socket.addEventListener('close', function (event) {
    console.log("WebSocket connection closed.");
});
socket.addEventListener('message', function (event) {
    const sensorType = JSON.parse(event.data)

    if (sensorType.type === 'update_map') {

        convertDataToHeat(JSON.parse(sensorType.message),
            document.getElementById('selected_sensor').value)
            .then((newData) => {
                if (heatLayer) heatLayer.setLatLngs(newData)
            })
    }
});

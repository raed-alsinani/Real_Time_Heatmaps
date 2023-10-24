const selected_sensor = document.getElementById('selected_sensor')
selected_sensor.addEventListener('change', (e) => {
    e.preventDefault()
    const form = document.getElementById('sensors-form')
    form.submit()
})
selected_sensor.value = window.selected_sensor

const socket = new WebSocket('ws://' + window.location.host + '/ws/sensor/');
socket.addEventListener('open', function (event) {
    console.log("WebSocket connection opened.")
});
socket.addEventListener('close', function (event) {
    console.log("WebSocket connection closed.");
});


// socket.addEventListener('message', function (event) {
//     const sensorType = JSON.parse(event.data)
//     console.log(document.getElementById('selected_sensor').value)
//     if (sensorType.type === 'update_map') {
//         socket.send(JSON.stringify({sensor: window.selected_sensor}))
//     }
//
//     if (sensorType.type === "map_updated") {
//         let data = JSON.parse(event.data);
//         let monitorMap = document.getElementById('monitorMap')
//         let newMap = document.createElement('div')
//         newMap.innerHTML = sensorType.message
//
//         if (monitorMap.children[0]) {
//             monitorMap.children[0].replaceWith(newMap)
//         } else {
//             monitorMap.append(newMap)
//         }
//
//     }
//
//
// });
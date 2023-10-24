import folium
import pandas as pd
from asgiref.sync import sync_to_async
from folium.plugins import HeatMap

from dashboard.models import Location, Monitoring


def __build_formation_surfaces():
    geoJason_data = {
        "type": "FeatureCollection",
        "features": []
    }
    site1 = {
        "type": "Feature",
        "properties": {"name": "Site 1"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [55.8678241457011, 21.5626722623737],
                    [55.8678241457011, 21.616783846107328],
                    [55.89814239086861, 21.616783846107328],
                    [55.89814239086861, 21.5626722623737],
                    [55.8678241457011, 21.5626722623737],
                ]
            ]
        }
    }
    site2 = {
        "type": "Feature",
        "properties": {"name": "Site 2"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [55.8978241457011, 21.5626722623737],
                    [55.8678241457011, 21.616783846107328],
                    [55.86814239086861, 21.616783846107328],
                    [55.86814239086861, 21.5626722623737],
                    [55.8978241457011, 21.5626722623737],
                ]
            ]
        }
    }
    site3 = {
        "type": "Feature",
        "properties": {"name": "Site 2"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [55.8378241457011, 21.5726722623737],
                    [55.8378241457011, 21.646783846107328],
                    [55.86814239086861, 21.646783846107328],
                    [55.86814239086861, 21.526722623737],
                    [55.8378241457011, 21.5726722623737],
                ]
            ]
        }
    }

    geoJason_data['features'].append(site1)
    geoJason_data['features'].append(site2)
    geoJason_data['features'].append(site3)
    return geoJason_data


@sync_to_async
def _get_data_from_monitoring(sensor):
    print(sensor)
    total_of_sensor = Location.objects.count()
    monitoring_data = Monitoring.objects.all().order_by('-timestamp')[:total_of_sensor]
    res_data = [{'lat': row.lat, 'lon': row.lon, 'sensor': getattr(row, sensor)} for row in monitoring_data]
    return res_data


async def generate_live_heap_map(sensor):
    data = await _get_data_from_monitoring(sensor)

    df = pd.DataFrame.from_records(data)
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=11)

    # sensors in industrial site's location
    for row in data:
        folium.CircleMarker(
            location=(row['lat'], row['lon']),
            radius=5,
            fill=False,
            color="darkgray",
            fill_color='aliceblue',
        ).add_to(m)

    #  adding layers
    # 1- formation surface layers
    geoData = __build_formation_surfaces()
    folium.GeoJson(geoData, name="Formation Layers",
                   style_function=lambda feature: {
                       'fillColor': 'blue',
                       'color': 'black',
                       'weight': 2
                   }).add_to(m)

    # 2- satellite imagery,
    token = 'pk.eyJ1IjoicmFlZC1hbHNpbmFuaSIsImEiOiJjbG56bHY4OGkwMjJlMmpueWZodTNyZ2xrIn0.41hPSEJp9e7e64_XBsAvrA'
    tile_url = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=' + str(token)
    folium.TileLayer(tiles=tile_url, attr='Mapbox attribution', name='satellite map', control=True,
                     subdomains=['a', 'b', 'c']).add_to(m)
    # 3- other layers
    folium.TileLayer('Stamen Water Color').add_to(m)
    folium.TileLayer('CartoDB Positron').add_to(m)
    heat_data_steam = [(entry["lat"], entry["lon"], entry["sensor"]) for entry in data]
    HeatMap(heat_data_steam, name="tmp").add_to(m)
    folium.LayerControl().add_to(m)

    m = m._repr_html_()
    return m

import json
import folium
from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from folium.plugins import HeatMap, HeatMapWithTime
from dashboard.models import Monitoring, Location


# Create your views here.
# templates
def dashboard_screen(request):
    return render(request, 'dashboard_screen.html', {'title': "Monitor Dashboard"})


def history_dashboard(request):
    sensors_id = 'percentage'
    if request.method == 'POST':
        sensors_id = request.POST.get('sensors')

    monitoring_data = Monitoring.objects.all()
    df = pd.DataFrame.from_records(monitoring_data.values())
    if monitoring_data.count() == 0:
        return render(request, 'history_screen.html', {'map': '', 'title': "Monitor Dashboard"})
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=11)

    # sensors in industrial site's location
    monitor = [
        {
            "lat": row.lat,
            "lon": row.lon,
            "tmp": row.tmp,
            "pressure": row.pressure,
            "steam": row.steam_inj,
            "percentage": row.percentage
        }
        for row in monitoring_data]

    for row in monitor:
        folium.CircleMarker(
            location=(row['lat'], row['lon']),
            radius=5,
            fill=False,
            color="darkgray",
            fill_color='aliceblue',
        ).add_to(m)

    #  adding layers
    # 1- formation surface layers
    response = site_geo_json(request)
    geoData = json.loads(response.content)
    polygon = geoData.get("polygon")
    point = geoData.get("point"
                        )
    folium.GeoJson(polygon, name="Polygon Layers").add_to(m)
    folium.GeoJson(point, name="Point Layers").add_to(m)


    # 2- satellite imagery,
    token = 'pk.eyJ1IjoicmFlZC1hbHNpbmFuaSIsImEiOiJjbG56bHY4OGkwMjJlMmpueWZodTNyZ2xrIn0.41hPSEJp9e7e64_XBsAvrA'
    tile_url = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=' + str(token)
    folium.TileLayer(tiles=tile_url, attr='Mapbox attribution', name='satellite map', control=True,
                     subdomains=['a', 'b', 'c']).add_to(m)
    # 3- other layers
    folium.TileLayer('Stamen Water Color').add_to(m)
    folium.TileLayer('CartoDB Positron').add_to(m)

    # History Heatmap Generation:
    # 1 - normalized data
    m = __handle_heatmap(site_map=m, df=df, parameter='percentage')

    folium.LayerControl().add_to(m)

    m = m._repr_html_()
    return render(request, 'history_screen.html', {'map': m, 'title': "History Dashboard", 'sensors': sensors_id})


# api
def real_time_sensors_data(request):
    total_of_sensor = Location.objects.count()
    monitoring_data = Monitoring.objects.all().order_by('-timestamp')[:total_of_sensor]
    res_data = [{'lat': row.lat, 'lon': row.lon, "tmp": row.tmp, 'pressure': row.pressure,
                 'steam_inj': row.steam_inj, 'percentage': row.percentage} for row in monitoring_data]
    return JsonResponse(res_data, safe=False)


def history_sensors_data(request):
    monitoring_data = Monitoring.objects.all()
    res_data = [{'lat': row.lat, 'lon': row.lon, "tmp": row.tmp, 'pressure': row.pressure,
                 'steam': row.steam_inj, 'percentage': row.percentage} for row in monitoring_data]
    return JsonResponse(res_data, safe=False)


def all_locations(request):
    location = Location.objects.all()
    res_data = [{'lat': row.lat, 'lon': row.lon} for row in location]
    return JsonResponse(res_data, safe=False)


def site_info(request):
    total_of_sensor = Location.objects.count()
    monitoring_data = Monitoring.objects.all()
    df = pd.DataFrame.from_records(monitoring_data.values())
    data = {
        'totalSensorsInSite': total_of_sensor,
        'latitude': df['lat'].mean(),
        'longitude': df['lon'].mean(),
        'defaultZoom': 11
    }
    return JsonResponse(data=data, safe=False)


def site_geo_json(request):
    data = {
        "polygon": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [55.83992260225307, 21.726425712527416],
                                [55.808165726219784, 21.72535294746524],
                                [55.744651974151594, 21.739834600387297],
                                [55.74234238316737, 21.731789417775758],
                                [55.764860895265116, 21.6904837278921],
                                [55.796040373552444, 21.678143365834714],
                                [55.83992260225307, 21.726425712527416]
                            ]
                        ],
                        "type": "Polygon"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [55.84107739774518, 21.72535294746524],
                                [55.81393970368032, 21.696921758051957],
                                [55.91151992276605, 21.651312847245478],
                                [55.95366995822991, 21.69531227749256],
                                [55.84107739774518, 21.72535294746524]
                            ]
                        ],
                        "type": "Polygon"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [55.81336230223616, 21.69584878084939],
                                [55.795462972108254, 21.67653368332411],
                                [55.80354654055307, 21.657752634683007],
                                [55.80701092702947, 21.62233029210509],
                                [55.82029107518889, 21.592805040277526],
                                [55.8780308497964, 21.665265347626928],
                                [55.81336230223616, 21.69584878084939]
                            ]
                        ],
                        "type": "Polygon"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [55.878608247542445, 21.66419212687518],
                                [55.821445870681, 21.592805040277526],
                                [55.84916096249336, 21.535347754351108],
                                [55.94674118157903, 21.634138704925903],
                                [55.878608247542445, 21.66419212687518]
                            ]
                        ],
                        "type": "Polygon"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [55.955402147769945, 21.696921765890252],
                                [55.912097316814, 21.649166198031452],
                                [55.91729389652852, 21.653996131508137],
                                [55.914406907798224, 21.65077619381556],
                                [55.94847337481721, 21.6368223005245],
                                [56.024112479551235, 21.712479150380588],
                                [56.00390355843908, 21.711942716839587],
                                [55.97041448916755, 21.697458255412528],
                                [55.955402147769945, 21.696921765890252]
                            ]
                        ],
                        "type": "Polygon"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [56.024112479551235, 21.710333404217494],
                                [55.950782965801466, 21.6368223005245],
                                [56.06048853755448, 21.58904684875577],
                                [56.06510771952293, 21.625014107019823],
                                [56.09513240231814, 21.69209327025014],
                                [56.06510771952293, 21.70818762605846],
                                [56.024112479551235, 21.710333404217494]
                            ]
                        ],
                        "type": "Polygon"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [55.94962817030938, 21.633601979823624],
                                [55.85031575798547, 21.534810663007164],
                                [55.925377464973394, 21.50204433556351],
                                [55.992355603517865, 21.50956512946169],
                                [56.06106593530055, 21.587973061831846],
                                [55.94962817030938, 21.633601979823624]
                            ]
                        ],
                        "type": "Polygon"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [56.06106593530055, 21.586362366515928],
                                [55.99466519450212, 21.510102314140397],
                                [56.01718370659847, 21.504193173511325],
                                [56.033350843489586, 21.515474051750118],
                                [56.06106593530055, 21.586362366515928]
                            ]
                        ],
                        "type": "Polygon"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [
                            [
                                [56.05875634431632, 21.579919406110093],
                                [56.0345056389817, 21.513862551311377],
                                [56.03970221869628, 21.50956512946169],
                                [56.04085701418836, 21.48753884910103],
                                [56.048363184887194, 21.487001581091306],
                                [56.0766556744442, 21.50741637089766],
                                [56.0633755262848, 21.532125176486744],
                                [56.0627981285387, 21.53964441357455],
                                [56.05529195783987, 21.544478003185034],
                                [56.054714560093885, 21.533199377054885],
                                [56.05644675333207, 21.545552112348332],
                                [56.05875634431632, 21.579919406110093]
                            ]
                        ],
                        "type": "Polygon"
                    }
                }
            ]
        },
        "point": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [56.06650015383053, 21.68822982702659],
                        "type": "Point"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [55.99134036605409, 21.69372268634521],
                        "type": "Point"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [56.050454805878275, 21.637999693186217],
                        "type": "Point"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [56.05467726586551, 21.51313363861287],
                        "type": "Point"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [55.932225926229876, 21.524918049150486],
                        "type": "Point"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [55.83679833051386, 21.601885988792944],
                        "type": "Point"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [55.76923897071529, 21.717261138768833],
                        "type": "Point"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [55.878178438390506, 21.690583935240255],
                        "type": "Point"
                    }
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [55.94489330619257, 21.627794560895964],
                        "type": "Point"
                    }
                }
            ]
        }
    }

    return JsonResponse(data=data)


# private methods

def __handle_heatmap(site_map, df, parameter):
    heatmap_data = []
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.floor('S')
    for i in df['timestamp'].unique():
        temp = []
        for index, row in df[df['timestamp'] == i].iterrows():
            temp.append([row['lat'], row['lon'], row[parameter]])
        heatmap_data.append(temp)

    time_index = []
    for i in df['timestamp'].unique():
        time_index.append(i)

    date_strings = [d.strftime('%d/%m/%Y, %H:%M:%S') for d in time_index]

    colrGradient = {0.0: 'blue',
                    0.3: 'cyan',
                    0.5: 'lime',
                    0.8: 'yellow',
                    1.0: 'red'}

    HeatMapWithTime(heatmap_data,
                    radius=30,
                    auto_play=True,
                    position='bottomright',
                    name=parameter,
                    index=date_strings,
                    max_opacity=0.3,
                    gradient=colrGradient,

                    ).add_to(site_map)
    return site_map

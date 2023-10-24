import random
from threading import Timer
from .globals import max_temp, min_temp, max_pressure, min_pressure, max_steam_injection, min_steam_injection


def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)


_is_sensor_mock_start_counter = 0


def add_new_record():
    timer = random.uniform(5, 50)
    from dashboard.models import CurrentReading
    from dashboard.models import Location, Monitoring

    def add_dummy_record(site_id, reading, unit):
        sensor_right = CurrentReading(
            location_id=site_id,
            reading=reading,
            unit_code=unit
        )
        # sensor_right.save()

    location = Location.objects.all()

    for row in location:
        temp = random.uniform(min_temp, max_temp)
        pressure = random.uniform(min_pressure, max_pressure)
        steam_ing = random.uniform(min_steam_injection, max_steam_injection)
        add_dummy_record(row.id, temp, "°C")
        add_dummy_record(row.id, pressure, "kPa")
        add_dummy_record(row.id, steam_ing, "kg/s")

        normalize_temp = normalize(temp, min_temp, max_temp)
        normalize_pressure = normalize(pressure, min_pressure, max_pressure)
        normalize_stram_ing = normalize(steam_ing, min_steam_injection, max_steam_injection)
        percentage = 100 * (normalize_temp + normalize_pressure + normalize_stram_ing) / 3
        monitorRecord = Monitoring(
            lat=row.lat,
            lon=row.lon,
            tmp=temp,
            pressure=pressure,
            percentage=percentage,
            steam_inj=steam_ing
        )
        monitorRecord.save()
    global _is_sensor_mock_start_counter
    _is_sensor_mock_start_counter += 1
    if not (_is_sensor_mock_start_counter % 2) == 0:
        _is_sensor_mock_start_counter = 0
        Timer(timer, add_new_record).start()


is_utils_started = False


def my_callback(name):
    print("Request finished!" + name)
    Timer(random.uniform(20, 50), add_new_record).start()

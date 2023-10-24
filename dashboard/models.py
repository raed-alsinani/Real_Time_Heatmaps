from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from django.db import models
from django.dispatch import receiver
import json

# Create your models here.
counter = 0


class Monitoring(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    tmp = models.FloatField()
    pressure = models.FloatField()
    steam_inj = models.FloatField()
    percentage = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Location(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class SiteDetails(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    site_name = models.CharField(max_length=100)
    site_admin = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)


class UnitDetails(models.Model):
    unit_code = models.CharField(max_length=10)
    unit_name = models.CharField(max_length=50)
    unit_desc = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)


class CurrentReading(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    unit_code = models.CharField(max_length=6)
    reading = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


def monitoring_model_to_dict(row):
    model_to_dict = {
        'lat': row.lat,
        'lon': row.lon,
        'tmp': row.tmp,
        'percentage': row.percentage,
        'steam_inj': row.steam_inj,
        'pressure': row.pressure
    }
    return model_to_dict


@receiver(post_save, sender=Monitoring)
def sensor_update(sender, instance, created, **kwargs):
    if created:
        global counter
        counter = counter + 1
        total_of_sensor = Location.objects.count()

        if counter == total_of_sensor:
            counter = 0
            channel_layer = get_channel_layer()
            to_remove_data = Monitoring.objects.all().order_by('timestamp')[:total_of_sensor]
            for row in to_remove_data:
                row.delete()
            last_update = Monitoring.objects.all().order_by('-timestamp')[:total_of_sensor]
            last_update = [monitoring_model_to_dict(row) for row in last_update]
            last_update = json.dumps(last_update)
            data = {'type': 'send_sensor_data', 'data': {'type': 'update_map', 'message': last_update}}
            async_to_sync(channel_layer.group_send)("sensor", data)

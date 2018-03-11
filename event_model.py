from pynamodb.attributes import ListAttribute, MapAttribute, NumberAttribute,\
    UnicodeAttribute, UTCDateTimeAttribute, BooleanAttribute
from pynamodb.models import Model


class Service(MapAttribute):
    name = UnicodeAttribute()
    duration = NumberAttribute()


class Event(Model):
    class Meta:
        table_name = 'EventTable'
        host = 'http://localhost:8000'
        write_capacity_units = 1
        read_capacity_units = 1
    event_id = UnicodeAttribute(hash_key=True)
    service = Service()
    start_time = UTCDateTimeAttribute(range_key=True)
    end_time = UTCDateTimeAttribute()
    persons = ListAttribute()

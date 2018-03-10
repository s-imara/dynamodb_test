from pynamodb.attributes import ListAttribute, MapAttribute, NumberAttribute,\
    UnicodeAttribute, UTCDateTimeAttribute, BooleanAttribute
from pynamodb.models import Model


class Service(MapAttribute):
    name = UnicodeAttribute()
    duration = NumberAttribute()


class Event(MapAttribute):
    service = Service()
    start_time = UTCDateTimeAttribute()
    end_time = UTCDateTimeAttribute()


class Person(Model):
    class Meta:
        table_name = 'PersonTable'
        host = 'http://localhost:8000'
        write_capacity_units = 1
        read_capacity_units = 1
    email = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute(range_key=True)
    staff = BooleanAttribute(default=False)
    age = NumberAttribute(default=0)
    phone_number = UnicodeAttribute(default="")  # if we want storing more one number use UnicodeSetAttribute()
    address = UnicodeAttribute(default="")
    events = ListAttribute(of=Event)

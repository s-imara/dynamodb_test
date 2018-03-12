from pynamodb.attributes import MapAttribute, NumberAttribute,\
    UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


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
    start_time = UTCDateTimeAttribute()
    end_time = UTCDateTimeAttribute()

    def add_people(self, persons):
        people_in_event = list()
        for person in persons:
            people_in_event.append(
                EventPeople(
                    event_id=self.event_id,
                    email=person.email,
                ))
            with EventPeople.batch_write() as event_people_batch:
                for person_on_event in people_in_event:
                    event_people_batch.save(person_on_event)


class EventPeopleEmailIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "event_people_email_index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    email = UnicodeAttribute(hash_key=True)
    event_id = UnicodeAttribute(range_key=True)


class EventPeople(Model):
    class Meta:
        table_name = 'EventPeopleTable'
        host = 'http://localhost:8000'
        write_capacity_units = 1
        read_capacity_units = 1
    event_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(range_key=True)
    email_index = EventPeopleEmailIndex()


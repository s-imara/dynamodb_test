from pynamodb.attributes import ListAttribute, MapAttribute, NumberAttribute,\
    UnicodeAttribute, UTCDateTimeAttribute, BooleanAttribute
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class Service(MapAttribute):
    name = UnicodeAttribute()
    duration = NumberAttribute()


class EventStartIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "event_start_index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()
    start_time = UTCDateTimeAttribute(hash_key=True)
    event_id = UnicodeAttribute(range_key=True)


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
    start_index = EventStartIndex()

    def add_people(self, staff, *persons):
        people_in_event = list()
        for person in persons:
            people_in_event.append(
                EventPeople(
                    event_id=self.event_id,
                    email=person.email,
                    staff=staff
                ))
            with Event.batch_write() as event_batch:
                for person_on_event in people_in_event:
                    event_batch.save(person_on_event)
                    print('added {0} on event {1}'.format(person_on_event.email, self.event_id))


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
    staff = BooleanAttribute(default=False)
    email_index = EventPeopleEmailIndex()

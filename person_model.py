from pynamodb.attributes import NumberAttribute, UnicodeAttribute, BooleanAttribute
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from event_model import EventPeople


class PersonNameIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "person_name_index"
        read_capacity_units = 1
        write_capacity_units = 1
        projection = AllProjection()

    name = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(range_key=True)


class Person(Model):

    email = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    age = NumberAttribute(default=0)
    phone_number = UnicodeAttribute(default="")  # if we want storing more one number use UnicodeSetAttribute()
    address = UnicodeAttribute(default="")

    def get_events_for_person(self):
        events = list()
        for event_people in EventPeople.email_index.query(self.email):
            events.append(event_people.event_id)
        return events


class Client(Person):
    class Meta:
        table_name = 'ClientTable'
        host = 'http://localhost:8000'
        write_capacity_units = 1
        read_capacity_units = 1
    name_index = PersonNameIndex()


class Staff(Person):
    class Meta:
        table_name = 'StaffTable'
        host = 'http://localhost:8000'
        write_capacity_units = 1
        read_capacity_units = 1
    name_index = PersonNameIndex()

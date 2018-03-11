import unittest
from person_model import Person
from event_model import Event, Service, EventPeople
from random import randint
from dateutil import parser
import uuid


class TestDynamoDBCase(unittest.TestCase):
    @staticmethod
    def get_random_services():
        service_data = [('piano lesson', 45), ('piano lesson', 60), ('violin lesson', 30)]
        data = service_data[randint(0, len(service_data)-1)]
        return Service(
                name=data[0],
                duration=data[1]
        )

    @staticmethod
    def create_list_events(n):
        for i in range(n):
            day = randint(1, 31)
            yield Event(
                event_id=str(uuid.uuid4()),
                service=TestDynamoDBCase.get_random_services(),
                start_time=parser.parse("Mar {0} 00:00:00 PST 2018".format(day)),
                end_time=parser.parse("Mar {0} 15:00:00 PST 2018".format(day))#,
                )

    @staticmethod
    def create_person_item(n):
        for i in range(n):
            yield Person(
                email='person{}@gmail.com'.format(i),
                name='Mister Person{0}'.format(i),
                age=31,
                phone_number='+380667472123',
                address='Zaporojie,Verhniaja 11b/26'
            )

    def setUp(self):
        super(TestDynamoDBCase, self).setUp()
        #Person.delete_table()
        #Event.delete_table()
        #EventPeople.delete_table()
        print('setup table')
        # Create the table
        if not Person.exists():
            Person.create_table(wait=True)
        if not Event.exists():
            Event.create_table(wait=True)
        if not EventPeople.exists():
            EventPeople.create_table(wait=True)
        # Save the person
        if Person.count() < 100:
            with Person.batch_write() as p_batch:
                persons = self.create_person_item(100)
                for person in persons:
                    print(person.name)
                    p_batch.save(person)
        if Event.count() < 10:
            with Event.batch_write() as e_batch:
                events = self.create_list_events(10)
                for event in events:
                    print(event.event_id, event.start_time, event.service.name)
                    e_batch.save(event)

        print('persons=', Person.count(), ', events=', Event.count())

    def test_search_by_email(self):
        for person in Person.query('person30@gmail.com'):
            print(person)

    def test_search_by_name(self):
        for person in Person.name_index.query('Mister Person33'):
            print(person)

    def test_add_to_event(self):
        for event in Event.start_index.query(parser.parse("Mar 15 00:00:00 PST 2018")):
            event.add_people(True, *Person.query('person30@gmail.com'))
            print(event.event_id)

    def test_search_on_event_date(self):
        pass


if __name__ == '__main__':
    unittest.main()


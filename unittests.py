import unittest
from person_model import Person
from event_model import Event, Service
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
                id=str(uuid.uuid4()),
                service=TestDynamoDBCase.get_random_services(),
                start_time=parser.parse("Mar {0} 00:00:00 PST 2018".format(day)),
                end_time=parser.parse("Mar {0} 15:00:00 PST 2018".format(day)),
                persons=[]
                )

    @staticmethod
    def create_user_item(n):
        for i in range(n):
            yield Person(
                email='person{}@gmail.com'.format(i),
                name='Mister Person{0}'.format(i),
                staff=True if i % 2 == 0 else False,
                age=31,
                phone_number='+380667472123',
                address='Zaporojie,Verhniaja 11b/26',
                events=[]
            )

    def setUp(self):
        super(TestDynamoDBCase, self).setUp()
        print('setup table')
        # Create the table
        if not Person.exists():
            Person.create_table(wait=True)
        if not Event.exists():
            Event.create_table(wait=True)
        # Save the person
        if Person.count() < 100:
            with Person.batch_write() as p_batch:
                persons = self.create_user_item(100)
                for person in persons:
                    print(person.name, person.events)
                    p_batch.save(person)
        if Event.count() < 10:
            with Event.batch_write() as e_batch:
                events = self.create_list_events(10)
                for event in events:
                    print(event.id, event.start_time, event.service.name)
                    e_batch.save(event)

        print('persons=', Person.count(), ', events=', Event.count())

    def test_search_email_name(self):
        for item in Person.query('person30@gmail.com'):
            print(item.staff, item.events[1].service.name)
            self.assertEqual(item.name, 'Mister Person30')
        for fnd in Person.scan(Person.name == 'Mister Person10'):
            print(fnd.events)

    def test_add_event(self):
        pass

    def test_search_on_event_date(self):
        pass


if __name__ == '__main__':
    unittest.main()


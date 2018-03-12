import unittest
from person_model import Client, Staff, Person
from event_model import Event, Service, EventPeople
from random import randint
from dateutil import parser
import uuid


class TestDynamoDBCreateTableAndFillCase(unittest.TestCase):
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
            day = randint(1, 5) if i % 2 == 0 else randint(15, 30)
            yield Event(
                event_id=str(uuid.uuid4()),
                service=TestDynamoDBCreateTableAndFillCase.get_random_services(),
                start_time=parser.parse("Mar {0} 00:00:00 PST 2018".format(day)),
                end_time=parser.parse("Mar {0} 15:00:00 PST 2018".format(day))
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
        super(TestDynamoDBCreateTableAndFillCase, self).setUp()
        # Create the tables
        if Client.exists():
            Client.delete_table()
        Client.create_table(wait=True)
        if Staff.exists():
            Staff.delete_table()
        Staff.create_table(wait=True)
        if Event.exists():
            Event.delete_table()
        Event.create_table(wait=True)
        if EventPeople.exists():
            EventPeople.delete_table()
        EventPeople.create_table(wait=True)

        # fill client table
        with Client.batch_write() as p_batch:
            persons = self.create_person_item(50)
            for person in persons:
                print('Client name - ', person.name)
                p_batch.save(person)

        # fill staff table
        with Staff.batch_write() as p_batch:
            persons = self.create_person_item(50)
            for person in persons:
                print('Staff name - ', person.name)
                p_batch.save(person)

        # fill event table
        with Event.batch_write() as event_batch:
            events = self.create_list_events(10)
            for event in events:
                print(event.event_id, event.start_time, event.service.name)
                event_batch.save(event)

    def test_table_counts(self):
            self.assertEqual(Client.count() + Staff.count(), 100)
            self.assertEqual(Event.count(), 10)


class SchemaFieldsTestCase(unittest.TestCase):

    def setUp(self):
        super(SchemaFieldsTestCase, self).setUp()

    def test_search_by_email(self):
        client = Client.get('person30@gmail.com')
        self.assertEqual(client.name, 'Mister Person30')
        staff = Staff.get('person40@gmail.com')
        self.assertEqual(staff.name, 'Mister Person40')

    def test_search_by_name(self):
        for client in Client.name_index.query('Mister Person33'):
            self.assertEqual(client.email, 'person33@gmail.com')
        for staff in Staff.name_index.query('Mister Person20'):
            self.assertEqual(staff.email, 'person20@gmail.com')

    def test_search_all_events_for_person(self):
        for event in Event.scan(limit=5):
            event.add_people(*[Client.get('person30@gmail.com'), Staff.get('person44@gmail.com')])

        events = Client.get('person30@gmail.com').get_events_for_person()
        self.assertEqual(len(events), 5)

    def test_search_on_event_date(self):
        count = 0
        for event in Event.scan(Event.start_time.between(parser.parse("Mar 1 00:00:00 PST 2018"),
                                                         parser.parse("Mar 10 23:59:00 PST 2018"))):
            count += 1
        self.assertEqual((Event.count()/2), count)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDynamoDBCreateTableAndFillCase())
    suite.addTest(SchemaFieldsTestCase())
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(test_suite())

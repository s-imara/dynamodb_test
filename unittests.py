import unittest
from pynamodb.connection import TableConnection
from model import Person, Event, Service
from random import randint
from dateutil import parser


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
                service=TestDynamoDBCase.get_random_services(),
                start_time=parser.parse("Mar {0} 00:00:00 PST 2018".format(day)),
                end_time=parser.parse("Mar {0} 15:00:00 PST 2018".format(day))
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
                events=list(TestDynamoDBCase.create_list_events(randint(0, 5)))
            )

    def setUp(self):
        super(TestDynamoDBCase, self).setUp()
        print('setup table')
        # Create the table
        if not Person.exists():
            self.table = Person.create_table(wait=True)
        # Save the person
        with Person.batch_write() as batch:
            persons = self.create_user_item(100)
            for person in persons:
                print(person.name, person.events)
                batch.save(person)
        print(Person.count())

    def test_keys(self):
        print(Person.scan())
        table = TableConnection(Person.Meta.table_name, host=Person.Meta.host)
        item = table.query('andersen3@gmail.com')
        name = list(map(lambda d: d['name'], item.get('Items')))
        print(name)
        emails = table.scan(attributes_to_get='email')['Items']


if __name__ == '__main__':
    unittest.main()


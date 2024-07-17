from db_connection import Neo4jConnector
from faker import Faker

class DataCreationApp:
    def __init__(self):
        self.connector = Neo4jConnector()

    def close(self):
        self.connector.close()

    def create_person(self, name):
        query = "CREATE (p:Person {name: $name}) RETURN p"
        result = self.connector.execute_query(query, {"name": name})
        return result[0][0] if result else None

    def add_phone_number(self, name, phone_number):
        query = (
            "MATCH (p:Person {name: $name}) "
            "CREATE (p)-[:HAS_PHONE]->(ph:PhoneNumber {number: $phone_number}) "
            "RETURN p, ph"
        )
        result = self.connector.execute_query(query, {"name": name, "phone_number": phone_number})
        return result[0] if result else None

    def generate_fake_people(self, count=100):
        fake = Faker('it_IT')
        for _ in range(count):
            name = fake.name()
            phone_number = '3' + ''.join([str(fake.random_digit()) for _ in range(9)])
            self.create_person(name)
            self.add_phone_number(name, phone_number)
        print(f"Generated {count} fake people with phone numbers.")


if __name__ == "__main__":
    creation_app = DataCreationApp()

    creation_app.generate_fake_people(100)

    creation_app.close()
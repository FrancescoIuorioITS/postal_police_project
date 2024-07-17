from db_connection import Neo4jConnector
import random, os 
from faker import Faker

connector = Neo4jConnector()

class CriminalTrackingApp:
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

    def get_phone_by_name(self, name):
        query = (
            "MATCH (p:Person {name: $name})-[:HAS_PHONE]->(ph:PhoneNumber) "
            "RETURN ph.number AS phone_number"
        )
        result = self.connector.execute_query(query, {"name": name})
        return result[0]['phone_number'] if result else None


    def get_person_by_phone(self, phone_number):
        query = (
            "MATCH (p:Person)-[:HAS_PHONE]->(ph:PhoneNumber {number: $phone_number}) "
            "RETURN p.name AS name"
        )
        result = self.connector.execute_query(query, {"phone_number": phone_number})
        return result[0] if result else None

    def generate_fake_people(self, count=100):
        fake = Faker('it_IT')
        for _ in range(count):
            name = fake.name()
            phone_number = '3' + ''.join([str(fake.random_digit()) for _ in range(9)])
            self.create_person(name)
            self.add_phone_number(name, phone_number)
        print(f"Generated {count} fake people with phone numbers.")


    def get_all_people(self):
        query = "MATCH (p:Person) RETURN p.name AS name"
        result = self.connector.execute_query(query)
        return [record['name'] for record in result]

    def get_all_phone_numbers(self):
        query = "MATCH (ph:PhoneNumber) RETURN ph.number AS number"
        result = self.connector.execute_query(query)
        return [record['number'] for record in result]

if __name__ == "__main__":
    app = CriminalTrackingApp()

    # Generate 100 fake people
    app.generate_fake_people(100)

    # Get all people and phone numbers
    all_people = app.get_all_people()
    all_phones = app.get_all_phone_numbers()

    print(f"Total people in database: {len(all_people)}")
    print(f"Total phone numbers in database: {len(all_phones)}")

    # Example: Get a random person by their phone number
    
    random_phone = random.choice(all_phones)
    random_person = random.choice(all_people)
    person = app.get_person_by_phone(random_phone)
    phone = app.get_phone_by_name(random_person)
    print(f"Random person found: {person['name']} with phone {random_phone}")
    print(f"Random phone found: {random_person} with phone {phone}")
    
    app.close()

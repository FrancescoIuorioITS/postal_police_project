from db_connection import Neo4jConnector
import random

class DataRetrievalApp:
    def __init__(self):
        self.connector = Neo4jConnector()

    def close(self):
        self.connector.close()

    def get_person_by_phone(self, phone_number):
        query = (
            "MATCH (p:Person)-[:HAS_PHONE]->(ph:PhoneNumber {number: $phone_number}) "
            "RETURN p.name AS name"
        )
        result = self.connector.execute_query(query, {"phone_number": phone_number})
        return result[0] if result else None

    def get_phone_by_name(self, name):
        query = (
            "MATCH (p:Person {name: $name})-[:HAS_PHONE]->(ph:PhoneNumber) "
            "RETURN ph.number AS phone_number"
        )
        result = self.connector.execute_query(query, {"name": name})
        return result[0]['phone_number'] if result else None

    def get_all_people(self):
        query = "MATCH (p:Person) RETURN p.name AS name"
        result = self.connector.execute_query(query)
        return [record['name'] for record in result]

    def get_all_phone_numbers(self):
        query = "MATCH (ph:PhoneNumber) RETURN ph.number AS number"
        result = self.connector.execute_query(query)
        return [record['number'] for record in result]
    
if __name__ == "__main__":
    retrieval_app = DataRetrievalApp()

    all_people = retrieval_app.get_all_people()
    all_phones = retrieval_app.get_all_phone_numbers()

    print(f"Total people in database: {len(all_people)}")
    print(f"Total phone numbers in database: {len(all_phones)}")

    if all_phones:
        random_phone = random.choice(all_phones)
        person = retrieval_app.get_person_by_phone(random_phone)
        if person:
            print(f"Random person found: {person['name']} with phone {random_phone}")

    retrieval_app.close()
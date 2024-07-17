from db_connection import Neo4jConnector

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

    def get_person_by_phone(self, phone_number):
        query = (
            "MATCH (p:Person)-[:HAS_PHONE]->(ph:PhoneNumber {number: $phone_number}) "
            "RETURN p.name AS name"
        )
        result = self.connector.execute_query(query, {"phone_number": phone_number})
        return result[0] if result else None

if __name__ == "__main__":
    app = CriminalTrackingApp()

    # Create a person
    person = app.create_person("John Doe")
    print(f"Created person: {person['name']}")

    # Add a phone number to the person
    app.add_phone_number("John Doe", "123-456-7890")
    print(f"Added phone number to {person['name']}")

    # Find a person by phone number
    result = app.get_person_by_phone("123-456-7890")
    if result:
        print(f"Found person: {result['name']}")
    else:
        print("Person not found")

    app.close()
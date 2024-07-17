from db_connection import with_database
import random

@with_database
class DataRetrievalApp:

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
    
    def get_all_cells(self):
        query = "MATCH (c:Cell) RETURN c.id AS id, c.latitude AS latitude, c.longitude AS longitude, c.type AS type"
        result = self.connector.execute_query(query)
        return [{"id": record["id"], "latitude": record["latitude"], "longitude": record["longitude"], "type": record["type"]} for record in result]
    
    def get_all_connections(self):
        query = """
        MATCH (ph:PhoneNumber)-[r:CONNECTED_TO]->(c:Cell)
        RETURN ph.number AS phone_number, c.id AS cell_id, r.date AS date, r.time AS time
        """
        result = self.connector.execute_query(query)
        return [{"phone_number": record["phone_number"], "cell_id": record["cell_id"], 
                "date": record["date"], "time": record["time"]} for record in result]

    def get_connections_by_phone(self, phone_number):
        query = """
        MATCH (ph:PhoneNumber {number: $phone_number})-[r:CONNECTED_TO]->(c:Cell)
        RETURN c.id AS cell_id, r.date AS date, r.time AS time
        ORDER BY r.date, r.time
        """
        result = self.connector.execute_query(query, {"phone_number": phone_number})
        return [{"cell_id": record["cell_id"], "date": record["date"], "time": record["time"]} for record in result]

    def get_connection_dates(self, phone_number):
        query = """
        MATCH (ph:PhoneNumber {number: $phone_number})-[r:CONNECTED_TO]->()
        RETURN DISTINCT r.start_date AS start_date, r.end_date AS end_date
        ORDER BY start_date, end_date
        """
        result = self.connector.execute_query(query, {"phone_number": phone_number})
        return [(record['start_date'], record['end_date']) for record in result]

    def get_connection_times(self, phone_number, date):
        query = """
        MATCH (ph:PhoneNumber {number: $phone_number})-[r:CONNECTED_TO]->()
        WHERE r.start_date <= $date AND r.end_date >= $date
        RETURN r.start_time AS start_time, r.end_time AS end_time
        ORDER BY start_time, end_time
        """
        result = self.connector.execute_query(query, {"phone_number": phone_number, "date": date})
        return [(record['start_time'], record['end_time']) for record in result]

    def get_connection_coordinates(self, phone_number, date, time):
        query = """
        MATCH (ph:PhoneNumber {number: $phone_number})-[r:CONNECTED_TO]->(c:Cell)
        WHERE r.start_date <= $date AND r.end_date >= $date
        AND r.start_time <= $time AND r.end_time >= $time
        RETURN c.latitude AS latitude, c.longitude AS longitude
        """
        result = self.connector.execute_query(query, {"phone_number": phone_number, "date": date, "time": time})
        return [(record['latitude'], record['longitude']) for record in result]



if __name__ == "__main__":
    with DataRetrievalApp() as retrieval_app:

        all_people = retrieval_app.get_all_people()
        print(f"Total people in database: {len(all_people)}")

        all_phones = retrieval_app.get_all_phone_numbers()
        print(f"Total phone numbers in database: {len(all_phones)}")

        all_cells = retrieval_app.get_all_cells()
        print(f"Total cells in database: {len(all_cells)}")

        if all_phones:
            random_phone = random.choice(all_phones)
            person = retrieval_app.get_person_by_phone(random_phone)
            if person:
                print(f"Random person found: {person['name']} with phone {random_phone}")

        if all_phones:
            random_phone = random.choice(all_phones)
            connections = retrieval_app.get_connections_by_phone(random_phone)
            print(f"Connections for phone {random_phone}: {len(connections)}")

        all_connections = retrieval_app.get_all_connections()
        print(f"Total connections in database: {len(all_connections)}")

        all_phones = retrieval_app.get_all_phone_numbers()
        
        if all_phones:
            random_phone = random.choice(all_phones)
            
            # Test get_connection_dates
            dates = retrieval_app.get_connection_dates(random_phone)
            print(f"Connection dates for phone {random_phone}: {dates[:5]}")
            
            if dates:
                random_date = random.choice(dates)[0]
                
                # Test get_connection_times
                times = retrieval_app.get_connection_times(random_phone, random_date)
                print(f"Connection times for phone {random_phone} on {random_date}: {times[:5]}")
                
                if times:
                    random_time = random.choice(times)[0]
                    
                    # Test get_connection_coordinates
                    coordinates = retrieval_app.get_connection_coordinates(random_phone, random_date, random_time)
                    print(f"Connection coordinates for phone {random_phone} on {random_date} at {random_time}: {coordinates[:5]}")
        

    print("Data retrieval tests completed successfully.")

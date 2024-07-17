from db_connection import Neo4jConnector

class CriminalTrackingApp:
    def __init__(self):
        self.connector = Neo4jConnector()

    def close(self):
        self.connector.close()

    def find_person_location(self, name, start_date, end_date):
        query = """
            MATCH (p:Person {name: $name})-[:HAS_PHONE]->(ph:PhoneNumber)-[r:CONNECTED_TO]->(c:Cell)
            WHERE r.date >= $start_date AND r.date <= $end_date
            RETURN c.id AS cell_id, r.date AS date, r.time AS time
        """
        result = self.connector.execute_query(query, {"name": name, "start_date": start_date, "end_date": end_date})
        return result

    def find_suspects_in_cell(self, cell_id, date, time):
        query = """
            MATCH (p:Person)-[:HAS_PHONE]->(ph:PhoneNumber)-[r:CONNECTED_TO]->(c:Cell {id: $cell_id})
            WHERE r.date = $date AND r.time = $time
            RETURN p.name AS name, ph.number AS phone_number
        """
        result = self.connector.execute_query(query, {"cell_id": cell_id, "date": date, "time": time})
        return result

    def find_suspects_near_location(self, latitude, longitude, date, time, radius):
        query = """
            MATCH (p:Person)-[:HAS_PHONE]->(ph:PhoneNumber)-[r:CONNECTED_TO]->(c:Cell)
            WHERE distance(point({latitude: c.latitude, longitude: c.longitude}), point({latitude: $latitude, longitude: $longitude})) <= $radius
            AND r.date = $date AND r.time = $time
            RETURN p.name AS name, ph.number AS phone_number
        """
        result = self.connector.execute_query(query, {"latitude": latitude, "longitude": longitude, "date": date, "time": time, "radius": radius})
        return result

if __name__ == "__main__":
    app = CriminalTrackingApp()
    
    # Example: Find person location
    name = "Gigi Marraffa"
    start_date = "2022-10-04"
    end_date = "2022-10-10"
    locations = app.find_person_location(name, start_date, end_date)
    for location in locations:
        print(f"Person {name} was at cell {location['cell_id']} on {location['date']} at {location['time']}")
    
    # Example: Find suspects in a cell
    cell_id = "1938234"
    date = "2022-10-04"
    time = "12:33:00"
    suspects = app.find_suspects_in_cell(cell_id, date, time)
    for suspect in suspects:
        print(f"Suspect {suspect['name']} with phone {suspect['phone_number']} was in cell {cell_id} on {date} at {time}")

    # Example: Find suspects near a location
    latitude = 34.3
    longitude = -56.4
    date = "2022-10-04"
    time = "12:33:00"
    radius = 1000  # in meters
    nearby_suspects = app.find_suspects_near_location(latitude, longitude, date, time, radius)
    for suspect in nearby_suspects:
        print(f"Suspect {suspect['name']} with phone {suspect['phone_number']} was near {latitude}N, {longitude}W on {date} at {time}")

    app.close()

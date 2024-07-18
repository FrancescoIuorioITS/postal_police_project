from db_connection import with_database
from data_retrieval import DataRetrievalApp
from geopy.geocoders import Nominatim
from geopy.distance import distance
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from neo4j.exceptions import ServiceUnavailable, AuthError
from datetime import timedelta
from faker import Faker
import random, math

@with_database
class UserCreationApp:

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

@with_database
class CellCreationApp:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="postal_police_project")

    def create_cell(self, cell_id, latitude, longitude, cell_type):
        query = (
            "CREATE (c:Cell {id: $cell_id, latitude: $latitude, longitude: $longitude, type: $cell_type}) "
            "RETURN c"
        )
        try:
            result = self.connector.execute_query(query, {"cell_id": cell_id, "latitude": latitude, "longitude": longitude, "cell_type": cell_type})
            return result[0] if result else None
        except (ServiceUnavailable, AuthError) as e:
            print(f"Database error while creating cell {cell_id}: {str(e)}")
        except Exception as e:
            print(f"An error occurred while creating cell {cell_id}: {str(e)}")
        return None

    def generate_cells_for_italy(self, total_cells=1500, ratio_5g=0.3):
        cities = ["Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa", "Bologna", "Florence", "Bari", "Catania"]
        cells_per_city = total_cells // len(cities)
        traditional_cells_per_city = int(cells_per_city * (1 - ratio_5g))
        five_g_cells_per_city = cells_per_city - traditional_cells_per_city

        for city in cities:
            self.generate_cells_for_city(city, traditional_cells_per_city, five_g_cells_per_city)

        print(f"Generated approximately {total_cells} cell towers for {len(cities)} Italian cities.")

    def generate_cells_for_city(self, city_name, traditional_cells, five_g_cells):
        location = self.geolocator.geocode(f"{city_name}, Italy")
        if location:
            city_center = (location.latitude, location.longitude)
            city_radius = 10  # km, adjust as needed
            self.generate_traditional_cells(city_name, city_center, city_radius, traditional_cells)
            self.generate_5g_cells(city_name, city_center, city_radius, five_g_cells)
        else:
            print(f"Could not locate {city_name}")

    def generate_traditional_cells(self, city_name, city_center, city_radius, num_cells):
        for i in range(num_cells):
            angle = random.uniform(0, 360)
            radius = random.uniform(0, city_radius)
            lat = city_center[0] + radius * math.cos(math.radians(angle))
            lon = city_center[1] + radius * math.sin(math.radians(angle))
            cell_id = f"TRAD_{city_name}_{i}"
            self.create_cell(cell_id, lat, lon, "traditional")

    def generate_5g_cells(self, city_name, city_center, city_radius, num_cells):
        for i in range(num_cells):
            angle = random.uniform(0, 360)
            radius = random.uniform(0, city_radius * 0.7)  # 5G cells typically have shorter range
            lat = city_center[0] + radius * math.cos(math.radians(angle))
            lon = city_center[1] + radius * math.sin(math.radians(angle))
            cell_id = f"5G_{city_name}_{i}"
            self.create_cell(cell_id, lat, lon, "5G")

@with_database
class ConnectionCreationApp:
    def __init__(self, retrieval_app):
        self.retrieval_app = retrieval_app

    def connect_phone_to_cell(self, phone_number, cell_id, start_date, start_time, end_date, end_time):
        query = (
            "MATCH (ph:PhoneNumber {number: $phone_number}), (c:Cell {id: $cell_id}) "
            "CREATE (ph)-[:CONNECTED_TO {start_date: $start_date, start_time: $start_time, end_date: $end_date, end_time: $end_time}]->(c)"
        )
        self.connector.execute_query(query, {
            "phone_number": phone_number, 
            "cell_id": cell_id, 
            "start_date": start_date, 
            "start_time": start_time,
            "end_date": end_date,
            "end_time": end_time
        })

    def generate_fake_connections(self, connection_count=1000):
        fake = Faker()
        phone_numbers = self.retrieval_app.get_all_phone_numbers()
        cell_ids = self.get_all_cell_ids()
        for _ in range(connection_count):
            phone_number = random.choice(phone_numbers)
            cell_id = random.choice(cell_ids)
            start_datetime = fake.date_time_between(start_date='-30d', end_date='now')
            end_datetime = start_datetime + timedelta(minutes=random.randint(1, 120))
            self.connect_phone_to_cell(
                phone_number, 
                cell_id, 
                str(start_datetime.date()), 
                str(start_datetime.time()),
                str(end_datetime.date()),
                str(end_datetime.time())
            )
        print(f"Generated {connection_count} fake connections between phones and cells.")

    def get_all_cell_ids(self):
        query = "MATCH (c:Cell) RETURN c.id AS id"
        result = self.connector.execute_query(query)
        return [record['id'] for record in result]


if __name__ == "__main__":
    with UserCreationApp() as user_creation, \
         CellCreationApp() as cell_creation, \
         DataRetrievalApp() as retrieval_app, \
         ConnectionCreationApp(DataRetrievalApp()) as connection_creation:
         

        #user_creation.generate_fake_people(7500)
        all_people = retrieval_app.get_all_people()
        print(f"Total people created: {len(all_people)}")

        random_person = random.choice(all_people)
        phone = retrieval_app.get_phone_by_name(random_person)
        print(f"Random person: {random_person}, Phone: {phone}")

        #cell_creation.generate_cells_for_italy(total_cells=1000, ratio_5g=0.3)
        all_cells = retrieval_app.get_all_cells()
        print(f"Total cells created: {len(all_cells)}")

        traditional_cells = [cell for cell in all_cells if cell['type'] == 'traditional']
        five_g_cells = [cell for cell in all_cells if cell['type'] == '5G']
        print(f"Traditional cells: {len(traditional_cells)}, 5G cells: {len(five_g_cells)}")

        connection_creation.generate_fake_connections(10000)
        all_connections = retrieval_app.get_all_connections()
        print(f"Total connections created: {len(all_connections)}")

        phone_connections = retrieval_app.get_connections_by_phone(phone)
        print(f"Connections for {random_person}: {len(phone_connections)}")

    print("Database operations completed and resources properly closed.")



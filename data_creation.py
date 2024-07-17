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

    def generate_traditional_cells(self, city_name, city_center, city_radius, traditional_range=5):
        for i in range(int(city_radius * 2 / traditional_range)):
            for j in range(int(city_radius * 2 / traditional_range)):
                lat = city_center[0] - city_radius + i * traditional_range
                lon = city_center[1] - city_radius + j * traditional_range
                if distance(city_center, (lat, lon)).km <= city_radius:
                    cell_id = f"TRAD_{city_name}_{i}_{j}"
                    self.create_cell(cell_id, lat, lon, "traditional")

    def generate_5g_cells(self, city_name, city_center, city_radius, five_g_range=0.5):
        num_5g_cells = int((city_radius * 2 / five_g_range) ** 2 * 0.3)  # 30% coverage
        for i in range(num_5g_cells):
            angle = random.uniform(0, 360)
            radius = random.uniform(0, city_radius)
            lat = city_center[0] + radius * math.cos(math.radians(angle))
            lon = city_center[1] + radius * math.sin(math.radians(angle))
            cell_id = f"5G_{city_name}_{i}"
            self.create_cell(cell_id, lat, lon, "5G")

    def generate_cells_for_city(self, city_name):
        try:
            location = self.geolocator.geocode(f"{city_name}, Italy")
            if not location:
                print(f"Could not locate {city_name}")
                return

            city_center = (location.latitude, location.longitude)
            city_radius = 10 

            self.generate_traditional_cells(city_name, city_center, city_radius)
            self.generate_5g_cells(city_name, city_center, city_radius)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Geocoding error for {city_name}: {str(e)}")

        city_center = (location.latitude, location.longitude)
        city_radius = 10 

        self.generate_traditional_cells(city_name, city_center, city_radius)
        self.generate_5g_cells(city_name, city_center, city_radius)

    def generate_cells_for_italy(self):
        cities = ["Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa", "Bologna", "Florence", "Bari", "Catania"]
        for city in cities:
            self.generate_cells_for_city(city)
        print(f"Generated cell towers for {len(cities)} Italian cities.")

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
         

        #user_creation.generate_fake_people(100)
        all_people = retrieval_app.get_all_people()
        print(f"Total people created: {len(all_people)}")

        random_person = random.choice(all_people)
        phone = retrieval_app.get_phone_by_name(random_person)
        print(f"Random person: {random_person}, Phone: {phone}")

        #cell_creation.generate_cells_for_italy()
        all_cells = retrieval_app.get_all_cells()
        print(f"Total cells created: {len(all_cells)}")

        traditional_cells = [cell for cell in all_cells if cell['type'] == 'traditional']
        five_g_cells = [cell for cell in all_cells if cell['type'] == '5G']
        print(f"Traditional cells: {len(traditional_cells)}, 5G cells: {len(five_g_cells)}")

        #connection_creation.generate_fake_connections(10000)
        all_connections = retrieval_app.get_all_connections()
        print(f"Total connections created: {len(all_connections)}")

        phone_connections = retrieval_app.get_connections_by_phone(phone)
        print(f"Connections for {random_person}: {len(phone_connections)}")

    print("Database operations completed and resources properly closed.")



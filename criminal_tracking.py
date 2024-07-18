from db_connection import with_database
from data_retrieval import DataRetrievalApp
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import distance
import random

@with_database
class CriminalTrackingApp(DataRetrievalApp):
    def __init__(self):
        super().__init__()
        self.geolocator = Nominatim(user_agent="criminal_tracking_app")

    def find_person_cell(self, name, date, time):
        phone_number = self.get_phone_by_name(name)
        print(f'(The phone number of {name} is {phone_number}')
        if phone_number:
            return self.get_cell_for_person_at_time(phone_number, date, time)
        return None


    def find_person_location(self, name, date, time):
        phone_number = self.get_phone_by_name(name)
        if phone_number:
            return self.get_connection_coordinates(phone_number, date, time)
        return []
    
    def get_location_info(self, latitude, longitude, radius=1):  # radius in km
        geolocator = Nominatim(user_agent="criminal_tracking_app")
        try:
            locations = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=False)
            if locations:
                for location in locations:
                    dist = distance((latitude, longitude), (location.latitude, location.longitude)).km
                    if dist <= radius:
                        address = location.raw['address']
                        comune = address.get('city') or address.get('town') or address.get('village')
                        if comune:
                            return f"in the comune of {comune}"
            return f"within {radius}km of coordinates ({latitude}, {longitude})"
        except GeocoderTimedOut:
            return f"within {radius}km of coordinates ({latitude}, {longitude})"



    def find_suspects_in_cell(self, cell_id, date, time):
        query = """
        MATCH (p:Person)-[:HAS_PHONE]->(ph:PhoneNumber)-[r:CONNECTED_TO]->(c:Cell {id: $cell_id})
        WHERE r.start_date = $date AND r.start_time <= $time AND r.end_time >= $time
        RETURN p.name AS name, ph.number AS phone_number
        """
        result = self.connector.execute_query(query, {"cell_id": cell_id, "date": date, "time": time})
        return [(record['name'], record['phone_number']) for record in result]


    def find_suspects_near_location(self, latitude, longitude, date, time, radius):
        query = """
        MATCH (p:Person)-[:HAS_PHONE]->(ph:PhoneNumber)-[r:CONNECTED_TO]->(c:Cell)
        WHERE r.start_date = $date AND r.start_time <= $time AND r.end_time >= $time
        AND point.distance(point({latitude: c.latitude, longitude: c.longitude}), 
                        point({latitude: $latitude, longitude: $longitude})) / 1000 <= $radius
        RETURN DISTINCT p.name AS name, ph.number AS phone_number
        """
        result = self.connector.execute_query(query, {
            "latitude": latitude,
            "longitude": longitude,
            "date": date,
            "time": time,
            "radius": radius
        })
        return [(record['name'], record['phone_number']) for record in result]


if __name__ == "__main__":
    with CriminalTrackingApp() as app:
        # Get a random person
        all_people = app.get_all_people()
        name = random.choice(all_people)

        # Get phone number for the random person
        phone_number = app.get_phone_by_name(name)

        # Get random connection dates for this phone number
        connection_dates = app.get_connection_dates(phone_number)
        if connection_dates:
            start_date, end_date = random.choice(connection_dates)

            # Get random connection times for the selected date
            connection_times = app.get_connection_times(phone_number, start_date)
            if connection_times:
                start_time, end_time = random.choice(connection_times)

                locations = app.find_person_location(name, start_date, start_time)
                if locations:
                    latitude, longitude = locations[0]
                    location_info = app.get_location_info(latitude, longitude, radius=1)
                    print(f"Person {name} with phone {phone_number} was located {location_info} on {start_date} at {start_time}")

                    # Test find_suspects_in_cell
                    all_cells = app.get_all_cells()
                    random_cell = random.choice(all_cells)
                    cell_id = random_cell['id']

                    suspects_in_cell = app.find_suspects_in_cell(cell_id, start_date, start_time)
                    print(f"\nSuspects in cell {cell_id} on {start_date} at {start_time}:")
                    for suspect_name, suspect_phone in suspects_in_cell:
                        print(f"- {suspect_name} (Phone: {suspect_phone})")

                    # Test find_suspects_near_location
                    search_radius = 5  # km
                    suspects_near_location = app.find_suspects_near_location(latitude, longitude, start_date, start_time, search_radius)
                    print(f"\nSuspects within {search_radius}km of ({latitude}, {longitude}) on {start_date} at {start_time}:")
                    for suspect_name, suspect_phone in suspects_near_location:
                        print(f"- {suspect_name} (Phone: {suspect_phone})")

                else:
                    print(f"No location found for {name} on {start_date} at {start_time}")
            else:
                print(f"No connection times found for {name} on {start_date}")
        else:
            print(f"No connection dates found for {name}")

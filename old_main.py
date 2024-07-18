from criminal_tracking import CriminalTrackingApp
from datetime import datetime, date, timedelta
from fuzzywuzzy import process
import re, random

def fuzzy_match(query, choices, limit=5):
    return process.extract(query, choices, limit=limit)

def regex_match(pattern, choices):
    regex = re.compile(pattern, re.IGNORECASE)
    return [choice for choice in choices if regex.search(choice)]

def get_best_matches(query, choices):
    regex_matches = regex_match(query, choices)
    if regex_matches:
        return regex_matches[:25]  # Limit to 25 matches
    else:
        fuzzy_matches = fuzzy_match(query, choices, limit=25)  # Limit fuzzy matches to 25
        return [match[0] for match in fuzzy_matches]

def parse_flexible_date_time(date_input, time_input):
    # Parse date
    if date_input.lower() == 'today':
        parsed_date = date.today()
    elif date_input.lower() == 'yesterday':
        parsed_date = date.today() - timedelta(days=1)
    else:
        try:
            parsed_date = datetime.strptime(date_input, "%Y-%m-%d").date()
        except ValueError:
            return None, None

    # Parse time
    if not time_input:
        parsed_time = None
    else:
        time_formats = ["%H", "%H:%M", "%H:%M:%S"]
        for fmt in time_formats:
            try:
                parsed_time = datetime.strptime(time_input, fmt).time()
                break
            except ValueError:
                continue
        else:
            return None, None

    return str(parsed_date), str(parsed_time) if parsed_time else None



def get_date_time_input():
    while True:
        date_input = input("Enter date (YYYY-MM-DD or 'today' or 'yesterday') or date range (YYYY-MM-DD to YYYY-MM-DD): ")
        
        if ' to ' in date_input:
            start_date_str, end_date_str = date_input.split(' to ')
            try:
                start_date = parse_date(start_date_str)
                end_date = parse_date(end_date_str)
                return (str(start_date), "00:00:00"), (str(end_date), "23:59:59")
            except ValueError:
                print("Invalid date range format. Please try again.")
                continue
        else:
            date = parse_date(date_input)
            if not date:
                continue
        
        time_input = input("Enter time (HH:MM or HH:MM:SS, or press Enter for all day): ")
        if not time_input:
            return (str(date), "00:00:00"), (str(date), "23:59:59")
        
        time = parse_time(time_input)
        if time_input and not time:
            continue
        
        return (str(date), str(time) if time else None)

def parse_date(date_input):
    if date_input.lower() == 'today':
        return datetime.now().date()
    elif date_input.lower() == 'yesterday':
        return datetime.now().date() - timedelta(days=1)
    else:
        try:
            return datetime.strptime(date_input, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please try again.")
            return None

def parse_time(time_input):
    if not time_input:
        return None
    try:
        return datetime.strptime(time_input, "%H:%M").time()
    except ValueError:
        try:
            return datetime.strptime(time_input, "%H:%M:%S").time()
        except ValueError:
            print("Invalid time format. Please try again.")
            return None



def main():
    app = CriminalTrackingApp()

    while True:
        print("\nCriminal Tracking System")
        print("1. Find a suspect's location")
        print("2. Find suspects in a cell")
        print("3. Find suspects near coordinates")
        print("4. List all people")
        print("5. List all cells")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            name_query = input("Enter suspect's name (or part of the name, use regex for advanced search): ")
            all_people = app.get_all_people()
            matches = get_best_matches(name_query, all_people)
            if matches:
                print("Matching names:")
                for i, name in enumerate(matches, 1):
                    print(f"{i}. {name}")
                selection = input("Select a number or press Enter to search for the top match: ")
                if selection.isdigit() and 1 <= int(selection) <= len(matches):
                    name = matches[int(selection)-1]
                else:
                    name = matches[0]
            else:
                print("No matching names found.")
                continue

            date = input("Enter date (YYYY-MM-DD or 'today' or 'yesterday'): ")
            time = input("Enter time (HH or HH:MM or HH:MM:SS, or press Enter for all day): ")

            date, time = parse_flexible_date_time(date, time)
            if date:
                locations = app.find_person_location(name, date, time)
                if locations:
                    for lat, lon in locations:
                        location_info = app.get_location_info(lat, lon)
                        print(f"{name} was located {location_info} on {date} at {time or 'any time'}")
                else:
                    print(f"No location found for {name} on {date} at {time or 'any time'}")
            else:
                print("Invalid date or time format. Please try again.")


        elif choice == '2':
            all_cells = app.get_all_cells()
            cell_ids = [cell['id'] for cell in all_cells]
            cell_query = input("Enter cell ID (or part of it, use regex for advanced search): ")
            matches = get_best_matches(cell_query, cell_ids)
            if matches:
                print("Matching cell IDs:")
                for i, cell_id in enumerate(matches, 1):
                    print(f"{i}. {cell_id}")
                selection = input("Select a number or press Enter to search for the top match: ")
                if selection.isdigit() and 1 <= int(selection) <= len(matches):
                    cell_id = matches[int(selection)-1]
                else:
                    cell_id = matches[0]
            else:
                print("No matching cell IDs found.")
                continue

            date, time = get_date_time_input()
            suspects = app.find_suspects_in_cell(cell_id, date, time)
            print(f"Suspects in cell {cell_id} on {date} at {time or 'any time'}:")
            for name, phone in suspects:
                print(f"- {name} (Phone: {phone})")

        elif choice == '3':
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            radius = float(input("Enter search radius (km): "))
            date, time = get_date_time_input()
            suspects = app.find_suspects_near_location(lat, lon, date, time, radius)
            print(f"Suspects within {radius}km of ({lat}, {lon}) on {date} at {time or 'any time'}:")
            for name, phone in suspects:
                print(f"- {name} (Phone: {phone})")

        elif choice == '4':
            all_people = app.get_all_people()
            sample_size = min(15, len(all_people))  # Ensure we don't try to sample more than we have
            random_sample = random.sample(all_people, sample_size)
            print(f"Random sample of {sample_size} people from the database:")
            for person in random_sample:
                print(f"- {person}")

        elif choice == '5':
            print("Cell Listing Options:")
            print("1. List cells by city")
            print("2. List cells by type")
            print("3. List cells by city and type")
            
            sub_choice = input("Enter your choice (1-3): ")
            
            if sub_choice == '1':
                city = input("Enter city name: ")
                filtered_cells = [cell for cell in app.get_all_cells() if cell['city'].lower() == city.lower()]
            elif sub_choice == '2':
                cell_type = input("Enter cell type: ")
                filtered_cells = [cell for cell in app.get_all_cells() if cell['type'].lower() == cell_type.lower()]
            elif sub_choice == '3':
                city = input("Enter city name: ")
                cell_type = input("Enter cell type: ")
                filtered_cells = [cell for cell in app.get_all_cells() if cell['city'].lower() == city.lower() and cell['type'].lower() == cell_type.lower()]
            else:
                print("Invalid choice. Returning to main menu.")
                continue
            
            if filtered_cells:
                sample_size = min(15, len(filtered_cells))
                random_sample = random.sample(filtered_cells, sample_size)
                print(f"Random sample of {sample_size} cells matching your criteria:")
                for cell in random_sample:
                    print(f"- ID: {cell['id']}, Type: {cell['type']}, City: {cell['city']}, Location: ({cell['latitude']}, {cell['longitude']})")
            else:
                print("No cells found matching your criteria.")

        elif choice == '6':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

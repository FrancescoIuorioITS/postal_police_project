from criminal_tracking import CriminalTrackingApp

def get_date_time_input():
    date = input("Enter date (YYYY-MM-DD): ")
    time = input("Enter time (HH:MM:SS): ")
    return date, time

def main():
    app = CriminalTrackingApp()

    while True:
        print("\nCriminal Tracking System")
        print("1. Find a suspect's location")
        print("2. Find suspects in a cell")
        print("3. Find suspects near coordinates")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            name = input("Enter suspect's name: ")
            date, time = get_date_time_input()
            locations = app.find_person_location(name, date, time)
            if locations:
                for lat, lon in locations:
                    location_info = app.get_location_info(lat, lon)
                    print(f"{name} was located {location_info} on {date} at {time}")
            else:
                print(f"No location found for {name} on {date} at {time}")

        elif choice == '2':
            cell_id = input("Enter cell ID: ")
            date, time = get_date_time_input()
            suspects = app.find_suspects_in_cell(cell_id, date, time)
            print(f"Suspects in cell {cell_id} on {date} at {time}:")
            for name, phone in suspects:
                print(f"- {name} (Phone: {phone})")

        elif choice == '3':
            lat = float(input("Enter latitude: "))
            lon = float(input("Enter longitude: "))
            radius = float(input("Enter search radius (km): "))
            date, time = get_date_time_input()
            suspects = app.find_suspects_near_location(lat, lon, date, time, radius)
            print(f"Suspects within {radius}km of ({lat}, {lon}) on {date} at {time}:")
            for name, phone in suspects:
                print(f"- {name} (Phone: {phone})")

        elif choice == '4':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
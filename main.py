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
    
def main():
    with CriminalTrackingApp() as app:
        while True:
            print("\nCriminal Tracking System")
            print("1. Find a suspect's location")
            print("2. Find suspects in a cell")
            print("3. Find suspects near coordinates")

            choice = input("Enter your choice (1-3): ")

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

                date = input("Enter exact date (YYYY-MM-DD): ")
                time = input("Enter exact time (HH:MM:SS): ")

                cell = app.find_person_cell(name, date, time)
                if cell:
                    print(f"{name} was connected to cell {cell} on {date} at {time}")
                else:
                    print(f"No connection found for {name} at the specified time")

            if choice == '2':
                cell_id = input("Enter cell ID: ")
                date = input("Enter exact date (YYYY-MM-DD): ")
                time = input("Enter exact time (HH:MM:SS): ")

                suspects = app.find_suspects_in_cell(cell_id, date, time)
                if suspects:
                    print(f"Suspects in cell {cell_id} on {date} at {time}:")
                    for suspect in suspects:
                        print(f"- {suspect}")
                else:
                    print(f"No suspects found in cell {cell_id} on {date} at {time}")

            if choice == '3':
                latitude = float(input("Enter latitude: "))
                longitude = float(input("Enter longitude: "))
                date = input("Enter exact date (YYYY-MM-DD): ")
                time = input("Enter exact time (HH:MM:SS): ")
                radius = float(input("Enter search radius (in km): "))

                suspects = app.find_suspects_near_location(latitude, longitude, date, time, radius)
                print(f"Suspects within {radius}km of ({latitude}, {longitude}) on {date} at {time}:")
                
if __name__ == "__main__":
    main()

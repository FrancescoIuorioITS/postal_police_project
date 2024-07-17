import streamlit as st
from criminal_tracking import CriminalTrackingApp

def main():
    st.title("Criminal Tracking System")

    app = CriminalTrackingApp()

    option = st.sidebar.selectbox(
        "Choose an operation",
        ("Find a suspect's location", "Find suspects in a cell", "Find suspects near coordinates")
    )

    if option == "Find a suspect's location":
        name = st.text_input("Enter suspect's name")
        date = st.date_input("Select date")
        time = st.time_input("Select time")

        if st.button("Find Location"):
            locations = app.find_person_location(name, str(date), str(time))
            if locations:
                for lat, lon in locations:
                    location_info = app.get_location_info(lat, lon)
                    st.success(f"{name} was located {location_info} on {date} at {time}")
            else:
                st.warning(f"No location found for {name} on {date} at {time}")

    elif option == "Find suspects in a cell":
        cell_id = st.text_input("Enter cell ID")
        date = st.date_input("Select date")
        time = st.time_input("Select time")

        if st.button("Find Suspects"):
            suspects = app.find_suspects_in_cell(cell_id, str(date), str(time))
            st.write(f"Suspects in cell {cell_id} on {date} at {time}:")
            for name, phone in suspects:
                st.write(f"- {name} (Phone: {phone})")

    elif option == "Find suspects near coordinates":
        lat = st.number_input("Enter latitude", format="%.6f")
        lon = st.number_input("Enter longitude", format="%.6f")
        radius = st.number_input("Enter search radius (km)", min_value=0.1, value=1.0)
        date = st.date_input("Select date")
        time = st.time_input("Select time")

        if st.button("Find Suspects"):
            suspects = app.find_suspects_near_location(lat, lon, str(date), str(time), radius)
            st.write(f"Suspects within {radius}km of ({lat}, {lon}) on {date} at {time}:")
            for name, phone in suspects:
                st.write(f"- {name} (Phone: {phone})")

if __name__ == "__main__":
    main()
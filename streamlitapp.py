import pandas as pd
import pydeck as pdk
import numpy as np
import altair as alt
from google.oauth2 import service_account
from google.cloud import bigquery
import streamlit as st

credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
# Create a BigQuery client
client = bigquery.Client(credentials=credentials)

# Load the Bay Area bike share data and cache it using st.cache_data
#========================load data =========================
@st.cache_data
def load_data_from_bigquery():
    # Define your BigQuery SQL query
    query = f"""
    SELECT *
    FROM `BikeshareSF.cmpe255-400623`
    """
    # Execute the query and load the results into a DataFrame
    data = client.query(query).to_dataframe()
    return data

# Create separate dataframes for different areas
#========================function page 1=========================
def create_area_data(data, area_name):
    return data[data["start_station_name"].str.contains(area_name)]

# Function to display the hexagon map
def display_hexagon_map(data, title, latitude, longitude, hour_selected):
    st.subheader(title)
    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={
                "latitude": latitude.mean(),
                "longitude": longitude.mean(),
                "zoom": 11,
                "pitch": 50,
            },
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=data[data["start_date"].dt.hour == hour_selected],
                    get_position=["start_station_longitude", "start_station_latitude"],
                    radius=100,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
            ],
        )
    )

# Function to display the histogram of rides per hour
def display_rides_per_hour_histogram(data):
    st.header("Rides Per Hour Distribution")
    hist = np.histogram(data["start_date"].dt.hour, bins=24, range=(0, 24))
    chart_data = pd.DataFrame({"Hour": range(24), "Rides": hist[0]})

    # Create an Altair chart
    chart = (
        alt.Chart(chart_data)
        .mark_area(interpolate="step-after", opacity=0.2, color="red")
        .encode(
            x=alt.X("Hour:O", axis=alt.Axis(title="Hour of the Day", labelAngle=-45,grid=True)),
            y=alt.Y("Rides:Q", axis=alt.Axis(title="Number of Rides", grid=True)),
            tooltip=["Hour:O", "Rides:Q"]
        )
        .configure_view(stroke='transparent')
        .properties(width=600, height=400)
    )

    # Display the Altair chart using st.altair_chart
    st.altair_chart(chart, use_container_width=True)

#========================page 1 =========================
def Geo_visualization():
    # Create separate dataframes for different areas
    sf_data = create_area_data(data, "San Francisco")
    oakland_data = create_area_data(data, "Oakland")
    sj_data = create_area_data(data, "San Jose")

    # 3D Station Stacking Visualization
    st.title("Bay Area Bike Sharing Data")
    st.write( """
    Examining how bike share vary over time in Bay Area. By sliding the slider on the
    left you can view different slices of time and explore
    different rush hours""")

    # Create a sidebar for filtering by hour
    hour_selected = st.slider("Select hour of the day", 0, 23, 12)

    # Create a row layout for the maps
    maps_row = st.columns(3)  # Three maps in a row

    # San Francisco Area Map
    with maps_row[0]:
        display_hexagon_map(sf_data, "San Francisco Area", sf_data["start_station_latitude"], sf_data["start_station_longitude"], hour_selected)

    # Oakland Area Map
    with maps_row[1]:
        display_hexagon_map(oakland_data, "Oakland Area", oakland_data["start_station_latitude"] - 0.05, oakland_data["start_station_longitude"], hour_selected)

    # San Jose Area Map
    with maps_row[2]:
        display_hexagon_map(sj_data, "San Jose Area", sj_data["start_station_latitude"] - 0.06, sj_data["start_station_longitude"] + 0.1, hour_selected)

    # Histogram of rides per hour for all data
    display_rides_per_hour_histogram(data)


#========================page 2 =========================
def data_comp():

    st.title("Time vs Rides Analysis")
  
    # Create a dropdown to select the time frame
    time_frame = st.sidebar.selectbox("Select Time Frame", ["Per Date", "Per Month", "Per Week", "Per Day"])

    # Data aggregation based on the selected time frame
    if time_frame == "Per Date":
        grouped_data = data.groupby(data["start_date"].dt.date).size().reset_index(name="Number of Rides")
    elif time_frame == "Per Month":
        grouped_data = data.groupby(data["start_date"].dt.strftime('%Y-%m')).size().reset_index(name="Number of Rides")
    elif time_frame == "Per Week":
        grouped_data = data.groupby(data["start_date"].dt.strftime('%U')).size().reset_index(name="Number of Rides")
    else:
        grouped_data = data.groupby(data["start_date"].dt.day).size().reset_index(name="Number of Rides")

    # Create a bar chart using Streamlit's st.bar_chart
    st.bar_chart(grouped_data.set_index(grouped_data.columns[0]))



#========================page 3 =========================

def visualize_start_station_ride_count():
    st.title('Top 15 Start Station vs Rides Count Analysis')

    # Get the top 15 start locations with the most rides counts
    top_start_locations = data['start_station_name'].value_counts().head(15).index.tolist()

    # Sidebar to select start stations
    selected_stations = st.sidebar.multiselect('Select two or more Start Stations', top_start_locations)

    if selected_stations:
        # Filter data based on selected stations
        filtered_data = data[data['start_station_name'].isin(selected_stations)]

        # Group and count data by start station name
        grouped_data = filtered_data['start_station_name'].value_counts().reset_index()
        grouped_data.columns = ['start_station_name', 'trip_count']

        # Create the area chart
        chart = (
            alt.Chart(grouped_data)
            .mark_area()
            .encode(
                x=alt.X('start_station_name:N', title='Start Station Name'),
                y=alt.Y('trip_count:Q', title='Number of Trips'),
                tooltip=['start_station_name:N', alt.Tooltip('trip_count:Q', title='Number of Trips')]
            )
            .properties(width=800, height=400)
            .interactive()
        )

        # Display the chart
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Select two or more start stations to visualize the number of rides.")

#========================page 4 =========================

def Use_Profile_Comparison():
    st.title("User Demographics Analysis")

    # Predefined columns and their filter options
    predefined_columns = {
        "Subscriber Type": "subscriber_type",
        "Member Birth Year": "member_birth_year",
        "Member Gender": "member_gender"
    }

    # Get the column selection from the user
    selected_column = st.sidebar.selectbox("Select Column", list(predefined_columns.keys()))

    if selected_column:
      selected_column_name = predefined_columns[selected_column]

    # Provide filter options based on unique values in the selected column
    filter_options = data[selected_column_name].unique()

    if selected_column_name == "member_birth_year":
        # For Member Birth Year column, display unique values in ascending order
        filter_options = sorted(filter_options)

    selected_filter = st.sidebar.selectbox(f"Select {selected_column}", filter_options)

    # Filter the data based on the selected filter
    if selected_filter:
        filtered_data = data[data[selected_column_name] == selected_filter]
        st.write(f"Filtered Data for {selected_column}: {selected_filter}")
        st.write(filtered_data)

    # Visualization
    st.header("Data Visualization")

    # Group data by start stations and count the trips
    station_trip_counts = data['start_station_name'].value_counts().reset_index()
    station_trip_counts.columns = ['start_station_name', 'trip_count']

    # Create a bar chart
    chart = alt.Chart(station_trip_counts).mark_bar().encode(
        x='trip_count:Q',
        y=alt.Y('start_station_name:N', sort='-x'),
        tooltip=['start_station_name:N', 'trip_count:Q']
    ).properties(width=600, height=400)

    st.altair_chart(chart)


#========================main run =========================

# Load the data
data = load_data_from_bigquery()

# Create multi-page app
pages = {
    'Geographical Analysis 🌎 ': Geo_visualization,
    'Time Analysis 📊': data_comp,
    'Start Station Analysis 📈': visualize_start_station_ride_count,
    'User Demographics Comparison 🆚': Use_Profile_Comparison  
}

st.sidebar.title('DashBoard')
page = st.sidebar.radio('Go to page', list(pages.keys()))

# Display the selected page
pages[page]()

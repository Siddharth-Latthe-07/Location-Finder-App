import pandas as pd
import folium
from sklearn.neighbors import DistanceMetric
import streamlit as st
from streamlit_folium import folium_static


# Load the dataset
df = pd.read_csv("open_pubs - open_pubs.csv")

# Remove rows with missing latitude or longitude values
df.dropna(subset=["latitude", "longitude"], inplace=True)

# Remove pubs with invalid latitude or longitude values
df = df[df["latitude"] != "\\N"]
df = df[df["longitude"] != "\\N"]

# Convert latitude and longitude columns to floats
df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)

# Create a dictionary of local authorities and their respective postal codes
local_authorities = df.groupby("local_authority")["postcode"].unique().to_dict()

# Create a dictionary of local authorities and their respective latitude and longitude values
local_authorities_lat_lon = df.groupby("local_authority").first()[["latitude", "longitude"]].to_dict()

# Create a DistanceMetric object using Euclidean distance
dist = DistanceMetric.get_metric("euclidean")



def home():
    st.title("Welcome to the Pub Finder App")
    st.write("This app allows you to find pubs in different areas and also the nearest pubs to a particular location.")
    st.write("Please select a page from the sidebar to get started.")


def pub_locations():
    st.title("Pub Locations")

    # Get user input for borough or postcode
    borough_or_postcode = st.radio("Search by:", ("Borough", "Postcode"))

    # Get borough or postcode from user
    if borough_or_postcode == "Borough":
        borough_dict = {
            "Barking and Dagenham": "Barking and Dagenham",
            "Barnet": "Barnet",
            "Bexley": "Bexley",
            "Brent": "Brent",
            "Bromley": "Bromley",
            "Camden": "Camden",
            "Croydon": "Croydon",
            "Ealing": "Ealing",
            "Enfield": "Enfield",
            "Greenwich": "Greenwich",
            "Hackney": "Hackney",
            "Hammersmith and Fulham": "Hammersmith and Fulham",
            "Haringey": "Haringey",
            "Harrow": "Harrow",
            "Havering": "Havering",
            "Hillingdon": "Hillingdon",
            "Hounslow": "Hounslow",
            "Islington": "Islington",
            "Kensington and Chelsea": "Kensington and Chelsea",
            "Kingston upon Thames": "Kingston upon Thames",
            "Lambeth": "Lambeth",
            "Lewisham": "Lewisham",
            "Merton": "Merton",
            "Newham": "Newham",
            "Redbridge": "Redbridge",
            "Richmond upon Thames": "Richmond upon Thames",
            "Southwark": "Southwark",
            "Sutton": "Sutton",
            "Tower Hamlets": "Tower Hamlets",
            "Waltham Forest": "Waltham Forest",
            "Wandsworth": "Wandsworth",
            "Westminster": "Westminster"
        }

        borough = st.selectbox("Select a borough", list(borough_dict.keys()))
        df_filtered = df[df["local_authority"] == borough_dict[borough]]
    else:
        postcode = st.text_input("Enter a postcode (e.g. N1):")
        df_filtered = df[df["postcode"].str.startswith(postcode.upper())]

    # Display map with pub locations
    if not df_filtered.empty:
        m = folium.Map(location=[df_filtered["latitude"].mean(), df_filtered["longitude"].mean()], zoom_start=13)

        for index, row in df_filtered.iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=row["Name"],
                tooltip=row["Name"]
            ).add_to(m)

        folium_static(m)
    else:
        st.warning("No pubs found in this location. Please try a different search.")


def nearest_pub():
    st.title("Find Nearest Pubs")
    user_lat = st.number_input("Enter your Latitude")
    user_lon = st.number_input("Enter your Longitude")
    n = st.number_input("How many nearest pubs do you want to find?", min_value=1, max_value=50, value=5, step=1)

    # Check if the 'name' column is present in the 'df' dataframe
    if 'Name' not in df.columns:
        st.warning("The 'name' column is not present in the dataset.")
        return

    # Create a new dataframe with only the required columns
    df_geo = df[['Name', 'latitude', 'longitude']].dropna()

    # Compute the distance between user location and all pub locations
    dist = DistanceMetric.get_metric('euclidean')
    distances = dist.pairwise(df_geo[['latitude', 'longitude']].values, [[user_lat, user_lon]])

    # Add the distances as a new column to the df_geo dataframe
    df_geo['distance'] = distances

    # Sort the pubs by distance and get the top n pubs
    nearest_pubs = df_geo.sort_values(by='distance').head(n)

    # Display the nearest pubs on a map
    m = folium.Map(location=[user_lat, user_lon], zoom_start=12)
    tooltip = "Click for more info"
    for index, row in nearest_pubs.iterrows():
        folium.Marker([row['latitude'], row['longitude']], popup=row['Name'], tooltip=tooltip).add_to(m)
    folium_static(m)



# Set up the app
def app():
    st.set_page_config(page_title="Pub Finder App")
    st.sidebar.title("Navigation")
    pages = {"Home": home, "Pub Locations": pub_locations, "Nearest Pub": nearest_pub}
    page = st.sidebar.radio("", tuple(pages.keys()))
    pages[page]()

if __name__ == "__main__":
    app()

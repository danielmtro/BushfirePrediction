import requests

def get_lat_long(location_name):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location_name,
        "format": "json",
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data:
            # Extract latitude and longitude from the first result
            latitude = float(data[0]["lat"])
            longitude = float(data[0]["lon"])
            return latitude, longitude
        else:
            return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
    

def main():
    location_name = "Badja Forest Rd, Countegany"
    coordinates = get_lat_long(location_name)

    if coordinates:
        print(f"Latitude: {coordinates[0]}")
        print(f"Longitude: {coordinates[1]}")


if __name__ == '__main__':
    main()
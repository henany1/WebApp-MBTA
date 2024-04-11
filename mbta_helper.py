# Your API KEYS (you need to use your own keys - very long random characters)
from config import MAPBOX_TOKEN, MBTA_API_KEY, OPENWEATHER_API_KEY


# Useful URLs (you need to add the appropriate parameters for your requests)
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"


# A little bit of scaffolding if you want to use it
import json
import pprint
import urllib.request

def get_json(url: str) -> dict:
    """
    Given a properly formatted URL for a JSON web API request, return a Python JSON object containing the response to that request.

    Both get_lat_lng() and get_nearest_station() might need to use this function.
    """
    with urllib.request.urlopen(url) as f:
        response_text = f.read().decode('utf-8')
        response_data = json.loads(response_text)
        pprint.pprint(response_data)
    try: #If there is an error 
        with urllib.request.urlopen(url) as response:
            response_text = response.read().decode('utf-8')
            return json.loads(response_text)
    except urllib.error.URLError as e:
        print(f"URL error: {e.reason}")
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return {}  # Return an empty dict if the request fails or is not JSON

def get_weather(lat: str, lon: str) -> dict:
    """Gets weather data for the given latitude and longitude."""
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    return get_json(weather_url)

def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Given a place name or address, return a (latitude, longitude) tuple with the coordinates of the given place.

    See https://docs.mapbox.com/api/search/geocoding/ for Mapbox Geocoding API URL formatting requirements.
    """
    import urllib.request

    place_name = place_name.replace(' ', '%20')
    url =f'{MAPBOX_BASE_URL}/{place_name}.json?access_token={MAPBOX_TOKEN}&types=poi'

    with urllib.request.urlopen(url) as f:
        response_text = f.read().decode('utf-8')
        response_data = json.loads(response_text)

    longitude, latitude = response_data['features'][0]['center']
    return latitude,longitude 

def get_realtime_arrivals(stop_id: str) -> list:
    """
    Fetches real-time arrival data for a given MBTA stop ID and returns a list of upcoming arrivals.
    """
    predictions_url = f"{MBTA_BASE_URL.replace('/stops', '/predictions')}?filter[stop]={stop_id}&api_key={MBTA_API_KEY}"
    response_data = get_json(predictions_url)
    
    arrivals = []
    if response_data and 'data' in response_data:
        for prediction in response_data['data']:
            route_id = prediction['relationships']['route']['data']['id']
            arrival_time = prediction['attributes']['arrival_time']
            if arrival_time:
                arrivals.append({"route_id": route_id, "arrival_time": arrival_time})
    
    return arrivals

def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool, str]:
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible) tuple for the nearest MBTA station to the given coordinates.

    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL formatting requirements for the 'GET /stops' API.
    """
    mbta_url = f"{MBTA_BASE_URL}?filter[latitude]={latitude}&filter[longitude]={longitude}&sort=distance&api_key={MBTA_API_KEY}"
    response_data = get_json(mbta_url)
    
    if response_data['data']:
        station_data = response_data['data'][0]
        station_name = station_data['attributes']['name']
        wheelchair_accessible = "Yes" if station_data['attributes'].get('wheelchair_boarding', 0) == 1 else "No"
        stop_id = station_data['id']
        return station_name, wheelchair_accessible, stop_id
    else:
        return '', "No", ''

def find_stop_near(place_name: str) -> tuple:
    """
    Given a place name or address, return the nearest MBTA stop and whether it is wheelchair accessible.

    This function might use all the functions above.
    """
    latitude, longitude = get_lat_lng(place_name)
    if latitude and longitude:
        station_name, wheelchair_accessible, stop_id = get_nearest_station(latitude, longitude)
        if station_name: 
            arrivals = get_realtime_arrivals(stop_id)
            return (station_name, wheelchair_accessible, arrivals, latitude, longitude)
    return ("", "No", [], "", "")

def main():
    """
    You should test all the above functions here
    """

    # place_name = 'fenway park'
    # find_stop_near(place_name)


if __name__ == '__main__':
    main()
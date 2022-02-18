"""Builds a map of user's Twitter friends location"""
import requests
import json
from geopy.geocoders import Nominatim
import folium
from flask import Flask, render_template, request
from geopy.exc import GeocoderUnavailable


def get_id(username):
    """Gets the id of a user in Twitter

    :param username: name of the user
    :type username: str
    """
    api = <your API-key>
    resp = requests.get("https://api.twitter.com/2/users/by/username/" + 
                    username, headers={'Authorization': 'Bearer ' + api})
    if resp.status_code == 200:
        response = json.loads(resp.text)
        if 'data' in response.keys():
            return response['data']['id']
        else:
            return 'DictError'
    return 'AccessError'



def get_location(username):
    """Gets the location of user's friends"""
    api = <your API-key>
    user_id = get_id(username)
    resp = requests.get('https://api.twitter.com/2/users/' + user_id + 
                    '/following?user.fields=location',
                    headers={'Authorization': 'Bearer ' + api})
    response = json.loads(resp.text)
    if 'data' in response.keys():
        locations = []
        for friend in response['data']:
            if 'location' in friend.keys():
                locations.append([friend['location'], friend['name']])
        return locations
    return False



def find_coordinates(username):
    """Finds coordinates of user's friends if possible"""
    locations = get_location(username)
    coordinates = []
    for i in range(len(locations)):
        try:
            geolocator = Nominatim(user_agent="twitter_requests.py")
            location = geolocator.geocode(locations[i][0])
            coordinates.append(([location.latitude, \
location.longitude], locations[i][1]))
        except AttributeError:
            continue
        except GeocoderUnavailable:
            continue
    return coordinates


def build_map(username):
    """Builds a map of friend's locations"""
    coordinates = find_coordinates(username)
    map = folium.Map(location=(0, 0), zoom_start=2)
    for friend in coordinates:
        map.add_child(folium.Marker(location=friend[0],
                                    popup=friend[1],
                                    icon=folium.Icon()))
    return map



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/map', methods=['GET', 'POST'])
def react():
    username = request.args.get('q')
    username = str(username)
    id = get_id(username)
    if id == 'AccessError':
        return render_template('access_er.html')
    elif id == 'DictError':
        return render_template('username_fail.html')
    elif not get_location(username):
        return render_template('username_fail.html')
    else:
        map = build_map(username)
        return map.get_root().render()




if __name__ == '__main__':
    app.run(debug=False)

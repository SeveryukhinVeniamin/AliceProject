# Import all module and library
import requests
from data.statistics import Statistics
from data import db_session

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# This is address for geocode
server_address_geocode = 'http://geocode-maps.yandex.ru/1.x/?'

# This is api key for geocode
api_key_geocode = '8013b162-6b42-4997-9691-77b7074026e0'

# This is address for static maps
server_address_maps = 'https://static-maps.yandex.ru/v1?'

# This is api key for static maps
api_key_maps = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'

# This is path for loading map
MAP_FILE = "map.png"

# This is id for alice skill
SKILL_ID = "4d9bc848-79e1-4e46-a915-0ba0822d0ebd"

# This is token for sending images to alice skill
YANDEX_TOKEN = "y0__xC_lMXPBRij9xMgzezK-xaKlt5OX2HisrB0C4VM6L23kucj1A"


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for getting ll of place
def get_coordinates(name):
    geocoder_request = f'{server_address_geocode}apikey={api_key_geocode}&geocode={name}&format=json'
    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        return list(map(float, toponym_coodrinates.split(' ')))
    else:
        return None


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for getting full name of place
def get_full_name(name):
    geocoder_request = f'{server_address_geocode}apikey={api_key_geocode}&geocode={name}&format=json'
    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        return toponym_address
    else:
        return None


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for getting location of place
def get_location(coordinates, location):
    geocoder_request = (f'''{server_address_geocode}apikey={api_key_geocode}
                            &geocode={coord_list_into_string(coordinates)}&format=json&kind={location}''')
    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        return toponym_address
    else:
        return None


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for transforming list of ll into string
def coord_list_into_string(coordinates):
    return str(coordinates[0]) + ',' + str(coordinates[1])


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for creating url for request to static maps
def make_image_url(ll, z, theme='light', maptype='map', pt=[]):
    ll_spn = f'll={coord_list_into_string(ll)}&z={z}&maptype={maptype}'
    map_request = f"{server_address_maps}{ll_spn}&apikey={api_key_maps}&theme={theme}"

    if pt != []:
        map_request += '&pt=' + '~'.join(list(map(lambda x: f'{x[0]},{x[1]},pm2rdm', pt)))

    return map_request


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for getting and saving image
def save_image(url, file_name=MAP_FILE):
    response = requests.get(url)

    if not response:
        return None

    with open(file_name, "wb") as file:
        file.write(response.content)

    return file_name


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for sending image to alice skill
def send_image(image_name):
    with open(image_name, "rb") as image_file:
        files = {
            "file": image_file
        }

        headers = {'Authorization': f"OAuth {YANDEX_TOKEN}"}
        resp = requests.post(f'https://dialogs.yandex.net/api/v1/skills/{SKILL_ID}/images',
                             files=files, headers=headers)

    return resp.json()['image']['id']


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for doing all process about creating image
def all_for_picture(place, size, pt=[], theme='light', maptype='map', user_id=None):
    pt = list(map(lambda x: get_coordinates(x), pt))

    url = make_image_url(get_coordinates(place), z=size, theme=theme, maptype=maptype, pt=pt)

    db_sess = db_session.create_session()

    map_id = None
    for stat in db_sess.query(Statistics).filter(Statistics.url == url):
        map_id = stat.picture_id
        break

    if map_id is None:
        file_name = save_image(url, MAP_FILE)
        map_id = send_image(file_name)

    stat = Statistics()
    if user_id is not None:
        stat.user_id = user_id
    stat.url = url
    stat.full_name_place = get_full_name(place)
    stat.picture_id = map_id
    db_sess.add(stat)
    db_sess.commit()

    return map_id


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for clearing the data base
def clear_db():
    db_sess = db_session.create_session()

    for line in db_sess.query(Statistics):
        db_sess.delete(line)

    db_sess.commit()


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# If file was used not like module clear data base
if __name__ == '__main__':
    db_session.global_init('db/statistics.db')
    clear_db()
    # Пример запроса:
    # print(all_for_picture('Москва', 9, ["Метро Чертановское",  "Метро Чистые пруды"]))

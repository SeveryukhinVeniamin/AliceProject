import requests

server_address_geocode = 'http://geocode-maps.yandex.ru/1.x/?'
api_key_geocode = '8013b162-6b42-4997-9691-77b7074026e0'
server_address_maps = 'https://static-maps.yandex.ru/v1?'
api_key_maps = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
MAP_FILE = "map.png"
YANDEX_TOKEN = "y0__xC_lMXPBRij9xMgzezK-xaKlt5OX2HisrB0C4VM6L23kucj1A"
SKILL_ID = "4d9bc848-79e1-4e46-a915-0ba0822d0ebd"  # !Пока ссылается на ДРУГОЙ скил, но служит для проверки!


def get_coordinates(name):
    geocoder_request = f'{server_address_geocode}apikey={api_key_geocode}&geocode={name}&format=json'
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        toponym_coodrinates = toponym["Point"]["pos"]
        return list(map(float, toponym_coodrinates.split(' ')))
    else:
        return None


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


def get_location(coordinates, location):
    geocoder_request = (f'{server_address_geocode}apikey={api_key_geocode}' +
                        f'&geocode={coord_list_into_string(coordinates)}&format=json&kind={location}')
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        return toponym_address
    else:
        return None


def coord_list_into_string(coordinates):
    return str(coordinates[0]) + ',' + str(coordinates[1])


def make_image_url(ll, z, theme='light', maptype='map', pt=[]):
    ll_spn = f'll={coord_list_into_string(ll)}&z={z}&maptype={maptype}'

    map_request = f"{server_address_maps}{ll_spn}&apikey={api_key_maps}&theme={theme}"
    if pt != []:
        map_request += '&pt=' + '~'.join(list(map(lambda x: f'{x[0]},{x[1]},pm2rdm', pt)))
    return map_request


def save_image(url, file_name=MAP_FILE):
    response = requests.get(url)

    if not response:
        return None

    with open(file_name, "wb") as file:
        file.write(response.content)
    return file_name


def send_image(image_name):
    with open(image_name, "rb") as image_file:
        files = {
            "file": image_file
        }
        headers = {'Authorization': f"OAuth {YANDEX_TOKEN}"}
        resp = requests.post(f'https://dialogs.yandex.net/api/v1/skills/{SKILL_ID}/images',
                             files=files, headers=headers)
    return resp.json()['image']['id']


def all_for_picture(place, size, pt=[], theme='light', maptype='map'):
    pt = list(map(lambda x: get_coordinates(x), pt))
    url = make_image_url(get_coordinates(place), z=size, theme=theme, maptype=maptype, pt=pt)
    file_name = save_image(url)
    map_id = send_image(file_name)
    return map_id

# Пример запроса:
# id_image = all_for_picture('Москва', 10, ["Метро Чертановское",  "Метро Чистые пруды"]))

import requests

server_address_geocode = 'http://geocode-maps.yandex.ru/1.x/?'
api_key_geocode = '8013b162-6b42-4997-9691-77b7074026e0'
server_address_maps = 'https://static-maps.yandex.ru/v1?'
api_key_maps = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
MAP_FILE = "map.png"
YANDEX_TOKEN = "y0__xC_lMXPBRij9xMgzezK-xaKlt5OX2HisrB0C4VM6L23kucj1A"
SKILL_ID = "1087850d-a5d5-45c5-96da-dfcef7cf0448"  # !Пока ссылается на ДРУГОЙ скил, но служит для проверки!


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


def save_image(ll, z, theme='light', maptype='map', pt=[]):
    ll_spn = f'll={coord_list_into_string(ll)}&z={z}&maptype={maptype}'

    map_request = f"{server_address_maps}{ll_spn}&apikey={api_key_maps}&theme={theme}"
    if pt != []:
        map_request += '&pt=' + '~'.join(list(map(lambda x: f'{x[0]},{x[1]},pm2rdm', pt)))
    response = requests.get(map_request)

    if not response:
        return None

    with open(MAP_FILE, "wb") as file:
        file.write(response.content)
    return MAP_FILE


def send_image(image_name):
    with open(image_name, "rb") as image_file:
        files = {
            "file": image_file
        }
        headers = {'Authorization': f"OAuth {YANDEX_TOKEN}"}
        resp = requests.post(f'https://dialogs.yandex.net/api/v1/skills/{SKILL_ID}/images',
                             files=files, headers=headers)
    return resp.json()['image']['id']

# Пример запроса:
# id_image = send_image(save_image(get_coordinates('Москва'), 10, theme='dark', maptype='transit', pt=[get_coordinates('Москва сити')]))

import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from constants import CAR_BRANDS_MODELS
from requests import RequestException, Session, request
import math
from bs4 import BeautifulSoup
import threading

# 30 seconds for OLX Scrapping
def initialize_olx_car_data():
    def get_category_ids (brand_name):
        brand_dict = {
            "audi": 182,
            "bmw": 183,
            "chevrolet": 184,
            "chrysler": 185,
            "citroen": 186,
            "daewoo": 187,
            "fiat": 188,
            "ford": 189,
            "honda": 190,
            "hyundai": 191,
            "kia": 192,
            "mazda": 194,
            "mercedes": 195,
            "mitsubishi": 196,
            "nissan": 197,
            "opel": 198,
            "peugeot": 199,
            "renault": 200,
            "saab": 201,
            "seat": 202,
            "skoda": 203,
            "subaru": 204,
            "suzuki": 205,
            "toyota": 206,
            "volkswagen": 207,
            "volvo": 208,
            "rover": 296,
            "abarth": 2533,
            "acura": 2534,
            "mini": 2554,
            "rolls-royce": 2556,
            "aixam": 772,
            "dodge": 770,
            "dacia": 742,
            "smart": 760,
            "land-rover": 762,
            "lexus": 767,
            "jaguar": 769,
            "jeep": 768,
            "lada": 771,
            "ssangyong": 823,
            "hummer": 827,
            "porsche": 829,
            "infiniti": 831,
            "alfa-romeo": 181,
            "tesla": 1638,
            "aro": 2535,
            "aston-martin": 2536,
            "bentley": 2539,
            "bugatti": 2540,
            "ferrari": 2543,
            "lamborghini": 2546,
            "maserati": 2550,
            "cadillac": 841,
            "daihatsu": 837
        }
        return brand_dict[brand_name]

    def scrape_olx_autos_for_a_brand_and_model(brand, model):

        target_url = "https://www.olx.ro/api/v1/offers/"
        category_id = get_category_ids(brand)
        if category_id is not None:
            query_params = {
            'offset': '0',
            'limit': '40',
            'category_id': get_category_ids(brand),
            'currency': 'EUR',
            'filter_enum_model[0]': model,
            'sl': '184ae48a052x1b738825'
            }   
            try:
                session = get_olx_session()
                response = session.get(url=target_url, params=query_params)
                response.raise_for_status()

                data = response.json()
                
                total_entitites = data['metadata']['total_elements']
                # promoted = data['metadata']['promoted']
                encountered_ids = set()
                cars = []

                cars, encountered_ids = parse_olx_car_data(encountered_ids ,cars, data['data'])
                
                remaining_cars_number = total_entitites - 40
                current_offset = 0
                while remaining_cars_number > 0:
                    remaining_cars_number -= 40
                    current_offset += 40
                    query_params['offset'] = str(current_offset)

                    try:
                        response = session.get(target_url, query_params)
                        response.raise_for_status()
                        data = response.json()
                        cars, encountered_ids = parse_olx_car_data(encountered_ids ,cars, data['data'])

                    except RequestException as e:
                        print(f"An error occurred: {e}")
                        return 0

                return cars
            
            except RequestException as e:
                print(f"An error occurred: {e}")
                return 0 
        else:
            return []

    def parse_olx_car_data(old_encountered_ids ,oldcars, data):
        cars = oldcars
        encountered_ids = old_encountered_ids.copy()

        for item in data: 
            id = item.get('id', '')
            if(id == '' or id in encountered_ids):
                continue
            
            # Exclude Autovit vehicles since they will be added in the other scrapper
            partner = item.get('partner', '')
            if partner != '' and partner != None:
                code = partner.get('code', '')
                if code != '' and code == 'autovit':
                    continue

            title = item.get('title', '')
            url = item.get('url', '')
            description = item.get('description', '')
            city = item.get('location', {}).get('city', {}).get('name', '')
            region = item.get('location', {}).get('region', {}).get('name', '')
            created_time = item.get('created_time', '')
            business = item.get('business', False)
            photo = ''

            photoEntries = item.get('photos', '')
            if(photoEntries != '', len(photoEntries) > 0):
                link = photoEntries[0].get('link', '')
                if(link != ''):
                    photo = link.replace(';s={width}x{height}', '')

            
            # Initialize price and year to None in case they are not found in params
            price = None
            vin = None
            year = None
            mileage = None
            enginesize = None
            engine_power = None
            fuel_type = None
            car_body = None
            color = None
            door_count = None
            use_state = None
            gearbox = None
            steering_wheel = None

            for param in item.get('params', []):
                if param.get('key') == 'price':
                    price = param.get('value', {}).get('value', '')
                elif param.get('key') == 'year':
                    year = param.get('value', {}).get('key', '')  
                elif param.get('key') == 'rulaj_pana':
                    mileage = param.get('value', {}).get('key', '')
                elif param.get('key') == 'enginesize':
                    enginesize = param.get('value', {}).get('key', '')
                elif param.get('key') == 'engine_power':
                    engine_power = param.get('value', {}).get('key', '')
                elif param.get('key') == 'petrol':
                    fuel_type = param.get('value', {}).get('key', '')
                elif param.get('key') == 'vin':
                    vin = param.get('value', {}).get('key', '')
                elif param.get('key') == 'car_body':
                    car_body = param.get('value', {}).get('key', '')
                elif param.get('key') == 'color':
                    color = param.get('value', {}).get('key', '')
                elif param.get('key') == 'door_count':
                    door_count = param.get('value', {}).get('key', '')
                elif param.get('key') == 'state':
                    use_state = param.get('value', {}).get('key', '')
                elif param.get('key') == 'gearbox':
                    gearbox = param.get('value', {}).get('key', '')
                elif param.get('key') == 'steering_wheel':
                    steering_wheel = param.get('value', {}).get('key', '')

            car = {
                'car_id': f'olx-{id}',
                'title': title,
                'url': url,
                'price': int(price) if price is not None else None,
                'vin': vin,
                'year': int(year) if year is not None else None,
                'mileage': int(mileage) if mileage is not None else None,
                'description': description,
                'city': city,
                'region': region,
                'created_time': created_time,
                'photo': photo,
                'enginesize': int(enginesize) if enginesize is not None else None,
                'engine_power': int(engine_power) if engine_power is not None else None,
                'fuel_type': fuel_type,
                'car_body': car_body,
                'color': color,
                'door_count': int(door_count) if door_count is not None else None,
                'use_state': use_state,
                'gearbox': gearbox,
                'steering_wheel': steering_wheel,
                'business': business,
                'site_source': 'RO-OLX'
            }

            encountered_ids.add(id)
            cars.append(car)
        return cars, encountered_ids
    olx_car_data = {}
    olx_brand_model_data = {}

    def get_olx_car_data(brand, model):
        response = scrape_olx_autos_for_a_brand_and_model(brand["olxBrand"], model[0])
        if(type(response) != int):
            olx_car_data[(brand['brand'], model[1])].extend(response)
            olx_brand_model_data[brand['brand']]["models"][model[1]][1] += len(response)
            print(f"Got {len(response)} entities for OLX: {brand['brand']}: {model[1]}")

    # Thread-local storage for the Autovit session
    olx_session_local = threading.local()

    def get_olx_session():
        if not hasattr(olx_session_local, "session"):
            olx_session_local.session = Session()
        return olx_session_local.session

    with ThreadPoolExecutor(max_workers=20) as executor:
        for brand in CAR_BRANDS_MODELS:
            olx_brand_model_data[brand["brand"]] = {"brand": brand["brand"], "models": {}}
            for model in brand["models"]:
                olx_car_data[(brand["brand"], model[1])] = []
                olx_brand_model_data[brand["brand"]]["models"][model[1]] = [model[1], 0] # name, total count
                if model[0] != "": # Check if olx name is not empty
                    executor.submit(get_olx_car_data, brand, model)
    try:
        with open('./olx_cars.json', 'w') as f:
            # Convert tuple keys to string keys
            str_dict_data = {str(key): value for key, value in olx_car_data.items()}
            json.dump(str_dict_data, f)
        with open('./olx_cars_brands_models.json', 'w') as f:
            # First transform the models dict into an array
            for brand in CAR_BRANDS_MODELS:
                olx_brand_model_data[brand["brand"]]["models"] = list(olx_brand_model_data[brand["brand"]]["models"].values())
            # Then transform the whole car brand models dict into an array
            values_list = list(olx_brand_model_data.values())
            json_str = json.dumps(values_list)
            f.write(json_str)
        # If successful, create a success.txt file
        open('./olx_success.txt', 'w').close()
    except Exception as e:
            # If an error occurred, write the error message to error.txt
            with open('./olx_error.txt', 'w') as f:
                f.write(str(e))


import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from constants import CAR_BRANDS_MODELS
from requests import RequestException, Session, request
import math
from bs4 import BeautifulSoup
import threading

# CAR_BRANDS_MODELS Model: [olxName, name, autovitName]

# 120 minutes for Autovit Scrapping
def initialize_autovit_car_data():
    def translate_service(type, text):
        text = ''.join(text.split()) # Removes spaces, tabs, newlines
        if type == 'use_state':
            if text == 'Second hand' or text == 'Secondhand':
                return 'used'
            if text == 'Nou':
                return 'new'
        if type == 'gearbox':
            if text == 'Automata':
                return 'automatic'
            if text == 'Manuala':
                return 'manual'
        if type == 'car_body':
            if text == 'Cabrio':
                return 'cabrio'
            if text == 'Combi':
                return 'combi'
            if text == 'Compacta':
                return 'berlina'
            if text == 'Coupe':
                return 'coupe'
            if text == 'Masina de oras':
                return 'hatchback'
            if text == 'Masina mica':
                return 'mini'
            if text == 'Monovolum':
                return 'minivan'
            if text == 'Sedan':
                return 'berlina'
        if type == 'color':
            if text == 'Alb':
                return 'white'
            if text == 'Portocaliu':
                return 'orange'
            if text == 'Albastru':
                return 'blue'
            if text == 'Alte culori':
                return 'other'
            if text == 'Argint':
                return 'silver'
            if text == 'Bej':
                return 'belge'
            if text == 'Galben/Auriu':
                return 'yellow/gold'
            if text == 'Gri':
                return 'gray'
            if text == 'Maro':
                return 'brown'
            if text == 'Negru':
                return 'black'
            if text == 'Rosu':
                return 'red'
            if text == 'Verde':
                return 'green'
        return text

    def scrape_autovit_autos_for_a_brand_and_model(brand, model):
        target_url = f"https://www.autovit.ro/graphql?operationName=listingScreen&variables=%7B%22after%22%3Anull%2C%22click2BuyExperimentId%22%3A%22%22%2C%22click2BuyExperimentVariant%22%3A%22%22%2C%22experiments%22%3A%5B%7B%22key%22%3A%22MCTA-900%22%2C%22variant%22%3A%22a%22%7D%2C%7B%22key%22%3A%22MCTA-1028%22%2C%22variant%22%3A%22a%22%7D%2C%7B%22key%22%3A%22MCTA-1029%22%2C%22variant%22%3A%22a%22%7D%5D%2C%22filters%22%3A%5B%7B%22name%22%3A%22filter_enum_make%22%2C%22value%22%3A%22{brand}%22%7D%2C%7B%22name%22%3A%22filter_enum_model%22%2C%22value%22%3A%22{model}%22%7D%2C%7B%22name%22%3A%22category_id%22%2C%22value%22%3A%2229%22%7D%5D%2C%22includeClick2Buy%22%3Afalse%2C%22includeFiltersCounters%22%3Afalse%2C%22includePriceEvaluation%22%3Atrue%2C%22includePromotedAds%22%3Afalse%2C%22includeRatings%22%3Afalse%2C%22includeSortOptions%22%3Afalse%2C%22maxAge%22%3A60%2C%22page%22%3A1%2C%22parameters%22%3A%5B%22make%22%2C%22vat%22%2C%22fuel_type%22%2C%22mileage%22%2C%22engine_capacity%22%2C%22engine_code%22%2C%22engine_power%22%2C%22first_registration_year%22%2C%22model%22%2C%22version%22%2C%22year%22%5D%2C%22searchTerms%22%3Anull%7D&extensions=%7B%22persistedQuery%22%3A%7B%22sha256Hash%22%3A%2250e3cc18dfb6ea5468e45630696e2e5bd35e7bc8acc7555bc32419ddececae32%22%2C%22version%22%3A1%7D%7D"
        session = get_autovit_session()
        try:
            response = session.get(target_url)
            response.raise_for_status()
            jsn = response.json()

            data = jsn['data']['advertSearch']
            total_entitites = data['totalCount']
            encountered_ids = set()
            cars = []
            
            cars, encountered_ids = parse_autovit_car_data(encountered_ids ,cars, data['edges'])
            number_of_pages = math.ceil(total_entitites / 32)      
            for i in range(2, number_of_pages + 1):  
                target_url = f"https://www.autovit.ro/graphql?operationName=listingScreen&variables=%7B%22after%22%3Anull%2C%22click2BuyExperimentId%22%3A%22%22%2C%22click2BuyExperimentVariant%22%3A%22%22%2C%22experiments%22%3A%5B%7B%22key%22%3A%22MCTA-900%22%2C%22variant%22%3A%22a%22%7D%2C%7B%22key%22%3A%22MCTA-1028%22%2C%22variant%22%3A%22a%22%7D%2C%7B%22key%22%3A%22MCTA-1029%22%2C%22variant%22%3A%22a%22%7D%5D%2C%22filters%22%3A%5B%7B%22name%22%3A%22filter_enum_make%22%2C%22value%22%3A%22{brand}%22%7D%2C%7B%22name%22%3A%22filter_enum_model%22%2C%22value%22%3A%22{model}%22%7D%2C%7B%22name%22%3A%22category_id%22%2C%22value%22%3A%2229%22%7D%5D%2C%22includeClick2Buy%22%3Afalse%2C%22includeFiltersCounters%22%3Afalse%2C%22includePriceEvaluation%22%3Atrue%2C%22includePromotedAds%22%3Afalse%2C%22includeRatings%22%3Afalse%2C%22includeSortOptions%22%3Afalse%2C%22maxAge%22%3A60%2C%22page%22%3A{i}%2C%22parameters%22%3A%5B%22make%22%2C%22vat%22%2C%22fuel_type%22%2C%22mileage%22%2C%22engine_capacity%22%2C%22engine_code%22%2C%22engine_power%22%2C%22first_registration_year%22%2C%22model%22%2C%22version%22%2C%22year%22%5D%2C%22searchTerms%22%3Anull%7D&extensions=%7B%22persistedQuery%22%3A%7B%22sha256Hash%22%3A%2250e3cc18dfb6ea5468e45630696e2e5bd35e7bc8acc7555bc32419ddececae32%22%2C%22version%22%3A1%7D%7D"
                
                try:
                    response = session.get(target_url)
                    response.raise_for_status()
                    jsn = response.json()
                    cars, encountered_ids = parse_autovit_car_data(encountered_ids, cars, jsn['data']['advertSearch']['edges'])
                except RequestException as e:
                    print(f"An error occurred: {e}")
                    return 0

            return cars
            
        except RequestException as e:
            print(f"An error occurred: {e}")
            return 0
    
    def parse_autovit_car_data(old_encountered_ids ,oldcars, data):
        cars = oldcars
        encountered_ids = old_encountered_ids.copy()

        for item in data: 
            
            node_data = item.get('node', '')
            if node_data == '':
                continue

            id = node_data.get('id', '')
            if(id == '' or id in encountered_ids):
                continue

            title = node_data.get('title', '')
            url = node_data.get('url', '')

            city = node_data.get('location', {}).get('city', {}).get('name', '')
            region = node_data.get('location', {}).get('region', {}).get('name', '')

            created_time = node_data.get('createdAt', '')
            photo_node = node_data.get('thumbnail')
            if photo_node is not None:
                photo = photo_node.get('x2', '')
            price = node_data.get('price', {}).get('amount', {}).get('units', '')

            vin = ''
            year = None
            mileage = None
            enginesize = None
            engine_power = None
            fuel_type = None
            car_body = ''
            color = ''
            door_count = ''
            use_state = ''
            gearbox = ''
            description = ''
            business = True
            steering_wheel = 'lhd'

            for param in node_data.get('parameters', []):
                if param.get('key') == 'year':
                    year = param.get('value', '')  
                elif param.get('key') == 'mileage':
                    mileage = param.get('value', '')  
                elif param.get('key') == 'engine_capacity':
                    enginesize = param.get('value', '') 
                elif param.get('key') == 'engine_power':
                    engine_power = param.get('value', '') 
                elif param.get('key') == 'fuel_type':
                    fuel_type = param.get('value', '') 

            try:
                # For the rest of the params we have to use beautiful soup to get the url
                response = request.get(target_url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                
                car_body_span = soup.find('span', text='Tip Caroserie') 
                if car_body_span:
                    car_body_link = car_body_span.find_next_sibling('div').find('a')
                    if car_body_link:
                        car_body = translate_service('car_body', car_body_link.text)
    
                color_span = soup.find('span', text='Culoare') 
                if color_span:
                    color_link = color_span.find_next_sibling('div').find('a')
                    if color_link:
                        color = translate_service('color', color_link.text)
                
                door_count_span = soup.find('span', text='Numar de portiere') 
                if door_count_span:
                    door_count_link = door_count_span.find_next_sibling('div').find('a')
                    if door_count_link:
                        door_count = door_count_link.text

                state_span = soup.find('span', text='Stare') 
                if state_span:
                    state_link = state_span.find_next_sibling('div').find('a')
                    if state_link:
                        use_state = translate_service('use_state', state_link.text)

                gearbox_span = soup.find('span', text='Cutie de viteze') 
                if gearbox_span:
                    gearbox_link = gearbox_span.find_next_sibling('div').find('a')
                    if gearbox_link:
                        gearbox = translate_service('gearbox', gearbox_link.text)

                description_div = soup.find('div', {'class': 'offer-description__description'})
                if description_div:
                    description = description_div.text

                business_span = soup.find('span', text='Oferit de') 
                if business_span:
                    business_link = state_span.find_next_sibling('div').find('a')
                    if business_link:
                        if business_link.text == 'Proprietar':
                            business = False
                        else:
                            business = True
            except RequestException as e:
                print(f"An error occurred from autovit beautifulsoup: {e}")
            car = {
                'car_id': f'autovit-{id}',
                'title': title,
                'url': url,
                'price': int(price) if price is not None  and price != '' else None,
                'vin': vin,
                'year': int(year) if year is not None  and year != '' else None,
                'mileage': int(mileage) if mileage is not None  and mileage != '' else None,
                'description': description,
                'city': city,
                'region': region,
                'created_time': created_time,
                'photo': photo,
                'enginesize': int(enginesize) if enginesize is not None  and enginesize != '' else None,
                'engine_power': int(engine_power) if engine_power is not None  and engine_power != '' else None,
                'fuel_type': fuel_type,
                'car_body': car_body,
                'color': color,
                'door_count': int(door_count) if door_count is not None and door_count != '' else None,
                'use_state': use_state,
                'gearbox': gearbox,
                'steering_wheel': steering_wheel,
                'business': business,
                'site_source': 'RO-AUTOVIT'
            }

            encountered_ids.add(id)
            cars.append(car)
        return cars, encountered_ids

    autovit_car_data = {}
    autovit_brand_model_data = {}

    # Thread-local storage for the Autovit session
    autovit_session_local = threading.local()

    def get_autovit_session():
        if not hasattr(autovit_session_local, "session"):
            autovit_session_local.session = Session()
        return autovit_session_local.session

    def get_autovit_car_data(brand, model_name, model_big_name):
        response = scrape_autovit_autos_for_a_brand_and_model(brand["olxBrand"], model_name)
        if(type(response) != int):
            autovit_car_data[(brand['brand'], model_big_name)].extend(response)
            autovit_brand_model_data[brand['brand']]["models"][model_big_name][1] += len(response)
            print(f"Got {len(response)} entities for Autovit: {brand['brand']}: {model_big_name}")

    with ThreadPoolExecutor(max_workers=20) as executor:
        for brand in CAR_BRANDS_MODELS:
            autovit_brand_model_data[brand["brand"]] = {"brand": brand["brand"], "models": {}}
            # Get a model list from autovit instead of having to write constants
            target_url = f"https://www.autovit.ro/graphql?operationName=listingScreen&variables=%7B%22after%22%3Anull%2C%22click2BuyExperimentId%22%3A%22%22%2C%22click2BuyExperimentVariant%22%3A%22%22%2C%22experiments%22%3A%5B%7B%22key%22%3A%22MCTA-900%22%2C%22variant%22%3A%22a%22%7D%2C%7B%22key%22%3A%22MCTA-1028%22%2C%22variant%22%3A%22a%22%7D%2C%7B%22key%22%3A%22MCTA-1029%22%2C%22variant%22%3A%22a%22%7D%5D%2C%22filters%22%3A%5B%7B%22name%22%3A%22filter_enum_make%22%2C%22value%22%3A%22{brand['olxBrand']}%22%7D%2C%7B%22name%22%3A%22category_id%22%2C%22value%22%3A%2229%22%7D%2C%7B%22name%22%3A%22new_used%22%2C%22value%22%3A%22used%22%7D%5D%2C%22includeClick2Buy%22%3Afalse%2C%22includeFiltersCounters%22%3Afalse%2C%22includePriceEvaluation%22%3Atrue%2C%22includePromotedAds%22%3Afalse%2C%22includeRatings%22%3Afalse%2C%22includeSortOptions%22%3Afalse%2C%22maxAge%22%3A60%2C%22page%22%3A1%2C%22parameters%22%3A%5B%22make%22%2C%22vat%22%2C%22fuel_type%22%2C%22mileage%22%2C%22engine_capacity%22%2C%22engine_code%22%2C%22engine_power%22%2C%22first_registration_year%22%2C%22model%22%2C%22version%22%2C%22year%22%5D%2C%22searchTerms%22%3Anull%7D&extensions=%7B%22persistedQuery%22%3A%7B%22sha256Hash%22%3A%2250e3cc18dfb6ea5468e45630696e2e5bd35e7bc8acc7555bc32419ddececae32%22%2C%22version%22%3A1%7D%7D"
            try:
                session = get_autovit_session()
                response = session.get(target_url)
                response.raise_for_status()
                data = response.json()

                models_links_data = data.get('data', {}).get('advertSearch', {}).get('alternativeLinks', [])
                if len(models_links_data) == 0:
                    print("Could not get models from autovit: " + str(brand['brand']))
                else:
                    models_links = models_links_data[0].get('links', [])
                    print("Got " + str(len(models_links)) + " Autovit models for " + brand['brand'])

                    for model in models_links:
                        parsed_url = urlparse(model.get('url', ''))
                        model_name = parsed_url.path.split('/')[-1] # Get only the model name
                        model_big_name = model.get('title', '')
                        
                        car_string_without_keyword = model_big_name.replace(brand['brand'], "") # Replace the known keyword brand with an empty string
                        model_big_name = car_string_without_keyword.strip() # Remove any leading or trailing whitespaces

                        autovit_car_data[(brand["brand"], model_big_name)] = []
                        autovit_brand_model_data[brand["brand"]]["models"][model_big_name] = [model_big_name, 0] # name, total count
                        executor.submit(get_autovit_car_data, brand, model_name, model_big_name)
                
            except RequestException as e:
                print(f"An error occurred at grabbing the models from autovit: {e}")
                
    
    try:
        with open('./autovit_cars.json', 'w') as f:
            # Convert tuple keys to string keys
            str_dict_data = {str(key): value for key, value in autovit_car_data.items()}
            json.dump(str_dict_data, f)
        with open('./autovit_cars_brands_models.json', 'w') as f:
            # First transform the models dict into an array
            for brand in CAR_BRANDS_MODELS:
                autovit_brand_model_data[brand["brand"]]["models"] = list(autovit_brand_model_data[brand["brand"]]["models"].values())
            # Then transform the whole car brand models dict into an array
            values_list = list(autovit_brand_model_data.values())
            json_str = json.dumps(values_list)
            f.write(json_str)
        # If successful, create a success.txt file
        open('./autovit_success.txt', 'w').close()
    except Exception as e:
            # If an error occurred, write the error message to error.txt
            with open('./autovit_error.txt', 'w') as f:
                f.write(str(e))
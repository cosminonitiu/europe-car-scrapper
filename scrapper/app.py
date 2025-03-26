import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from ast import literal_eval
import json
#import redis
#from pympler.asizeof import asizeof

from helpers.logger import logger
from helpers.helperfunctions import get_car_options_dictionary, get_part_of_array, compare_old_params, specific_filter_car_data, specific_sort
from evaluator_service.main import gpt_evaluate
from scrapper_service.constants import CAR_BRANDS_MODELS, SITE_SOURCES
from classes import AutoCleanDict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
cors = CORS(app, origins='http://localhost:4200')

### REDIS NOTES
# 1 car storage -> 35 KB of Redis Memory (476 cars per 1$ at 15$ a month, 649 cars at 22$, 1058 at 27$)
# 1 car storage -> 4 KB of Python Global Memory
### REDIS NOTES

#r = redis.Redis(
  #host='redis-10617.c55.eu-central-1-1.ec2.cloud.redislabs.com',
  #port=10617,
  #password='YzXC15Ik0LvIX06fJYGbWIGOcoes60vD')
### REDIS SIMULATOR USING SERVER MEMORY ###

# Cache with a cleanup function every minute for data keys older than 3 minutes
sim_redis_cache = AutoCleanDict()
main_car_data = {}
cars_brands_models_data = {}

# Data store for keeping track of AI Priced and Car Vertical Data so we don't buy them twice for the same car
ai_priced_cars = {}

def midnight_check():
    global ai_priced_cars
    global main_car_data
    global cars_brands_models_data
    # Check for new scrapped data
    if os.path.isfile('success.txt'):
        with open('./cars.json', 'r') as f:
            str_dict_data = json.load(f)
        with open('./cars_brands_models.json', 'r') as f:
            cars_brands_models_data = json.load(f)
        # Convert the string keys back to tuple keys
        main_car_data = {literal_eval(key): value for key, value in str_dict_data.items()}
        # os.remove('success.txt')

    if os.path.isfile('error.txt'):
        print('error.txt has been created.')

    # Rollup the old priced / verified cars by GPT or Car Vertical and Eliminate 30 days or older cars / buyers
    root_path = './priced'
    result = {}
    with open('./priced/priced.json', 'r') as f:
        result = json.load(f)

    # Function to check if a date is older than 30 days
    def is_older_than_30_days(date_str):
        date_format = '%Y:%m:%d'
        date_obj = datetime.strptime(date_str, date_format)
        return datetime.today() > date_obj + timedelta(days=30)

    # Iterate through the brand folders
    for brand in os.listdir(root_path):
        brand_path = os.path.join(root_path, brand)

        if os.path.isdir(brand_path):
            # Check if the brand exists in the result
            if brand not in result:
                result[brand] = {}

            # Iterate through the model folders
            for model in os.listdir(brand_path):
                model_path = os.path.join(brand_path, model)

                if os.path.isdir(model_path):
                    # Check if the model exists in the result
                    if model not in result[brand]:
                        result[brand][model] = {}

                    # Iterate through the JSON files
                    for file in os.listdir(model_path):
                        file_path = os.path.join(model_path, file)

                        if file_path.endswith('.json'):
                            with open(file_path, 'r') as f:
                                car_data = json.load(f)

                            # Check if car_id exists
                            car_id = car_data['car_id']
                            existing_car = result[brand][model].get(car_id)

                            # If car_id exists, append the user; else, insert the entire car data
                            if existing_car:
                                existing_car['users'].extend(car_data['users'])
                            else:
                                result[brand][model][car_id] = car_data

                            # Remove the JSON file after processing
                            os.remove(file_path)

            # Check date_purchased for cars and users, and remove if older than 30 days
            for model, cars in result[brand].items():
                for car_id, car in list(cars.items()):
                    if is_older_than_30_days(car['date_purchased']):
                        del result[brand][model][car_id]
                    else:
                        car['users'] = [user for user in car['users'] if not is_older_than_30_days(user['date_purchased'])]

    ai_priced_cars = result
    with open('./priced/priced.json', 'w') as f:
        json.dump(result, f)

# Run it at start of the server
midnight_check()

scheduler = BackgroundScheduler()
# calculate the next midnight from now
now = datetime.now()
start_date = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
scheduler.add_job(midnight_check, 'interval', days=1, start_date=start_date)
scheduler.start()

@app.route('/car_brands_models', methods=['GET'])
def car_brands_models_endpoint():
    if request.method == 'GET':
        return(jsonify(cars_brands_models_data))

@app.route('/site_sources', methods=['GET'])
def site_sources_endpoint():
    if request.method == 'GET':
        return(jsonify(SITE_SOURCES))
    
@app.route('/evaluate', methods=['GET'])
def evaluate_endpoint():
    global ai_priced_cars
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        car_id = request.args.get('car_id')
        brand = request.args.get('brand')
        model = request.args.get('model')
        title = request.args.get('title')
        year = request.args.get('year')
        country = request.args.get('country')
        mileage = request.args.get('mileage')
        description = request.args.get('description')
        engine_size = request.args.get('engine_size')
        power = request.args.get('power')
        fuel_type = request.args.get('fuel_type')
        body = request.args.get('body')
        gear_box = request.args.get('gear_box')
        steering_wheel = request.args.get('steering_wheel')
        
        dict_brand = ai_priced_cars.get(brand, '')
        dict_model = ''
        dict_car = {}
        new_uid = False
        if dict_brand != '':
            dict_model = dict_brand.get(model, '')
            if dict_model != '':
                dict_car = ai_priced_cars[brand][model].get(car_id, '')
                if dict_car == '':
                    new_uid = True
            else:
                ai_priced_cars[brand][model] = {}
                new_uid = True
        else:
            ai_priced_cars[brand] = {}
            ai_priced_cars[brand][model] = {}
            new_uid = True
        
        # Each car will have the following
        # id: ID of the car
        # updated_date: Date at the last pricing, over 30 days means automatic removal at midnight or if any of the users has more than 10 days left, automatic reprice
        # users: Array of user: {user_id: string, date_purchased: datestring} -> Each user purchase lasts for 30 days
        
        res = {}
        if new_uid == True:
            res = gpt_evaluate(car_id, brand,model,title,year,country,mileage,description,engine_size,power,fuel_type,body,gear_box, steering_wheel)
        else:
            res = ai_priced_cars[brand][model][car_id]

            # Check if the latest update is 15 days before this purchase, and if so, rebuy the call
            date_to_check = datetime.strptime(res['date_purchased'], '%Y:%m:%d')
            today_date = datetime.today()

            if today_date >= date_to_check + timedelta(days=15):
                previous_users = res['users']
                res = gpt_evaluate(car_id, brand,model,title,year,country,mileage,description,engine_size,power,fuel_type,body,gear_box, steering_wheel)
                res['users'] = previous_users

        res['users'].append({
            "user_id": user_id,
            "date_purchased": datetime.today().strftime('%Y:%m:%d')
        })

        # Save the data in the dictionary and replicate it in the temporary file storage to be rolled-up / and act as backup
        ai_priced_cars[brand][model][car_id] = res

        # Check first if the directory is already there
        path = f'./priced/{brand}/{model}/'
        os.makedirs(path, exist_ok=True)

        filename = f'{path}/{car_id}.json'
        with open(filename, 'w') as f:
            json.dump(res, f)

        return(jsonify(res))

@app.route('/evaluated', methods=['GET'])
def evaluated_endpoint():
    global ai_priced_cars
    if request.method == 'GET':
        brand = request.args.get('brand')
        model = request.args.get('model')

        models = ai_priced_cars.get(brand, '')
        if models != '':
            cars = models.get(model, '')
            if cars != '':
                return jsonify(cars)
    return jsonify([])

@app.route('/main_car_data', methods=['GET'])
def main_car_data_endpoint():
    if request.method == 'GET':
        global main_car_data
        global sim_redis_cache

        user_id = request.args.get('user_id')
        brand = request.args.get('brand')
        model = request.args.get('model')
        skip = request.args.get('skip')
        take = request.args.get('take')
        sort_col = request.args.get('sort_col')
        sort_dir = request.args.get('sort_dir')

        # Redis caching logic, if the user only adds another filter and not removes one, filter the already cached list
        params = {key: request.args.get(key) for key in request.args}

        ### Redis simulator
        if user_id in sim_redis_cache:
            filters_and_data = sim_redis_cache.get(user_id)
            will_use_cached_data = compare_old_params(filters_and_data['params'], params)
            if will_use_cached_data[0] == True:
                update_params = will_use_cached_data[1]
                cached_car_data = filters_and_data['car_data']
                new_car_data = specific_filter_car_data(cached_car_data, update_params, **params)

                # Redis store this filtering and options without sorting the data
                if len(update_params) > 0:
                    updated_redis_dict_for_user = {
                        'params': params,
                        'car_data': new_car_data,
                        'car_options': filters_and_data['car_options']
                    }
                    sim_redis_cache[user_id] = updated_redis_dict_for_user
                    # Print memory usage
                    # print('Size of main_car_data:', asizeof(main_car_data), 'bytes')
                    # print('Size of cached car data:', asizeof(sim_redis_cache), 'bytes')
                sorted_car_data = specific_sort(new_car_data, sort_col, sort_dir)
                response = {
                    'entities': get_part_of_array(sorted_car_data, int(skip), int(take)),
                    'total_entities': len(new_car_data),
                    'options': filters_and_data['car_options']
                }
                return jsonify(response)

        if brand and model:
            car_data = main_car_data.get((brand, model))
            param_list = ['years', 'min_price', 'max_price', 'min_mileage', 'max_mileage', 'fuel_type', 'transmission', 'sale_type', 'body_style', 'color', 'doors', 'engine_capacity', 'power', 'volan_part', 'used_or_not', 'last_days', 'selected_site_sources']
            if car_data:
                if len(car_data) > 0:
                    if int(skip) == 0:
                        # Even if the filters change and we get here, the car options are still brand and model based, so if they are the same as redis cache, we return them
                        combined_dict = {}
                        if user_id in sim_redis_cache:
                            #filters_and_data = json.loads(r.get(user_id))
                            filters_and_data = sim_redis_cache[user_id]
                            combined_dict = filters_and_data['car_options'] if filters_and_data['car_options'] is not None and filters_and_data['params']['brand'] is not None and filters_and_data['params']['model'] is not None and filters_and_data['params']['brand'] == brand and filters_and_data['params']['model'] == model else get_car_options_dictionary(car_data)
                        else:
                            combined_dict = get_car_options_dictionary(car_data)
                        new_car_data = specific_filter_car_data(car_data, param_list, **params)
                        # Redis store this filtering and options
                        updated_redis_dict_for_user = {
                            'params': params,
                            'car_data': new_car_data,
                            'car_options': combined_dict
                        }
                        sim_redis_cache[user_id] = updated_redis_dict_for_user
                        # Print memory usage
                        # print('Size of main_car_data:', asizeof(main_car_data), 'bytes')
                        # print('Size of cached car data:', asizeof(sim_redis_cache), 'bytes')

                        sorted_car_data = specific_sort(new_car_data, sort_col, sort_dir)
                        response = {
                            'entities': get_part_of_array(sorted_car_data, int(skip), int(take)),
                            'total_entities': len(sorted_car_data),
                            'options': combined_dict
                        }
                        return jsonify(response)
                    
                    # Safe fail in case the redis cache get did not work, manual filtering
                    new_car_data = specific_filter_car_data(car_data, param_list, **params )
                    sorted_car_data = specific_sort(new_car_data, sort_col, sort_dir)
                    return jsonify({'entities': get_part_of_array(sorted_car_data, int(skip), int(take)), 'total_entities': len(sorted_car_data)})
                else:
                    return jsonify({'entities': [], 'total_entities': 0})
            else:
                return jsonify({'entities': [], 'total_entities': 0})
        else:
            return jsonify({'error': 'Missing brand or model query parameter.'}), 400
             
if __name__ == "__main__":
    app.run(app, host='0.0.0.0', port=5000)
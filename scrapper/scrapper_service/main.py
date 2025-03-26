import json
import os
from constants import CAR_BRANDS_MODELS
from scrappers.autovit import initialize_autovit_car_data
from scrappers.olx import initialize_olx_car_data
from ast import literal_eval

#TODO Optimize Data Structure Access: Using tuples as keys for dictionaries can slow down access time. Consider changing the way you structure your data, maybe by using nested dictionaries.
#TODO Handle Exceptions More Efficiently: If you expect certain types of exceptions, handle them explicitly rather than catching a general Exception.

#TODO  REMOVE EXTRA QUERY PARAMS
#TODO  GET MORE PROPERTIES FROM AUTOVIT
#TODO DEAL WITH STEERING WHEEL HERE
#TODO USE PRICE INDICATION HERE WITH HISTORY INSTEAD OF CARVERTICAL
#TODO CATCHA FOR VIN
#initialize_olx_car_data()
#initialize_autovit_car_data()

def load_and_merge_json_files(filepaths):
    merged_data = {}

    for filepath in filepaths:
        success_file = filepath.replace("cars.json", "success.txt")

        # Check if JSON file and success file exist
        if os.path.exists(filepath) and os.path.exists(success_file):
            with open(filepath, 'r') as f:
                str_dict_data = json.load(f)
                # Convert the string keys back to tuple keys
                data = {literal_eval(key): value for key, value in str_dict_data.items()}

                # Merge the data into merged_data
                for key, value in data.items():
                    if key in merged_data:
                        merged_data[key] += value
                    else:
                        merged_data[key] = value
             # Delete the JSON file and success file if successfully read
            os.remove(filepath)
            os.remove(success_file)
        else:
            print(f"File path does not exist: {filepath}")
    return merged_data

def merge_brand_and_model_data(filepaths):
    merged_brands = {}

    for filepath in filepaths:
        # Check if the JSON file exists
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                brand_model_data = json.load(f)
                # Iterate through the data and merge it into merged_brands
                for item in brand_model_data:
                    brand = item['brand']
                    models = item['models']
                    if brand in merged_brands:
                        for model in models:
                            model_name = model[0]
                            model_count = model[1]
                            # Find the model in merged_brands and add the count if it exists
                            existing_model = next((m for m in merged_brands[brand]['models'] if m[0] == model_name), None)
                            if existing_model:
                                existing_model[1] += model_count
                            else:
                                merged_brands[brand]['models'].append(model)
                    else:
                        merged_brands[brand] = {'brand': brand, 'models': models}

            # Delete the JSON file if successfully read
            os.remove(filepath)

    # Convert the merged data into the desired format
    result = [value for value in merged_brands.values()]
    return result

filepaths = ['./olx_cars.json', './autovit_cars.json']
main_car_data = load_and_merge_json_files(filepaths)

bm_filepaths = ['./olx_cars_brands_models.json', './autovit_cars_brands_models.json']
merged_brands_and_models = merge_brand_and_model_data(bm_filepaths)

try:
    with open('../cars.json', 'w') as f:
        # Convert tuple keys to string keys
        str_dict_data = {str(key): value for key, value in main_car_data.items()}
        json.dump(str_dict_data, f)
    with open('../cars_brands_models.json', 'w') as f:
        json.dump(merged_brands_and_models, f)
    # If successful, create a success.txt file
    open('../success.txt', 'w').close()
except Exception as e:
    # If an error occurred, write the error message to error.txt
    with open('../error.txt', 'w') as f:
        f.write(str(e))
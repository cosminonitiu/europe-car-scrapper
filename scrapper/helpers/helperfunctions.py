from datetime import datetime, timedelta
import pytz

def specific_filter_car_data(car_data, update_params, user_id, brand, model, skip, take, 
                             sort_col, sort_dir, years, min_price, max_price, min_mileage, max_mileage, fuel_type, transmission, 
                             sale_type, body_style, color, doors, engine_capacity, power, volan_part, used_or_not, last_days, selected_site_sources):
    
    if('selected_site_sources' in update_params):
        site_list = [str(site) for site in selected_site_sources.split(',')] if selected_site_sources != '' else []
        car_data = [obj for obj in car_data if obj['site_source'] is not None and obj['site_source'] in site_list] if len(site_list) > 0 else car_data

    if('years' in update_params):
        years_list = [int(year) for year in years.split(',')] if years != '' else []
        car_data = [obj for obj in car_data if obj['year'] is not None and obj['year'] in years_list] if len(years_list) > 0 else car_data

    if('min_price' in update_params):
        car_data = [obj for obj in car_data if obj['price'] is not None and  obj['price'] >= int(min_price)] if min_price != '' else car_data
    
    if('max_price' in update_params):
        car_data = [obj for obj in car_data if obj['price'] is not None and obj['price'] <= int(max_price)] if max_price != '' else car_data

    if('min_mileage' in update_params):
        car_data = [obj for obj in car_data if obj['mileage'] is not None and obj['mileage'] >= int(min_mileage)] if min_mileage != '' else car_data

    if('max_mileage' in update_params):
        car_data = [obj for obj in car_data if obj['mileage'] is not None and obj['mileage'] <= int(max_mileage)] if max_mileage != '' else car_data

    if('fuel_type' in update_params):
        fuel_types = [str(ft) for ft in fuel_type.split(',')] if fuel_type != '' else []
        car_data = [obj for obj in car_data if obj['fuel_type'] is not None and obj['fuel_type'] in fuel_types] if len(fuel_types) > 0 else car_data
    
    if('transmission' in update_params):
        transmissions = [str(ft) for ft in transmission.split(',')] if transmission != '' else []
        car_data = [obj for obj in car_data if obj['gearbox'] is not None and obj['gearbox'] in transmissions] if len(transmissions) > 0 else car_data
    
    if('sale_type' in update_params):
        sale_type_to_bool = False if sale_type == 'false' else True
        car_data = [obj for obj in car_data if obj['business'] is not None and obj['business'] == sale_type_to_bool] if sale_type != '' else car_data
    
    if('body_style' in update_params):
        body_styles = [str(ft) for ft in body_style.split(',')] if body_style != '' else []
        car_data = [obj for obj in car_data if obj['car_body'] is not None and obj['car_body'] in body_styles] if len(body_styles) > 0 else car_data
    
    if('color' in update_params):
        colors = [str(ft) for ft in color.split(',')] if color != '' else []
        car_data = [obj for obj in car_data if obj['color'] is not None and obj['color'] in colors] if len(colors) > 0 else car_data
    
    if('doors' in update_params):
        doors_list = [int(ft) for ft in doors.split(',')] if doors != '' else []
        car_data = [obj for obj in car_data if obj['door_count'] is not None and obj['door_count'] in doors_list] if len(doors_list) > 0 else car_data

    if('engine_capacity' in update_params):
        capacities = [int(ft) for ft in engine_capacity.split(',')] if engine_capacity != '' else []
        car_data = [obj for obj in car_data if obj['enginesize'] is not None and obj['enginesize'] in capacities] if len(capacities) > 0 else car_data
    
    if('power' in update_params):
        powers = [int(ft) for ft in power.split(',')] if power != '' else []
        car_data = [obj for obj in car_data if obj['engine_power'] is not None and obj['engine_power'] in powers] if len(powers) > 0 else car_data

    if('volan_part' in update_params):
        car_data = [obj for obj in car_data if obj['steering_wheel'] is not None and obj['steering_wheel'] == volan_part] if volan_part != '' else car_data
    
    if('used_or_not' in update_params):
        car_data = [obj for obj in car_data if obj['use_state'] is not None and obj['use_state'] == used_or_not] if used_or_not != '' else car_data
    
    if('last_days' in update_params):
        utc_timezone = pytz.utc
        specific_date = datetime.now(utc_timezone)
        bucharest_timezone = pytz.timezone('Europe/Bucharest')
        specific_date_bucharest = specific_date.astimezone(bucharest_timezone)  
        start_date = datetime.now(bucharest_timezone)

        if last_days is not None and last_days != '':
            start_date = specific_date_bucharest - timedelta(days=int(last_days))
            
        car_data = [obj for obj in car_data if obj['created_time'] is not None and datetime.fromisoformat(obj['created_time']) >= start_date] if last_days != '' and last_days is not None else car_data
    return car_data

def specific_sort(car_data, sort_col, sort_dir):
    def custom_sort(x):
         # Define a default value for the sorting property based on its data type
        default_value = None  # Default value for string sorting
        if isinstance(x[sort_col], int):
            default_value = 0  # Default value for integer sorting
        elif isinstance(x[sort_col], datetime):
            default_value = datetime.min  # Default value for datetime sorting

        # Return the sorting property or the default value based on its data type
        return x[sort_col] if x[sort_col] is not None else default_value
    
    if sort_dir == 'down':
        return sorted(car_data, key=custom_sort, reverse=True)
    else:
        return sorted(car_data, key=custom_sort)

def compare_old_params(old_params, new_params):
    try:
        if new_params['brand'] is None or new_params['model'] is None:
            return [False, ['REDIS: Could not get the brand and model in the new request params']]
        if new_params['brand'] != old_params['brand'] or new_params['model'] != old_params['model']:
            return [False, ['REDIS: The brand and model changed from last caching']]
        
        param_list = ['years', 'min_price', 'max_price', 'min_mileage', 'max_mileage', 'fuel_type', 'transmission', 'sale_type', 'body_style', 'color', 'doors', 'engine_capacity', 'power', 'volan_part', 'used_or_not', 'last_days', 'selected_site_sources']
        update_params = []
        for p in param_list:
            if old_params[p] != '' and new_params[p] != old_params[p]:
                return [False, ['REDIS: Query Parameter changed: ' + p +', could not use the cached data, recaching']]
            if old_params[p] == '' and new_params[p] != old_params[p]:
                update_params.append(p)

        return [True, update_params]
    except KeyError:
        return [False, ['REDIS: Could not get the key in new or old params dictionary']]

def get_part_of_array(arr, skip, take):
    start_index = skip
    end_index = skip + take
    return arr[start_index:end_index]

def get_car_options_dictionary(car_data):
    years_set = set()
    fuel_types = set()
    transmissions = set()
    body_styles = set()
    sale_types = set()
    colors = set()
    doors_set = set()
    engine_capacities = set()
    powers = set()
    volan_parts = set()
    used_or_nots = set()
    for car in car_data:
        if car['year'] is not None:
            years_set.add(car['year']) 
        if car['fuel_type'] is not None:
            fuel_types.add(car['fuel_type'])
        if car['gearbox'] is not None:
            transmissions.add(car['gearbox'])
        if car['car_body'] is not None:
            body_styles.add(car['car_body'])
        if car['business'] is not None:
            sale_types.add(car['business'])
        if car['color'] is not None:
            colors.add(car['color'])
        if car['door_count'] is not None:
            doors_set.add(car['door_count'])
        if car['enginesize'] is not None:
            engine_capacities.add(car['enginesize'])
        if car['engine_power'] is not None:
            powers.add(car['engine_power'])
        if car['steering_wheel'] is not None:
            volan_parts.add(car['steering_wheel'])
        if car['use_state'] is not None:
            used_or_nots.add(car['use_state'])  

    # Combine the sets into a dictionary
    combined_dict = {
        'years': list(years_set),
        'fuel_types': list(fuel_types),
        'transmissions': list(transmissions),
        'body_styles': list(body_styles),
        'sale_types': list(sale_types),
        'colors': list(colors),
        'doors': list(doors_set),
        'engine_capacities': list(engine_capacities),
        'powers': list(powers),
        'volan_parts': list(volan_parts),
        'used_or_nots': list(used_or_nots)
    }

    return combined_dict
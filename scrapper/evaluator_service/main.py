import json
from datetime import datetime, timedelta

def gpt_evaluate(car_id, car_brand, car_model, car_title, car_year, car_country,
                 car_mileage, car_description, car_engine_size, car_power, car_fuel_type, car_body, car_gear_box, car_steering_wheel):
	# GPT TEXT
	gpt_text = ["Act as an expert car salesman with 10 years in the business, fair pricing, could you price a few cars for me based on brand, model, year, km's run and a description which contains packages and trims? ",
	"Please respond to me as succint as possible and only print the JSON, no more writing :" ,
	"Price Range: Min - Max €" ,
	"Additional info: (Like imported from somewhere (taxes), if it's well equipped, packages) in json format like:" ,
	"{" ,
	'"Price Range": {' ,
	'"Min": 20000,' ,
	'"Max": 23000' ,
	'},' ,
	'"Additional Info": "Well-equipped, imported from Germany. Confirm if duties/taxes are due. Features: S-Tronic auto transmission, start-stop system, touchscreen, navigation, audio system, smartphone connectivity."' ,
	'}',
	'',
	f"Title: {car_title}" ,
	f"Brand: {car_brand}" ,
	f"Model: {car_model}" ,
	f"Country: {car_country}" ,
	f"Year: {car_year}" ,
	f"Engine-size: {car_engine_size}" ,
	f"Power: {car_power}" ,
	f"Fuel: {car_fuel_type}" ,
	f"Mileage: {car_mileage}" ,
	f"Body style: {car_body}" ,
	f"Gear box: {car_gear_box}" ,
	f"Steering wheel: {car_steering_wheel}" ,
	f"Description: {car_description}"
	]

	json_string = """
	{
		"Price Range": {
			"Min": 90000,
			"Max": 105000
		},
		"Additional Info": "Limited edition BMW M4 (M4CSL), nearly new with only 6 km driven. Equipped with a 2993 cc petrol engine and automatic gearbox. Color: Grey. Confirm if duties/taxes are due. Vehicle details are from Autovit.ro. Further features and package details not provided."
	}
	"""
	python_json = json.loads(json_string)
	python_json['car_id'] = car_id
	python_json['users'] = []
	python_json['date_purchased'] = datetime.today().strftime('%Y:%m:%d')
	return python_json

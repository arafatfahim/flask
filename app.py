from flask import Flask, render_template, request,redirect ,jsonify
# from flask_restful import Resource, Api, reqparse
import json
from flask_cors import CORS


import pandas as pd
import pymongo

# from sklearn.preprocessing import minmax_scale
from skcriteria import Data, MIN, MAX
from skcriteria.madm import simple

cluster = pymongo.MongoClient('mongodb+srv://arsalan:abcdefghijk@cluster0.dy37i.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

db = cluster.iot_project
col = db.test_collection

app = Flask(__name__)
CORS(app)

# def todo_serializer(todo):
# 	return {
# 		'Room' : todo.Room,
# 		'Temperature' : todo.Temperature,
# 		'Acoustic' : todo.Acoustic,
# 	}


@app.route('/latest_record', methods = ['GET'])
def all_info():
	latest_record = json.dumps((col.find().sort([('DateTime', -1)]).limit(1))[0], default=str)
	return latest_record

@app.route('/latest_record/<weights>', methods = ['GET'])
def user_weights(weights):
	latest_record = json.dumps((col.find().sort([('DateTime', -1)]).limit(1))[0], default=str)
	latest_record_json = json.loads(latest_record)
	latest_record_pd_df = pd.DataFrame.from_dict(latest_record_json)

	useful_cols_df = pd.DataFrame(latest_record_pd_df, columns = ["Room", "Temperature", "Acoustic", "Illuminance", "Air_Quality", "Vent_Rate", "WiFi_RSS"])

	weights_array = []
	counter = 0
	num_str = ""
	for char in weights:
		if char != ",":
			num_str += char
		else:
			weights_array.append(int(num_str))
			num_str = ""
	weights_array.append(int(num_str))

	criteria_data = Data(
	useful_cols_df.iloc[:, 1:],
	[MAX, MIN, MAX, MIN, MIN, MAX],
	anames = useful_cols_df['Room'],
	cnames = useful_cols_df.columns[1:],
	weights= weights_array
)

	dm = simple.WeightedSum(mnorm="sum")
	dec = dm.decide(criteria_data)

	print(dec)
	print(dec.e_.points)

	New_Indicator_Vals = {"Indicator":dec.e_.points.tolist()}

	return (json.dumps(New_Indicator_Vals))



if __name__ == '__main__':
	app.run(debug=True)

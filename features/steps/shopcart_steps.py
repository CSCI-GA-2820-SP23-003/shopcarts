######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Shopcart Steps

Steps file for shopcart.feature

For information on Waiting until elements are present in the HTML see:
	https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect

@given('the following shopcart entries in DB')
def step_impl(context):
	""" Delete all Shopcart records and load new ones """
	
	rest_endpoint = f"{context.BASE_URL}/api/shopcarts"
	context.resp = requests.get(rest_endpoint)
	data = context.resp.json()
	expect(context.resp.status_code).to_equal(200)
	customer_ids = []

	for cart in data:
		customer_ids.append(cart['customer_id'])
	
	# delete shopcarts of all customers in DB
	for cid in customer_ids:
		context.resp = requests.delete(f"{rest_endpoint}/{cid}")
		expect(context.resp.status_code).to_equal(204)
	
	# load the DB with the new shopcart records
	for row in context.table:
		payload = {
			'customer_id': int(row['customer_id']), 
			'product_id': int(row['product_id']), 
			'quantities':  int(row['quantities'])
		}

		if payload['product_id'] == -1:
			# create shopcart request
			context.resp = requests.post(rest_endpoint, json=payload)
		else:
			# create shopcart item
			context.resp = requests.post(f"{rest_endpoint}/{row['customer_id']}/items", json=payload)
		expect(context.resp.status_code).to_equal(201)
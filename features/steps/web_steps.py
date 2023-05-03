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

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from behave import when, then
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

ID_PREFIX = 'shopcart_'


@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.BASE_URL)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@when('I set row "{row_num}" of add-item-table to "{cell}"')
def step_impl(context, row_num, cell):
    row_num = int(row_num)
    item_id, quantity = cell.split(',')
    item_id, quantity = int(item_id), int(quantity)

    input_table = context.driver.find_element_by_id("update-cart-table-body")
    rows = input_table.find_elements(By.TAG_NAME, "tr")
    print('rows in input_table: ', len(rows))

    required_row = rows[row_num-1]

    item_input = required_row.find_element(By.ID, "item-id-input")
    quantity_input = required_row.find_element(By.ID, "quantity-input")

    item_input.send_keys(item_id)
    quantity_input.send_keys(quantity)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    error_msg = "I should not see '%s' in '%s'" % (text_string, element.text)
    ensure(text_string in element.text, False, error_msg)


@then('I should see "{text_string}" in "{element_name}" area')
def step_impl(context, text_string, element_name):
    element_id = element_name.lower().replace(' ', '_')
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)

@then('I should not see any content in the table "{table_name}"')
def step_impl(context, table_name):
    table_div = context.driver.find_element_by_id(table_name)
    table = table_div.find_elements(By.TAG_NAME, 'tbody')
    if len(table) > 0:
        rows = table.find_elements(By.TAG_NAME, 'tr')
        expect(len(rows)).to_be(0)


@then('I should see "{text_string}" in row "{row_num}", col "{col_num}" of table "{table_name}"')
def step_impl(context, text_string, row_num, col_num, table_name):
    table_div = context.driver.find_element_by_id(table_name)
    table = table_div.find_element(By.TAG_NAME, 'tbody')

    row_num = int(row_num) - 1
    col_num = int(col_num) - 1

    rows = table.find_elements(By.TAG_NAME, 'tr')

    cell = rows[row_num].find_elements(By.TAG_NAME, 'td')[col_num]
    expect(int(cell.text)).to_be(int(text_string))

@then('Only one shopcart should exist for the customer in table "{table_name}"')
def step_impl(context, table_name):
    table_div = context.driver.find_element_by_id(table_name)
    table = table_div.find_element(By.TAG_NAME, 'tbody')

    col_num = 1 #shopcart # column

    rows = table.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        cart_num = row.find_elements(By.TAG_NAME, 'td')[col_num]
        expect(int(cart_num.text)).to_be(1)



# @then('the "{element_name}" field should be empty')
# def step_impl(context, element_name):
#     element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
#     element = context.driver.find_element_by_id(element_id)
#     expect(element.get_attribute('value')).to_be(u'')

# ##################################################################
# # These two function simulate copy and paste
# ##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

# ##################################################################
# # This code works because of the following naming convention:
# # The buttons have an id in the html hat is the button text
# # in lowercase followed by '-btn' so the Clean button has an id of
# # id='clear-btn'. That allows us to lowercase the name and add '-btn'
# # to get the element id of any button
# ##################################################################

@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)


@then('I should not see "{name}" in the item search results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('items_search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then('the number of item search results should be "{number}"')
def step_impl(context, number):
    table_div = context.driver.find_element_by_id('items_search_results')
    table = table_div.find_element(By.TAG_NAME, 'tbody')
    rows = table.find_elements(By.TAG_NAME, 'tr')
    expect(len(rows)).to_be(1)

# ##################################################################
# # This code works because of the following naming convention:
# # The id field for text input in the html is the element name
# # prefixed by ID_PREFIX so the Name field has an id='pet_name'
# # We can then lowercase the name and prefix with pet_ to get the id
# ##################################################################

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = element_name
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)

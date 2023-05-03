Feature: The shopcart Items APIs
	As a shopcart service provider
	I need a RESTful shopcart service for items within each cart
	So that I can keep track of all customers's shopcarts.

	Background:
		Given the following shopcart entries in DB
			| id | customer_id | product_id | quantities |
			| 1  | 10          | -1         | 3          |
			| 2  | 10          | 1          | 3          |
			| 3  | 20          | -1         | 1          |
			| 4  | 10          | 2          | 3          |
			| 5  | 20          | 2          | 2          |

	Scenario: List all items of a customer's shopcart
		When I visit the "Home Page"
		And I set the "item_customer_id" to "10"
		And I press the "item_search" button
		Then I should see "Success" in "item flash message" area
		And I should see "1" in the "item_item_id" field
		And I should see "3" in the "item_quantity" field
		And I should see "1" in row "1", col "2" of table "items_search_results"
		And I should see "3" in row "1", col "3" of table "items_search_results"
		And I should see "2" in row "2", col "2" of table "items_search_results"
		And I should see "3" in row "2", col "3" of table "items_search_results"

	Scenario: Add new item to customer's shopcart
		When I visit the "Home Page"
		And I set the "item_customer_id" to "10"
		And I set the "item_item_id" to "3"
		And I set the "item_quantity" to "30"
		And I press the "item_create" button
		Then I should see "Success" in "item flash message" area
		And I should see "3" in the "item_item_id" field
		And I should see "30" in the "item_quantity" field

	Scenario: Update item in customer's shopcart
		When I visit the "Home Page"
		And I set the "item_customer_id" to "10"
		And I set the "item_item_id" to "1"
		And I set the "item_quantity" to "25"
		And I press the "item_update" button
		Then I should see "Success" in "item flash message" area
		And I should see "1" in the "item_item_id" field
		And I should see "25" in the "item_quantity" field

	Scenario: Read an item in customer's shopcart
		When I visit the "Home Page"
		And I set the "item_customer_id" to "10"
		And I set the "item_item_id" to "2"
		And I press the "retrieve-item" button
		Then I should see "Success" in "item flash message" area
		And I should see "3" in the "item_quantity" field

	Scenario: Delete an item from customer's shopcart
		When I visit the "Home Page"
		And I set the "item_customer_id" to "10"
		And I set the "item_item_id" to "2"
		And I press the "delete-item" button
		Then I should see "Item has been Deleted!" in "item flash message" area
		When I set the "item_customer_id" to "10"
		And I press the "item_search" button
		Then I should see "Success" in "item flash message" area
		And I should not see "2" in the item search results

	Scenario: Query items in a customer's shopcart with parameters
		When I visit the "Home Page"
		And I set the "item_customer_id" to "10"
		And I set the "item_item_id" to "3"
		And I set the "item_quantity" to "30"
		And I press the "item_create" button
		Then I should see "Success" in "item flash message" area
		When I set the "item_customer_id" to "10"
		And I set the "item_quantity" to "30"
		And I press the "item_search" button
		Then I should see "Success" in "item flash message" area
		And the number of item search results should be "1"
		And I should see "3" in row "1", col "2" of table "items_search_results"
		And I should see "30" in row "1", col "3" of table "items_search_results"

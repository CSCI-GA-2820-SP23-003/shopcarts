Feature: The shopcart service back-end
    As a shopcart service provider
    I need a RESTful shopcart service
    So that I can keep track of all customers's shopcarts.

    Background:
        Given the following shopcart entries in DB
            | id | customer_id | product_id | quantities |
            | 1  | 10          | -1         | 3          |
            | 2  | 10          | 1          | 3          |
            | 3  | 20          | -1         | 1          |
            | 4  | 10          | 2          | 3          |
            | 5  | 20          | 2          | 2          |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Shopcart RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Update a Shopcart
        When I visit the "Home Page"
        And I set the "customer_id" to "10"
        And I press the "add-row" button
        And I set row "1" of add-item-table to "1, 10"
        And I set row "2" of add-item-table to "3, 9"
        And I press the "update" button
        Then I should see "Success" in "flash message" area
        And I should see "1" in row "1", col "3" of table "search_results"
        And I should see "10" in row "1", col "4" of table "search_results"
        And I should see "3" in row "2", col "3" of table "search_results"
        And I should see "9" in row "2", col "4" of table "search_results"

    Scenario: List All Shopcarts
        When I visit the "Home Page"
        And I press the "search" button
        Then I should see "Success" in "flash message" area
        And I should see "10" in row "1", col "1" of table "search_results"
        And I should see "20" in row "2", col "1" of table "search_results"

    Scenario: Display A Customer's Shopcart
        When I visit the "Home Page"
        And I set the "customer_id" to "10"
        And I press the "retrieve-shopcart" button
        Then I should see "Success" in "flash message" area
        And I should see "10" in row "1", col "1" of table "search_results"
        And I should see "1" in row "1", col "2" of table "search_results"
        And I should see "1" in row "1", col "3" of table "search_results"
        And I should see "3" in row "1", col "4" of table "search_results"
        And I should see "10" in row "2", col "1" of table "search_results"
        And I should see "1" in row "2", col "2" of table "search_results"
        And I should see "2" in row "2", col "3" of table "search_results"
        And I should see "3" in row "2", col "4" of table "search_results"
        And Only one shopcart should exist for the customer in table "search_results"


    Scenario: Create a Shopcart
        When I visit the "Home Page"
        And I set the "customer_id" to "5"
        And I press the "Create" button
        Then I should see "Success" in "flash message" area

    Scenario: Delete a Shopcart
        When I visit the "Home Page"
        And I set the "customer_id" to "6"
        And I press the "Create" button
        Then I should see "Success" in "flash message" area
        When I set the "customer_id" to "6"
        And I press the "Delete-shopCart" button
        Then I should see "Shopcart has been Deleted!" in "flash message" area
        When I set the "customer_id" to "6"
        And I press the "Search" button
        Then I should see "Success" in "flash message" area
        And I should not see "6" in the results

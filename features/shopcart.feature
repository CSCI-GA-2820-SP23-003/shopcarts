Feature: The shopcart service back-end
    As a shopcart service provider
    I need a RESTful shopcart service
    So that I can keep track of all customers's shopcarts. 

Background:
    Given the following shopcart entries for all the customers
        | id         | customer_id | product_id | quantities  | 
        | 1          | 1           | 1          | 3           |
        | 2          | 2           | 3          | 1           |
        | 3          | 1           | 2          | 3           |
        | 4          | 2           | 2          | 2           |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart RESTful Service" in the title
    And I should not see "404 Not Found"\

Scenario: Update a Shopcarrt
    When I visit the "Home Page"   
    And I press the "add-row-btn" button
    And I set the "customer_id" to "1"
    And I set the "item-id-input" to "1"
    And I set the "quantity-input" to "10"
    And I set the "item-id-input" to "3"
    And I set the "quantity-input" to "9"
    Then I should see the message "Success" in "flash message"
    And For row "1", I should see "1" in col "1" and "10" in col "3" in table "update-cart-table"
    And For row "2", I should see "3" in col "1" and "9" in col "3" in table "update-cart-table"
    

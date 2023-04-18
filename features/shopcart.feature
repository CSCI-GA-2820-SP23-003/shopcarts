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
    And I should not see "404 Not Found"

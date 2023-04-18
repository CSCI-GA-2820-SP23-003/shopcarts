$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // -------------------------------- SHOPCART API --------------------------------

    function clear_search_results_table() {
        $("#search_results").empty();
        let table = '<table class="table table-striped" cellpadding="10">';
        table += '<thead><tr>';
        table += '<th class="col-md-3">Customer ID</th>';
        table += '<th class="col-md-3">Shopcart #</th>';
        table += '<th class="col-md-3">Item ID</th>';
        table += '<th class="col-md-3">Quantity</th>';
        table += '</tr></thead><tbody>';
        table += '</tbody></table>';
        $("#search_results").append(table);

    }

    /// Clears all form fields
    function clear_form_data() {
        clear_search_results_table();
        $("#customer_id").val("");

    }

    function get_item_form_data() {
        var items = [];
        let customer_id = $("#customer_id").val();
        // Iterate over each row in the table
        $("#update-cart-table-body tr").each(function () {
            // Get the values of the input fields in the current row
            var itemId = $(this).find("#item-id-input").val();
            var quantity = $(this).find("#quantity-input").val();

            // If both fields have a value, add them to the array
            if (itemId && quantity) {
                items.push({
                    customer_id: Number(customer_id),
                    product_id: itemId,
                    quantities: quantity
                });
            }
        });

        return items;
    }

    function update_shopcart_results(res) {
        $("#search_results").empty();
        let table = '<table class="table table-striped" cellpadding="10">';
        table += '<thead><tr>';
        table += '<th class="col-md-3">Customer ID</th>';
        table += '<th class="col-md-3">Shopcart #</th>';
        table += '<th class="col-md-3">Item ID</th>';
        table += '<th class="col-md-3">Quantity</th>';
        table += '</tr></thead><tbody>';

        let customer_id = res.customer_id;
        let num_shopcarts = res.shopcarts.length;

        for (let i = 0; i < num_shopcarts; i++) {
            let current_cart = res.shopcarts[i];
            let num_items = current_cart.items.length;
            for (let j = 0; j < num_items; j++) {
                let current_item = current_cart.items[j];
                table += `<tr id="cart_row_${i + j}" ><td>${customer_id}</td><td>${i + 1}</td><td>${current_item.item_id}</td><td>${current_item.quantity}</td></tr>`;
            }
        }
        table += '</tbody></table>';
        $("#search_results").append(table);
    }

    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
        if (message === "Success" || message === "Shopcart has been Deleted!") {
            $("#flash_message").css("color", "green");
        } else {
            $("#flash_message").css("color", "red");
        }

    }

    function update_form_data(res) {
        $("#customer_id").val(res.customer_id);
    }


    // -------------------------------- ITEMS API --------------------------------

    // Updates the form with data from the response
    function update_item_form_data(res) {
        $("#item_customer_id").val(res.customer_id);
        $("#item_item_id").val(res.product_id);
        $("#item_quantity").val(res.quantities);
    }

    function clear_item_search_results_table() {
        $("#items_search_results").empty();
        let table = '<table class="table table-striped" cellpadding="10">';
        table += '<thead><tr>';
        table += '<th class="col-md-4">Customer ID</th>';
        table += '<th class="col-md-4">Item ID</th>';
        table += '<th class="col-md-4">Quantity</th>';
        table += '</tr></thead><tbody>';
        table += '</tbody></table>';
        $("#items_search_results").append(table);
    }


    // Updates the flash message area
    function item_flash_message(message) {
        $("#item_flash_message").empty();
        $("#item_flash_message").append(message);
        if (message === "Success" || message === "Item has been Deleted!") {
            $("#item_flash_message").css("color", "green");
        } else {
            $("#item_flash_message").css("color", "red");
        }

    }

    /// Clears all form fields
    function clear_item_form_data() {
        clear_item_search_results_table();
        $("#item_customer_id").val("");
        $("#item_item_id").val("");
        $("#item_quantity").val("");
    }

    // ****************************************
    //  A P I   C A L L S
    // ****************************************

    // -------------------------------- SHOPCARTS API --------------------------------

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#add-row-btn").click(function () {
        var newRow = "<tr>" +
            "<td><label for='item-id-input'>Item ID:</label></td>" +
            "<td><input id='item-id-input' type='text' class='form-control' placeholder='Enter Item ID'></td>" +
            "<td><label for='quantity-input'>Quantity:</label></td>" +
            "<td><input id='quantity-input' type='number' class='form-control' placeholder='Enter Quantity'></td>" +
            "<td><button class='btn btn-danger delete-row-btn'>Delete</button></td>" +
            "</tr>";
        $("#update-cart-table-body").append(newRow);
    });

    // Remove the current row when the "Delete" button is clicked
    $(document).on("click", ".delete-row-btn", function () {
        $(this).closest("tr").remove();
    });

    $("#create-btn").click(function () {
        let customer_id = $("#customer_id").val();

        let data = {
            "customer_id": Number(customer_id),
            "product_id": -1,
            "quantities": 1
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: '/shopcarts',
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************


    $("#retrieve-shopcart-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${customer_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_shopcart_results(res);
            // update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Clear a Shopcart
    // ****************************************

    $("#clear-shopcart-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/shopcarts/${customer_id}/clear`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            // update_shopcart_results(res);
            clear_search_results_table();
            // update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-shopcart-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${customer_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data();
            clear_search_results_table();
            flash_message("Shopcart has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Search for Shopcarts
    // ****************************************

    $("#search-btn").click(function () {

        // currently lists all shopcarts - can modify this after implementing query params for this API

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: "/shopcarts",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-3">Customer ID</th>'
            table += '<th class="col-md-3">Shopcart #</th>'
            table += '<th class="col-md-3"></th>'
            table += '<th class="col-md-3"></th>'
            table += '</tr></thead><tbody>'

            for (let i = 0; i < res.shopcart_lists.length; i++) {
                let cur_cart = res.shopcart_lists[i];
                table += `<tr id = "row_${i}" ><td>${cur_cart.customer_id}</td><td>1</td><td></td><td></td></tr > `;

            }

            table += '</tbody></table>';
            $("#search_results").append(table);

            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_search_results_table();
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update a Shopcart
    // ****************************************
    $("#update-btn").click(function () {

        let items = get_item_form_data();
        let customer_id = $("#customer_id").val();

        let data = {
            "customer_id": Number(customer_id),
            "items": items
        };

        $("#flash_message").empty();

        let url = '/shopcarts/' + customer_id;

        let ajax = $.ajax({
            type: "PUT",
            url: url,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-3">Customer ID</th>';
            table += '<th class="col-md-3">Shopcart #</th>';
            table += '<th class="col-md-3">Item ID</th>';
            table += '<th class="col-md-3">Quantity</th>';
            table += '</tr></thead><tbody>';

            let customer_id = res.customer_id;

            for (let j = 0; j < res.items.length; j++) {
                let current_item = res.items[j];
                table += `<tr id="cart_row_${j}" ><td>${customer_id}</td><td>1</td><td>${current_item.product_id}</td><td>${current_item.quantities}</td></tr>`;
            }

            table += '</tbody></table>';
            $("#search_results").append(table);
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });


    // -------------------------------- ITEMS API --------------------------------

    // ****************************************
    // Create a Shopcart Item
    // ****************************************

    $("#item_create-btn").click(function () {
        let customer_id = $("#item_customer_id").val();
        let item_id = $("#item_item_id").val();
        let quantity = $("#item_quantity").val();

        let url = '/shopcarts/' + customer_id + '/items'

        let data = {
            "customer_id": Number(customer_id),
            "product_id": Number(item_id),
            "quantities": Number(quantity)
        };

        $("#item_flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: url,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_item_form_data(res)
            item_flash_message("Success")
        });

        ajax.fail(function (res) {
            item_flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Shopcart Item
    // ****************************************

    $("#item_update-btn").click(function () {

        let customer_id = $("#item_customer_id").val();
        let item_id = $("#item_item_id").val();
        let quantity = $("#item_quantity").val();

        let data = {
            "customer_id": Number(customer_id),
            "product_id": Number(item_id),
            "quantities": quantity
        };

        $("#item_flash_message").empty();

        let url = '/shopcarts/' + customer_id + '/items/' + item_id;

        let ajax = $.ajax({
            type: "PUT",
            url: url,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_item_form_data(res)
            item_flash_message("Success")
        });

        ajax.fail(function (res) {
            item_flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Item
    // ****************************************

    $("#retrieve-item-btn").click(function () {

        let customer_id = $("#item_customer_id").val();
        let item_id = $("#item_item_id").val();

        $("#item_flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${customer_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_item_form_data(res)
            item_flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_item_form_data()
            item_flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Item
    // ****************************************

    $("#delete-item-btn").click(function () {

        let customer_id = $("#item_customer_id").val();
        let item_id = $("#item_item_id").val();


        $("#item_flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${customer_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_item_form_data()
            item_flash_message("Item has been Deleted!")
        });

        ajax.fail(function (res) {
            item_flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#item_clear-btn").click(function () {
        $("#item_flash_message").empty();
        clear_item_form_data()
    });


    $("#clear-btn").click(function () {
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for an Item
    // ****************************************

    $("#item_search-btn").click(function () {

        let customer_id = $("#item_customer_id").val();
        let item_id = $("#item_item_id").val();
        let quantity = $("#item_quantity").val();

        let queryString = ""

        if (quantity) {
            queryString += 'quantity=' + quantity
        }

        $("#item_flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${customer_id}/items?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#items_search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-4">Customer ID</th>'
            table += '<th class="col-md-4">Item ID</th>'
            table += '<th class="col-md-4">Quantity</th>'
            table += '</tr></thead><tbody>'

            let firstItem = "";
            result_items = res.items;
            result_customer_id = res.customer_id;

            for (let i = 0; i < result_items.length; i++) {
                item_id = result_items[i].item_id;
                quantity = result_items[i].quantity;
                table += `<tr id = "item_row_${i}"><td>${result_customer_id}</td><td>${item_id}</td><td>${quantity}</td></tr> `;
                if (i == 0) {
                    firstItem = {
                        customer_id: result_customer_id,
                        product_id: item_id,
                        quantities: quantity
                    };
                }
            }
            table += '</tbody></table>';
            $("#items_search_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_item_form_data(firstItem)
            }

            item_flash_message("Success")
        });

        ajax.fail(function (res) {
            $("#items_search_results").empty();
            item_flash_message(res.responseJSON.message)
        });

    });

})

[![Build Status](https://github.com/CSCI-GA-2820-SP23-003/shopcarts/actions/workflows/tdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP23-003/shopcarts/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP23-003/shopcarts/branch/master/graph/badge.svg?token=G3CD93815L)](https://codecov.io/gh/CSCI-GA-2820-SP23-003/shopcarts)

# NYU DevOps - Shopcarts Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)


## Overview

This repository contains code for Customer Shop Cart for an e-commerce web site. This show what the API does, how to calls them and what are the expeced inputs. Also include how to run and test the code. The APIs are built using Python and the Flask web framework.

## Prerequisite Software Installation
This project uses Docker and Visual Studio Code with the Remote Containers extension to provide a consistent repeatable disposable development environment for all of the labs in this course.

You will need the following software installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com)
- [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension from the Visual Studio Marketplace

All of these can be installed manually by clicking on the links above or you can use a package manager like **Homebrew** on Mac of **Chocolatey** on Windows.

You can read more about creating these environments in this article: [Creating Reproducible Development Environments](https://johnrofrano.medium.com/creating-reproducible-development-environments-fac8d6471f35)
## Setup
You should clone this repo, change into the repo directory and open Visual Studio Code using the `code .` command. VS Code will prompt you to reopen in a container and you should say **yes**. This will take a while as it builds the Docker image and creates a container from it to develop in.

```bash
git clone https://github.com/CSCI-GA-2820-SP23-003/shopcarts.git
cd shopcarts
code .
```
Note that there is a period `.` after the `code` command. This tells Visual Studio Code to open the editor and load the current folder of files.

Once the environment is loaded you should be placed at a `bash` prompt in the `/app` folder inside of the development container. This folder is mounted to the current working directory of your repository on your computer. This means that any file you edit while inside of the `/app` folder in the container is actually being edited on your computer. You can then commit your changes to `git` from either inside or outside of the container.

You can run test on this folder.
```bash
cd shopcarts
nosetests -v --with-spec --spec-color
```

## APIS

| URL | Description | Return code |
| -------- | -------- | -------- |
| GET / | Return all REST API name, all available paths | 200 |
| GET /health | Return the health status | 200 |
| GET /shopcarts | Retrieve all shopcarts of all customers | 200 |
| POST /shopcarts | Creates a new shopcart for a customer given customer_id | 201, 409, 400|
| GET /shopcarts/<int:customer_id> | Retrieve all the shopcarts of a customer<customer_id> | 200, 404 |
| PUT /shopcarts/<int:customer_id> | Update a shop cart for customer<customer_id> | |
| DELETE /shopcarts/<int:customer_id> | Deletes the shopcart of customer<customer_id> | 204 |
| GET /shopcarts/<int:customer_id>/items | Return all the items in customer<customer_id> shopcart lists| |
| POST /shopcarts/<int:customer_id>/items | Adds a new item to the customer<customer_id>'s shopcart | 201, 400, 409 |
| GET /shopcarts/<int:customer_id>/items/<int:product_id> | Return detail information about product<product_id> in customer<customer_id> shopcart| |
| PUT /shopcarts/<int:customer_id>/items/<int:product_id> | Update a shop cart item<product_id> for customer<customer_id> | 200, 404 |
| DELETE /shopcarts/<int:customer_id>/items/<int:product_id> | Delete a shop cart item<product_id> for customer<customer_id> | 200, 404 |
| PUT /shopcarts/<int:customer_id>/clear | Clear the shopcart of customer<customer_id> | |


## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.

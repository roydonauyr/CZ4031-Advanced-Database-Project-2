# Project 2

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/roydonauyr/CZ4031-Advanced-Database-Project-2)
![GitHub repo size](https://img.shields.io/github/repo-size/roydonauyr/CZ4031-Advanced-Database-Project-2)
![GitHub language count](https://img.shields.io/github/languages/count/roydonauyr/CZ4031-Advanced-Database-Project-2)
![GitHub last commit](https://img.shields.io/github/last-commit/roydonauyr/CZ4031-Advanced-Database-Project-2)

## Project description:

**Introduction**

In this project, we are tasked with the goal to translate and annotate a given SQL Query by
obtaining their Optimal QEP and respective AQPs. Using these AQPs, we are able to explain how
different components of the query are executed by the underlying query processor and why the
operators are chosen among other alternatives.

**File structure**

Our project is split into four main python files:
1) Project.py

This is the main file that our application uses that invokes all the necessary procedures
from the other three files.

2) Interface.py

This file is incharge of the display of the optimal query plan together with annotations on
the plan. This file also contains the logic for how the user interacts with the program. (e.g.
Handling errors from user inputs)

3) Preprocessing.py

The main responsibilities of these file are:

● To establish connection with the database tables

● Obtain Optimal QEP

● Obtain AQPs

● Make preparations before passing over to annotations to annotate the Optimal QEP.


4) Annotation.py

This file is in charge of annotating respective tree nodes in the optimal QEP.

**Libraries Used:**
The libraries that are required to run this project are:

● Psycopg2, which is a library that is used as a PostgreSQL database adapter for Python.

● Tkinter, which is a built-in python library that is made for building simple GUI for
application in python

### Running Instructions
a. Ensure python version is 3.8 (For 3.10 version and above psycopg2 wont run and an error
will show: ModuleNotFoundError: No module named 'psycopg2')
b. Pip install psycopg2 (If that doesn’t work, use pip install psycopg2-binary)
c. Change to the correct directory and Run the project.py file

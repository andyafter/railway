# Summary
We can use this api to get suggestion shortest route in Singapore rail.

# Algorithm
Base on BFS, implemented two scenario: 
1. shortest route without time consideration
2. shortest route with time cost

## Shortest route
we don't have every stop's real distance ,so we just consider the station number as the distance. 
shortest route mean the stop number from source to destination is least



## Consider time cost
time cost considered the scenario:
1. Single time,eg. travels in Non-peak time
2. Crossing two interval, eg. travels from Peak time to Non-Peak time
3. Crossing three interval, eg. travels from Peak time to Non-Peak time and to Night time
4. If interval changes, the very station's time cost changed too, 
> eg. start time is 21:50, take 1 station, time is 22:00, now is in Non-peak time, 
> the time cost in this interval stop is 8 minutes, so follow stop's time cost change to 8 minutes



# How to run
In the terminal type follow command
```bash
cd railway
pip install -r requirements.txt
python app.py
```

Then open browser, type follow url
```html
http://127.0.0.1:5000/api/search?from=Holland Village&to=Bugis&order_by=distance
```

* The input parameters `from`, `to`, `order_by` are case-insensitive.
* The API output is json format, the demo data is in file [api_output.json](api_output.json)


# How to do unit test
Use the Flask and Unittest, covered 9 situations

Open your terminal and type the follow commands
```bash
cd railway
python manager.py test
```

# Language & Libraries & Tools 
Language: Python 3.7
Web Framework: Flask
Database: Sqlite3
Unit Test: unittest

We can find the more Libraries details in requirements.txt 



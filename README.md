# API Documentation



## GET Request
![Alt text](resources/get.png)

### Querying Sensors
Sensors are identified by a single integer (for simplicity), and can be appended to the endpoint to get only results for each Sensor.

**Example**: `http://example-endpoint.com/weather-readings?sensor_ids=4,7`
The above example will return any weather readings for sensors 4 and 7. Single or multiple sensors can be queried at once, and if no sensor_id is specified, then all sensors will be included in the response. 

### Querying Metrics


### Querying Statistics


### Combining Queries

## Post Request
![Alt text](resources/post.png)
Below is an example POST request that a sensor would call in order to place a reading into the database. Timestamp is omitted as the Lambda calculates the current time. In theory, a sensor would record a reading which would immediately POST to the API so the timestamp would roughly reflect the time of the reading. Assuming no latency issues the difference would be negligible. 

Command below to POST via Postman or equiovalent.
```
{
    "sensor_id": 1,
    "temperature": 23.4,
    "humidity": 0.5,
    "pressure": 1013.2,
}
```

Command below to POST via terminal
```
curl -X POST -H "Content-Type: application/json" -d '{"sensor_id": 4, "temperature": 20, "humidity": 10, "wind_speed": 5}' https://vcajt5jvr7.execute-api.us-east-1.amazonaws.com/Beta/weather-readings 
```
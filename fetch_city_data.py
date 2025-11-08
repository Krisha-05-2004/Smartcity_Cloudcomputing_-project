import os
import json
import uuid
import urllib.request
import urllib.parse
import boto3
from datetime import datetime


TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "SmartCityEmissions")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY", "")
CITIES = os.environ.get("CITIES", "Bengaluru,Delhi,Mumbai").split(",")


def fetch_city_weather(city, api_key):
    if not api_key:
        raise RuntimeError("OPENWEATHER_KEY not set in environment")
    q = urllib.parse.quote(city)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={q}&appid={api_key}&units=metric"
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.load(resp)


def lambda_handler(event, context):
    """Fetch current weather for configured cities and write a record per city to DynamoDB.

    Environment variables used:
    - OPENWEATHER_KEY: required
    - DYNAMODB_TABLE: defaults to SmartCityEmissions
    - CITIES: comma-separated list of city names
    """
    client = boto3.client("dynamodb")
    results = []

    for city in CITIES:
        city = city.strip()
        if not city:
            continue
        try:
            data = fetch_city_weather(city, OPENWEATHER_KEY)
            temp = None
            if isinstance(data, dict):
                temp = data.get("main", {}).get("temp")

            item = {
                "user_id": {"S": f"city_{city}"},
                "timestamp": {"S": datetime.utcnow().isoformat() + "Z"},
                "activity_type": {"S": "city_weather"},
                "city": {"S": city},
                "record_id": {"S": str(uuid.uuid4())},
                "source": {"S": "fetch_city_data"},
            }

            if temp is not None:
                # store as number
                item["temperature"] = {"N": str(temp)}

            client.put_item(TableName=TABLE_NAME, Item=item)
            results.append({"city": city, "temperature": temp})
        except Exception as e:
            results.append({"city": city, "error": str(e)})

    return {"status": "ok", "results": results}

# lambda_function.py
import json
import os
from datetime import datetime
from decimal import Decimal
from urllib.request import Request, urlopen
from urllib.parse import urlencode

import boto3

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "SmartCityEmissions")
table = dynamodb.Table(TABLE_NAME)

# Optional API keys (leave empty to skip external calls)
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY", "")
CLIMATIQ_KEY = os.environ.get("CLIMATIQ_KEY", "")


def simple_http_post_json(url, body, headers=None):
    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, headers=(headers or {}), method="POST")
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def simple_http_get_json(url):
    req = Request(url, method="GET")
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def calc_travel_emission(distance_km, mode="car"):
    factors = {"car": 0.192, "bus": 0.089, "train": 0.041, "bike": 0.0, "walk": 0.0}
    try:
        return round(factors.get(mode.lower(), 0.2) * float(distance_km), 4)
    except Exception:
        return 0.0


def to_decimal_safe(value, default=None):
    """Convert numeric-like value to Decimal safely; return default if None/invalid."""
    if value is None:
        return default
    try:
        # Use str() to avoid binary float precision issues
        return Decimal(str(value))
    except Exception:
        return default


def sanitize_extra_for_dynamo(extra_dict):
    """
    Convert numbers inside extra to Decimal or strings so DynamoDB accepts them.
    Leaves strings as-is.
    """
    cleaned = {}
    for k, v in (extra_dict or {}).items():
        if v is None:
            continue
        # if it's already a Decimal, keep
        if isinstance(v, Decimal):
            cleaned[k] = v
            continue
        # numbers -> Decimal
        if isinstance(v, (int, float)):
            dec = to_decimal_safe(v)
            if dec is not None:
                cleaned[k] = dec
            else:
                cleaned[k] = str(v)
            continue
        # try parse numeric-like strings
        if isinstance(v, str):
            # try to convert numeric string to Decimal
            try:
                # but avoid converting long text accidentally; attempt simple float cast
                float(v)
                dec = to_decimal_safe(v)
                if dec is not None:
                    cleaned[k] = dec
                else:
                    cleaned[k] = v
            except Exception:
                cleaned[k] = v
            continue
        # fallback: JSON-serialize complex objects into string
        try:
            cleaned[k] = json.dumps(v)
        except Exception:
            cleaned[k] = str(v)
    return cleaned


def lambda_handler(event, context):
    try:
        # Accept event JSON string from CLI or proper dict
        if isinstance(event, str):
            try:
                event = json.loads(event)
            except Exception:
                event = {}

        user_id = event.get("user_id", "anonymous")
        activity_type = event.get("activity_type", "travel")
        city = event.get("city", "Unknown")
        timestamp = event.get("timestamp", datetime.utcnow().isoformat() + "Z")
        mode = event.get("mode", "car")

        # distance may be int/float/str
        try:
            distance_val = float(event.get("distance", 0))
        except Exception:
            distance_val = 0.0

        co2_kg = 0.0
        extra = {}

        if activity_type == "travel":
            co2_kg = calc_travel_emission(distance_val, mode)
            # keep numeric values in extra, but we'll sanitize before put_item
            extra["mode"] = mode
            extra["distance_km"] = distance_val

        # Optional: Climatiq (if CLIMATIQ_KEY set) - example (may need adaptation)
        if CLIMATIQ_KEY and activity_type == "travel":
            try:
                payload = {
                    "emission_factor": {
                        "activity_id": "passenger_vehicle-vehicle_type_car-fuel_source_na-distance_na-engine_size_na"
                    },
                    "parameters": {"distance": distance_val, "distance_unit": "km"},
                }
                headers = {"Authorization": f"Bearer {CLIMATIQ_KEY}", "Content-Type": "application/json"}
                resp = simple_http_post_json("https://beta3.api.climatiq.io/estimate", payload, headers=headers)
                co2_from_api = resp.get("co2e") or resp.get("co2") or (resp.get("data") and resp.get("data").get("co2e"))
                if co2_from_api is not None:
                    co2_kg = float(co2_from_api)
            except Exception as e:
                extra["climatiq_error"] = str(e)

        # Optional: OpenWeather (if OPENWEATHER_KEY set)
        temperature_val = None
        try:
            if OPENWEATHER_KEY:
                params = urlencode({"q": city, "appid": OPENWEATHER_KEY, "units": "metric"})
                url = f"https://api.openweathermap.org/data/2.5/weather?{params}"
                resp = simple_http_get_json(url)
                temperature_val = resp.get("main", {}).get("temp")
        except Exception as e:
            extra["openweather_error"] = str(e)

        # Build item using Decimal for numeric fields (DynamoDB requires Decimal for numbers)
        item = {
            "user_id": user_id,
            "timestamp": timestamp,
            "activity_type": activity_type,
            "mode": mode,
            "city": city,
            "distance": to_decimal_safe(distance_val, Decimal("0")),
            "co2_emission": to_decimal_safe(co2_kg, Decimal("0")),
        }

        if temperature_val is not None:
            dec_temp = to_decimal_safe(temperature_val)
            if dec_temp is not None:
                item["temperature"] = dec_temp

        # sanitize extra: convert numbers to Decimal, strings kept, complex -> json string
        if extra:
            item["extra"] = sanitize_extra_for_dynamo(extra)

        # Remove any keys with value None (DynamoDB doesn't accept None by default)
        cleaned = {k: v for k, v in item.items() if v is not None}

        # Put item
        table.put_item(Item=cleaned)

        # Return the inserted item (note: Decimal not JSON serializable; convert for response)
        def dec_to_native(obj):
            if isinstance(obj, Decimal):
                # if integer-like, return int else float
                if obj == obj.to_integral():
                    return int(obj)
                return float(obj)
            raise TypeError

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Data stored successfully", "item": cleaned}, default=dec_to_native),
        }

    except Exception as e:
        # Log error to CloudWatch and return 500 to caller
        print("Error in lambda:", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

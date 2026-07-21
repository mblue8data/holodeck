import yaml
from pyiceberg.schema import Schema
from pyiceberg.types import StructType, StringType, LongType, TimestampType, BooleanType, DoubleType

# Mapping faker-ish types to Iceberg types
FAKER_TO_ICEBERG = {
    # Strings
    "str": StringType(),
    "word": StringType(),
    "name": StringType(),
    "email": StringType(),
    "address": StringType(),
    "building_number": StringType(),
    "city": StringType(),
    "city_prefix": StringType(),
    "city_suffix": StringType(),
    "country": StringType(),
    "country_code": StringType(),
    "postcode": StringType(),
    "state": StringType(),
    "street_address": StringType(),
    "street_name": StringType(),
    "street_suffix": StringType(),
    "company": StringType(),
    "job": StringType(),
    "hex_color": StringType(),
    "rgb_color": StringType(),
    "currency_code": StringType(),
    "currency_name": StringType(),
    "currency_symbol": StringType(),
    "credit_card_number": StringType(),
    "license_plate": StringType(),
    "domain_name": StringType(),
    "ipv4": StringType(),
    "ipv6": StringType(),
    "mac_address": StringType(),
    "slug": StringType(),
    "url": StringType(),
    "uuid4": StringType(),
    "file_name": StringType(),
    "file_path": StringType(),
    "mime_type": StringType(),
    "paragraph": StringType(),
    "sentence": StringType(),
    "text": StringType(),
    "color_name": StringType(),
    "company_suffix": StringType(),
    "catch_phrase": StringType(),
    "bs": StringType(),
    "simple_profile": StringType(),  # technically a dict but storing as string
    "profile": StringType(),

    # Dates & Time
    "date": TimestampType(),
    "date_time": TimestampType(),
    "datetime": TimestampType(),
    "year": LongType(),
    "time": StringType(),  # could be TimestampType but needs parsing

    # Booleans
    "boolean": BooleanType(),
    "null_boolean": BooleanType(),
    "pybool": BooleanType(),

    # Integers
    "integer": LongType(),
    "int": LongType(),
    "random_digit": LongType(),
    "random_int": LongType(),
    "random_number": LongType(),
    "pyint": LongType(),
    "pages_visited": LongType(),
    "num_sessions": LongType(),
    "credit_score": LongType(),
    "age": LongType(),

    # Doubles/Floats
    "float": DoubleType(),
    "double": DoubleType(),
    "pyfloat": DoubleType(),
    "pydecimal": DoubleType(),
    "annual_income": DoubleType(),
    "last_purchase_amount": DoubleType(),
    "avg_session_duration_min": DoubleType(),

    # Categorical
    "gender": StringType(),
    "subscription_level": StringType(),
}


def schema_from_yaml(yaml_file):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)

    fields = []
    for col in data.get("schema", []):
        name = col["column"]
        dtype = col["dtype"].lower()
        iceberg_type = FAKER_TO_ICEBERG.get(dtype, StringType())
        fields.append((name, iceberg_type))

    return Schema(
        StructType(fields),
        identifier_field_names=["ID"] if any(f[0] == "ID" for f in fields) else []
    )


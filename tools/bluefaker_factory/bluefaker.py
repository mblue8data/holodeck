import pandas as pd
from faker import Faker
import argparse
import sys
import yaml
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from prettytable import PrettyTable
import random
import importlib

# Create an instance of Faker
fake = Faker('en-US')

# Function to generate consistent name and email
def generate_name_and_email():
    name = fake.name()
    uname = name.lower().replace(" ", ".").replace("'", "")
    email = f"{uname}@{fake.domain_name()}"
    return name, email


# Function to map faker_type to faker function
def get_fake_data(faker_type, name=None, email=None, options=None):
    # Handle options if specified
    if faker_type == "random_element" and isinstance(options, list) and options:
        return fake.random_element(elements=options)

    faker_type_mapper = {
        'str': fake.word,
        'name': lambda: name,
        'email': lambda: email,
        'address': fake.address,
        'building_number': fake.building_number,
        'city': fake.city,
        'city_prefix': fake.city_prefix,
        'city_suffix': fake.city_suffix,
        'country': fake.country,
        'country_code': fake.country_code,
        'postcode': fake.postcode,
        'state': fake.state,
        'street_address': fake.street_address,
        'street_name': fake.street_name,
        'street_suffix': fake.street_suffix,
        # Automobiles
        'license_plate': fake.license_plate,
        # Business
        'bs': fake.bs,
        'catch_phrase': fake.catch_phrase,
        'company': fake.company,
        'company_suffix': fake.company_suffix,
        'job': fake.job,
        # Color
        'color_name': fake.color_name,
        'hex_color': fake.hex_color,
        'rgb_color': fake.rgb_color,
        # Credit Card
        'credit_card_expire': fake.credit_card_expire,
        'credit_card_full': fake.credit_card_full,
        'credit_card_number': fake.credit_card_number,
        'credit_card_provider': fake.credit_card_provider,
        'credit_card_security_code': fake.credit_card_security_code,
        # Currency
        'cryptocurrency': fake.cryptocurrency,
        'cryptocurrency_code': fake.cryptocurrency_code,
        'cryptocurrency_name': fake.cryptocurrency_name,
        'currency': fake.currency,
        'currency_code': fake.currency_code,
        'currency_name': fake.currency_name,
        'currency_symbol': fake.currency_symbol,
        # Date and Time
        'am_pm': fake.am_pm,
        'date': fake.date,
        'date_between': fake.date_between,
        'date_time': fake.date_time,
        'day_of_week': fake.day_of_week,
        'month': fake.month,
        'month_name': fake.month_name,
        'time': fake.time,
        'timezone': fake.timezone,
        'year': fake.year,
        # File
        'file_extension': fake.file_extension,
        'file_name': fake.file_name,
        'file_path': fake.file_path,
        'mime_type': fake.mime_type,
        # Internet
        'ascii_company_email': fake.ascii_company_email,
        'ascii_email': fake.ascii_email,
        'ascii_free_email': fake.ascii_free_email,
        'ascii_safe_email': fake.ascii_safe_email,
        'company_email': fake.company_email,
        'domain_name': fake.domain_name,
        'domain_word': fake.domain_word,
        'free_email': fake.free_email,
        'free_email_domain': fake.free_email_domain,
        'ipv4': fake.ipv4,
        'ipv6': fake.ipv6,
        'mac_address': fake.mac_address,
        'safe_email': fake.safe_email,
        'slug': fake.slug,
        'tld': fake.tld,
        'url': fake.url,
        'user_name': fake.user_name,
        # Job
        'job': fake.job,
        # Lorem
        'paragraph': fake.paragraph,
        'paragraphs': fake.paragraphs,
        'sentence': fake.sentence,
        'sentences': fake.sentences,
        'text': fake.text,
        'texts': fake.texts,
        'word': fake.word,
        'words': fake.words,
        # Miscellaneous
        'boolean': fake.boolean,
        'md5': fake.md5,
        'null_boolean': fake.null_boolean,
        'password': fake.password,
        'sha1': fake.sha1,
        'sha256': fake.sha256,
        'uuid4': fake.uuid4,
        # Name
        'first_name': fake.first_name,
        'first_name_female': fake.first_name_female,
        'first_name_male': fake.first_name_male,
        'last_name': fake.last_name,
        'name_female': fake.name_female,
        'name_male': fake.name_male,
        'prefix': fake.prefix,
        'prefix_female': fake.prefix_female,
        'prefix_male': fake.prefix_male,
        'suffix': fake.suffix,
        'suffix_female': fake.suffix_female,
        'suffix_male': fake.suffix_male,
        # Phone Number
        'phone_number': fake.phone_number,
        #'phone_number_formats': fake.phone_number_formats,
        # Profile
        'simple_profile': fake.simple_profile,
        'profile': fake.profile,
        # SSN
        'ssn': fake.ssn,
        # User Agent
        'chrome': fake.chrome,
        'firefox': fake.firefox,
        'internet_explorer': fake.internet_explorer,
        'opera': fake.opera,
        'safari': fake.safari,
        'windows_platform_token': fake.windows_platform_token,
        'linux_platform_token': fake.linux_platform_token,
        'mac_platform_token': fake.mac_platform_token,
        'user_agent': fake.user_agent,
        # Random Data
        'random_digit': fake.random_digit,
        'random_digit_not_null': fake.random_digit_not_null,
        'random_element': fake.random_element,
        'random_int': fake.random_int,
        'random_letter': fake.random_letter,
        'random_number': fake.random_number,
        'random_sample': fake.random_sample,
        #'random_string': fake.random_string,
        'random_choices': fake.random_choices,
        # Barcode
        'ean': fake.ean,
        # Banking
        'bban': fake.bban,
        'iban': fake.iban,
        # Other
        'isbn10': fake.isbn10,
        'isbn13': fake.isbn13,
        'locale': fake.locale,
        'password': fake.password,
        'pybool': fake.pybool,
        'pydecimal': fake.pydecimal,
        'pyfloat': fake.pyfloat,
        'pyint': fake.pyint,
        'pyiterable': fake.pyiterable,
        'pylist': fake.pylist,
        'pyset': fake.pyset,
        'pystr': fake.pystr,
        'pystruct': fake.pystruct,
        'pytimezone': fake.pytimezone,
        'datetime_date': fake.date_object,  # returns datetime.date
        'datetime_range': lambda: fake.date_between(start_date='-2y', end_date='today'),
        'datetime': fake.date_time, 
        # Add to the map
        # Controlled ML-style types
    	'gender': lambda: random.choice(["Male", "Female", "Non-binary"]),
    	'subscription_level': lambda: random.choice(["Free", "Basic", "Premium", "Enterprise"]),
    	'num_sessions': lambda: random.randint(1, 100),
    	'credit_score': lambda: random.randint(300, 850),
    	'annual_income': lambda: random.randint(30000, 200000),
    	'last_purchase_amount': lambda: round(random.uniform(10.0, 1000.0), 2),
    	'avg_session_duration_min': lambda: round(random.uniform(1.0, 90.0), 2),
    	'pages_visited': lambda: random.randint(1, 50),
    	'age': lambda: random.randint(18, 90),

    }

    # Return the generated fake data based on the faker_type
    return faker_type_mapper.get(faker_type, fake.word)()

def generate_row(schema):
    row = {}

    for item in schema['schema']:
        # Generate name/email only if needed
        if item['faker_type'] in ['name', 'email']:
            name, email = generate_name_and_email()
        else:
            name, email = None, None

        # Smart nullable handling: default to 0% if not set
        nullable_chance = item.get("nullable", 0)

        if isinstance(nullable_chance, (int, float)) and nullable_chance > 0:
            if random.uniform(0, 100) < nullable_chance:
                row[item["column"]] = None
                continue  # skip generating data

        # Generate data if not null
        row[item['column']] = get_fake_data(
            item['faker_type'],
            name=name,
            email=email,
            options=item.get("options")
        )

    for domain in schema.get("domains", []):
        try:
            mod = importlib.import_module(f"logic_modules.{domain}")
            row = mod.apply(row)
        except ModuleNotFoundError:
            print(f"[WARN] No logic module found: {domain}")

    return row



# Wrapper function to generate row for multiprocessing
def generate_row_wrapper(schema):
    return generate_row(schema)

# Function to create a DataFrame in parallel
def create_df_parallel(num_rows, schema):
    with ProcessPoolExecutor() as executor:
        rows = list(tqdm(executor.map(generate_row_wrapper, [schema] * num_rows), total=num_rows, colour="#18F6F6"))
    return pd.DataFrame(rows)

def display_pretty_table(df):
    table = PrettyTable()
    table.field_names = df.columns.tolist()
    for row in df.itertuples(index=False, name=None):
        table.add_row(row)
    print(table)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', nargs='*', dest="data_file", help='name for the file -e user_data.parquet')
    parser.add_argument('--records', '-r', nargs='*', dest="num_records", type=str, help='Enter the amount of records like 100 = 100 rows of data')
    parser.add_argument('--format', dest="format_name", type=str, help="Specify the format of the output")
    parser.add_argument('--schema', dest="schema_file", type=str, required=True, help="YAML file containing column names and data types")
    parser.add_argument('--append', '-a', help='Uses 5.7 Grant Syntax', action="store_true")
    args = parser.parse_args()

    # arg conditions
    if args.data_file:
        FNAME = ''.join(args.data_file)
    else:
        # Setting default value
        FNAME = "fake_user_data"

    if args.num_records:
        REC = ''.join(args.num_records)
    else:
        REC = 100

    if args.format_name is None:
        print("Needs 'csv, json or parquet' format argument:\n\
        Usage is: python3 fkdata_generator --file mytestdata --records 1000 --format parquet")
        sys.exit()

    if args.format_name:
        FORMAT = ''.join(args.format_name)
        print("\nGenerating Fake Data with", '\'' + REC + '\'', 'records.... \n')

    REC = int(REC)

    # Read schema YAML to get columns and their data types
    with open(args.schema_file, 'r') as file:
        schema = yaml.safe_load(file)

    df = create_df_parallel(REC, schema)

    def head_it():
        print("\nSample Data:")
        h1 = df.head(3)
        display_pretty_table(h1)

    def Message1():
        MESSAGE = f"\nCreated file: {FNAME}\nNumber of rows added: {REC}\n"
        print(MESSAGE)

    def Message2():
        MESSAGE = f"\nAppended to file: {FNAME}\nNumber of rows added: {REC}\n"
        print(MESSAGE)

    # Write to CSV
    if args.format_name == "csv":
        if args.append:
            head_it()
            FNAME = FNAME + ".csv"
            with open(FNAME, 'a') as f:
                df.to_csv(FNAME, mode='a', index=False)
            Message2()
            sys.exit()
        else:
            head_it()
            FNAME = FNAME + ".csv"
            df.to_csv(FNAME, index=False)
            Message1()
            sys.exit()

    # Write to Parquet
    if args.format_name == "parquet":
        if args.append:
            head_it()
            FNAME = FNAME + ".parquet"
            df.to_parquet(FNAME, engine='fastparquet', append=True)
            Message2()
            sys.exit()
        else:
            FNAME = FNAME + ".parquet"
            df.to_parquet(FNAME)
            head_it()
            Message1()
            sys.exit()

    # Write to Json
    if args.format_name == "json":
        FNAME = FNAME + ".json"
        df.to_json(FNAME, orient='records')
        head_it()
        Message1()
        sys.exit()

    else:
        print("Format not supported must be either 'csv, json or parquet' format.")
    sys.exit()

if __name__ == "__main__":
    main()

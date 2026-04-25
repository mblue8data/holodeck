# blue_fkdata_gen

blue_fkdata_gen is a versatile tool for generating fake data in CSV, Parquet, and JSON formats. It leverages the `faker` module to create realistic fake data and allows easy configuration through YAML files. With blue_fkdata_gen, you can quickly generate files containing anywhere from 100 to millions of rows, all within minutes, thanks to its concurrency capabilities. Additionally, you can append data to existing files.

### Why? 

If you ever need realistic data for testing a pipeline, database, or any other application, blue_fkdata_gen provides a safe and efficient way to create data without using sensitive production data, which can be vulnerable. 

blue_fkdata_gen uses faker functions as the dtypes that are mapped out in the function `get_fake_data()`. Here can see what the avaible mapped out faker types are. There are some  conditions added.  Like name and email I have combined them so you can have the same name as name and email.  ie Bob Smith and bob.smith@whatever.com 

Docs to the faker module:
https://faker.readthedocs.io/en/master/index.html

## Configuration

In your YAML configuration file, specify the columns you want and the corresponding `faker` data types. For example:

```yaml
columns:
  - column: Email_Id
    dtype: email
  - column: Name
    dtype: name
  - column: Gamer_Id
    dtype: user_name
  - column: Device
    dtype: user_agent
  - column: Phone_Number
    dtype: phone_number
```


## Example Usage:

```
python3 blue_fkdata_gen.py --file mytestdata --records 10000 --format parquet --schema test_schema.yml
```

## Sample output
```
Generating Fake Data with '10000' records....

100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10000/10000 [00:05<00:00, 1668.28it/s]

Sample Data:
+-----------------------------+----------------+---------------+-------------------------------------------------------------------------------------------------+--------------------+
|           Email_Id          |      Name      |    Gamer_Id   |                                              Device                                             |    Phone_Number    |
+-----------------------------+----------------+---------------+-------------------------------------------------------------------------------------------------+--------------------+
| roger.schwartz@ferguson.com | Roger Schwartz |   browneric   | Mozilla/5.0 (Windows NT 6.0; ht-HT; rv:1.9.1.20) Gecko/8189-08-02 16:57:46.645020 Firefox/3.6.4 |     9066232881     |
|   edward.james@walker.biz   |  Edward James  |  ravenparker  |                   Mozilla/5.0 (compatible; MSIE 5.0; Windows 95; Trident/3.0)                   | (958)521-2763x1161 |
|   douglas.garza@holmes.biz  | Douglas Garza  | johnsonjoshua |   Mozilla/5.0 (X11; Linux x86_64; rv:1.9.6.20) Gecko/7958-09-05 14:17:35.965302 Firefox/3.6.19  |    564-921-1439    |
+-----------------------------+----------------+---------------+-------------------------------------------------------------------------------------------------+--------------------+

Created file: mytestdata.parquet
Number of rows added: 10000
```

### If you want to  append rows to a file that exist:

```
python3 blue_fkdata_gen.py --file mytestdata --records 10000 --format parquet --schema test_schema.yml -a
```

## To Install

```
pip install -r requirements.txt
```

## Example Workflow for duckdb:

```
# Run the generator based off of schema yml file called game_a_user.yml
# This command created a parquet file of 10,000 records with the schema defined in the yml.

python3 blue_fkdata_gen.py --file game_a_tdata --records 10000 --format parquet --schema game_a_user.yml

Generating Fake Data with '10000' records....

100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10000/10000 [00:06<00:00, 1558.48it/s]

Sample Data:
+--------------------------------+---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+---------------------+-------+
|            Email_Id            |      Name     |  Gamer_Id  |                                                                   Device                                                                  |     Phone_Number    | Spent |
+--------------------------------+---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+---------------------+-------+
|     thomas.riggs@lynch.org     |  Thomas Riggs |  phiggins  | Mozilla/5.0 (iPhone; CPU iPhone OS 4_3_5 like Mac OS X) AppleWebKit/533.0 (KHTML, like Gecko) CriOS/28.0.880.0 Mobile/70R240 Safari/533.0 |  373-318-2820x8911  |  1325 |
|     amber.hurst@hanson.net     |  Amber Hurst  | jennifer65 | Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/532.0 (KHTML, like Gecko) CriOS/51.0.899.0 Mobile/20X692 Safari/532.0 |     389-258-7806    |  7459 |
| carrie.guzman@black-graves.org | Carrie Guzman |  robert20  |          Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_10_3) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/55.0.846.0 Safari/535.1          | +1-348-704-9598x804 |  2157 |
+--------------------------------+---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+---------------------+-------+

Created file: game_a_tdata.parquet
Number of rows added: 10000

# DuckDB is a serverless db which makes it easy to test.
# I am using the  duckcli in this example:

#I am persisting the data by passing the name game_test_data.db but you could do this from memory.

blue_fk_data_gen % duckcli game_test_data.db
Version: 0.2.1
GitHub: https://github.com/dbcli/duckcli
game_test_data.db> SELECT count(*) FROM read_parquet('game_a_tdata.parquet')
+--------------+
| count_star() |
+--------------+
| 10000        |
+--------------+
1 row in set
Time: 0.014s

game_test_data.db> CREATE TABLE game_a_test AS SELECT * FROM read_parquet('game_a_tdata.parquet') WHERE FALSE;
+-------+
| Count |
+-------+
| 0     |
+-------+
1 row in set
Time: 0.013s

game_test_data.db> INSERT INTO game_a_test SELECT * FROM read_parquet('game_a_tdata.parquet');
+-------+
| Count |
+-------+
| 10000 |
+-------+
1 row in set
Time: 0.039s

game_test_data.db> select * from game_a_test limit 5;
+--------------------------------+---------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------+---------------------+-------+
| Email_Id                       | Name          | Gamer_Id       | Device                                                                                                                                    | Phone_Number        | Spent |
+--------------------------------+---------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------+---------------------+-------+
| thomas.riggs@lynch.org         | Thomas Riggs  | phiggins       | Mozilla/5.0 (iPhone; CPU iPhone OS 4_3_5 like Mac OS X) AppleWebKit/533.0 (KHTML, like Gecko) CriOS/28.0.880.0 Mobile/70R240 Safari/533.0 | 373-318-2820x8911   | 1325  |
| amber.hurst@hanson.net         | Amber Hurst   | jennifer65     | Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_5 like Mac OS X) AppleWebKit/532.0 (KHTML, like Gecko) CriOS/51.0.899.0 Mobile/20X692 Safari/532.0 | 389-258-7806        | 7459  |
| carrie.guzman@black-graves.org | Carrie Guzman | robert20       | Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_10_3) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/55.0.846.0 Safari/535.1                   | +1-348-704-9598x804 | 2157  |
| corey.crosby@torres.info       | Corey Crosby  | upowell        | Mozilla/5.0 (compatible; MSIE 7.0; Windows CE; Trident/5.1)                                                                               | 783.733.1686x130    | 9193  |
| andrew.thomas@day-freeman.com  | Andrew Thomas | leonardstephen | Mozilla/5.0 (iPad; CPU iPad OS 17_4 like Mac OS X) AppleWebKit/532.2 (KHTML, like Gecko) FxiOS/18.0g0894.0 Mobile/05E299 Safari/532.2     | (240)462-3874       | 4252  |
+--------------------------------+---------------+----------------+-------------------------------------------------------------------------------------------------------------------------------------------+---------------------+-------+
5 rows in set
Time: 0.009s
game_test_data.db>
```

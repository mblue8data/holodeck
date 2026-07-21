python3 bluefaker.py \
            --file data/raw/churn_data_$(date +"%d-%m-%Y-%H") \
            --records 100000 \
            --format parquet \
            --schema schemas/churn_schema.yml

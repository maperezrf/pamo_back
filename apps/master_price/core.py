from django.db import connection
import re
import pandas as pd 
pd.options.display.max_columns = 500

def read_sql(filename):
    path = r"queries/" + filename +'.sql'
    sql_file = open(path, mode='r', encoding="utf-8")
    return sql_file.read()

def execute_query(query, columns_df):
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=columns_df)
    df = df.fillna('')
    results = [fila.to_dict() for _, fila in df.iterrows()]
    return results
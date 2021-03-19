import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
from ballpark import business
#SPECIFY ALL DATA TYPES
dtype_daily_sales = {
    'Store Code': int,
    'Count of Invoices': 'float64',
    'Sales Qty': 'float64', 
    'COGS': 'float32',
    'Gross Margin': 'float32',
    'Sales Value': 'float32',
}

upper = lambda x: str.upper(x)
converters_daily_sales = {
    'Concept': upper,
    'Territory': upper,
    'Brands': upper,
    'I/E': upper,
    'Store Type': upper,
    'Store Sub Type': upper,
}

dtype_budgeted_daily_sales = {
    'Store Code': int,
    'Sales Qty': 'float64',  
    'Budgeted COGS': 'float32',
    'Budgeted Gross Margin': 'float32',
    'Budgeted Sales Value': 'float32',
}

converters_store_master = {
    'Store Code': int, 
    'Store Name': upper, 
    'Concept': upper,
    'Brand': upper, 
    'Territory': upper, 
    'Region': upper,
    'Sub-Region': upper,
    'Store Type': upper,
    'Store Sub-Type': upper,
    'Mall Name': upper,
    'LFL / Non-LFL': upper,
    'CP / Non-CP': upper,             
}
dtype_store_master = {
    'Area': np.float64,
}

def rename_df_cols_budgeted(col_name):
    if re.search(r"budget(ed)? sales? *(val(ue)?)?", col_name, flags=re.IGNORECASE):
        return "Budgeted Sales Value"
    elif re.search(r"budget(ed)? *cogs|budget(ed)? cost of goods? sold", col_name, flags=re.IGNORECASE):
        return "Budgeted COGS"
    elif re.search(r"budget(ed)? (gross)? margins?", col_name, flags=re.IGNORECASE):
        return "Budgeted Gross Margin"
    else:
        return col_name
        
def rename_df_cols(col_name):
    if re.search(r"sales( val(ue)?)?(?! q)", col_name, flags=re.IGNORECASE):
        return "Sales Value"
    elif re.search(r"cogs|cost of goods? sold", col_name, flags=re.IGNORECASE):
        return "COGS"
    elif re.search(r"(gross)? margins?", col_name, flags=re.IGNORECASE):
        return "Gross Margin"
    elif re.search(r"store sub( |-)type", col_name, flags=re.IGNORECASE):
        return "Store Sub Type"
    elif re.search(r"store( |-)type", col_name, flags=re.IGNORECASE):
        return "Store Type"
    else:
        return col_name

def clean_df_head(df_header, bool_budgeted):
    result_dict = {}
    if bool_budgeted:
        for col_name in df_header:
            result_dict[col_name] = rename_df_cols_budgeted(col_name)
    else:
        for col_name in df_header:
            result_dict[col_name] = rename_df_cols(col_name)
    return result_dict


def df_processor(df, bool_budgeted):
    df.rename(columns=clean_df_head(df.columns, bool_budgeted), inplace=True)
    df.round(1)
    if bool_budgeted:
        df['Budgeted Gross Profit'] = df['Budgeted Gross Margin'] *100/ df['Budgeted Sales Value']
        df.loc[np.isinf(df['Budgeted Gross Profit']), 'Budgeted Gross Profit'] = 0
    else:
        df['Gross Profit'] = df['Gross Margin'] * 100/ df['Sales Value']
        df.loc[np.isinf(df['Gross Profit']), 'Gross Profit'] = 0
    df.merge(store_master_df, on='Store Code', how = 'left')
    return df

custom_date_parser = lambda x: pd.to_datetime(x, errors='coerce',)


store_master_df=pd.read_csv("C:/Users/saksham.bajaj/Documents/RPA Reports/DSR/CSV_files/Store Master.csv", converters=converters_store_master, dtype=dtype_store_master,   
usecols=['Store Code', 'Store Name', 'Concept', 'Brand', 'Territory', 'Region', 'Sub-Region', 'Store Type', 'Store Sub-Type', 'Mall Name', 'LFL / Non-LFL', 'Area', 'Date of Open', 'Date of Close', 'CP / Non-CP', 'Active Status'], low_memory=False)

df_Daily_Sales_17_18 = df_processor(pd.read_csv("C:/Users/saksham.bajaj/Documents/RPA Reports/DSR/CSV_files/Daily Sales 17_18.csv", parse_dates=['Date of Sale'], date_parser = custom_date_parser,
 dtype=dtype_daily_sales, converters = converters_daily_sales, error_bad_lines=False), False)
df_Daily_Sales_18_19 = df_processor(pd.read_csv("C:/Users/saksham.bajaj/Documents/RPA Reports/DSR/CSV_files/Daily Sales 18_19.csv", parse_dates=['Date of Sale'], date_parser = custom_date_parser,
 dtype=dtype_daily_sales, converters = converters_daily_sales, error_bad_lines=False), False)
df_Daily_Sales_19_20 = df_processor(pd.read_csv("C:/Users/saksham.bajaj/Documents/RPA Reports/DSR/CSV_files/Daily Sales 19_20.csv", parse_dates=['Date of Sale'], date_parser = custom_date_parser,
 dtype=dtype_daily_sales, converters = converters_daily_sales, error_bad_lines=False), False)
df_Daily_Sales_20_21 = df_processor(pd.read_csv("C:/Users/saksham.bajaj/Documents/RPA Reports/DSR/CSV_files/Daily Sales 20_21.csv", parse_dates=['Date of Sale'], date_parser = custom_date_parser,
 dtype=dtype_daily_sales, converters = converters_daily_sales, error_bad_lines=False), False)

df_Budget_Daily_Sales_17_18 = df_processor(pd.read_csv("C:/Users/saksham.bajaj/Documents/RPA Reports/DSR/CSV_files/Budget Daily Sales 17_18.csv",  parse_dates=['Budget Date of Sale'], date_parser = custom_date_parser,
converters = converters_daily_sales, dtype=dtype_budgeted_daily_sales, error_bad_lines=False), True)
df_Budget_Daily_Sales_18_19 = df_processor(pd.read_csv("C:/Users/saksham.bajaj/Documents/RPA Reports/DSR/CSV_files/Budget Daily Sales 18_19.csv",  parse_dates=['Budget Date of Sale'], date_parser = custom_date_parser,
converters = converters_daily_sales, dtype=dtype_budgeted_daily_sales, error_bad_lines=False), True)
df_Budget_Daily_Sales_19_20 = df_processor(pd.read_csv("C:/Users/saksham.bajaj/Documents/RPA Reports/DSR/CSV_files/Budget Daily Sales 19_20.csv",  parse_dates=['Budget Date of Sale'], date_parser = custom_date_parser,
converters = converters_daily_sales, dtype=dtype_budgeted_daily_sales, error_bad_lines=False), True)
df_Budget_Daily_Sales_20_21 = df_processor(pd.read_csv("C:/Users/saksham.bajaj/Documents/RPA Reports/DSR/CSV_files/Budget Daily Sales 20_21.csv",  parse_dates=['Budget Date of Sale'], date_parser = custom_date_parser,
converters = converters_daily_sales, dtype=dtype_budgeted_daily_sales, error_bad_lines=False), True)

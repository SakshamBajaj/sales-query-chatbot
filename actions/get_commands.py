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
    df = df.merge(store_master_df, on='Store Code', how = 'left', suffixes = (None, "_b"))
    return df

custom_date_parser = lambda x: pd.to_datetime(x, errors='coerce',)


store_master_df=pd.read_csv("", converters=converters_store_master, dtype=dtype_store_master,   
usecols=['Store Code', 'Store Name', 'Brand', 'Region', 'Sub-Region', 'Store Type', 'Store Sub-Type', 'Mall Name', 'LFL / Non-LFL', 'Area', 'Date of Open', 'Date of Close', 'CP / Non-CP', 'Active Status'], low_memory=False)

df_Daily_Sales_17_18 = df_processor(pd.read_csv("", parse_dates=['Date of Sale'], date_parser = custom_date_parser,
 dtype=dtype_daily_sales, converters = converters_daily_sales, error_bad_lines=False), False)
df_Daily_Sales_18_19 = df_processor(pd.read_csv("", parse_dates=['Date of Sale'], date_parser = custom_date_parser,
 dtype=dtype_daily_sales, converters = converters_daily_sales, error_bad_lines=False), False)
df_Daily_Sales_19_20 = df_processor(pd.read_csv("", parse_dates=['Date of Sale'], date_parser = custom_date_parser,
 dtype=dtype_daily_sales, converters = converters_daily_sales, error_bad_lines=False), False)

df_Daily_Sales_20_21 = df_processor(pd.read_csv("", parse_dates=['Date of Sale'], date_parser = custom_date_parser,
 dtype=dtype_daily_sales, converters = converters_daily_sales, error_bad_lines=False), False)

df_Budget_Daily_Sales_17_18 = df_processor(pd.read_csv("",  parse_dates=['Budget Date of Sale'], date_parser = custom_date_parser,
converters = converters_daily_sales, dtype=dtype_budgeted_daily_sales, error_bad_lines=False), True)
df_Budget_Daily_Sales_18_19 = df_processor(pd.read_csv("",  parse_dates=['Budget Date of Sale'], date_parser = custom_date_parser,
converters = converters_daily_sales, dtype=dtype_budgeted_daily_sales, error_bad_lines=False), True)
df_Budget_Daily_Sales_19_20 = df_processor(pd.read_csv("",  parse_dates=['Budget Date of Sale'], date_parser = custom_date_parser,
converters = converters_daily_sales, dtype=dtype_budgeted_daily_sales, error_bad_lines=False), True)
df_Budget_Daily_Sales_20_21 = df_processor(pd.read_csv("",  parse_dates=['Budget Date of Sale'], date_parser = custom_date_parser,
converters = converters_daily_sales, dtype=dtype_budgeted_daily_sales, error_bad_lines=False), True)

def choose_df_for_date_range(bool_budgeted, start_date, end_date):

    if (start_date>=datetime(2017, 6, 1) and end_date <= datetime(2018, 6, 1)):
        df = df_Budget_Daily_Sales_17_18 if bool_budgeted else df_Daily_Sales_17_18   
    elif (start_date>=datetime(2018, 6, 1) and end_date <= datetime(2019, 6, 1)):
        df=df_Budget_Daily_Sales_18_19 if bool_budgeted else df_Daily_Sales_18_19   
    elif (start_date>=datetime(2019, 6, 1) and end_date <= datetime(2020, 6, 1)):
        df=df_Budget_Daily_Sales_19_20 if bool_budgeted else df_Daily_Sales_19_20
    elif (start_date>=datetime(2020, 6, 1) and end_date <= datetime(2021, 6, 1)):
        df=df_Budget_Daily_Sales_20_21 if bool_budgeted else df_Daily_Sales_20_21
    else:
        raise Exception("Incorrect Date Range") # Make this an error
    
    date_of_sale_header = 'Budget Date of Sale' if bool_budgeted else 'Date of Sale'
    df=filter_by_date_range(df, start_date, end_date, date_of_sale_header)
    return df

def filter_by_date_range(df, start_date, end_date, date_of_sale_header):
    return df[(df[date_of_sale_header] >= start_date) & (df[date_of_sale_header] < end_date)]

def build_single_query(name, value):
    queryString="("
    if isinstance(value, str):
        queryString += "`" + name + "`" + "==" + "'" + value.upper() + "'" + "|"
    else:
        for val in value:
            queryString += "`" + name + "`" + "==" + "'" + val.upper() + "'" + "|"
    queryString = queryString[:-1]
    queryString +=")"
    return queryString 
    
#Takes in dictionary of name:value pairs to build the query for the DataFrame
def build_query(dict_category_name_value):
    query_string=""
    for name, value in dict_category_name_value.items():
        if value is not None:
            query_string+= build_single_query(name, value) + "&"
    return query_string[:-1]

def set_dates(values_dict):
    if values_dict['type']=='interval':
        start_date = (datetime.strptime(values_dict['from']['value'][:10], "%Y-%m-%d"))
        end_date = (datetime.strptime(values_dict['to']['value'][:10], "%Y-%m-%d"))
    else:
        start_date = (datetime.strptime(values_dict['value'][:10], "%Y-%m-%d"))
        end_date = (start_date + get_timedelta_by_grain(values_dict['grain']))

    return start_date, end_date
    
def subtract_one_year(dateobj):
    return dateobj - relativedelta(years=1)

def get_timedelta_by_grain(grain):
    if grain == 'day':
        return relativedelta(days=1)
    elif grain == 'week':
        return relativedelta(weeks=1)
    elif grain == 'month':
        return relativedelta(months=1)
    else:
        return relativedelta(years=1)

def isAllNone(dict):
    for val in dict.values():
        if val is not None:
            return False
    return True

def filter_dataframe(filters, start_date, end_date, bool_budgeted):
    filtered_df=choose_df_for_date_range(bool_budgeted, start_date, end_date)
    if not isAllNone(filters):
        filtered_df = filtered_df.query(build_query(filters)) 
    return filtered_df
    


def get_metric_for_categories_by_date_range(metric, category_filters, store_filters, bool_budgeted, start_date, end_date):
    category_filters.update(store_filters)
    filtered_df = filter_dataframe(category_filters, start_date, end_date, bool_budgeted)
    
    if metric_type(metric) == 'value':
        result=filtered_df[metric].sum()
    else:
        result=filtered_df[metric].mean()

    return result

def get_calculated_metric(calculated_metric, metric, category_filters, store_filters, bool_budgeted, start_date, end_date):
    if calculated_metric.upper() == 'PSF':
        return get_mpd_psf(metric, category_filters, store_filters, bool_budgeted, start_date, end_date)
    elif calculated_metric == 'Budget Achievement':
        return get_budget_achievement_for_categories_by_date_range(metric, category_filters, store_filters, start_date, end_date)
    elif calculated_metric == 'Growth':
        return get_growth_for_categories_by_date_range(metric, category_filters, store_filters, bool_budgeted, start_date, end_date)
    else:
        raise Exception(str(calculated_metric) + " is not a valid calculated metric")

def get_df_with_mpd_psf(metric, category_filters, store_filters, bool_budgeted, start_date, end_date):
    #merge with store columns
    #spd/sqft = metric/sqft
    #df[spd/sqft].mean()
    category_filters.update(store_filters)
    filtered_df = filter_dataframe(category_filters, start_date, end_date, bool_budgeted)
    filtered_df.dropna(subset=['Area'], inplace=True)
    filtered_df = filtered_df[filtered_df.Area>0]
    filtered_df['PSF'] = filtered_df[metric]/filtered_df['Area']
    return filtered_df

def get_df_with_growth(metric, category_filters, store_filters, bool_budgeted, start_date, end_date):
    category_filters.update(store_filters)
    filtered_df_curr = filter_dataframe(category_filters, start_date, end_date, bool_budgeted)
    filtered_df_last = filter_dataframe(category_filters, subtract_one_year(start_date), subtract_one_year(end_date), bool_budgeted)
    filtered_df_curr = filtered_df_curr.merge(filtered_df_last[['Store Code', metric]], on='Store Code', )
    filtered_df_curr['Growth'] = (filtered_df_curr[metric + "_x"] - filtered_df_curr[metric + "_y"])*100/filtered_df_curr[metric + "_y"]
    return filtered_df_curr

def get_df_with_budget_achievement(metric, category_filters, store_filters, start_date, end_date):
    category_filters.update(store_filters)
    filtered_df = filter_dataframe(category_filters, start_date, end_date, False)
    filtered_df_budgeted = filter_dataframe(category_filters, start_date, end_date, True)
    filtered_df = filtered_df.merge(filtered_df_budgeted[['Store Code', 'Budgeted '+ metric]], on='Store Code', )
    filtered_df['Budget Achievement'] = (filtered_df[metric]*100/(filtered_df['Budgeted ' + metric]))
    return filtered_df

def get_mpd_psf(metric, category_filters, store_filters, bool_budgeted, start_date, end_date):
    filtered_df = get_df_with_mpd_psf(metric, category_filters, store_filters, bool_budgeted, start_date, end_date)
    result = filtered_df['PSF'].mean()
    return result



def get_growth_for_categories_by_date_range(metric, category_filters, store_filters, bool_budgeted, start_date, end_date, calculated_metric = None):
    if calculated_metric is None:
        curr_value=get_metric_for_categories_by_date_range(metric, category_filters, store_filters, bool_budgeted, start_date, end_date)
        
        prev_value=get_metric_for_categories_by_date_range(metric, category_filters, store_filters, bool_budgeted, subtract_one_year(start_date), subtract_one_year(end_date))
        
    else:
        curr_value = get_calculated_metric(calculated_metric, metric, category_filters, store_filters, bool_budgeted, start_date, end_date)
        prev_value = get_calculated_metric(calculated_metric, metric, category_filters, store_filters, bool_budgeted, subtract_one_year(start_date), subtract_one_year(end_date))
        
    growth = (((curr_value-prev_value)/prev_value)*100).round(2)
    return growth

def get_budget_achievement_for_categories_by_date_range(metric, category_filters, store_filters, start_date, end_date):
    actual_value = get_metric_for_categories_by_date_range(metric, category_filters, store_filters, False, start_date, end_date)
    budgeted_value = get_metric_for_categories_by_date_range('Budgeted ' + metric, category_filters, store_filters, True, start_date, end_date,)
    budget_achievement = (actual_value/budgeted_value)*100
    return budget_achievement


def get_stores_by_superlative_by_category_by_date_range(metric, superlative, number_of_stores, category_filters, store_filters, bool_budgeted, start_date, end_date, calculated_metric = None): 
    if calculated_metric is not None:
        if calculated_metric == 'Growth':
            selected_df = get_df_with_growth(metric, category_filters, store_filters, bool_budgeted, start_date, end_date)
        elif calculated_metric == 'PSF':
            selected_df = get_df_with_mpd_psf(metric, category_filters, store_filters, bool_budgeted, start_date, end_date)
        elif calculated_metric == 'Budget Achievement':
            selected_df = get_df_with_budget_achievement(metric, category_filters, store_filters, start_date, end_date)
            print(selected_df)
        calculated_df = selected_df[['Store Code', 'Concept', 'Store Name', calculated_metric]].groupby(by = ['Store Code', 'Concept', 'Store Name']).mean()
        metric = calculated_metric
    else:
        category_filters.update(store_filters)
        selected_df = filter_dataframe(category_filters, start_date, end_date, bool_budgeted)
        
        if metric_type(metric) == 'value':
            calculated_df = selected_df[['Store Code', 'Concept', 'Store Name', metric]].groupby(by = ['Store Code', 'Concept', 'Store Name']).sum()
        else:
            calculated_df = selected_df[['Store Code', 'Concept', 'Store Name', metric]].groupby(by = ['Store Code', 'Concept', 'Store Name']).mean()
        
    if superlative.lower()=="best":
        chosen_store_df = calculated_df.nlargest(number_of_stores, metric, keep='all')
    else:
        chosen_store_df = calculated_df.nsmallest(number_of_stores, metric, keep='all')

    chosen_store_df[metric] = chosen_store_df[metric].apply(convert_to_business)
    return chosen_store_df.reset_index().to_html(index=True)

def convert_to_business(num):
    if abs(num) < 0.1:
        return 0
    else:
        num_str = business(abs(num), precision=5, )
        if num < 0:
            return "-"+ num_str
        else:
            return num_str 
    
def metric_type(metric_name):
    if metric_name in ['Gross Profit', 'Growth', 'Budget Achievement']:
        return 'percentage'
    else:
        return 'value'


metrics = ['Gross Profit', 'Gross Margin','Sales Value', 'COGS', 'Sales Qty', ]
budgeted_metrics = [  'Budgeted Sales Value', 'Budgeted COGS', 'Budgeted Gross Margin', 'Budgeted Gross Profit', ]

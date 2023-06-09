import time
import string 
from collections import OrderedDict
import pandas as pd
import json
import time
import requests

import re
from pandas.io.json import json_normalize
import datetime as dt
from dateutil.relativedelta import relativedelta

import math
import os, sys
import ast
import numpy as np
from collections import Counter
import random
import streamlit as st
import warnings
import plotly.express as px
warnings.filterwarnings("ignore", category=FutureWarning )

st.set_page_config(page_title='Active Physician Tracker', page_icon='🫀', layout='wide')

st.header('Physicians Data Analysis')

st.subheader('Number of Issued Licenses Per Quarter')


n_quarters_ago = st.number_input('Number of Months Lookback:', step = 1, min_value=1, value=6)

###

physicians = pd.read_pickle('texas_doctors.pkl')
physicians = physicians.drop_duplicates('license', keep='last')
physicians['issuance_date'] = pd.to_datetime(physicians['issuance_date'], errors = 'coerce')

# physicians['age'] = dt.date.today().year - physicians['birth_year']
# physicians['graduation_year'] = physicians['med_school'].map(lambda x: str(x)[-4:])
# physicians['graduation_year'] = pd.to_numeric(physicians['graduation_year'], errors='coerce')

date_n_quarters_ago = dt.date.today() - relativedelta(months=n_quarters_ago)

physicians = physicians[(physicians['addr1'].str.contains('TX', na=False)) |
						(physicians['addr2'].str.contains('TX', na=False)) |
						(physicians['addr3'].str.contains('TX', na=False)) |
						(physicians['addr4'].str.contains('TX', na=False))]


physicians_og  = physicians.copy()
physicians = physicians[(physicians['issuance_date'].dt.date >= date_n_quarters_ago) & (physicians['issuance_date'].dt.date <= dt.date.today())]



# physicians['full_addr'] = physicians[['addr1', 'addr2', 'addr3', 'addr4']].apply(lambda x: ', '.join(x.astype('string').dropna()), axis=1)
# physicians['full_addr'] = physicians['full_addr'].replace(r'^\s*$', np.nan, regex=True)
# physicians['full_addr'] = physicians['full_addr'].fillna(physicians[['address', 'city']].apply(lambda x: ', '.join(x.astype('string').dropna()), axis=1))

# physicians['state'] = physicians.full_addr.str.extract(', ([A-Z]{2}) [\d]{5}')


physicians_plot = physicians.copy()

physicians_plot.index = physicians_plot['issuance_date']
issued_licenses_per_month = physicians_plot.resample('M')['license'].count()



issued_licenses_per_month = issued_licenses_per_month.rename('Number of Licenses')

issued_licenses_per_month = issued_licenses_per_month.reset_index()
issued_licenses_per_month['issuance_date'] = issued_licenses_per_month['issuance_date'].dt.date

plot = px.bar(issued_licenses_per_month, x='issuance_date', y = 'Number of Licenses', labels={'issuance_date': 'License Issuance Date'})
plot.update_xaxes(showgrid=False)
plot.update_yaxes(showgrid=False)

st.plotly_chart(plot, use_container_width=True)

### 
st.subheader('Active Physicians by City')

active_physicians = physicians_og[(physicians_og['curr_status'] == 'ACTIVE')]

city_geo = pd.read_csv('tx_city_lat_lon.csv')
city_lat_map = pd.Series(city_geo['Lat'].values, index=city_geo['City']).to_dict()
city_lon_map = pd.Series(city_geo['Lon'].values, index=city_geo['City']).to_dict()
active_physicians['lat'] = pd.to_numeric(active_physicians['city'].map(city_lat_map))
active_physicians['lon'] = pd.to_numeric(active_physicians['city'].map(city_lon_map))
active_physicians = active_physicians.dropna(subset=['lat', 'lon'])
# active_physicians['lat']

st.map(active_physicians)

# streamlit_app.py

import streamlit as st
import mysql.connector

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

rows = run_query("SELECT * from mytable;")

# Print results.
for row in rows:
    st.write(f"{row[0]} has a :{row[1]}:")

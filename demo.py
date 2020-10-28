import streamlit as st
import pandas as pd
import numpy as np
import datetime 

st.title('Testing')

DATE_COLUMN = 'date/time'

@st.cache
def load_data(nrows):
    data = pd.read_csv('../../data/covid_metrics_full_time.csv', index_col=0)
    data['date'] = pd.to_datetime(data['date'])
    return data.set_index('date')

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Missouri Cases')

st.line_chart(data[data['state'] == 'Missouri']['cases'])

st.subheader('Missouri Cases Insight')

date = st.sidebar.date_input('Date', datetime.date(2020,1,21))

st.write(data[data.index == str(date)])
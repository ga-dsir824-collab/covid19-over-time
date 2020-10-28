import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime 
import us_states

st.title('Testing')

DATE_COLUMN = 'date/time'

us_state_abbrev = us_states.abbrev_us_state
state = dict(map(reversed, us_state_abbrev.items()))

@st.cache
def load_data(nrows):
    df = pd.read_csv('data/covid_metrics_full_time.csv', index_col=0)

    df['date'] = pd.to_datetime(df['date'])
    df['code'] = [state.get(i) for i in df['state']]
    df['total'] = df['cases'] + df['deaths']

    for col in df.columns:
        df[col] = df[col].astype(str)

    df['text'] = df['state'] + '<br>' + \
        'Date: ' + df['date'].astype('str') + '<br>' + \
        'Cases: ' + df['cases'] + '<br>' + \
        'Deaths: ' + df['deaths']
    return df.set_index('date')

df_load_state = st.text('Loading data...')
df = load_data(10000)
df_load_state.text("Done! (using st.cache)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df)

start = df.index.min()
end = df.index.max()

slider_date = st.slider('Dates', datetime.date(2020,1,21), datetime.date(2020,10,12), datetime.date(2020,1,21))
df_filtered = df[df.index == str(slider_date)]
if st.checkbox('Show filtered data'):
    st.subheader('Filtered data')
    st.write(df_filtered)

fig = go.Figure(data=go.Choropleth(
    locations=df_filtered['code'],
    z=df_filtered['total'],
    locationmode='USA-states',
    colorscale='Reds',
    autocolorscale=False,
    text=df_filtered['text'], # hover text
    marker_line_color='white', # line markers between states
    colorbar_title="Total Affected"
))

fig.update_layout(
    title_text='2020 Covid Metrics over Time<br>(Hover for breakdown)',
    geo = dict(
        scope='usa',
        projection=go.layout.geo.Projection(type = 'albers usa'),
        showlakes=True, # lakes
        lakecolor='rgb(255, 255, 255)'),)

st.plotly_chart(fig, use_container_width=True) 

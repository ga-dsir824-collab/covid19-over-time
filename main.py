import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime 
import us_states
import time

st.title('US Covid Metric Snapshots')
st.write("Application created by Vivian Nguyen in conjunction with General Assembly's DSIR-824 Cohort")

url = 'https://github.com/nytimes/covid-19-data'
if st.button('Link: Data Source, NYTimes: Coronavirus (Covid-19) Data in the United States'):
    webbrowser.open_new_tab(url)

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

df = load_data(10000)

if st.checkbox('Show embedded data'):
    st.subheader('Raw data')
    st.write(df)

start = df.index.min()
end = df.index.max()

st.header('Play Animation:')

datelist = pd.date_range(datetime.date(2020,1,21), datetime.date(2020,10,13))

def interactive_map(filtered_dataframe):
    fig = go.Figure(data=go.Choropleth(
        locations=filtered_dataframe['code'],
        z=filtered_dataframe['total'],
        locationmode='USA-states',
        colorscale='Reds',
        autocolorscale=False,
        text=filtered_dataframe['text'], # hover text
        marker_line_color='white', # line markers between states
        colorbar_title="Total Affected"
    ))

    fig.update_layout(
        title_text=f'USA Covid Snapshot for {str(x)[:10]} <br>(Hover for breakdown)',
        geo = dict(
            scope='usa',
            projection=go.layout.geo.Projection(type = 'albers usa'),
            showlakes=True, # lakes
            lakecolor='rgb(255, 255, 255)'),)

    st.plotly_chart(fig, use_container_width=True)

if st.button('Animate'):
    with st.empty():
        for x in datelist:
            # https://discuss.streamlit.io/t/animate-st-slider/1441/7
            time.sleep(0.06)

            # This API will take a little more work. 
            # Probably a couple more months after that.
            df_filtered_animate = df[df.index == str(x)[:10]]

            interactive_map(df_filtered_animate)

        df_filtered_end = df[df.index == str(datetime.date(2020,10,12))[:10]]
        interactive_map(df_filtered_end)

st.header('Interactive:')
st.write('Move the Slider to show different snapshots of the US and visualize some COVID metrics')
slider_date = st.slider('Snapshot Date', datetime.date(2020,1,21), datetime.date(2020,10,12), datetime.date(2020,1,21))
df_filtered = df[df.index == str(slider_date)]

if st.checkbox('Show filtered data'):
    st.subheader('Filtered data')
    st.write(df_filtered)

interactive_map(df_filtered)

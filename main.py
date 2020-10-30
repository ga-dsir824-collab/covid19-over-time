import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime 
import us_states
import time

st.title('US Covid Metric Snapshots')
st.write("Application created by Vivian Nguyen in conjunction with General Assembly's DSIR-824 Cohort")

st.markdown('[Link: Data Source, NYTimes: Coronavirus (Covid-19) Data in the United States](https://github.com/nytimes/covid-19-data)')

st.markdown('[Visit Our Project Page! - Decoding COVID-19: Alex Fioto, Vivian Nguyen, Varun Mohan](https://github.com/ga-dsir824-collab/project-5)')

DATE_COLUMN = 'date/time'

us_state_abbrev = us_states.abbrev_us_state
state = dict(map(reversed, us_state_abbrev.items()))

@st.cache
def load_data(nrows):
    df = pd.read_csv('data/covid_metrics_full_time.csv', index_col=0)
    df2 = pd.read_csv('data/sme.csv', index_col=0)

    df['date'] = pd.to_datetime(df['date'])
    df['code'] = [state.get(i) for i in df['state']]
    df['total'] = df['cases'] + df['deaths']

    df_temp = df[['code', 'total']]
    df_temp.rename(columns={'code': 'state'}, inplace=True)
    df_temp2 = df2[['STATE', 'Pop']]
    df_temp2.columns = [i.lower() for i in df_temp2.columns]
    df_temp2 = df_temp2.set_index('state')
    key = df_temp2.to_dict()

    df_temp['pop'] = [key.get('pop').get(i) for i in df_temp['state'].copy()]

    df['proportion'] = (df_temp['total'] / df_temp['pop']) * 100

    for col in df.columns:
        df[col] = df[col].astype(str)

    df['text'] = df['state'] + '<br>' + \
        'Date: ' + df['date'].astype('str') + '<br>' + \
        'Cases: ' + df['cases'] + '<br>' + \
        'Deaths: ' + df['deaths'] + '<br>' + \
        'Proportion of Population Affected: ' + df['proportion'] + ' %'
    return df.set_index('date'), df2

df, df2 = load_data(10000)

if st.checkbox('Show raw covid data'):
    st.subheader('Raw data')
    st.write(df)

if st.checkbox('Show mask sentiment, 2016 voting history data'):
    st.subheader('Raw data')
    st.write(df2)

start = df.index.min()
end = df.index.max()

st.header('Play Animation:')

datelist = pd.date_range(datetime.date(2020,1,21), datetime.date(2020,10,13))

def interactive_map(filtered_dataframe, current_date):
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
        title_text=f'USA COVID-19 Snapshot for {str(current_date)[:10]} <br>(Hover for breakdown)',
        geo = dict(
            scope='usa',
            projection=go.layout.geo.Projection(type = 'albers usa'),
            showlakes=True, # lakes
            lakecolor='rgb(255, 255, 255)'),)

    st.plotly_chart(fig, use_container_width=True)

def interactive_map_proportion(filtered_dataframe, current_date):
    fig = go.Figure(data=go.Choropleth(
        locations=filtered_dataframe['code'],
        z=filtered_dataframe['proportion'],
        locationmode='USA-states',
        colorscale='Reds',
        autocolorscale=False,
        text=filtered_dataframe['text'], # hover text
        marker_line_color='white', # line markers between states
        colorbar_title="% Population Affected"
    ))

    fig.update_layout(
        title_text=f'USA COVID-19 Proportion Affected {str(current_date)[:10]} <br>(Hover for breakdown)',
        geo = dict(
            scope='usa',
            projection=go.layout.geo.Projection(type = 'albers usa'),
            showlakes=True, # lakes
            lakecolor='rgb(255, 255, 255)'),)

    st.plotly_chart(fig, use_container_width=True)

if st.button('Animate Total'):
    with st.empty():
        for x in datelist:
            # https://discuss.streamlit.io/t/animate-st-slider/1441/7
            time.sleep(0.06)

            # This API will take a little more work. 
            # Probably a couple more months after that.
            df_filtered_animate = df[df.index == str(x)[:10]]

            interactive_map(df_filtered_animate, x)

        df_filtered_end = df[df.index == str(datetime.date(2020,10,12))[:10]]
        interactive_map(df_filtered_end, datetime.date(2020,10,12))

if st.button('Animate Proportion'):
    with st.empty():
        for x in datelist:
            # https://discuss.streamlit.io/t/animate-st-slider/1441/7
            time.sleep(0.06)

            # This API will take a little more work. 
            # Probably a couple more months after that.
            df_filtered_animate = df[df.index == str(x)[:10]]

            interactive_map_proportion(df_filtered_animate, x)

        df_filtered_end = df[df.index == str(datetime.date(2020,10,12))[:10]]
        interactive_map_proportion(df_filtered_end, datetime.date(2020,10,12))


st.header('Interactive:')
st.write('Move the Slider to show different snapshots of the US and visualize some COVID metrics')
slider_date = st.slider('Snapshot Date', datetime.date(2020,1,21), datetime.date(2020,10,12), datetime.date(2020,1,21))
df_filtered = df[df.index == str(slider_date)]

if st.checkbox('Show filtered data'):
    st.subheader('Filtered data')
    st.write(df_filtered)

interactive_map(df_filtered, slider_date)
interactive_map_proportion(df_filtered, slider_date)
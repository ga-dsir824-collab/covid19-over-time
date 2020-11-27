'''
This is revision two of the data visualization created during GA-DSIR 824
Some updates to the code include:

- Using the NYT data directly with less processing by using county codes 
    and not considering the average per state

- Periodic updates to the dataset by occasionally pulling the data from the
    NYT github
'''

import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime 
import us_states
import time
import git

import datetime
import io
import requests

# Some Streamlit stuff

'''
# US Covid Metric Snapshots

Keep up to date on what is going on in the United States of America through data visualization

Application created by Vivian Nguyen in conjunction with General Assembly's DSIR-824 Cohort

'''
if st.checkbox('View Original Readme Information:'):
    '''
    Legacy Versions of this data visualization can be found by looking in the github repository and loading the file 'ga-dsir-example.py'. 

    Original data can be found in ./data

    Original Application created by Vivian Nguyen in conjunction with General Assembly's DSIR-824 Cohort
    '''

st.markdown('[Link: Data Source, NYTimes: Coronavirus (Covid-19) Data in the United States](https://github.com/nytimes/covid-19-data)')

st.markdown('[Visit Our Project Page! - Decoding COVID-19: Alex Fioto, Vivian Nguyen, Varun Mohan](https://github.com/ga-dsir824-collab/project-5)')

DATE_COLUMN = 'date/time'

us_state_abbrev = us_states.abbrev_us_state
state = dict(map(reversed, us_state_abbrev.items()))

# Download US Population Data and Cache
census_url = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv'

try:
    census_data = pd.read_csv('./data/co-est2019-alldata.csv', index_col=0)
except:
    census_url=requests.get(census_url).content
    census_data = pd.read_csv(io.StringIO(census_url.decode('latin-1')))
    census_data.to_csv('./data/co-est2019-alldata.csv')
    census_data = census_data.drop('Unnamed: 0')

if st.checkbox('Show Census Data:'):
    st.markdown(f"[Source]({census_url})")
    st.write(census_data)
# Load Data from NYT github
url='https://github.com/nytimes/covid-19-data'

try:
    st.text('Loading data from cached repository')
    # check if the repo exists
    repo = git.Repo(path='./covid-19-data')
    st.text(f'Data Loaded at: {repo}')
    # pull repo updates
    st.text('Fetching updates')
    repo.remotes.origin.pull()

    # https://www.programiz.com/python-programming/datetime/timestamp-datetime
    timestamp = repo.commit("master").committed_date
    st.text(f'Commit: {repo.commit("master")} \nFrom {datetime.datetime.fromtimestamp(timestamp)}')
except:
    st.text(f'Could not find existing repo, downloading data from {url}')
    # Clone the whole repo to disk
    git.Repo.clone_from(url='https://github.com/nytimes/covid-19-data', to_path='./covid-19-data')
    repo = git.Repo(path='./covid-19-data')
    assert not repo.bare
    st.text(f'Data Loaded at: {repo}')

@st.cache
def load_data():
    df = pd.read_csv('covid-19-data/us-states.csv')
    df_pop = census_data.copy()

    df_pop = df_pop[df_pop['STNAME'] == df_pop['CTYNAME']]
    df_pop = df_pop[['STNAME', 'POPESTIMATE2019']]
    df_pop = df_pop.rename(columns={'STNAME':'state', 'POPESTIMATE2019':'pop'})
    df_pop = df_pop.set_index('state')
    key = df_pop.to_dict()

    df['pop'] = [key.get('pop').get(i) for i in df['state'].copy()]

    df['date'] = pd.to_datetime(df['date'])
    df['code'] = [state.get(i) for i in df['state']]
    df['total'] = df['cases'] + df['deaths']
    df['proportion'] = round((df['total'] / df['pop']) * 100, 4)

    for col in df.columns:
        df[col] = df[col].astype(str)

    df['text'] = df['state'] + '<br>' + \
    'Date: ' + df['date'].astype('str') + '<br>' + \
    'Cases: ' + df['cases'] + '<br>' + \
    'Deaths: ' + df['deaths'] + '<br>' + \
    'Proportion of Population Affected: ' + df['proportion'] + ' %'

    return df

df = load_data()

if st.checkbox('Show raw covid data'):
    st.subheader('Raw data')
    st.write(df)

# Get the range of the current data
start = df['date'].iloc[0]
end = df['date'].iloc[-1]

# Convert strings to datetime format

start = datetime.datetime.strptime(start, "%Y-%m-%d")
end = datetime.datetime.strptime(end, '%Y-%m-%d')

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

datelist = pd.date_range(start, end)

if st.button('Animate Total'):
    with st.empty():
        for x in datelist:
            # https://discuss.streamlit.io/t/animate-st-slider/1441/7
            time.sleep(0.02)

            # This API will take a little more work. 
            # Probably a couple more months after that.
            df_filtered_animate = df[df['date'] == str(x)[:10]]

            interactive_map(df_filtered_animate, x)

        df_filtered_end = df[df['date'] == str(end)[:10]]
        interactive_map(df_filtered_end, end)

if st.button('Animate Proportion'):
    with st.empty():
        for x in datelist:
            # https://discuss.streamlit.io/t/animate-st-slider/1441/7
            time.sleep(0.02)

            # This API will take a little more work. 
            # Probably a couple more months after that.
            df_filtered_animate = df[df['date'] == str(x)[:10]]

            interactive_map_proportion(df_filtered_animate, x)

        df_filtered_end = df[df['date'] == str(end)[:10]]
        interactive_map_proportion(df_filtered_end, end)

st.header('Interactive:')
st.write('Move the Slider to show different snapshots of the US and visualize some COVID metrics')
slider_date = st.slider('Snapshot Date', start, end, start)
df_filtered = df[df['date'] == str(slider_date)[:10]]

if st.checkbox('Show filtered data'):
    st.subheader('Filtered data')
    st.write(df_filtered)

interactive_map(df_filtered, slider_date)
interactive_map_proportion(df_filtered, slider_date)
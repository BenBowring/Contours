import streamlit as st
import itertools
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go

url = "https://api.opentopodata.org/v1/srtm90m"
colorscale = [[0, 'black'], [1, 'black']]

colors = {
    'background': '#000000',
    'text': '#FFFFFF'
}

# Chunk the request so url doesnt bounce us
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# URL pull, cached so we don't bombard

@st.cache_data
def get_grid(lat_co, lon_co, size, granular):
    
    mod = granular // 2
    size_norm = size / 110.574

    lat_grid = [lat_co + (size_norm * x) for x in range(-mod, mod + 1)]
    lon_grid = [lon_co + (size_norm * x) for x in range(-mod, mod + 1)]

    full_request = [x for x in itertools.product(lat_grid, lon_grid)]
    full_response = []

    for chunk in chunks(full_request, 100):

        json_format_loc = "|".join([str(x[0]) + "," + str(x[1]) for x in chunk])

        pull_params =  {
            "locations": json_format_loc,
            "interpolation": "cubic",
        }

        resp = requests.get(url=url, params=pull_params)
        pull_data = resp.json()

        elev_data = [point['elevation'] for point in pull_data['results']]
        full_response += elev_data

    data = pd.DataFrame(np.array_split(full_response, granular), 
                        index = lat_grid, 
                        columns = lon_grid)

    return data

# Figure Function

@st.cache_data
def update_chart(input1, input2, granularity, size = 2, labels = True):
    
    z_data = get_grid(input1, input2, size, granularity)
    
    fig = go.Figure(data =
        go.Contour(
            z = z_data.values,
            line_smoothing=0.95,
            line_color = 'slategrey',
            line_width = 1.25,
            showscale=False,
            colorscale = colorscale,
            contours=dict(
                showlabels = labels, # show labels on contours
                labelfont = dict( # label font properties
                    size = 14,
                    color = 'slategrey',
                    family = 'Droid Serif'
                )
            )
        
            
        ))

    fig.update_layout(
        yaxis={'visible': False},
        xaxis={'visible': False},
        autosize=True,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}, 
        height=800,

        
       
    )

    fig.add_annotation(text=city,
                  xref="paper", yref="paper", textangle=-90,
                  x=0.95, y=0.95, showarrow=False)
    
    fig.layout.font.family = "Droid Serif"
    fig.layout.font.size = 32
    fig.layout.font.color = 'slategrey'
    
    return fig

# User selection of generation inputs

city = st.sidebar.selectbox('Select City:', ['Belfast', 'Edinburgh', 'New York', 'Rio'])
granularilty = st.sidebar.selectbox('Select Granularity:', ['S', 'M', 'L'])
size = st.sidebar.selectbox('Select Scale:', ['S', 'M', 'L'])
show_labs = st.sidebar.radio('Show Elevation Labels:', ['Nah', 'Yes'])


# Define dicts so we can pull associated values

granny_dict = {'S': 5, 'M': 9, 'L': 15}
size_dict = {'S': 2, 'M': 3, 'L': 5}
label_dict = {'Yes': True, 'Nah': False}
city_dict = {'Belfast': [54.5973, -5.9301], 'Edinburgh': [55.9533, -3.1883], 
             'New York': [40.7128, -74.0060], 'Rio': [-22.9068, -43.1729]}

# Select everything from the inputs on the page

fig = update_chart(city_dict.get(city)[0], city_dict.get(city)[1], 
                   granny_dict.get(granularilty), 
                   size_dict.get(size),
                   label_dict.get(show_labs)
                   )



st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import itertools
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
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
def update_chart(input1, input2, granularity, size = 2, labels = True, line_smooth = 1):
    
    z_data = get_grid(input1, input2, size, granularity)
    
    fig = go.Figure(data =
        go.Contour(
            z = z_data.values,
            line_smoothing=line_smooth,
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
        yaxis={'visible': False,'fixedrange':True},
        xaxis={'visible': False,'fixedrange':True},
        height = 800,
        #width = 2400,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        

    )

    fig.add_annotation(text=city,
                  xref="paper", yref="paper", textangle=-90,
                  x=0.95, y=0.95, showarrow=False)
    
    fig.layout.font.family = "Droid Serif"
    fig.layout.font.size = 32
    fig.layout.font.color = 'slategrey'
    
    return fig


st.sidebar.title("Plot the contour map for a certain city or custom co-ords :globe_with_meridians:")
st.sidebar.write(
    "Adjust the scale & colours of map and adjust to a given ratio for wallpapers downloads if required!"
)
st.sidebar.write(
    "_Source code on my [GitHub](https://github.com/BenBowring/Contours)._"
)

st.sidebar.markdown('#')
st.sidebar.markdown('#')

# User selection of generation inputs

granny_dict = {'S': 5, 'M': 9, 'L': 15}
size_dict = {'S': 2, 'M': 3, 'L': 5}
label_dict = {'Yes': True, 'Nah': False}
city_dict = {'Belfast': [54.5973, -5.9301], 'Edinburgh': [55.9533, -3.1883], 
             'New York': [40.7128, -74.0060], 'Rio': [-22.9068, -43.1729]}



city = st.sidebar.selectbox('Select City:', [x for x in city_dict.keys()])
granularilty = st.sidebar.selectbox('Select Granularity:', ['S', 'M', 'L'])
size = st.sidebar.selectbox('Select Scale:', ['S', 'M', 'L'])

st.sidebar.markdown('#')

side_col_1_1, side_col_1_2 = st.sidebar.columns([1,1], gap = 'large')
with side_col_1_1:
    line_smooth = st.slider('Contour Smoothness:', 0.0, 1.0, 1.0, step = 0.1)

with side_col_1_2:
    show_labs = st.radio('Show Elevation Labels:', ['Nah', 'Yes'], horizontal=True)

st.sidebar.markdown('#')

side_col_1, side_col_2, side_col_3 = st.sidebar.columns([1,1,1], gap = 'small')
with side_col_1:
    background_col = st.color_picker('Background', '#000000')

with side_col_2:
    contour_col = st.color_picker('Contours', '#616375')
    
with side_col_3:
    text_col = st.color_picker('Text', '#616375')

# Define dicts so we can pull associated values



# Select everything from the inputs on the page


fig = update_chart(city_dict.get(city)[0], city_dict.get(city)[1], 
                   granny_dict.get(granularilty), 
                   size_dict.get(size),
                   label_dict.get(show_labs),
                   line_smooth
                   )



st.plotly_chart(fig, use_container_width=True)

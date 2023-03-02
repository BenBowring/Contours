import streamlit as st
import itertools
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# Boring setup stuff for url slug and page width
st.set_page_config(layout="wide")
url = "https://api.opentopodata.org/v1/srtm90m"

# Define a function that chunks the request so url doesnt bounce us
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# Function that creates a grid around the co-ord space and gets elevation at each point
def get_grid(lat_co, lon_co, granular, size):
    
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

# Contour plot function
def update_chart(input1, input2, granularity, size, elev_labels, city_label, line_smooth = 1):
    
    z_data = get_grid(input1, input2, granularity, size)
    
    fig = go.Figure(data =
        go.Contour(
            hoverinfo='none',
            z = z_data.values,
            line_smoothing=line_smooth,
            line_color = st.session_state.ForeCol,
            line_width = 1.25,
            showscale=False,
            colorscale = [[0, st.session_state.BackCol], [1, st.session_state.BackCol]],
            contours=dict(
                showlabels = elev_labels, # show labels on contours
                labelfont = dict( # label font properties
                    size = 14,
                    color = st.session_state.ForeCol,
                    family = 'Droid Serif'
                )
            )
        
            
        ))

    fig.update_layout(
        yaxis={'visible': False,'fixedrange':True},
        xaxis={'visible': False,'fixedrange':True},
        height = 800,
        #width = width,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        

    )

    if city_label:

        fig.add_annotation(text=st.session_state.chart_label,
                    xref="paper", yref="paper", textangle=-90,
                    x=0.95, y=0.95, showarrow=False)
        
        fig.layout.font.family = "Droid Serif"
        fig.layout.font.size = 32
        fig.layout.font.color = st.session_state.TextCol
    
    return fig

# Initiate sidebar with text and the like
st.sidebar.title("Plot the contour map for a certain city or custom co-ordinates  :globe_with_meridians:")
st.sidebar.header(
    "_Adjust the scale & colours of map and hover over to download!_"
)
st.sidebar.write(
    "_Source code on [GitHub](https://github.com/BenBowring/Contours)._"
)

st.sidebar.markdown('#')

# Define dictionaries that hold keys in selections and associated values
scale_dict = {'Small': [5,2], 'Medium': [9,3], 'Large': [15,5]}
label_dict = {'Yes': True, 'Nah': False}
city_dict = {'Belfast': [54.5973, -5.9301], 'Edinburgh': [55.9533, -3.1883], 'New York': [40.7128, -74.0060]}
image_dict = {'800x800': [800, 800], '1920x1080': [1920,1080]}



# Init global variables to be used in labelling and charting

if 'Latitude' not in st.session_state:
    st.session_state.Latitude = city_dict.get('Belfast')[0]
    st.session_state.Longitude = city_dict.get('Belfast')[1]

if 'chart_label' not in st.session_state:
    st.session_state.chart_label = 'Belfast'

# Callback functions for changes in dropdowns and number inputs

def update_coords():
    
    st.session_state.Latitude = city_dict.get(st.session_state.city)[0]
    st.session_state.Longitude = city_dict.get(st.session_state.city)[1]
    
    st.session_state.chart_label = st.session_state.city
    
    return

def update_label():
    
    
    if st.session_state.custom_coords:
        
        st.session_state.chart_label = f"{st.session_state.Latitude}  {st.session_state.Longitude}"

    else:
        st.session_state.chart_label = st.session_state.city
        
    return

# City and co-ordinate selection, updates both lat/long and chart labelling with callbacks

with st.sidebar:
    
        custom_coords = st.checkbox('Custom Co-Ordinates', value = False, key = 'custom_coords', on_change=update_label)
    
        # First selections for city and size of elevation grid
        city = st.selectbox('Select City:', [x for x in city_dict.keys()], on_change = update_coords, disabled=st.session_state.custom_coords, key = 'city')
        scale = st.selectbox('Select Scale:', [x for x in scale_dict.keys()], on_change = update_coords, disabled=st.session_state.custom_coords, key = 'scale')
            
        latlong_cols = st.columns([1,1], gap = 'small')
        
        with latlong_cols[0]:
            lat = st.number_input('Latitude:', -90.0000, 90.0000, step = 0.1, key = 'Latitude', format="%.4f", disabled=not st.session_state.custom_coords)
            
        with latlong_cols[1]:
            long = st.number_input('Longitude:', -180.0000, 180.0000, step = 0.1, key = 'Longitude', format="%.4f", disabled=not st.session_state.custom_coords)
            


# st.sidebar.markdown('#')

# with st.sidebar:

#     size_col = st.columns([1,1], gap = 'small')
        
#     with st.form(key = 'DownloadVals'):

#         with size_col[0]:
            
#             pic_size = st.selectbox('Select Image Size:', [x for x in image_dict.keys()], key = 'ImageSize')
            
# Define reset values that will be used in form state
def resetcolVals():

    st.session_state.Elevation = 'Yes'
    st.session_state.Label = 'Yes'
    st.session_state.BackCol = '#000000'
    st.session_state.ForeCol = '#616375'
    st.session_state.TextCol = '#616375'

st.sidebar.markdown('#')

# Wrap in form to allow resetting of all adjustment values
with st.form(key = 'AppVals'):

    with st.sidebar:

        st.write('Adjust Visuals:')

        side_col_1_1, side_col_1_2 = st.columns([1,1], gap = 'small')

        with side_col_1_1:
            show_elev_labs = st.radio('Show Elevation:', ['Yes', 'Nah'], horizontal=True, key = 'Elevation')

        with side_col_1_2:
            show_city_labs = st.radio('Show Label:', ['Yes', 'Nah'], horizontal=True, key = 'Label')

        side_col_1, side_col_2, side_col_3 = st.columns([1,1,1], gap = 'small')

        with side_col_1:
            background_col = st.color_picker('Background', '#000000', key = 'BackCol')

        with side_col_2:
            contour_col = st.color_picker('Contours', '#616375', key = 'ForeCol')
            
        with side_col_3:
            text_col = st.color_picker('Text', '#616375', key = 'TextCol')

        reset_button = st.form_submit_button(label = 'Reset Visuals', on_click=resetcolVals)



# Call figure chart with all selected variables
fig = update_chart(st.session_state.Latitude, st.session_state.Longitude, 
                   scale_dict.get(scale)[0], 
                   scale_dict.get(scale)[1],
                   label_dict.get(show_elev_labs),
                   label_dict.get(show_city_labs)
                   )



# Plot chart, noting container width var
st.plotly_chart(fig, use_container_width=True)
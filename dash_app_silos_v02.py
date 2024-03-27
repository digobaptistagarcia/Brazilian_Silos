import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Load data
df = pd.read_excel('Base_completa.xlsx')
df = df[['CDA', 'Armazenador', 'Endereço', 'Município', 'UF', 'Tipo', 'Telefone',
         'Email', 'Capacidade (t)', 'lat_ok1', 'Long_ok1']]
df.columns = ['CDA', 'Armazenador', 'Endereco', 'Municipio', 'UF', 'Tipo', 'Telefone',
              'Email', 'Capacidade (t)', 'latitude', 'longitude']


# Create Dash app
app = dash.Dash(__name__)

# Define dropdown options including "All"
dropdown_options = [{'label': 'All', 'value': 'All'}] + [{'label': state, 'value': state} for state in df['UF'].unique()]

# Define app layout
app.layout = html.Div([
    html.H1("Grain Storage Capacity in Brazil"),
    html.H3("Explore grain storage facilities in Brazil by state and capacity."),

    # Dropdown filter for states
    dcc.Dropdown(
        id='state-filter',
        options=dropdown_options,
        value=['All'],  # Default value as a list
        multi=True,
        placeholder="Select a state(s) or 'All'"
    ),

    # Slider for capacity
    html.P('Capacidade (t)'),
    dcc.RangeSlider(
        id="capacity-slider",
        min=0,
        max=300000,
        value=[0, 300000],
        marks={0: '0', 50000: '50,000', 100000: '100,000', 150000: '150,000', 200000: '200,000', 250000: '250,000', 300000: '300,000'},
        step=5000,
    ),

    # Scatter mapbox figure
    dcc.Graph(id='scatter-map', style={'height': '600px'}), 
    
    # Histogram graph
    dcc.Graph(id='histogram'),

    # Bar graph
    dcc.Graph(id='bar-graph')
])

# Callback to update scatter mapbox figure, histogram, and bar graph based on state filter and capacity slider
@app.callback(
    [Output('scatter-map', 'figure'), Output('histogram', 'figure'), Output('bar-graph', 'figure')],
    [Input('state-filter', 'value'),
     Input('capacity-slider', 'value'),
     Input('histogram', 'clickData')]  # Added Input for histogram click
)
def update_plots(selected_states, selected_capacity, clickData):
    if 'All' in selected_states:
        filtered_df = df.copy()  # Copy the entire dataframe for "All" option
    else:
        filtered_df = df[df['UF'].isin(selected_states)]
    
    filtered_df = filtered_df[(filtered_df['Capacidade (t)'] >= selected_capacity[0]) & (filtered_df['Capacidade (t)'] <= selected_capacity[1])]
    
    scatter_fig = px.scatter_mapbox(
        filtered_df,
        lat='latitude',
        lon='longitude',
        hover_name='Armazenador',
        size='Capacidade (t)',
        color='Capacidade (t)',
        color_continuous_scale='Viridis',
        hover_data={'latitude': True, 'longitude': True, 'Capacidade (t)': True},
        zoom=3
    )
    scatter_fig.update_layout(
        mapbox_style='carto-positron',
        mapbox_zoom=4,
        mapbox_center={'lat': -15, 'lon': -55},
        title='Scatter Map of Silos',
        height=800 
    )
    # Histogram graph
    histogram_fig = px.histogram(filtered_df, x='Capacidade (t)', nbins=80, title='Histogram of Capacity',
                                 color_discrete_sequence=['darkblue']) # color of histogram bars)
    histogram_fig.update_xaxes(title_text='Capacity (t)')
    histogram_fig.update_yaxes(title_text='Frequency')
    histogram_fig.update_layout(template='plotly_white')

    # Bar graph 
    bar_data = filtered_df.groupby('UF')['Capacidade (t)'].sum().reset_index()
    bar_data = bar_data.sort_values(by='Capacidade (t)', ascending=False)  # Sort by capacity in descending order
    bar_fig = px.bar(bar_data, x='UF', y='Capacidade (t)', title='Capacity per State',
                     color_discrete_sequence=['darkblue'])
    bar_fig.update_layout(template='plotly_white')

    # Apply filtering based on histogram click
    if clickData is not None:
        selected_capacity = clickData['points'][0]['x']
        filtered_df = filtered_df[filtered_df['Capacidade (t)'] == selected_capacity]
        scatter_fig.update_traces(selectedpoints=None, unselected={'marker': {'opacity': 0.3}})
        scatter_fig.add_trace(px.scatter_mapbox(filtered_df, lat='latitude', lon='longitude').data[0])

    return scatter_fig, histogram_fig, bar_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

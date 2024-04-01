# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site here.",
                 searchable=True
                 ),
    html.Br(),

    html.Div(id='success-pie-chart-container'),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0,  # Starting point of the slider (0 kg)
                    max=10000,  # Ending point of the slider (10,000 kg)
                    step=1000,  # Interval of the slider (1,000 kg)
                    marks={i: str(i) for i in range(0, 10001, 1000)},  # Custom marks for slider ticks
                    value=[min_payload, max_payload]  # Initial selected range
                    ),

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Define callback to update pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        launch_site = spacex_df.groupby('Launch Site')['class'].mean().reset_index()
        fig = px.pie(launch_site, names='Launch Site', values='class', title='Total Success Launches')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        if filtered_df.empty:
            fig = px.pie(names=['Failure', 'Success'], values=[0, 0], title=f'No data available for {selected_site}')
        else:
            fig = px.pie(filtered_df, names='class', title=f'Success and Failure Count for {selected_site}')
    return fig


@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, selected_payload):
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_payload[0]) &
                                (spacex_df['Payload Mass (kg)'] <= selected_payload[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title='Payload vs. Outcome for All Sites')
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                (spacex_df['Payload Mass (kg)'] >= selected_payload[0]) &
                                (spacex_df['Payload Mass (kg)'] <= selected_payload[1])]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                         title=f'Payload vs. Outcome for {selected_site}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()

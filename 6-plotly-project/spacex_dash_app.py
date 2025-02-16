import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df['Payload Mass (kg)'] = pd.to_numeric(spacex_df['Payload Mass (kg)'], errors='coerce')
spacex_df['class'] = pd.to_numeric(spacex_df['class'], errors='coerce')
min_payload = spacex_df['Payload Mass (kg)'].min(skipna=True) if not spacex_df['Payload Mass (kg)'].isna().all() else 0
max_payload = spacex_df['Payload Mass (kg)'].max(skipna=True) if not spacex_df['Payload Mass (kg)'].isna().all() else 10000
app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].dropna().unique()],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, names='Launch Site', title='Total Successful Launches By Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        fig = px.pie(success_counts, values='count', names='class', title=f'Success vs. Failure for {entered_site}')
    return fig
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'), Input('payload-slider', 'value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    low = pd.to_numeric(low, errors='coerce')
    high = pd.to_numeric(high, errors='coerce')
    if entered_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) & (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category' if 'Booster Version Category' in spacex_df.columns else None, title=f'Payload vs. Launch Outcome for {entered_site if entered_site != "ALL" else "All Sites"}')
    return fig
if __name__ == '__main__':
    app.run_server(debug=True)

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Your Mapbox token
token = 'pk.eyJ1Ijoic2ltZW9ud2kxNDEiLCJhIjoiY2x1MnB5ZzMxMDJhOTJtbmR3Y2Q4Nm9kMiJ9.HSaOQoSSZ_X_t8hWR9Ih4g'

# Load data
df = pd.read_csv("/Users/simeonkopf/Documents/visualisationProject/visualisationProject/data/AirplaneCrashwithLATandLong.csv")
df.dropna(subset=["Latitude", "Longitude"], inplace=True)

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Add Year column
df['Year'] = df['Date'].dt.year

# Ensure Fatalities column is numeric, coerce errors and fill NaNs with 0
df['Fatalities'] = pd.to_numeric(df['Fatalities'], errors='coerce').fillna(0).astype(int)

# Convert numeric columns to strings for hover text
df['Ground'] = pd.to_numeric(df['Ground'], errors='coerce').fillna(0).astype(int).astype(str)

# Format hover text
df['hover_text'] = (
    "Date: " + df["Date"].dt.strftime("%Y-%m-%d") + '\n' +
    "Time: " + df["Time"].fillna("") + '\n' +
    "Location: " + df["Location"].fillna("") + '\n' +
    "Operator: " + df["Operator"].fillna("") + '\n' +
    "Flight #: " + df["Flight #"].fillna("") + '\n' +
    "Route: " + df["Route"].fillna("") + '\n' +
    "AC Type: " + df["AC Type"].fillna("") + '\n' +
    "Registration: " + df["Registration"].fillna("") + '\n' +
    "Aboard: " + df["Aboard"].astype(str) + '\n' +
    "Aboard Crew: " + df["Aboard Crew"].astype(str) + '\n' +
    "Fatalities: " + df['Fatalities'].astype(str) + '\n' +
    "Fatalities Crew: " + df["Fatalities Crew"].astype(str) + '\n' +
    "Ground: " + df['Ground'] + '\n' +
    "Summary: " + df["Summary"].fillna("")
)

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Airplane Crashes"),
    dcc.RangeSlider(
        id='year-slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value=[df['Year'].min(), df['Year'].max()],
        marks={str(year): str(year) for year in range(df['Year'].min(), df['Year'].max() + 1, 5)},
        step=1
    ),
    dcc.Graph(id='map-graph'),
    html.Pre(id='map-info'),
    dcc.Graph(id='bar-chart'),
    html.Pre(id='bar-info')
])

@app.callback(
    [Output('map-graph', 'figure'),
     Output('map-info', 'children'),
     Output('bar-chart', 'figure'),
     Output('bar-info', 'children')],
    [Input('year-slider', 'value'),
     Input('map-graph', 'hoverData'),
     Input('bar-chart', 'hoverData')]
)
def update_graphs(selected_years, map_hover_data, bar_hover_data):
    filtered_df = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])]

    # Map figure
    map_fig = go.Figure()

    map_trace = go.Scattermapbox(
        lat=filtered_df["Latitude"],
        lon=filtered_df["Longitude"],
        mode="markers",
        marker=go.scattermapbox.Marker(
            size=10,
            color=filtered_df["Fatalities"],
            colorscale="Reds",
            cmax=filtered_df["Fatalities"].max(),
            cmin=filtered_df["Fatalities"].min(),
            colorbar=dict(
                title="Fatalities",
                tickvals=[filtered_df["Fatalities"].min(), filtered_df["Fatalities"].max()],
                ticktext=[str(filtered_df["Fatalities"].min()), str(filtered_df["Fatalities"].max())],
                len=0.7,
                thickness=15,
                yanchor="top",
                y=1,
            ),
            opacity=0.7,
        ),
        #text=filtered_df['hover_text'],
    )

    map_fig.add_trace(map_trace)

    map_fig.update_layout(
        mapbox=dict(
            style="dark",
            center=dict(lon=0, lat=0),
            zoom=1,
            accesstoken=token
        ),
        margin=dict(r=0, l=0, t=0, b=0)
    )

    map_info = filtered_df['hover_text'].iloc[map_hover_data['points'][0]['pointIndex']] if map_hover_data else ""

    # Bar chart figure
    bar_fig = px.bar(
        filtered_df.groupby('Year').size().reset_index(name='Counts'),
        x='Year',
        y='Counts',
        title='Number of Crashes per Year'
    )

    bar_info = ""  # Placeholder, you can customize this if needed
    if bar_hover_data:
        bar_info = filtered_df['hover_text'].iloc[bar_hover_data['points'][0]['pointIndex']]

    return map_fig, map_info, bar_fig, bar_info

if __name__ == '__main__':
    app.run_server(debug=True)
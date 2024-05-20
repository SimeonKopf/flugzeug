import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

#Mapbox Token hier einfügen
token = 'pk.eyJ1Ijoic2ltZW9ud2kxNDEiLCJhIjoiY2x1MnB5ZzMxMDJhOTJtbmR3Y2Q4Nm9kMiJ9.HSaOQoSSZ_X_t8hWR9Ih4g'

#Daten einlesen
#unterschiedlich weil man für die map den Datenset mit Longitude und latitude braucht
df_map = pd.read_csv("dataset/AirplaneCrashwithLATandLong.csv")
df_bar = pd.read_csv("dataset/AirplaneCrashesandFatalitiesSince190820190820105639.csv")
df_map.dropna(subset=["Latitude", "Longitude"], inplace=True)
df_map['Date'] = pd.to_datetime(df_map['Date'], errors='coerce')
df_map['Year'] = df_map['Date'].dt.year

# String to Numeric
df_map['Fatalities'] = pd.to_numeric(df_map['Fatalities'], errors='coerce').fillna(0).astype(int)
df_map['Ground'] = pd.to_numeric(df_map['Ground'], errors='coerce').fillna(0).astype(int)

df_map['hover_text'] = (
    "Date: " + df_map["Date"].dt.strftime("%Y-%m-%d") + '\n' +
    "Time: " + df_map["Time"].fillna("") + '\n' +
    "Location: " + df_map["Location"].fillna("") + '\n' +
    "Operator: " + df_map["Operator"].fillna("") + '\n' +
    "Flight #: " + df_map["Flight #"].fillna("") + '\n' +
    "Route: " + df_map["Route"].fillna("") + '\n' +
    "AC Type: " + df_map["AC Type"].fillna("") + '\n' +
    "Registration: " + df_map["Registration"].fillna("") + '\n' +
    "Aboard: " + df_map["Aboard"].astype(str) + '\n' +
    "Aboard Crew: " + df_map["Aboard Crew"].astype(str) + '\n' +
    "Fatalities: " + df_map['Fatalities'].astype(str) + '\n' +
    "Fatalities Crew: " + df_map["Fatalities Crew"].astype(str) + '\n' +
    "Ground: " + df_map['Ground'].astype(str) + '\n' +
    "Summary: " + df_map["Summary"].fillna("")
)
#neu Spalten erstellen
df_bar['Date'] = pd.to_datetime(df_bar['Date'], errors='coerce')
df_bar['Year'] = df_bar['Date'].dt.year
df_bar[['Fatalities', 'Ground']] = df_bar[['Fatalities', 'Ground']].fillna(0)
df_bar['Total_Fatalities'] = df_bar['Fatalities'] + df_bar['Ground']

#um den slider korrekt einzubinden
def update_data(start_year, end_year):
    filtered_df = df_bar[(df_bar['Year'] >= start_year) & (df_bar['Year'] <= end_year)]
    fatalities_by_operator = filtered_df.groupby('Operator')['Total_Fatalities'].sum().reset_index()
    top_10_fatalities_by_operator = fatalities_by_operator.sort_values(by='Total_Fatalities', ascending=False).head(10)
    return top_10_fatalities_by_operator

initial_start_year = df_bar['Year'].min()
initial_end_year = df_bar['Year'].max()
initial_data = update_data(initial_start_year, initial_end_year)

# Data für das top 100 diagramm
operator_count = df_map["Operator"].value_counts()
operator_counts_df = pd.DataFrame({'Operator': operator_count.index, 'Count': operator_count.values})
operator_counts_df_top100 = operator_counts_df.iloc[:100]

# Data für das Wochentagsdiagramm
df_map['Weekday'] = df_map['Date'].dt.day_name()
df_map['Total_Fatalities'] = df_map['Fatalities'] + df_map['Ground']
weekday_counts = df_map["Weekday"].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
colors = px.colors.sequential.Inferno[:7]
weekday_fatalities = df_map.groupby("Weekday")["Total_Fatalities"].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Airplane Crashes"),
    dcc.Graph(id='top-100-operators'),
    dcc.Graph(id='weekday-pie-chart'),
    dcc.Graph(id='polar-chart'),
    dcc.RangeSlider(
        id='year-slider',
        min=df_map['Year'].min(),
        max=df_map['Year'].max(),
        value=[df_map['Year'].min(), df_map['Year'].max()],
        marks={str(year): str(year) for year in range(df_map['Year'].min(), df_map['Year'].max() + 1, 5)},
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
     Output('bar-info', 'children'),
     Output('polar-chart', 'figure'),
     Output('top-100-operators', 'figure'),
     Output('weekday-pie-chart', 'figure')],
    [Input('year-slider', 'value'),
     Input('map-graph', 'hoverData'),
     Input('bar-chart', 'hoverData')]
)
#logik zum updaten der Grafik und initaliesriren je nach Slider Postion
def update_graphs(selected_years, map_hover_data, bar_hover_data):
    filtered_df_map = df_map[(df_map['Year'] >= selected_years[0]) & (df_map['Year'] <= selected_years[1])]
    filtered_df_bar = df_bar[(df_bar['Year'] >= selected_years[0]) & (df_bar['Year'] <= selected_years[1])]

    # Map data siehe karte.py
    map_fig = go.Figure()

    map_trace = go.Scattermapbox(
        lat=filtered_df_map["Latitude"],
        lon=filtered_df_map["Longitude"],
        mode="markers",
        marker=go.scattermapbox.Marker(
            size=10,
            color=filtered_df_map["Fatalities"],
            colorscale= px.colors.sequential.Viridis,
            cmax=filtered_df_map["Fatalities"].max(),
            cmin=filtered_df_map["Fatalities"].min(),
            colorbar=dict(
                title="Fatalities",
                tickvals=[filtered_df_map["Fatalities"].min(), filtered_df_map["Fatalities"].max()],
                ticktext=[str(filtered_df_map["Fatalities"].min()), str(filtered_df_map["Fatalities"].max())],
                len=0.7,
                thickness=15,
                yanchor="top",
                y=1,
            ),
            opacity=0.7,
        ),
        #text=filtered_df_map['hover_text'],
    )

    map_fig.add_trace(map_trace)

    map_fig.update_layout(
        mapbox=dict(
            style="light",
            center=dict(lon=0, lat=0),
            zoom=1,
            accesstoken=token
        ),
        margin=dict(r=0, l=0, t=0, b=0)
    )

    map_info = ""
    if map_hover_data:
        try:
            map_info = filtered_df_map['hover_text'].iloc[map_hover_data['points'][0]['pointIndex']]
        except IndexError:
            map_info = ""

    # siehe operatorKillCounter.py.py
    bar_data = update_data(selected_years[0], selected_years[1])

    bar_trace = go.Bar(
        x=bar_data['Operator'],
        y=bar_data['Total_Fatalities'],
        marker=dict(color=bar_data["Total_Fatalities"])
    )

    bar_fig = go.Figure(data=[bar_trace])

    bar_fig.update_layout(
        title='Total Fatalities by Operator (Top 10)',
        xaxis_title='Operator',
        yaxis_title='Total Fatalities',
        xaxis={'categoryorder': 'total descending'}
    )

    bar_info = ""
    if bar_hover_data:
        try:
            bar_hover_info = bar_data.iloc[bar_hover_data['points'][0]['pointIndex']].to_dict()
            bar_info = "\n".join([f"{key}: {value}" for key, value in bar_hover_info.items()])
        except IndexError:
            bar_info = ""

    # siehe top15ACTypeWithThemostKills.py
    polar_data = filtered_df_bar.groupby('AC Type')['Total_Fatalities'].sum().reset_index().nlargest(15, 'Total_Fatalities')

    polar_trace = go.Barpolar(
        r=polar_data['Total_Fatalities'],
        theta=polar_data['AC Type'],
        marker_color="blue"
    )

    polar_fig = go.Figure(data=[polar_trace])

    polar_fig.update_layout(
        title='Top 15 Aircraft Types by Fatalities',
        polar=dict(
            radialaxis=dict(showticklabels=False),
            angularaxis=dict(direction='clockwise')
        )
    )

    # siehe top100Operator.py
    top_100_operators_fig = go.Figure(go.Bar(
        y=operator_counts_df_top100["Count"],
        x=operator_counts_df_top100["Operator"],
        marker=dict(color="blue")
    ))
    top_100_operators_fig.update_layout(
        title='Top 100 Operators by Number of Crashes',
        xaxis_title='Operator',
        yaxis_title='Number of Crashes',
        xaxis={'categoryorder': 'total descending'}
    )

    # Weekday Pie Charts
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'domain'}, {'type': 'domain'}]],
        subplot_titles=("Crashes per Weekday", "Total Fatalities per Weekday")
    )

    pie_crashes = go.Pie(labels=weekday_counts.index, values=weekday_counts.values, marker=dict(colors=colors))
    fig.add_trace(pie_crashes, row=1, col=1)

    pie_fatalities = go.Pie(labels=weekday_fatalities.index, values=weekday_fatalities.values, marker=dict(colors=colors))
    fig.add_trace(pie_fatalities, row=1, col=2)

    fig.update_layout(
        title_text="Crashes and Fatalities per Weekday"
    )

    return map_fig, map_info, bar_fig, bar_info, polar_fig, top_100_operators_fig, fig

if __name__ == '__main__':
    app.run_server(debug=True , port=8051)

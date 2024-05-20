import pandas as pd
from plotly.subplots import make_subplots
from plotly import graph_objects as go
import plotly.express as px
import random


df = pd.read_csv("/Users/simeonkopf/Documents/visualisationProject/visualisationProject/data/AirplaneCrashesandFatalitiesSince190820190820105639.csv")



# Ensure the 'Date' column is in datetime format
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Extract the year from the 'Date' column
df['Year'] = df['Date'].dt.year

# Fill NaN values with 0 for fatalities and ground columns
df[['Fatalities', 'Ground']] = df[['Fatalities', 'Ground']].fillna(0)


# Calculate total fatalities
df['Total_Fatalities'] = df['Fatalities'] + df['Ground']




# Function to update the data based on the selected year range
def update_data(start_year, end_year):
    # Filter the dataframe based on the selected year range
    filtered_df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]
    
    # Group by 'Operator' and sum the 'Total_Fatalities'
    fatalities_by_operator = filtered_df.groupby('Operator')['Total_Fatalities'].sum().reset_index()
    
    # Sort by 'Total_Fatalities' in descending order and get the top 10
    top_10_fatalities_by_operator = fatalities_by_operator.sort_values(by='Total_Fatalities', ascending=False).head(10)

    
    return top_10_fatalities_by_operator

# Initial data for the full range of years
initial_start_year = df['Year'].min()
initial_end_year = df['Year'].max()
initial_data = update_data(initial_start_year, initial_end_year)




# Create the initial bar trace
bar_trace = go.Bar(
    x=initial_data['Operator'],
    y=initial_data['Total_Fatalities'],
    #marker=dict(color=[operator_colors[op] for op in initial_data['Operator']])
    marker=dict(color = initial_data["Total_Fatalities"])

)


# Initialize the figure
fig = go.Figure(data=[bar_trace])

# Create the year range slider
year_range_slider = go.layout.Slider(
    active=0,
    currentvalue={"prefix": "Year: "},
    pad={"t": 50},
    steps=[
        {
            'label': f"{year}",
            'method': 'update',
            'args': [
                {'x': [update_data(year, year)['Operator'].tolist()], 'y': [update_data(year, year)['Total_Fatalities'].tolist()]},
                {'title': f"Total Fatalities by Operator (Top 10) in {year}"}
            ],
        }
        for year in range(initial_start_year, initial_end_year + 1)
    ]
)

# Add the range slider to the layout
fig.update_layout(
    title='Total Fatalities by Operator (Top 10)',
    xaxis_title='Operator',
    yaxis_title='Total Fatalities',
    xaxis={'categoryorder': 'total descending'},
    sliders=[year_range_slider]
)



# Show the figure
fig.show()
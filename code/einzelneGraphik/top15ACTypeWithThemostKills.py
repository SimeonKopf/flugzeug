import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Read the CSV file
df = pd.read_csv("/Users/simeonkopf/Documents/visualisationProject/visualisationProject/data/AirplaneCrashwithLATandLong.csv")

# Aggregate total fatalities by aircraft type
fatalities_by_ac_type = df.groupby('AC Type')['Fatalities'].sum().reset_index()

# Select top 15 aircraft types by total fatalities
top_15_ac_types = fatalities_by_ac_type.nlargest(15, 'Fatalities')

# Filter the original dataframe to include only the top 15 aircraft types
filtered_df = df[df['AC Type'].isin(top_15_ac_types['AC Type'])]

# Sort the filtered dataframe by total fatalities in descending order
filtered_df = filtered_df.sort_values(by='Fatalities', ascending=False)
fig = go.Figure()

# Create a polar bar chart using Plotly Express
x = go.Barpolar(
                   r=filtered_df['Fatalities'],  
                   theta=filtered_df['AC Type'],  # Use 'Fatalities' for the angular position (theta-axis)
                   #title='AC Types with the Most Fatalities',
                   #marker_color = ["#E4FF87", '#709BFF', '#709BFF', '#FFAA70', '#FFAA70', '#FFDF70', '#B6FFB4', '#E4FF87', '#709BFF', '#709BFF', '#FFAA70', '#FFAA70', '#FFDF70', '#B6FFB4']
                   marker_color="blue"
                    # Choose your preferred color scale
                   )
fig.add_trace(x)
fig.update_layout(
    template=None,
    polar = dict(
        radialaxis = dict( showticklabels=False),
        angularaxis = dict(showticklabels=True)
    )
)


fig.show()
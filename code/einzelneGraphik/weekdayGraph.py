import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as ex

df = pd.read_csv("/Users/simeonkopf/Documents/visualisationProject/visualisationProject/data/AirplaneCrashwithLATandLong.csv")

                # Convert the Date column to datetime format
df["Date"] = pd.to_datetime(df["Date"], format='%m/%d/%Y')

df["Weekday"] = df["Date"].dt.day_name()

                # Add a column for total fatalities
df['Total_Fatalities'] = df['Fatalities'] + df['Ground']

                # Calculate the count of crashes per weekday
weekday_counts = df["Weekday"].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

colors = ex.colors.sequential.Inferno[:7]
weekday_fatalities = df.groupby("Weekday")["Total_Fatalities"].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

fig = make_subplots(
                    rows=1, cols=2,
                    specs=[[{'type': 'domain'}, {'type': 'domain'}]],  # Specify the types for each subplot
                    subplot_titles=("Crashes per Weekday", "Total Fatalities per Weekday")
                )

                # Create the pie chart for crashes per weekday
pie = go.Pie(labels=weekday_counts.index, values=weekday_counts.values, marker=dict(colors=colors))
fig.add_trace(pie, row=1, col=1)

bar = go.Pie(labels=weekday_fatalities.index, values=weekday_fatalities.values, marker=dict(colors=colors))
fig.add_trace(bar, row=1, col=2)
fig.show()

                # Update layout 

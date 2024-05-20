import pandas as pd
import plotly.graph_objects as go


        # Load the dataset
df = pd.read_csv("/Users/simeonkopf/Documents/visualisationProject/visualisationProject/data/AirplaneCrashwithLATandLong.csv")
        
operator_count = df["Operator"].value_counts()
operator_counts_df = pd.DataFrame({'Operator': operator_count.index, 'Count': operator_count.values})
        
        # Get the top 100 operators
operator_counts_df_top100 = operator_counts_df.iloc[:100]
        
        # Create the bar chart
fig = go.Figure(go.Bar(
            y=operator_counts_df_top100["Count"],
            x=operator_counts_df_top100["Operator"],
            marker=dict(color="blue")
        ))
        

fig.show()

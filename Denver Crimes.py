# the imports : ________________________________________________________________________________________________________
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import calendar


import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# the dataset ______________________________________________

df = pd.read_csv("crime.csv")
df2 = pd.read_csv("processed_crime.csv")

# ____________________________________________________________________________EDA ________________________________________________________________

slim_df = df[["OFFENSE_TYPE_ID", "OFFENSE_CATEGORY_ID",
              "NEIGHBORHOOD_ID", "IS_CRIME", "IS_TRAFFIC"]]
slim_df = slim_df.dropna()

#  split the month an year from FIRST_OCCURRENCE_DATE_______

slim_df["MONTH"] = df["FIRST_OCCURRENCE_DATE"].apply(
    lambda x: int("{}".format(x.split("/")[0])))
slim_df["YEAR"] = df["FIRST_OCCURRENCE_DATE"].apply(
    lambda x: int("{}".format(x.split("/")[2].split(" ")[0])))

# month name fron month number _____________________________

slim_df["MONTH"] = slim_df["MONTH"].apply(lambda x: calendar.month_abbr[x])
slim_df["CRIME_OR_TRAFFIC"] = slim_df["IS_TRAFFIC"].apply(
    lambda x: "TRAFFIC" if x == 1 else "CRIME")

# slim_df["TIME_TAKEN_TO_REPORT"] = df["REPORTED_DATE"].astype('datetime64[ns]') - df["FIRST_OCCURRENCE_DATE"].astype('datetime64[ns]')
# slim_df["TIME_TAKEN_TO_REPORT_IN_HOURS"] = slim_df["TIME_TAKEN_TO_REPORT"] / np.timedelta64(1, 'h')


# _________________________________________________________________________end EDA ____________________________________________________________________


# Create Labels
crime_category_label = list(df2["OFFENSE_CATEGORY_ID"].value_counts().index)
crime_category_label.append("None")
category_label = slim_df["OFFENSE_CATEGORY_ID"].value_counts().index
category_label = category_label.insert(0, "All Categories")
# the layout ______________________________________________

app.layout = html.Div([
    html.H1("Crimes over Time"),
    dcc.Graph(id="graph1"),
    html.Label([
        "year",
        dcc.Slider(
            id="year",
            min=2016,
            max=2021,
            value=2018,
            marks={
                2016: {"label": "2016"},
                2017: {"label": "2017"},
                2018: {"label": "2018"},
                2019: {"label": "2019"},
                2020: {"label": "2020"},
                2021: {"label": "2021"},
            }
        ),
    ]),

    html.Br([]),
    # Second Input
    html.Label([
        "caused by :",
        dcc.RadioItems(
            id="crime_traffic",
            options=[
               {'label': 'Traffic', 'value': 'IS_TRAFFIC'},
                {'label': 'Crime', 'value': 'IS_CRIME'},
                {'label': 'All', 'value': 'all'}
            ],
            value='all'
        )
    ]),
    html.Br([]),
    html.Br([]),

    html.H1("Crime Categories"),
    dcc.Graph(id="graph2"),
    html.Br([]),
    html.Label([
        "Choose a crime category",
        dcc.Dropdown(
            id='crime_category',
            clearable=False,
            value="None",
            options=[{"label": x, "value": x} for x in crime_category_label]
        )]),

    html.Br([]),
    html.H1("Top 10 "),
    dcc.Graph(id="graph3"),
    html.Label([
        "Choose a Neighborhood", 
        dcc.Dropdown(
        id="my_input",
        options=[
            {"label": "Five Points", "value": "five-points"},
            {"label": "Central Park", "value": "central-park"},
            {"label": "Capitol Hill", "value": "capitol-hill"},
            {"label": "Montbello", "value": "montbello"},
            {"label": "Cbd", "value": "cbd"},
            {"label": "Baker", "value": "baker"},
            {"label": "Lincoln Park", "value": "lincoln-park"},
            {"label": "Civic Center", "value": "civic-center"},
            {"label": "Union Station", "value": "union-station"},
            {"label": "East Colfax", "value": "east-colfax"}],
        value="five-points"),
        ]),

    html.Br([]),
    html.Br([]),
    html.H1("Number of Crimes"),
    dcc.Graph(id="graph4"),
    html.Label([
        "Choose a Category",
        dcc.Dropdown(
            id="category",
            clearable=False, 
            options = [{"label":x, "value":x} for x in category_label],
            value= "All Categories"
            
        ),
 
    ]),
    ])


@app.callback(
    Output('graph1', 'figure'),
    Input('year', 'value'),
    Input('crime_traffic', 'value')
)
def update_figure(val_year, val_crime_traffic):
    slim_df2 = slim_df[slim_df["YEAR"] == val_year]
    slim_df2 = slim_df2.groupby("MONTH").sum()

    if val_crime_traffic == "all":
        return px.line(slim_df2,
                       x=slim_df2.index,
                       y=["IS_TRAFFIC", "IS_CRIME"],
                       title="Number of crimes and Traffics Per Month"
                       )

    else:
        return px.line(slim_df2,
                       x=slim_df2.index,
                       y=val_crime_traffic,
                       title="Number of crimes and Traffics Per Month"
                       )


@app.callback(
    Output('graph2', 'figure'),
    Input('crime_category', 'value'),
)
def update_figure(crime_category):
    if (crime_category == "None"):
        temp_df = df2.groupby("OFFENSE_CATEGORY_ID").mean(
        ).sort_values("TIME_TAKEN_TO_REPORT_IN_HOURS")

        return px.bar(
            data_frame=temp_df,
            x=temp_df.index,
            y="TIME_TAKEN_TO_REPORT_IN_HOURS",
            title="Count of Crimes per Category",
            labels={"x": "Crime Category", "y": "Count"}
        )
    else:
        temp_df = df2[df2["OFFENSE_CATEGORY_ID"] == crime_category].groupby(
            "OFFENSE_TYPE_ID").mean().sort_values("TIME_TAKEN_TO_REPORT_IN_HOURS")
        return px.bar(
            data_frame=temp_df,
            x=temp_df.index,
            y="TIME_TAKEN_TO_REPORT_IN_HOURS",
            title="Count of Crimes per Type",
            labels={"x": "Crime Type", "y": "Count"}
        )


@app.callback(
    Output(component_id="graph3", component_property="figure"),
    Input(component_id="my_input", component_property="value")
)
def update_output(input_value):
    slim_df2 = slim_df[slim_df["NEIGHBORHOOD_ID"] == input_value]
    slim_df2 = slim_df2.groupby('NEIGHBORHOOD_ID')[
        'CRIME_OR_TRAFFIC'].value_counts()
    slim_df2.values
    return px.pie(
        data_frame=slim_df2,
        values=slim_df2.values,
        names=["IS_CRIME", "IS_TRAFFIC"],
        title="Percentage of Crimes and Traffics in Top 10 Neighborhoods in Denver")

#--------------------------

@app.callback(
    Output('graph4', 'figure'),
    Input('category', 'value'),
    
)
def update_figure(val_category):
     if (val_category == "All Categories"):
        return  px.bar(
            data_frame = slim_df,
            x = slim_df["OFFENSE_CATEGORY_ID"].value_counts().index,
            y = slim_df["OFFENSE_CATEGORY_ID"].value_counts().values,
            title = "Number of Crimes per Category",
            text=slim_df["OFFENSE_CATEGORY_ID"].value_counts().values,
            labels = {"x": "Category", "y":"Count of Crimes"}) 
     else:
        test = slim_df[slim_df["OFFENSE_CATEGORY_ID"] == val_category] 
        return  px.bar(
                data_frame = test,
                x = test["OFFENSE_TYPE_ID"].value_counts().index,
                y = test["OFFENSE_TYPE_ID"].value_counts().values,
                title = "Number of Crimes per Type for The selected Category",
                text = test["OFFENSE_TYPE_ID"].value_counts().values, 
                labels = {"x": "Type", "y":"Count of Crimes"}) 



if __name__ == '__main__':
    app.run_server(debug=True, port=8063)

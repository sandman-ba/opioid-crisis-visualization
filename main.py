import json
from urllib.request import urlopen
import polars as pl
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input
from DataProcessing import get_column_names, int_to_column_name

with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as response:
    counties = json.load(response)

mortality_rates_df: pl.LazyFrame = pl.scan_csv("Data/mortality_rates.csv", with_column_names=get_column_names)

app = Dash(__name__)
app.layout = [
    html.H1(children="Opioid Related Mortality in the US", style={"textAlign": "center"}),
    html.Figure([
        html.P("Select a year:"),
        dcc.Slider(min=2010, max=2022, step=1, value=2017, marks={i: f"{i}" for i in range(2010,2023)}, id="select-year"),
        dcc.Graph(id="mortality-graph", style={"height": 1000})
    ])
]

@callback(
    Output("mortality-graph", "figure"),
    Input("select-year", "value")
)
def update_mortality_graph(year: int):
    year_column: str = int_to_column_name(year)
    yearly_mortality_rates_df: pl.LazyFrame = mortality_rates_df.select(["fips", year_column])

    return px.choropleth(yearly_mortality_rates_df.collect(),
                         geojson=counties,
                         locations="fips",
                         color=year_column,
                         scope="usa",
                         color_continuous_scale="bluered",
                         labels={year_column:"mortality rate"}
                         )



if __name__ == "__main__":
    app.run(debug=True)

import json
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from typing import Any
from dash import Dash, html, dcc, callback, Output, Input
from DataProcessing import get_column_names, int_to_column_name

with open("Data/cb_2022_us_county_20m.geojson") as counties_file:
    counties: Any = json.load(counties_file)

roads: pl.LazyFrame = pl.scan_parquet("Data/tl_2021_us_primaryroads.parquet")

interstate_lats: list[float] = []
interstate_lons: list[float] = []
interstate_names: list[str] = []

for interstate_name, _, interstate_lat, interstate_lon in roads.filter(pl.col("type") == "I").collect().iter_rows():
    interstate_lats += interstate_lat + [None]
    interstate_lons += interstate_lon + [None]
    interstate_names += [interstate_name]*len(interstate_lat) + [None]

interstates: pl.LazyFrame = pl.LazyFrame({
    "name": interstate_names,
    "lat": interstate_lats,
    "lon": interstate_lons
})


mortality_rates_df: pl.LazyFrame = pl.scan_csv("Data/mortality_rates.csv", with_column_names=get_column_names)

mortality_figure: go.Figure = px.line_geo(
    interstates.collect(),
    lon = "lon",
    lat = "lat",
    hover_name = "name",
    scope = "usa"
)

app = Dash(__name__)
app.layout = [
    html.H1(children="Opioid Related Mortality in the US", style={"textAlign": "center"}),
    html.Figure([
        dcc.Graph(id="roads-graph", style={"height": 1000}, figure=mortality_figure)
    ]),
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
                         featureidkey="properties.GEOID",
                         locations="fips",
                         color=year_column,
                         scope="usa",
                         color_continuous_scale="bluered",
                         labels={year_column:"mortality rate"}
                         )



if __name__ == "__main__":
    app.run(debug=True)

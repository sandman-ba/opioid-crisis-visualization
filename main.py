import polars as pl
import plotly.graph_objects as go
from json import load as jsonload
from flask import Flask
from typing import Any
from dash import Dash, html, dcc, callback, Output, Input, ctx, Patch
from DataProcessing import get_column_names, int_to_column_name

with open("Data/cb_2022_us_county_20m.geojson") as counties_file:
    counties: Any = jsonload(counties_file)

interstates: pl.LazyFrame = pl.scan_parquet("Data/tl_2021_us_interstates.parquet")
mortality_rates_df: pl.LazyFrame = pl.scan_csv("Data/mortality_rates.csv", with_column_names=get_column_names)
min_year: int = 2010
max_year: int = 2022
default_year: int = 2017
default_column_name: str = int_to_column_name(default_year)

mortality_figure: go.Figure = go.Figure()
mortality_figure.add_trace(
    go.Choropleth(
        geojson = counties,
        featureidkey = "properties.GEOID",
        locations = mortality_rates_df.select("fips").collect()["fips"],
        z = mortality_rates_df.select(default_column_name).collect()[default_column_name],
        colorscale = "bluered",
        colorbar_title = "Mortality Rate",
        name = "Mortality"
    )
)
mortality_figure.add_trace(
    go.Scattergeo(
        lon = interstates.select("lon").collect()["lon"],
        lat = interstates.select("lat").collect()["lat"],
        hovertext = interstates.select("name").collect()["name"],
        mode = "lines",
        line = {"color": "black", "width": 2},
        name = "Interstates",
        visible = False
    )
)
mortality_figure.update_layout(geo_scope = "usa")

def update_mortality(year: int) -> Patch:
    year_column: str = int_to_column_name(year)
    mortality_patch = Patch()
    mortality_patch.data[0]["z"] = list(mortality_rates_df.select(year_column).collect()[year_column])
    return mortality_patch

def update_interstates(button_state: int) -> go.Figure:
    interstates_patch = Patch()
    if button_state % 2 != 0:
        interstates_patch.data[1]["visible"] = True
    else:
        interstates_patch.data[1]["visible"] = False
    return interstates_patch


server = Flask("opioid-crisis-visualization")
app = Dash(server=server)
app.layout = [
    html.H1(children="Opioid Related Mortality in the US", style={"textAlign": "center"}),
    html.Aside([
        html.Button("Toggle Interstates", id="toggle-interstates", n_clicks=0)
    ]),
    html.Figure([
        html.P("Select a year:"),
        dcc.Slider(min=min_year, max=max_year, step=1, value=default_year, marks={i: f"{i}" for i in range(min_year,max_year + 1)}, id="select-year"),
        dcc.Graph(id="mortality-graph", style={"height": 1000}, figure=mortality_figure)
    ])
]

@callback(
    Output("mortality-graph", "figure"),
    Input("select-year", "value"),
    Input("toggle-interstates", "n_clicks"),
    prevent_initial_call = True
)
def update_mortality_graph(year: int, button_state: int) -> go.Figure:
    trigger_id = ctx.triggered_id
    if trigger_id == "select-year":
        return update_mortality(year)
    elif trigger_id == "toggle-interstates":
        return update_interstates(button_state)


if __name__ == "__main__":
    app.run(debug=True)

import polars as pl
import plotly.express as px
import json
from dash import Dash, html, dcc, callback, Output, Input
from urllib.request import urlopen
from DataProcessing import get_column_names

with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as response:
    counties = json.load(response)

mortality_rates_df = pl.scan_csv("Data/mortality_rates.csv",
                                 with_column_names=get_column_names)

years_dict = {index : year for index, year in enumerate(mortality_rates_df.collect_schema().names()[1:])}

app = Dash(__name__)

app.layout = [
    html.H1(children="Opioid Related Mortality in the US", style={"textAlign": "center"}),
    dcc.Slider(marks=years_dict, value=1, id="slider-selection"),
    dcc.Graph(id="mortality-graph", style={"height": 1000})
]

@callback(
    Output("mortality-graph", "figure"),
    Input("slider-selection", "value")
)
def update_mortality_graph(year: int):
    yearly_mortality_rates_df = mortality_rates_df.select(["fips", years_dict[year]])
    return px.choropleth_map(yearly_mortality_rates_df.collect(), geojson=counties, locations="fips", color=years_dict[year],
                            color_continuous_scale="bluered",
                            map_style="carto-positron",
                            zoom=3, center = {"lat": 37.0902, "lon": -95.7129},
                            opacity=0.5,
                            labels={years_dict[year]:"mortality rate"})


def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    main()

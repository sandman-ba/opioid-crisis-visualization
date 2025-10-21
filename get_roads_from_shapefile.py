import geopandas as gps
import polars as pl


def main() -> None:
    roads_from_shapefile: gps.GeoDataFrame = gps.read_file("Data/tl_2021_us_primaryroads.zip")

    roads_lats: list[list[float]] = []
    roads_lons: list[list[float]] = []
    roads_names: list[str] = []
    roads_types: list[str] = []

    for road_geometry, road_name, road_type in zip(roads_from_shapefile.geometry, roads_from_shapefile.FULLNAME, roads_from_shapefile.RTTYP):
        x, y = road_geometry.xy
        roads_lats.append(list(y))
        roads_lons.append(list(x))
        roads_names.append(road_name)
        roads_types.append(road_type)

    roads_for_plotly: pl.LazyFrame = pl.LazyFrame({
        "name": roads_names,
        "type": roads_types,
        "lat": roads_lats,
        "lon": roads_lons
    })
    roads_for_plotly.sink_parquet("Data/tl_2021_us_primaryroads.parquet")

if __name__ == "__main__":
    main()

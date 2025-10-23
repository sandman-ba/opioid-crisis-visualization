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

    interstate_lats: list[float] = []
    interstate_lons: list[float] = []
    interstate_names: list[str] = []

    for interstate_name, _, interstate_lat, interstate_lon in roads_for_plotly.filter(pl.col("type") == "I").collect().iter_rows():
        interstate_lats += interstate_lat + [None]
        interstate_lons += interstate_lon + [None]
        interstate_names += [interstate_name]*len(interstate_lat) + [None]

    interstates: pl.LazyFrame = pl.LazyFrame({
        "name": interstate_names,
        "lat": interstate_lats,
        "lon": interstate_lons
    })

    interstates.sink_parquet("Data/tl_2021_us_interstates.parquet")


if __name__ == "__main__":
    main()

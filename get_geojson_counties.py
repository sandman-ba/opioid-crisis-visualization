import geopandas as gps

def main() -> None:
    counties = gps.read_file("Data/cb_2022_us_county_20m.zip")
    counties.to_file("Data/cb_2022_us_county_20m.geojson", driver="GeoJSON")

if __name__ == "__main__":
    main()

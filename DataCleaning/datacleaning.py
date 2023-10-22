import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon
import datetime 

def clean_data(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:

    # Remove any incomplete rows
    df = gdf.dropna()
    
    # Keep only relevant columns
    df = df[['AreaHa', 'StartDate', 'EndDate', 'Label', 'FireName', 'geometry']]

    # Consider only wildfires
    df = df[df['Label'].str.contains('Wildfire')]
    
    filter_list = df['StartDate'].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").year > 2009 if x is not None else False)
    # Only use data after 2010
    df = df[filter_list]

    # Convert releant columns into integers
    df['AreaHa'] = df['AreaHa'].apply(lambda x: int(x) * 1e4)  # Area in square metres
    
    df.reset_index(drop=True, inplace=True)
    return df


def get_nsw_outline_gdf(filename='StateBoundary/SED_2022_AUST_GDA94.shp'):
    state_boundaries = gpd.read_file('StateBoundary/SED_2022_AUST_GDA94.shp')
    nsw = state_boundaries[state_boundaries['STE_NAME21'] =='New South Wales']
    nsw_outline = nsw.unary_union
    geometry = gpd.GeoSeries([nsw_outline])
    nsw_gdf = gpd.GeoDataFrame(geometry, columns=['geometry'])
    
    # Set CRS
    if nsw_gdf.crs is None:
        nsw_gdf = nsw_gdf.set_crs('EPSG:4283')
    
    # Reduce the island off the coast of the mainland
    multi_polygon = nsw_gdf['geometry'][0]

    # Initialize variables to keep track of the largest area and geometry
    largest_area = 0
    largest_body = None

    # Iterate through the individual geometries in the MultiPolygon
    for body in multi_polygon.geoms:
        if body.area > largest_area:
            largest_area = body.area
            largest_body = body

    # Create a new MultiPolygon containing only the largest body
    new_multi_polygon = MultiPolygon([largest_body])
    nsw_gdf['geometry'] = [new_multi_polygon]
    return nsw_gdf


def get_and_clean_gdf(filename: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(filename)
    # Convert Date into Datetime
    gdf['StartDate'] = gdf['StartDate'].apply(lambda x: datetime.datetime.strptime(x[:10], "%Y-%m-%d").date())
    gdf['EndDate'] = gdf['EndDate'].apply(lambda x: datetime.datetime.strptime(x[:10], "%Y-%m-%d").date())
    return gdf


def main():

    bushfires_gdf_uncleaned = gpd.read_file('DataCleaning/NPWSFireHistory.shp')
    bushfires_gdf = clean_data(bushfires_gdf_uncleaned)
    bushfire_data_cleaned = bushfires_gdf.to_file('BushfireDataCleaned.shp', driver="ESRI Shapefile")
    bushfire_data_cleaned



if __name__ == '__main__':
    main()
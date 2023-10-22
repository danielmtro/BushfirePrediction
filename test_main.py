from DataCleaning.datacleaning import get_and_clean_gdf


def main():
    bushfire_gdf = get_and_clean_gdf('BushfireDataCleaned/BushfireDataCleaned.shp')
    print(bushfire_gdf)


if __name__ == '__main__':
    main()
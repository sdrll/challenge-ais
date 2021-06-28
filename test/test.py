import json
import unittest

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

import sys

sys.path.append('../src')

import AIS_loader


class AISTest(unittest.TestCase):
    def test_oriented_bounding_box_creation_from_csv(self):
        geojson_output_filepath = './test.geojson'
        ais_df = pd.read_csv('ais_test.csv', delimiter=',')
        ais_gdf = gpd.GeoDataFrame(ais_df, geometry=gpd.points_from_xy(ais_df['Longitude'], ais_df['Latitude']),
                                   crs='epsg:4326')
        DAL = AIS_loader.DanishAisLoader()
        DAL.save_ais_labels_in_geojson(ais_gdf, geojson_output_filepath)

        with open(geojson_output_filepath) as jsonfile:
            geojson_result = json.load(jsonfile)

        assert len(geojson_result['features']) == 53
        assert int(geojson_result['features'][0]['properties']['Length']) == 24
        assert Polygon(geojson_result['features'][0]['geometry']['coordinates'][0]) == Polygon(
            [[12.216159, 54.513057], [12.216375, 54.513057], [12.216375, 54.513099], [12.216159, 54.513099],
             [12.216159, 54.513057]])


if __name__ == '__main__':
    unittest.main()

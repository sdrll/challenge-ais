import os
from datetime import datetime

import geojson
import geopandas as gpd
import pandas as pd
import pyproj
import shapely
from shapely import affinity
from shapely.geometry import Polygon
from shapely.ops import transform
from tqdm import tqdm

from src.AIS_loader import DanishAisLoader
from src.sentinel_download import SentinelHubDownloader


def transform_shapelist(shapelist, target_crs, source_crs='epsg:4326'):
    """
    Transforms shapes from epsg:4326 (or another given source_crs) to another coordinate system
    :param shapelist: list of shapely.geometries
    :param target_crs: string of target coordinate system, like 'epsg:xxxx'
    :return: list of shapely.geometries (like input)
    """

    project = pyproj.Transformer.from_proj(source_crs, target_crs, always_xy=True).transform
    return [shapely.ops.transform(project, shape) for shape in shapelist]


def ais2geojson(ais_gdf, s2_tile_dict, output_folder_path: str):
    filtered_df = ais_gdf[(ais_gdf['Width'].notnull()) & (ais_gdf['Type of mobile'].str.startswith('Class'))]

    features = []

    for index, row in filtered_df.iterrows():
        reprojected_ship_point = transform_shapelist([row.geometry], 'epsg:3857')[0]
        ship_polygon = Polygon(
            [(reprojected_ship_point.x - (row["Length"] / 2), reprojected_ship_point.y - (row["Width"] / 2)),
             (reprojected_ship_point.x + (row["Length"] / 2), reprojected_ship_point.y - (row["Width"] / 2)),
             (reprojected_ship_point.x + (row["Length"] / 2), reprojected_ship_point.y + (row["Width"] / 2)),
             (reprojected_ship_point.x - (row["Length"] / 2), reprojected_ship_point.y + (row["Width"] / 2))])
        if not pd.isna(row["Heading"]):
            ship_polygon = affinity.rotate(ship_polygon, row["Heading"])
        ship_polygon = transform_shapelist([ship_polygon], 'epsg:4326', 'epsg:3857')[0]
        features.append(geojson.Feature(geometry=ship_polygon,
                                        properties={'Length': row["Length"], 'Timestamp': str(row["# Timestamp"])}))

    geojson_filename = f'{s2_tile_dict["properties"]["title"]}.geojson'
    with open(os.path.join(output_folder_path, geojson_filename), 'w', encoding='utf8') as fp:
        geojson.dump(geojson.FeatureCollection(features), fp, sort_keys=True, ensure_ascii=False)


if __name__ == '__main__':
    input_folder_path = '/opt/data/input'
    output_folder_path = '/opt/data/output'

    for ais_csv_filename in os.listdir(input_folder_path):
        ais_processing_date = os.path.splitext(ais_csv_filename)[0].split('_')[1]
        ais_processing_date_formatted = datetime.strptime(ais_processing_date, '%Y%m%d').strftime('%Y-%m-%d')
        SHD = SentinelHubDownloader()
        resp = SHD.request_daily_images(ais_processing_date_formatted, 53.3, 3.22, 59.1, 16.6)
        DAL = DanishAisLoader()

        ais_df = pd.read_csv(os.path.join(input_folder_path, ais_csv_filename), delimiter=',')

        for s2_tile_dict in tqdm(resp):
            print(s2_tile_dict["properties"]["title"])
            AIS_data = DAL.load_csv(ais_df, s2_tile_dict["properties"]["startDate"],
                                    s2_tile_dict["properties"]["completionDate"])
            s2_tile_shape = Polygon(s2_tile_dict['geometry']['coordinates'][0][0])
            ais_gdf_clipped = gpd.clip(AIS_data, s2_tile_shape)
            if len(ais_gdf_clipped) > 0:
                output_day_folder = os.path.join(output_folder_path, ais_processing_date_formatted)
                os.makedirs(output_day_folder, exist_ok=True)
                ais2geojson(ais_gdf_clipped, s2_tile_dict, output_day_folder)

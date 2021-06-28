import os
from datetime import datetime

import geojson
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
from tqdm import tqdm

from challenge.Part_2.repository.src.utils import create_ship_oriented_bounding_box_polygon
from src.AIS_loader import DanishAisLoader
from src.sentinel_download import SentinelHubDownloader

input_folder_path = '../data/input'
output_folder_path = '../data/output/test'

if __name__ == '__main__':

    # for each AIS csv
    for ais_csv_filename in os.listdir(input_folder_path):
        ais_processing_date = os.path.splitext(ais_csv_filename)[0].split('_')[1]
        ais_processing_date_formatted = datetime.strptime(ais_processing_date, '%Y%m%d').strftime('%Y-%m-%d')
        SHD = SentinelHubDownloader()
        resp = SHD.request_daily_images(ais_processing_date_formatted, 53.3, 3.22, 59.1, 16.6)
        DAL = DanishAisLoader()
        ais_df = pd.read_csv(os.path.join(input_folder_path, ais_csv_filename), delimiter=',')

        # for each satellite images available
        for s2_tile_dict in tqdm(resp):
            ais_filter_per_time = DAL.filter_unique_ship_location_with_timestamp(ais_df,
                                                                                 s2_tile_dict["properties"][
                                                                                     "startDate"],
                                                                                 s2_tile_dict["properties"][
                                                                                     "completionDate"])
            s2_tile_shape = Polygon(s2_tile_dict['geometry']['coordinates'][0][0])
            ais_filter_per_time_and_clip_per_s2_tile = gpd.clip(ais_filter_per_time, s2_tile_shape)
            output_day_folder = os.path.join(output_folder_path, ais_processing_date_formatted)
            os.makedirs(output_day_folder, exist_ok=True)
            DAL.ais2geojson(ais_filter_per_time_and_clip_per_s2_tile,
                            os.path.join(output_folder_path, f'{s2_tile_dict["properties"]["title"]}.geojson'))

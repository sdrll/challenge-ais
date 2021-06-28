# Contains data from the Danish Maritime Authority that is used in accordance with the conditions for the use of Danish public data.
import os
import shutil
import urllib.request as request
from contextlib import closing
from datetime import datetime, timedelta

import geopandas as gpd
import pandas as pd
from tqdm import tqdm


class DanishAisLoader:
    def __init__(self):
        pass

    def filter_unique_ship_location_with_timestamp(self, ais_df: str, min_timestamp: str, max_timestamp: str):
        """
        Filter ship location per date to get only location matching to the satellite images. Convert the dataframe into
        a GeoDataFrame to clip location easily

        :param ais_df: Dataframe with every location points from AIS for a whole day
        :param min_timestamp: minimal timestamp to keep
        :param max_timestamp: maximal timestamp to keep
        :return GeoDataframe with unique ship point location close to the satellite image timestamp
        """

        start_date = datetime.strptime(min_timestamp, '%Y-%m-%dT%H:%M:%SZ') - timedelta(seconds=5)
        end_date = datetime.strptime(max_timestamp, '%Y-%m-%dT%H:%M:%SZ') + timedelta(seconds=4)
        ais_df['# Timestamp'] = pd.to_datetime(ais_df['# Timestamp'])

        ais_df_date_filtred = ais_df[(ais_df['# Timestamp'] >= start_date) & (ais_df['# Timestamp'] <= end_date)]
        ais_df_date_filtred_unique = ais_df_date_filtred.drop_duplicates(subset=["MMSI"])

        return gpd.GeoDataFrame(ais_df_date_filtred_unique,
                                geometry=gpd.points_from_xy(ais_df_date_filtred_unique['Longitude'],
                                                            ais_df_date_filtred_unique['Latitude']),
                                crs='epsg:4326')

    def list_available_files(self):
        "List available files on Danish Maritime Authority FTP"
        ftp = "ftp://ftp.ais.dk/ais_data"
        with closing(request.urlopen(ftp)) as response:
            return response.readlines()

    def download_csv(self, date: str):
        """
        :param date: date to download in format YYYY-MM-DD (ex: "2021-01-01")
        :return:
        """
        available_files = self.list_available_files()
        file_name = f"aisdk_{date.replace('-', '')}.csv"
        output_path = os.path.join("output", file_name)
        assert True in [file_name in str(f) for f in available_files], "Date not available"

        ftp = f"ftp://ftp.ais.dk/ais_data/{file_name}"
        response = request.urlopen(ftp)

        with tqdm.wrapattr(open(output_path, "wb"), "write",
                           miniters=1,
                           total=getattr(response, 'length', None)) as file:
            shutil.copyfileobj(response, file)
        return output_path

from sentinelhub import (
    CRS,
    BBox,
    opensearch
)


class SentinelHubDownloader:
    def __init__(self, max_tries: int = 6):
        self.max_tries = max_tries

    def request_daily_images(self, request_date: str, tl_lat: float,
                             tl_lon: float, br_lat: float,
                             br_lon: float, maximum_clouds: str = 100):
        """
        :param request_date: Image acquisition date in format yyyy-mm-dd (ex: "2021-01-01")
        :param tl_lat: Bounding box top left latitude
        :param tl_lon: Bounding box top left longitude
        :param br_lat: Bounding box bottom right latitude
        :param br_lon: Bounding box bottom right longitude
        :param maximum_clouds:
        :return:
        """

        search_time_interval = (request_date + "T00:00:00", request_date + "T23:59:59")

        # Create BBox object to feed as input to the API
        search_bbox = BBox(bbox=[tl_lon, tl_lat, br_lon, br_lat], crs=CRS.WGS84)

        # Request API
        for i in range(1, self.max_tries):
            try:
                request_response = opensearch.get_area_info(
                    bbox=search_bbox, date_interval=search_time_interval, maxcc=None
                )
            except:
                pass

        return list(request_response)

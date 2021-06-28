import pandas as pd
import pyproj
import shapely
from mypy_extensions import TypedDict
from shapely import affinity
from shapely.geometry import Polygon, Point
from shapely.ops import transform

gps_projection = 'epsg:4326'
pseudo_mercator_projection = 'epsg:3857'


def reproject_shape(shape, target_crs, source_crs=gps_projection):
    """
    Transforms shape from epsg:4326 (or another given source_crs) to another coordinate system

    :param shape: shapely.geometries
    :param target_crs: string of target coordinate system, like 'epsg:xxxx'
    :param source_crs: string of source coordinate system, like 'epsg:xxxx'
    :return: shapely.geometries reprojected (like input)
    """

    project = pyproj.Transformer.from_proj(source_crs, target_crs, always_xy=True).transform
    return shapely.ops.transform(project, shape)


def create_ship_oriented_bounding_box_polygon(ship_attribute_dict: TypedDict):
    """
    Create a oriented bounding box polygon from the location point and the attributes we get from AIS for a ship.
    It needs to be reprojected to apply width and length attributes that are in meter

    :param ship_attribute_dict: Dictionary with ship attributes retrieve from AIS
    :return: Oriented bounding box shape
    """
    ship_point_in_pseudo_mercator = reproject_shape(ship_attribute_dict.geometry, pseudo_mercator_projection)
    ship_polygon = Polygon(
        [(ship_point_in_pseudo_mercator.x - (ship_attribute_dict["Length"] / 2),
          ship_point_in_pseudo_mercator.y - (ship_attribute_dict["Width"] / 2)),
         (ship_point_in_pseudo_mercator.x + (ship_attribute_dict["Length"] / 2),
          ship_point_in_pseudo_mercator.y - (ship_attribute_dict["Width"] / 2)),
         (ship_point_in_pseudo_mercator.x + (ship_attribute_dict["Length"] / 2),
          ship_point_in_pseudo_mercator.y + (ship_attribute_dict["Width"] / 2)),
         (ship_point_in_pseudo_mercator.x - (ship_attribute_dict["Length"] / 2),
          ship_point_in_pseudo_mercator.y + (ship_attribute_dict["Width"] / 2))])

    if not pd.isna(ship_attribute_dict["Heading"]):
        ship_polygon = affinity.rotate(ship_polygon, ship_attribute_dict["Heading"])

    ship_polygon = reproject_shape(ship_polygon, gps_projection, pseudo_mercator_projection)
    return ship_polygon

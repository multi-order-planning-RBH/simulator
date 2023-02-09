import pickle

from osmnx import graph_from_bbox, graph_to_gdfs, settings
from osmnx.distance import nearest_nodes, shortest_path
from osmnx.utils_geo import sample_points as osmnx_sample_points
from shapely.geometry import LineString, Point, MultiLineString
from random import uniform

from config import Config

import warnings
from common.system_logger import SystemLogger
logger = SystemLogger(__name__)

settings.use_cache = True

north, south, east, west = Config.MAP_NORTH, Config.MAP_SOUTH, Config.MAP_EAST, Config.MAP_WEST
MAP_PATH = './map/graph_{}_{}_{}_{}.pkl'.format(north, south, east, west)

try:
  file = open(MAP_PATH, 'rb')
  graph = pickle.load(file)
  file.close()
  logger.info('load local bkk graph')
except:
  logger.info('bkk graph does not exist')
  logger.info('loading bkk graph')
  graph = graph_from_bbox(north, south, east, west, network_type='drive')
  file = open(MAP_PATH, 'wb')
  pickle.dump(graph, file)
  file.close()

nodes, streets = graph_to_gdfs(graph)

def sample_uniform_bangkok_location() -> Point:
  x = uniform(south, north)
  y = uniform(west, east)
  return Point(y, x)

def sample_points_on_graph(number):
    # Catch warning from osmnx_sample_points
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        points = list(osmnx_sample_points(graph, number))
        for warn in caught_warnings:
            logger.warning(f'{warn.message} from {warn.filename} lineno {warn.lineno}')

    return points

def get_shapely_point(x, nodes=nodes):
  return nodes.loc[x]['geometry']

def project_point(point, line):
  dist = line.project(point)
  projected_point = line.interpolate(dist)
  return projected_point

number_of_fail_findding_path = [0]
def get_geometry_and_length_of_walking_and_riding_path(origin_point, dest_point, path):
  path_linear_string_geometry = []
  if path == None or len(path)<2: 
    global number_of_fail_findding_path
    number_of_fail_findding_path[0] += 1
    logger.warning(f"Fail to find path {origin_point} {dest_point} {path}")
    return LineString([origin_point, dest_point])

  for i in range(len(path)-1):
    node_start = get_shapely_point(path[i])
    node_end = get_shapely_point(path[i+1])
    geometry = LineString([node_start, node_end])
    path_linear_string_geometry.append(geometry)
  
  node_start = get_shapely_point(path[0])#nodes.loc[path[0]]['geometry']
  node_end = get_shapely_point(path[1])#nodes.loc[path[1]]['geometry']
  line = LineString([node_start, node_end])
  origin_projected_point = project_point(origin_point, line)

  node_start = get_shapely_point(path[-2])#nodes.loc[path[-2]]['geometry']
  node_end = get_shapely_point(path[-1])#nodes.loc[path[-1]]['geometry']
  line = LineString([node_start, node_end])
  dest_projected_point = project_point(dest_point, line)


  begin_of_path = nodes.loc[path[1]]['geometry']
  start_projected_point_to_begin_of_path = LineString([origin_projected_point, begin_of_path])
  end_of_path = nodes.loc[path[-2]]['geometry']
  end_of_path_to_end_projected_point = LineString([end_of_path, dest_projected_point])

  origin_line_point_to_projected = LineString([origin_point, origin_projected_point])
  dest_line_point_to_projected = LineString([dest_projected_point, dest_point])

  path_linear_string_geometry = [origin_line_point_to_projected, start_projected_point_to_begin_of_path]+\
                                  path_linear_string_geometry[1:-1]+\
                                  [end_of_path_to_end_projected_point, dest_line_point_to_projected]
  path_linear_string_geometry = MultiLineString(path_linear_string_geometry)

  return path_linear_string_geometry

def get_geometry_of_path(origin, dest) -> MultiLineString:
  origin_closest_node = nearest_nodes(graph, origin.x, origin.y, return_dist=False)
  destination_closest_node = nearest_nodes(graph, dest.x, dest.y, return_dist=False)
  path = shortest_path(graph, origin_closest_node, destination_closest_node)

  geo = get_geometry_and_length_of_walking_and_riding_path(origin, dest, path)

  return geo
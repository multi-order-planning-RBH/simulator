from osmnx import graph_from_bbox, graph_to_gdfs, config as ox_config
from osmnx.distance import nearest_nodes, shortest_path
from osmnx.utils_geo import sample_points as osmnx_sample_points
from shapely.geometry import LineString, Point, MultiLineString
from random import uniform

from config import Config

ox_config(use_cache=True)
north, south, east, west = Config.MAP_NORTH, Config.MAP_SOUTH, Config.MAP_EAST, Config.MAP_WEST#13.914579, 13.738166, 100.661622, 100.484028
graph = graph_from_bbox(north, south, east, west, network_type='drive')
nodes, streets = graph_to_gdfs(graph)

def sample_uniform_bangkok_location() -> Point:
  x = uniform(south, north)
  y = uniform(west, east)
  return Point(y, x)

def sample_points_on_graph(number):
    return list(osmnx_sample_points(graph, number))

def get_shapely_point(x, nodes=nodes):
  return nodes.loc[x]['geometry']

def project_point(point, line):
  dist = line.project(point)
  projected_point = line.interpolate(dist)
  return projected_point

def get_geometry_and_length_of_walking_and_riding_path(origin_point, dest_point, path):
  path_linear_string_geometry = []
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

#   a = origin_line_point_to_projected.length
#   c = dest_line_point_to_projected.length
#   b = path_linear_string_geometry.length-a-c
  return path_linear_string_geometry#, a, b, c

def get_geometry_of_path(origin, dest) -> MultiLineString:
  origin_node = nearest_nodes(graph, origin.x, origin.y, return_dist=False)
  destination_node = nearest_nodes(graph, dest.x, dest.y, return_dist=False)
  path = shortest_path(graph, origin_node, destination_node)

  geo = get_geometry_and_length_of_walking_and_riding_path(origin, dest, path)

  return geo
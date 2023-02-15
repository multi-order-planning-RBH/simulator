# import osmnx 
from osmnx.distance import nearest_nodes
from networkx import astar_path_length
import pickle as pkl
from math import * 

class DistanceCalculator: 
	def __init__(self):
		self.G = pkl.load(open('graph_fix.pkl', 'rb')) 
		self.nodes = self.G.nodes()

	def computeHeuristic(self, u, v):
		u_point = (self.nodes[u]['y'], self.nodes[u]['x'])
		v_point = (self.nodes[v]['y'], self.nodes[v]['x'])
		coords_1 = u_point
		coords_2 = v_point
		R = 6371000
		conversion_const = 0.0174533
		c_1 = (coords_1[0]*conversion_const,coords_1[1]*conversion_const)
		c_2 = (coords_2[0]*conversion_const,coords_2[1]*conversion_const)
		delta_phi = abs(c_1[1]-c_2[1])
		theta = c_1[0]
		delta_theta = abs(c_1[0]-c_2[0])
		del_x = R*cos(theta)*delta_phi 
		del_y = R*delta_theta
		ans = sqrt(del_x**2+del_y**2)
		return ans*2

	def shortestDistance(self, u, v):
		'''
			return the approximate shortest distance from u to v where u and v is in the (lat,long) format
		'''
		origin_node = nearest_nodes(self.G, u[1], u[0], return_dist=False)
		destination_node = nearest_nodes(self.G, v[1], v[0], return_dist=False)
        # print(origin_node, destination_node)
		return astar_path_length(self.G, origin_node, destination_node, heuristic=self.computeHeuristic, weight='length')
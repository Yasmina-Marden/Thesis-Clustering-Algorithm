##Yasmina Marden
##Thesis clustering algorithm implementation
import itertools
import math
import subprocess
import csv

class Clustering:

	seed = ''
	edges = {}
	new_edges = {}
	adjs = {}
	node_degrees = {}
	checked = {}
	all_clusters = {}
	current_clusters = {}
	nodes = []
	potential_boundaries = set([])
	C = set([])
	L = []
	to_remove = set([])

	def __init__(self, path):
		self.path = path

	#reads file by calling read function that corresponds to file type
	def read_file(self):
		length = len(self.path)
		if self.path[length-3:]=='txt':
			self.read_txt_file()
			self.path = self.path[:length-4]+'.csv'
			self.create_edge_list_csv(self.path)
		elif self.path[length-3:]=='csv':
			self.read_csv_file()
		else:
			print("Sorry, txt or csv files only.")
			return 0
		return 1

	def read_txt_file(self):
		f = open(self.path, 'r')
		if f.mode == 'r':
			data = f.read()
			data = data.split('\n')
			self.read_data(data)

	def read_csv_file(self):
		with open(self.path, 'rU') as f:
			data = csv.reader(f)
			self.read_data(data)

	#for each edge in data, edge is added to dictionary edges and
	#dictionary adjs is updated with the nodes within edge
	def read_data(self, data):
		for edge in data:
			if type(edge)!=list:
				edge = edge.split()
			if len(edge)==3:
				weight = float(edge[2])
				edge = edge[:2]
			else:
				weight = 1.0
			edge.sort()
			edge = tuple(edge)
			self.add_to_edges('orig', edge, weight)
			self.add_to_adjs(edge[0], edge[1], weight)
			self.add_to_adjs(edge[1], edge[0], weight)

		for node in self.adjs:
			self.node_degrees[node] = self.adjs[node]["degree"]

	#adds edge e with weight w to self.edges if which_edges is 'orig', to
	#self.new_edges if which_edges is 'new', or displays an error message
	def add_to_edges(self, which_edges, e, w):
		if which_edges=='orig':
			edges = self.edges
		elif which_edges=='new':
			edges = self.new_edges
		else:
			print("Invalid edges dictionary specification.")
			return
		if e in edges:
			edges[e]["weight"] = edges[e]["weight"]+w
		else:
			edges[e] = {}
			edges[e]["weight"] = w
			edges[e]["boundary"] = set([])
			edges[e]["cluster"] = set([])

	#adds n2 to the adjacency list adj_nodes of n1 in adjs
	def add_to_adjs(self, n1, n2, w):
		if n1 in self.adjs:
			if n2 in self.adjs[n1]["adj_nodes"]:
				self.adjs[n1]["adj_nodes"][n2]+=w
			else:
				self.adjs[n1]["adj_nodes"][n2] = w
			self.adjs[n1]["degree"] += w
		else:
			self.adjs[n1] = {}
			self.adjs[n1]["adj_nodes"] = {}
			self.adjs[n1]["adj_nodes"][n2] = w
			self.adjs[n1]["degree"] = w
			self.adjs[n1]["clusters"] = []

	def apply_alg(self, display):
		if self.read_file()==0:
			return
		orig_clusters = {}
		change = True
		iteration = 1
		path_start = self.path[:len(self.path)-4]
		current_path = self.path
		while change:
			self.all_clusters[iteration] = {}
			self.find_clusters(iteration)
			self.find_new_graph_info()
			orig_clusters = self.current_clusters
			current_cluster_path = path_start+'_'+str(iteration)+"_clusters.csv"
			self.create_clusters_csv(current_cluster_path, iteration)
			iteration+=1
			if len(self.current_clusters)<=1:
				change = False
				iteration-=1
		self.unfold_clusters(path_start)
		if display:
			self.display(path_start, iteration)
		return self.all_clusters

	def unfold_clusters(self, path_start):
		current_cluster_path = self.path
		iteration = 2
		while iteration in self.all_clusters:
			current_cluster_path = path_start+'_'+str(iteration)+'_clusters.csv'
			for seed in self.all_clusters[iteration]:
				cluster = tuple()
				for n in self.all_clusters[iteration][seed]:
					cluster = cluster+self.all_clusters[iteration-1][n]
				self.all_clusters[iteration][seed] = cluster
			self.create_clusters_csv(current_cluster_path, iteration)
			iteration+=1
		self.create_clusters_csv(path_start+'_1_clusters.csv', 1)

	#creates a folder within the current directory of each iteration's clustering
	#with a separate image saved for each cluster
	def display(self, path, max_iteration):
		for i in range(len(path),0,-1):
			if path[i-1]=='/':
				network_name = path[i:]
				basic_path = path[:i]
				break
		args = [basic_path, network_name, self.path, str(max_iteration)]
		subprocess.check_output(['Rscript','display_clustered_network.R']+args)

	def create_clusters_csv(self, path, iteration):
		with open(path,'w') as f:
			writer = csv.writer(f)
			for seed in self.all_clusters[iteration]:
				writer.writerow(self.all_clusters[iteration][seed])

	def create_edge_list_csv(self, path):
		with open(path,'w') as f:
			writer = csv.writer(f)
			for e in self.edges:
				writer.writerow(e+(self.edges[e]["weight"],))

	#sorts nodes from highest to lowest node degree within the list L
	def degree_sort(self):
		degrees = {}
		degree_list = []
		self.L = []
		for node in self.node_degrees:
			deg = self.node_degrees[node]
			if deg in degrees:
				degrees[deg] = [node] + degrees[deg]
			else:
				degrees[deg] = [node]
		degree_list = degrees.keys()
		degree_list.sort(reverse=True)
		for deg in degree_list:
			self.L.extend(degrees[deg])

	#iteratively finds a seed and its corresponding cluster until L is empty
	def find_clusters(self, iteration):
		self.current_clusters = {}
		original_checked = {}
		for n in self.adjs:
			original_checked[n] = 'N'
		self.degree_sort()

		while self.L:
			self.potential_boundaries = set([])
			self.checked = dict(original_checked)
			self.seed = self.L[0]
			seed_adj = self.adjs[self.seed]["adj_nodes"]
			self.C = set([self.seed])
			self.checked[self.seed] = 'YIC'
			self.L = self.L[1:]
			self.adjs[self.seed]["clusters"].append(self.seed)
			self.check_adj_nodes(self.seed, seed_adj, seed_adj)
			self.sort_boundaries()
			self.C = tuple(sorted(self.C))
			self.current_clusters[self.C] = self.seed
			self.all_clusters[iteration][self.seed] = self.C

	#returns a tuple edge from input nodes n1 and n2
	def make_edge(self, n1, n2):
		edge = [n1, n2]
		edge.sort()
		return tuple(edge)

	#Scores the adjacent nodes of current_node. If the score of a node n is greater or equal 
	#to zero, then the node is added to the current cluster. If the score of n is greater than
	#zero, then the adjacent nodes of n are recursively checked and scored if not previously
	#checked.
	def check_adj_nodes(self, current_node, match_nodes, current_adj_nodes):
		for n in current_adj_nodes:
			if self.checked[n]=='N':
				score = self.find_score(match_nodes, self.adjs[n]["adj_nodes"])
				if score<0:
					#Yes Not In Cluster
					self.checked[n]='YNIC'
				else:
					#Yes In Cluster
					self.checked[n]='YIC'
					self.C.update([n])
					self.adjs[n]["clusters"].append(self.seed)
					self.check_adj_nodes(n, match_nodes, self.adjs[n]["adj_nodes"])
					self.to_remove.update([n])
					if n in self.L:
						self.L.remove(n)
					for n2 in self.adjs[n]["adj_nodes"]:
						e = self.make_edge(n, n2)
						check = self.checked[n2]
						if check=='YIC':
							self.edges[e]["cluster"].update([self.seed])
						elif check=='YNIC':
							self.edges[e]["boundary"].update([self.seed])
						else:
							self.potential_boundaries.update([e])
			e = self.make_edge(current_node, n)
			if self.seed in self.adjs[n]["clusters"]:
				self.edges[e]["cluster"].update([self.seed])
			else:
				self.edges[e]["boundary"].update([self.seed])

	def find_score(self, match_nodes, adj_nodes):
		score = 0
		for n in adj_nodes:
			if n in match_nodes:
				score+=adj_nodes[n]
			elif n==self.seed:
				score+=adj_nodes[n]
			else:
				score-=adj_nodes[n]
		return score

	def sort_boundaries(self):
		for e in self.potential_boundaries:
			if self.checked[e[0]]=='YIC' and self.checked[e[1]]=='YIC':
				self.edges[e]["cluster"].update([self.seed])
			else:
				self.edges[e]["boundary"].update([self.seed])

	def find_new_graph_info(self):
		self.new_edges = {}
		self.adjs = {}
		for e in self.edges:
			cluster_list = self.edges[e]["cluster"]
			boundary_list = self.edges[e]["boundary"]

			cluster_count = len(cluster_list)
			boundary_count = len(boundary_list)
			if boundary_count>2:
				boundary_factorial = math.factorial(boundary_count)/(2*math.factorial(boundary_count-2))
			elif boundary_count==2:
				boundary_factorial = 1
			else:
				boundary_factorial = 0
			w = self.edges[e]["weight"]/(cluster_count + cluster_count*boundary_count + boundary_factorial)
			for n1 in cluster_list:
				e = self.make_edge(n1, n1)
				self.add_to_edges('new', e, w)
				self.add_to_adjs(n1, n1, w)
				for n2 in boundary_list:
					e = self.make_edge(n1, n2)
					self.add_to_edges('new', e, w)
					self.add_to_adjs(n1, n2, w)
			
			for e in itertools.combinations(boundary_list,2):
				e = tuple(sorted(e))
				self.add_to_adjs(e[0], e[1], w)
				self.add_to_adjs(e[1], e[0], w)
				self.add_to_edges('new', e, w)

		self.edges = self.new_edges
		self.node_degrees = {}
		for n in self.adjs:
			self.node_degrees[n] = self.adjs[n]["degree"]

test = Clustering('data/facebook_edges.csv')
test.apply_alg(True)
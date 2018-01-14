##Yasmina Marden
##Thesis clustering algorithm implementation

class Clustering:

	seed = ''
	edges = {}
	adjs = {}
	node_degrees = {}
	checked = {}
	clusters = {}
	nodes = []
	potential_boundaries = set([])
	C = set([])
	L = []

	def __init__(self, path):
		self.path = path

	#reads file by calling read function that corresponds to file type
	def read_file(self):
		if self.path[len(self.path)-3:]=='txt':
			self.read_txt_file()
		elif self.path[len(self.path)-3:]=='csv':
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
		import csv
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

			self.edges[edge] = {}
			self.edges[edge]["weight"] = weight
			self.edges[edge]["boundary"] = set([])
			self.edges[edge]["cluster"] = set([])

			self.add_to_adjs(edge[0], edge[1], weight)
			self.add_to_adjs(edge[1], edge[0], weight)

		for node in self.adjs:
			self.node_degrees[node] = self.adjs[node]["degree"]

	#adds n2 to the adjacency list adj_nodes of n1 in adjs
	def add_to_adjs(self, n1, n2, w):
		if n1 in self.adjs:
			self.adjs[n1]["adj_nodes"][n2] = w
			self.adjs[n1]["degree"] += w
		else:
			self.adjs[n1] = {}
			self.adjs[n1]["adj_nodes"] = {}
			self.adjs[n1]["adj_nodes"][n2] = w
			self.adjs[n1]["degree"] = w
			self.adjs[n1]["clusters"] = []

	def apply_alg(self):
		if self.read_file()==0:
			return
		self.find_clusters()

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
	def find_clusters(self):
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
			if self.seed in self.node_degrees:
				del self.node_degrees[self.seed]
			self.C = sorted(self.C)


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
					if score>0:
						self.check_adj_nodes(n, match_nodes, self.adjs[n]["adj_nodes"])
						if n in self.node_degrees and self.node_degrees[n]!=self.node_degrees[self.seed]:
							del self.node_degrees[n]
							self.L.remove(n)
					else:
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
				score+=2*adj_nodes[n]
			else:
				score-=adj_nodes[n]
		return score

	def sort_boundaries(self):
		for e in self.potential_boundaries:
			if self.checked[e[0]]=='YIC' and self.checked[e[1]]=='YIC':
				self.edges[e]["cluster"].update([self.seed])
			else:
				self.edges[e]["boundary"].update([self.seed])
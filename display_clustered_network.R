library(igraph)
library(RColorBrewer)

args <- commandArgs(trailingOnly = TRUE)
work_dir <- args[1]
path <- args[2]
net_file_name <- args[3]
net_file_path <- args[4]
max_iteration <- suppressWarnings(as.numeric(args[5]))

setwd(work_dir)

##Creates the network g
data <- read.csv(net_file_path, header=FALSE, stringsAsFactors = FALSE, colClasses = c("character"))
g <- graph.data.frame(data, directed=FALSE)

##Creates the color palette with which to color the clusters
col_vector <- brewer.pal(9, 'Set1')

##Plots the network g with one cluster colored
plot_cluster <- function(iteration, dir_name, net_file_name, cluster_num, g){
  vert_attrs <- find_vertex_attrs(gorder(g))
  vert_size <- vert_attrs[1]
  vert_label <- vert_attrs[2]
  png(paste(dir_name, "/", net_file_name, "_cluster", toString(cluster_num), sep=""), width = 2000, height = 2000, units = 'px', res = 300)
  set.seed(10)
  plot(g, vertex.label.color = "black", vertex.size=vert_size, vertex.label.cex=vert_label)
  title(main=paste("Cluster ", toString(cluster_num), " in Iteration ", toString(iteration), sep=""), cex=2000)
  dev.off()
}

##Sets the nodes of cluster within graph to the input color and all other
##nodes in graph to white
color_clusters <- function(graph, color, cluster) {
  cluster <- cluster[!is.na(cluster)]
  V(graph)$color <- "white"
  for(n in cluster) {
    if(n=="")
      break
    V(graph)[toString(n)]$color <- col
  }
  return(graph)
}

##Determines vert_size and vert_label according to vertex_count
find_vertex_attrs <- function(vertex_count) {
  if(vertex_count<25) {
    vert_size <- 15
    vert_label <- 0.75
  }else if(vertex_count<50) {
    vert_size <- 10
    vert_label <- 0.5
  }else if(vertex_count<100) {
    vert_size <- 8
    vert_label <- 0.4
  }else {
    vert_size <- 5
    vert_label <- 0.005
  }
  return(c(vert_size, vert_label))
}

##For each iteration, a folder is created within the current directory
##and a png image is saved for each cluster of the iteration
iteration <- 1
while(iteration<=max_iteration) {
  dir_name <- paste(net_file_name, "_", toString(iteration), sep="")
  dir.create(dir_name, showWarnings = FALSE)
  
  cluster_file_path <- paste(path, net_file_name, "_", toString(iteration), "_clusters.csv", sep="")
  clusters <- read.csv(cluster_file_path, header=FALSE, stringsAsFactors = FALSE, colClasses = c("character"))
  cluster_count <- seq(nrow(clusters))
  for(i in cluster_count){
    col <- col_vector[i%%9+1]
    cluster <- clusters[i,]
    g <- color_clusters(g, col, cluster)
    plot_cluster(iteration, dir_name, net_file_name, i, g)
  }
  iteration <- iteration + 1
}
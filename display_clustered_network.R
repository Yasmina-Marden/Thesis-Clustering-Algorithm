library(igraph)
library(RColorBrewer)

path <- commandArgs(trailingOnly = TRUE)
data <- read.csv(path, header=FALSE)
clusters <- read.csv(path, header=FALSE)
g = graph.data.frame(data, directed=FALSE)
plot(g)

col_vector <- brewer.pal(12, 'Paired')

cat('Success')

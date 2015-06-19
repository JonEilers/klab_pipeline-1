#!/usr/bin/env Rscript

library(ggplot2, quietly=TRUE)
args <- commandArgs(TRUE)
infile <- args[1]
if(length(args) > 1) {
  title <- args[2]
  pngname <- paste(title, 'pca.png', sep='_')
} else {
  title <- "Principal Components Analysis"
  pngname <- 'pca.png'
}

pca <- read.csv(infile, header=FALSE)
colnames(pca) <- c('sample', sprintf('pc%d', 1:(ncol(pca)-1)))
png(pngname, width=700, height=700)
p <- ggplot(pca, aes(x=pc1, y=pc2, colour=sample)) + geom_point() + 
  opts(title=title)
print(p)
dev.off()

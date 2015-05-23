library("DESeq2")

countdata <- read.csv('../input/Archaea.gene.tran.csv')
rownames(countdata) <- countdata$gene
countdata$gene <- NULL
coldata <- read.csv('../input/ETSP_tran.csv')
rownames(coldata) <- coldata$sra_id
coldata$sra_id <- NULL

#Normalize all the ETSP
dds <- DESeqDataSetFromMatrix(countData = countdata,colData = coldata,design = ~ depth)
#smallest library
dds$zone <- relevel(dds$depth, '85')
dds$zone <- droplevels(dds$depth)
featureData <- data.frame(gene=rownames(countdata))
dds_an <- DESeq(dds,betaPrior=FALSE)
res <- results(dds_an)
rld <- rlogTransformation(dds_an, blind=FALSE)
rld_ass <- assay(rld)
rownames(rld_ass) = rownames(res)
resOrdered <- res[order(res$padj),]
write.csv(file='DESeq2_ETSP_ALL.rld', x=rld_ass)
write.csv(file='DESeq2_ETSP_ALL.res', x=res)

# Run oxic vs. suboxic comparison
years <- unique(unlist(coldata$year))
for (i in 1:length(years)){
	year_coldata <- subset(coldata, year == years[i])
	year_countdata <- countdata[rownames(year_coldata)]
	dds <- DESeqDataSetFromMatrix(countData = year_countdata,colData = year_coldata,design = ~ zone)
	dds$zone <- relevel(dds$zone, 'oxic')
	dds$zone <- droplevels(dds$zone)
	featureData <- data.frame(gene=rownames(year_countdata))
	dds_an <- DESeq(dds)
	res <- results(dds_an)
	rld <- rlogTransformation(dds_an, blind=FALSE)
	rld_ass <- assay(rld)
	rownames(rld_ass) = rownames(res)
	resOrdered <- res[order(res$padj),]
	filename <-paste(c('DESeq2_',years[i],'_oxic_vs_suboxic.rld'), collapse='')
	write.csv(file=filename, x=rld_ass)
	filename <- paste(c('DESeq2_',years[i],'_oxic_vs_suboxic.res'), collapse='')
	write.csv(file=filename, x=res)
}
#Run year comparison
years <- unique(unlist(coldata$year))
for (i in 1:length(years)){
	year_coldata <- subset(coldata, year != years[i])
	year_countdata <- countdata[rownames(year_coldata)]
	dds <- DESeqDataSetFromMatrix(countData = year_countdata,colData = year_coldata,design = ~ year)
	featureData <- data.frame(gene=rownames(year_countdata))
	dds_an <- DESeq(dds)
	res <- results(dds_an)
	rld <- rlogTransformation(dds_an, blind=FALSE)
	rld_ass <- assay(rld)
	rownames(rld_ass) = rownames(res)
	resOrdered <- res[order(res$padj),]
	filename <- paste(c('DESeq2_no_',years[i],'.rld'), collapse='')
	write.csv(file=filename, x=rld_ass)
	filename <- paste(c('DESeq2_no_',years[i],'.res'), collapse='')
	write.csv(file=filename, x=res)
}

#Run first two analyses on only 50m and 110m
depth_coldata <- subset(coldata, depth=='50m'|depth=='110m')
depth_coldata$depth <- factor(depth_coldata$depth)
depth_countdata <- countdata[rownames(depth_coldata)]
# Run oxic vs. suboxic comparison
years <- unique(unlist(coldata$year))
for (i in 1:length(years)){
	year_coldata <- subset(depth_coldata, year == years[i])
	year_countdata <- depth_countdata[rownames(year_coldata)]
	dds <- DESeqDataSetFromMatrix(countData = year_countdata,colData = year_coldata,design = ~ depth)
	dds$depth <- relevel(dds$depth, '50m')
	dds$depth <- droplevels(dds$depth)
	featureData <- data.frame(gene=rownames(year_countdata))
	dds_an <- DESeq(dds)
	res <- results(dds_an)
	rld <- rlogTransformation(dds_an, blind=FALSE)
	rld_ass <- assay(rld)
	rownames(rld_ass) = rownames(res)
	resOrdered <- res[order(res$padj),]
	filename <-paste(c('DESeq2_',years[i],'_50m_vs_110m.rld'), collapse='')
	write.csv(file=filename, x=rld_ass)
	filename <- paste(c('DESeq2_',years[i],'_50m_vs_110m.res'), collapse='')
	write.csv(file=filename, x=res)
}

#Run year comparison
years <- unique(unlist(depth_coldata$year))
for (i in 1:length(years)){
	year_coldata <- subset(depth_coldata, year != years[i])
	year_countdata <- depth_countdata[rownames(year_coldata)]
	dds <- DESeqDataSetFromMatrix(countData = year_countdata,colData = year_coldata,design = ~ year)
	featureData <- data.frame(gene=rownames(year_countdata))
	dds_an <- DESeq(dds)
	res <- results(dds_an)
	rld <- rlogTransformation(dds_an, blind=FALSE)
	rld_ass <- assay(rld)	
	rownames(rld_ass) = rownames(res)
	resOrdered <- res[order(res$padj),]
	filename <- paste(c('DESeq2_no_',years[i],'_50m_110m.rld'), collapse='')
	write.csv(file=filename, x=rld_ass)
	filename <- paste(c('DESeq2_no_',years[i],'_50m_110m.res'), collapse='')
	write.csv(file=filename, x=res)
}

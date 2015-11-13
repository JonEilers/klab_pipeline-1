#  Author: C A Cobbold
#  14 December 2010

# This code computes the diversity of a community based on species similarity 
# and abundance.  The diversity measure is plotted as function of the 
# parameter q which indicates the importance placed or rare (q=0) and abundance
# species (q->infinity).  This code accompanices the manuscript:

# Measuring diversity: the importance of species similarity
# Authors: Tom Leinster and Christina A Cobbold

# This code is not optimised for effeciency but can generate a diversity profile
# from user supplied abundance data and species similarity data.

#obs = species abundances in samples, tab delimited text file
#species names as column headers
obs <-read.table(file.choose(), sep='\t', header=T, check.names=F)
obs$classification <- NULL  # drop column
obs$classification_name <- NULL  # drop column

#Z = similarity information, tab delimited text file with entries between 0 and 1.
Z <- read.table(file.choose(), sep='\t', header=T)

samples = length(obs[1,])
taxa = length(obs[,1])

# Initialise the abundance matrix
p=matrix(0,taxa,samples)

# Convert the data table to a matrix
for (k in 1:samples) {
  p[,k]<-obs[,k]/sum(obs[,k])
}

# Specify the x-axis on the diversity profile.  lenq should be at least 5 (probably larger) so the you can see the effect of the different weightings of abundant and rare species.
lenq = 100
qq <- seq(length=lenq, from=0, by=.11)

# Initialise the Zp matrix to zero
Zp=matrix(0,taxa,samples)

# Compute Zp
for (k in 1:samples) {
  for (i in 1:taxa) {
    for (j in 1:taxa) {
      Zp[i,k]<-Zp[i,k]+Z[i,j]*p[j,k]
    }
  }
}


# Initialise the Diversity matrix to zero
Dqz = matrix(0, lenq ,samples)

#  Loop to calculate the diversity Dqz for each value of q (iq) and each sample (k)
for (k in 1:samples) {
  for (iq in 1:lenq)  {
    q<-qq[iq];
    for (zpi in 1:length(Zp[,k])) {
      if (Zp[zpi,k]>0) {
          Dqz[iq,k]<-Dqz[iq,k]+ p[zpi,k]*(Zp[zpi,k])^(q-1)
      }
    }
    Dqz[iq,k] <- Dqz[iq,k]^(1/(1-q));
  }
}

# Plot the diversity profiles for all the samples (e.g. understorey and canopy) on the same graph.
#colors = c(4,2)  #heat.colors(6)

colors = c(4,2,6)
matplot(qq,Dqz, type="l", col = colors,
  xlab="Sensitivity Parameter q",
  ylab="Diversity DqZ(p)",
  main="Seastar Bacterial Metagenome SSU Diversity",
)
legend("topright", legend=colnames(obs), fill=colors, bty="n") 

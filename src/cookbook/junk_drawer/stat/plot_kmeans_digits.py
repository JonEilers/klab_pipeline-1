import sys

from sklearn.cluster import KMeans
import pandas as pd

data_file = sys.argv[1]
data = pd.DataFrame.from_csv(data_file, sep='\t', header=0, index_col=False)
print data.head()
data = data['cluster', 'lowest_classification', '']
kmeans = KMeans()
kmeans.fit(data.values)

'''
true_k = 2

vectorizer = TfidfVectorizer(stop_words='english')
x = vectorizer.fit_transform(data.functional_description)
print x[0]
data['functional_description'] = x

model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
model.fit(X)
print("Top terms per cluster:")
order_centroids = model.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()
for i in range(true_k):
    print "Cluster %d:" % i,
    for ind in order_centroids[i, :10]:
        print ' %s' % terms[ind],
    print
'''

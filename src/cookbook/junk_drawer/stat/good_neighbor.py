from sklearn.datasets import load_iris

iris = load_iris()
print iris

from sklearn import neighbors

X, y = iris.data, iris.target
knn = neighbors.KNeighborsClassifier(n_neighbors=1)
knn.fit(X, y)

# What kind of iris has 3cm x 5cm sepal and 4cm x 2cm petal?
print iris.target_names[knn.predict([[3, 5, 4, 2]])]
'''
from sklearn.cross_validation import train_test_split
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.4, random_state=0)

knn = neighbors.KNeighborsClassifier(n_neighbors=1)
knn.fit(X_train, y_train)
predicted = knn.predict(X_test)

from sklearn import metrics
print metrics.classification_report(y_test, predicted)
print metrics.confusion_matrix(y_test, predicted)
print metrics.f1_score(y_test, predicted)


from sklearn.cross_validation import cross_val_score

scores = cross_val_score(knn, iris.data, iris.target, cv=5)
'''

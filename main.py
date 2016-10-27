from sklearn import datasets
from sklearn.naive_bayes import GaussianNB

iris = datasets.load_iris()

print 'Data entries:',len(iris.data)
print iris.data
print '******************************'
print 'Target entries:', len(iris.target)
print iris.target

gnb = GaussianNB()
y_pred = gnb.fit(iris.data, iris.target).predict(iris.data)
#print iris.data.shape[0]
#print (iris.target != y_pred).sum()
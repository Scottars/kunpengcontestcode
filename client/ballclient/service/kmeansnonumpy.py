



fro
import numpy as np

# k均值聚类
def KMeans(dataSet, k):
    # m = np.shape(dataSet)[0]  # 行的数目
    m=len(dataSet)
    m=10
    # 第一列存样本属于哪一簇
    # 第二列存样本的到簇的中心点的误差
    clusterAssment = np.mat(np.zeros((m, 2)))
    print('clusterAssemntold          :',clusterAssment)
    clusterAssment=[]
    for i in range(m):
        clusterAssment += [[]]
        for j in range(2):
            clusterAssment[i].append(0)
        pass
        clusterAssment = [[0] * 2] * m
    print('clusterAssment   :', clusterAssment)
    clusterChange = True

    # 第1步 初始化centroids
    centroids = randCent(dataSet,k,m)
    while clusterChange:
        clusterChange = False

        # 遍历所有的样本（行数）
        for i in range(m):
            minDist = 100000.0
            minIndex = -1

            # 遍历所有的质心
            # 第2步 找出最近的质心
            for j in range(k):
                # 计算该样本到质心的欧式距离
                distance = distEclud(centroids[j, :], dataSet[i, :])
                if distance < minDist:
                    minDist = distance
                    minIndex = j
            # 第 3 步：更新每一行样本所属的簇
            if clusterAssment[i, 0] != minIndex:
                clusterChange = True
                clusterAssment[i, :] = minIndex, minDist ** 2
        # 第 4 步：更新质心
        for j in range(k):
            pointsInCluster = dataSet[np.nonzero(clusterAssment[:, 0].A == j)[0]]  # 获取簇类所有的点
            centroids[j, :] = np.mean(pointsInCluster, axis=0)  # 对矩阵的行求均值

            # print('打印当前的样本的分类', pointsInCluster)

    bestlist1, bestlist2, bestlist3, bestlist4=getorder(clusterAssment, m, dataSet,centroids)
    a=findbestarget(bestlist1)
    b=findbestarget(bestlist2)
    c=findbestarget(bestlist3)
    d=findbestarget(bestlist4)
    # print('打印一下abcd')
    # print(a)
    # print(b)
    # print(c)
    # print(d)
    #
    # print("Congratulations,cluster complete!")
    return a,b,c,d
    # return bestlist1,bestlist2,bestlist3,bestlist4,


# 为给定数据集构建一个包含K个随机质心的集合
def randCent(dataSet, k,m):
    # m, n = dataSet.shape
    n=2 #表示是两列，作为二维坐标

    centroids = np.zeros((k, n))
    for i in range(k):
        index = int(np.random.uniform(0, m))  # 有可能初始化成为同一个点
        centroids[i, :] = dataSet[index, :]
    return centroids

# 欧氏距离计算
def distEclud(x, y):
    return np.sqrt(np.sum((x - y) ** 2))  # 计算欧氏距离

def getorder(clusterAssment,m,dataSet,centroids):
    a=0
    alist=[[centroids[0,0],centroids[0,1]]]
    b=0
    blist=[[centroids[1,0],centroids[1,1]]]
    c=0
    clist=[[centroids[2,0],centroids[2,1]]]
    d=0
    dlist=[[centroids[3,0],centroids[3,1]]]
    # clusterAssment.tolist()
    # print('clusterAssment是什么样子',clusterAssment)
    # print(type(clusterAssment))
    # print('clusterAssment[i][0]    :',clusterAssment[0,0])
    for i in range(m):
       if clusterAssment[i,0]==0:
           # print('dataset[i]:00:::;',dataSet[i])

           alist.append([dataSet[i,0],dataSet[i,1]])
           # print('list的情况',alist)

       if clusterAssment[i,0] == 1:
           # print('dataset[i]::111::;',dataSet[i])
           blist.append([dataSet[i,0],dataSet[i,1]])
           # print('list的情况',blist)

       if clusterAssment[i,0] == 2:
           # print('dataset[i]:222:::;',dataSet[i])

           clist.append([dataSet[i,0],dataSet[i,1]])
           # print('list的情况',clist)

       if clusterAssment[i,0] == 3:
            # print('dataset[i]:333:::;', dataSet[i])

            dlist.append([dataSet[i,0],dataSet[i,1]])
            # print('list的情况', dlist)

    a = len(alist)
    b = len(blist)
    c = len(clist)
    d = len(dlist)
    if a >= b and a >= c and a >= d:
        bestlist1 = alist
        if b>=c and b>=d:
            bestlist2 = blist
            if c>=d:
                bestlist3=clist
                bestlist4=dlist
            else:
                bestlist3=dlist
                bestlist4=clist
        elif c>=b and c>=d:
            bestlist2=clist
            if b>=d:
                bestlist3=blist
                bestlist4=dlist
            else:
                bestlist3=dlist
                bestlist4=blist
        elif d>b and d>c:
            bestlist2=dlist
            if b>=c:
                bestlist3 = blist
                bestlist4 = clist
            else:
                bestlist3=clist
                bestlist4=blist
    elif b >= a and b >= c and b >= d:
        bestlist1 = blist
        if a>=c and a>=d:
            bestlist2 = alist
            if c>=d:
                bestlist3 = clist
                bestlist4 = dlist
            else:
                bestlist3=dlist
                bestlist4=clist
        elif c>=a and c>=d:
            bestlist2=clist
            if a>=d:
                bestlist3 = alist
                bestlist4 = dlist
            else:
                bestlist3=dlist
                bestlist4=alist
        elif d>a and d>c:
            bestlist2=dlist
            if a >=c:
                bestlist3 = alist
                bestlist4 = clist
            else:
                bestlist3=clist
                bestlist4=alist
    elif c >= a and c >= b and c >= d:
        bestlist1 = clist
        if b>=a and b>=d:
            bestlist2 = blist
            if a>=d:
                bestlist3 = alist
                bestlist4 = dlist
            else:
                bestlist3=dlist
                bestlist4=alist
        elif a>=b and a>=d:
            bestlist2=alist
            if b>=d:
                bestlist3 = blist
                bestlist4 = dlist
            else:
                bestlist3=dlist
                bestlist4=blist
        elif d>b and d>a:
            bestlist2=dlist
            if b>=a:
                bestlist3 = blist
                bestlist4 = alist
            else:
                bestlist3=alist
                bestlist4=blist

    elif d >= a and d >= b and d >= c:
        bestlist1 = dlist
        if b>=c and b>=a:
            bestlist2 = blist
            if c>=a:
                bestlist3 = clist
                bestlist4 = alist
            else:
                bestlist3=alist
                bestlist4=clist
        elif c>=b and c>=a:
            bestlist2=clist
            if b>=a:
                bestlist3 = blist
                bestlist4 = alist
            else:
                bestlist3=alist
                bestlist4=blist
        elif a>b and a>c:
            bestlist2=alist
            if b>=c:
                bestlist3 = blist
                bestlist4 = clist
            else:
                bestlist3=clist
                bestlist4=blist
    # print('best1list1',bestlist1)
    # print('best1list2',bestlist2)
    # print('best1list3',bestlist3)
    # print('best1list4',bestlist4)
    #
    return bestlist1,bestlist2,bestlist3,bestlist4


def findbestarget(bestlist):
    targetdismin = 1000
    targetdistemp    = 0
    targetposition = []
    cen=bestlist[0]
    # print('当前list的长度',len(bestlist))
    # print('bestlist的情况',bestlist)
    # print('cen的情况',cen[0])
    # print('bestlist ',bestlist[1])
    if len(bestlist)==1:
        return bestlist
    else:

        for i in range(1,len(bestlist)):
            print('i的大小   ',i)
            targetdistemp=abs(cen[0]-bestlist[i][0])+abs(cen[1]-bestlist[i][1])
            if targetdistemp < targetdismin:
                targetdismin=targetdistemp
                targetposition = bestlist[i]

        # print('打印一下当前要追的敌人',anamyttarget)
        return targetposition





def getorder1(clusterAssment,m,dataSet):
    a=0
    alist=[[]]
    b=0
    blist=[]
    c=0
    clist=[]
    d=0
    dlist=[]
    clusterAssment.tolist()
    print('clusterAssment是什么样子',clusterAssment)
    print(type(clusterAssment))
    print('clusterAssment[i][0]    :',clusterAssment[0,0])
    for i in range(m):
       if clusterAssment[i,0]==0:
           print('dataset[i]:00:::;',dataSet[i])
           x=dataSet[i,0]
           y=dataSet[i,1]
           print('x,y的数值',x,'   ',y)
           tempt=[x,y]


           alist.append([x,y])
           print('list的情况',alist)

       if clusterAssment[i,0] == 1:
           print('dataset[i]::111::;',dataSet[i])
           x = dataSet[i, 0]
           y = dataSet[i, 1]
           print('x,y的数值',x,'   ',y)
           blist.append([x,y])
           print('list的情况',blist)

       if clusterAssment[i,0] == 2:
           print('dataset[i]:222:::;',dataSet[i])
           x = dataSet[i, 0]
           y = dataSet[i, 1]
           print('x,y的数值',x,'   ',y)

           clist.append([x,y])

           print('list的情况',clist)

       if clusterAssment[i,0] == 3:
            print('dataset[i]:333:::;', dataSet[i])
            x = dataSet[i, 0]
            y = dataSet[i, 1]
            print('x,y的数值', x, '   ', y)

            dlist.append([x,y])
            print('list的情况', dlist)


    a=len(alist)
    b=len(blist)
    c=len(clist)
    d=len(dlist)

    tempt=[a,b,c,d]
    print('temp',tempt)
    max1=max(tempt)
    tempt.remove(max1)
    max2=max(tempt)
    tempt.remove(max2)
    max3=max(tempt)
    tempt.remove(max2)
    max4=tempt[0]
    return max1,max2,max3,max4


    pass
m=10
clusterAssment = np.mat(np.zeros((m, 2)))
print('clusterAssemntold          :',clusterAssment)

m = 10
# 第一列存样本属于哪一簇
# 第二列存样本的到簇的中心点的误差
# clusterAssment = np.mat(np.zeros((m, 2)))
clusterAssment = []
for i in range(m):
    clusterAssment += [[]]
    for j in range(2):
        clusterAssment[i].append(0)
    pass
    clusterAssment = [[0] * 2] * m
print('clusterAssment   :', clusterAssment)
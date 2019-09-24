# A* algorithm use the f = g + h
# That is a cost function. g:actual cost from begining   h :current to the goal


import random
m=20
w=m


h=m;
flag=0;


test=[]

test=1

openSet=[]
closedSet=[]




#openset 装着每一个点 这个对象 openset[1,2,3]
#每一个对象又有很多f g h i j 等这样的特征 以及它本身的内容。
#所以我们应当建立一个数据对象
#for count in xrange(4):
    # x = SimpleClass()
    # x.attr = count
    # simplelist.append(x)

class Grid:
    def __init__(self,x,y,h,w):
        #The evaluated value
        self.f = 0
        self.g = 0
        self.h = 0
        #The actual coordinate of the value
        self.x=x
        self.y=y  #j 也就代表了列了
        #the actual map
        #self.grid=grid

        self.h=h # i 有多少行
        self.w=w # j  有多少列

        self.myplayer=False
        self.truemyplayer=False
        self.trueanamyplayer=False
        self.attackwall=False

        self.cloud = False



        self.wall=False
        # anamy list
        self.anamy = False
        self.trueanamy=False

        self.tunnel='no'

        self.power='0' #默认是power for则我们用别的符号去代替，然后将能够使用context去表示这个东西到底是不是power
                        #每次更新的时候，都可以将所有的power都恢复默认，然后重新根据当前的powersetout 和powetsetin 分别
                        #重新更新当前的datasset，所以
                        #要想更新map，我们还需要进行每一个层级都进行更新
                        #更细你的顺序就是
                        #1、powerset
                        #2、tunne
                        #3、annamyset

        self.dangerouspos1=False
        self.dangerouspos2=False
        self.dangerouspos3=False


        self.wormhole=False
        self.wormholecontext='0'

        #parent
        self.previous=[]


        #the neibhbours
        self.upneighbours=[]
        self.downneighbours=[]
        self.leftneighbours=[]
        self.rightneighbours=[]
        self.neighbours=[]


        #grid context
        self.context='0'
        #
        # if (random.randint(0, 20) < 4):
        #     self.wall = True
        #     self.context='1'


    def show(self,a):
        print('showshowshow')
        print(grid[self.i][self.j])
        print('this is my a'+str(a))

    def calculatevalue(self):
        # #This part is for calculate the the f the g the h
        # self.g=(self.i-start.i)+abs(self.j-start.j)
        # self.h = (self.i - ad.i) + abs(self.j - end.j)
        # self.f=self.g+self.h
        pass


def heuristic(a,b):

    #d=math.sqrt((a.i-b.i)*(a.i-b.i)+(a.j-b.j)*(a.j-b.j))
    d=abs(a.i-b.i)+abs((a.j-b.j))
    print(d)
    return  d



def draw(grid,end):
    global  flag
    global openSet
    global closedSet

    while True:

        if len(openSet) > 0:
            winner = 0

            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            #current 是最小的节点
            current = openSet[winner]

            #判断当前节点是不是最终的节点
            if (current.i == end.i) & (current.j == end.j):
                print("we have DONE this test")
                flag=1

                #确定是最佳的节点
                path = []
                temp = current
                path.append(temp)


                while temp.previous:
                    path.append(temp.previous)
                    temp = temp.previous
                #    print(' we  have out of the path')
                #    print(' we  have out of the path')
                for i in range(len(path)):
                    #   print('x' + str(path[i].i) + 'y' + str(path[i].j))
                    path[i].context = '*'

                gridshow(grid)

                break

                # find the path




            ##将该节点移出openset
            openSet.remove(current)
            ##将该节点移入closedset
            closedSet.append(current)

            #理论上直接就右neighbours
            neighbours=current.neighbours

            #循环当前节点的所有的相邻的节点
            print(len(neighbours))
            for i in range(len(neighbours)):


                neighbour = neighbours[i]

                print(type(neighbour))

                #当前节点是否在closedset节点里面
                if (neighbour in closedSet) | neighbour.wall:
                    pass
                else:
                #当前的邻居不在closedset中

                    tempG = current.g + 1;
                    #当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        #其在open set
                        if tempG < neighbour.g:
                            neighbour.g = tempG
                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)


                    neighbour.h = heuristic(neighbour, end)
                    # if h==0:
                    #     neighbour.previous = current
                    #
                    #     break
                    neighbour.f = neighbour.g + neighbour.h
                    #came from
                    neighbour.previous = current



            # to show actual situation
            # for i in range(len(openSet)):
            #     grid[path[i].i][path[i].j].context = '*'

            #     print(i.context)

            # 展示一下当前的的grid


        else:
            print('no solution')
            break

            pass

 # if())

def opensethave(a):
    for i in range(len(openSet)):
        if (a.i==openSet[i].i)& (a.j==openSet[i]):
            return True
    return False
def closesethave(a):
    for i in range(len(closedSet)):
        if (a.i==closedSet[i].i)& (a.j==closedSet[i]):
            return True
    return False

def addneighbours(a):

    if a.i > 0:
        a.upneighbours.append(a.i-1)
        a.upneighbours.append(a.j)
        print('x'+str(a.upneighbours[0])+'y'+str(a.upneighbours[1]))
    if a.i < h - 1:
        print('x' + 'a.upneighbours[0]' + 'y' + 'a.upneighbours[1]')

        a.downneighbours.append(a.i + 1)
        a.downneighbours.append(a.j)
        print('x' + str(a.downneighbours[0]) + 'y' + str(a.downneighbours[1]))

    if a.j > 0:


        a.leftneighbours.append(a.i)
        a.leftneighbours.append(a.j-1)
        print('x' + str(a.leftneighbours[0]) + 'y' + str(a.leftneighbours[1]))
    if a.j < w - 1:


        a.rightneighbours.append(a.i)
        a.rightneighbours.append(a.j+1)
        print('x' + str(a.rightneighbours[0]) + 'y' + str(a.rightneighbours[1]))



      #################################

    if a.i > 0:
        a.neighbours.append(grid[a.i-1][a.j])


    if a.i < h - 1:
        a.neighbours.append(grid[a.i + 1][a.j])

    if a.j > 0:
        a.neighbours.append(grid[a.i ][a.j-1])
    if a.j < w - 1:
        a.neighbours.append(grid[a.i][a.j+1])

    #print('test my neighbours')
  #  print(a.neighbours[0].i)
def Initialization():
    global  grid
    grid=[]

    for i in range(m):
        grid += [[]]
        for j in range(m):
            grid[i].append(Grid(i,j,h,w))
        pass
    for i in range(m):
        for j in range(m):
            addneighbours(grid[i][j])



def gridshow(grid):
    for i in range(m):
        b=''
        for j in range(m):
            b+= grid[i][j].context+'   '
        print(b)




if __name__ == "__main__":
  #  spot=Spot(1,2)
    c=[]

    Initialization()
    # a=grid[1][1]
    # b=a
    # c.append(b)
    # c.append(grid[2][2])
    # c[0].context='hh'
    # print(c[0].context)
    # print(grid[1][1].context)
    gridshow(grid)





    start=grid[0][0]
    end=grid[m-1][m-1]
    openSet.append(grid[0][0])

    draw(grid,end)
        #openSet.append(start)
       # end.wall=False
        #start.wall=False
        # print(test)






      #  while draw()














#print(grid)
#
    #
    # print(type(grid[1][0]))
    # print(grid1[1][0])
    # print(len(grid))
    # print(spot.g)




#the core of the algorithm














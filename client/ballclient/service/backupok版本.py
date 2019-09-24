# encoding:utf8
'''
业务方法模块，需要选手实现

选手也可以另外创造模块，在本模块定义的方法中填入调用逻辑。这由选手决定

所有方法的参数均已经被解析成json，直接使用即可

所有方法的返回值为dict对象。客户端会在dict前面增加字符个数。
'''
import ballclient.service.constants as constants
import ballclient.service.astarpath as astarpath
import time
import copy
import random


import numpy as np

# import numpy as np
import ballclient.service.kmeans_4 as kmeans

global meteors   #陨石坐标位置
global tunnel  #隧道位置
global wormholes  #虫洞位置 传送
global mode    #强势还是弱势
global palyerposition #玩家位置
global visionrange


global powersetout
global powersetin
global powersetround
global powersetall
powersetin=[]
powersetout=[]
powersetround=[]
powersetall=[]

global playerworm
global playerwormtarget
global Game_mode
global Attack
Attack=True

global boundary
boundary=[]


global roundcount
roundcount=0
global f
f = open('test.txt', 'w')
global epsi
epsi=0
epsi = epsi + 1
f.write('roundstart:' + str(epsi) + '\n')  # 这个是为下一轮做准备
def leg_start(msg):
    # start1=time.clock()
    '''
    :param msg:
    :return: None
    '''
    global epsi
    global meteors
    global map_height
    global map_width
    global tunnels
    global  wormholes
    global playerworm
    global Game_mode
    global boundary
    global maptype
    global visionrange
    global powersetPos
    print ("round start")
    print(msg)
    print('这个时候打印一下powersetin 和 powersetout看是否下半场有记录到',powersetPos)


    # print ("msg_name:%s" % msg['msg_name'])
    # print ("map_width:%s" % msg['msg_data']['map']['width'])
    # print ("map_height:%s" % msg['msg_data']['map']['height'])
    # print ("vision:%s" % msg['msg_data']['map']['vision'])
    # print ("meteor:%s" % msg['msg_data']['map']['meteor'])
    # # print ("cloud:%s" % msg['msg_data']['map']['cloud'])
    # print ("tunnel:%s" % msg['msg_data']['map']['tunnel'])
    # print ("wormhole:%s" % msg['msg_data']['map']['wormhole'])
    # print ("teams:%s" % msg['msg_data']['teams'])
    if msg['msg_data']['teams'][0]['id']==constants.team_id:
         Game_mode=msg['msg_data']['teams'][0]['force']
    else:
        Game_mode = msg['msg_data']['teams'][1]['force']


    map_width= msg['msg_data']['map']['width']
    map_height= msg['msg_data']['map']['height']

    visionrange=msg['msg_data']['map']['vision']


    meteors=[]
    for i in range(len(msg['msg_data']['map']['meteor'])):
        meteors.append(msg['msg_data']['map']['meteor'][i])
      #  print(msg['msg_data']['map']['meteor'][i])

    # print(meteors)

    ###########get tunnel data###################
    # {'direction': 'up', 'x': 5, 'y': 5}
    tunnels=[]
    for i in range(len(msg['msg_data']['map']['tunnel'])):
        tunnels.append(msg['msg_data']['map']['tunnel'][i])
        # print(tunnel[i]0)
    # print('get tunnels')
    # print(tunnels)
    #########get wormhole data#################
    #teams:[{'force': 'beat', 'id': 2222, 'players': [0, 1, 2, 3]}, {'force': 'think', 'id': 1111, 'players': [4, 5, 6, 7]}]
    wormholes=[]
    for i in range(len(msg['msg_data']['map']['wormhole'])):
        wormholes.append(msg['msg_data']['map']['wormhole'][i])


    mapinittialization()


    boundary,maptype=boundary_get()
    # wormwholetarget是表示可以有好几个有能够进入内部的虫洞
    find_wormhole(xmin=boundary[0], ymin=boundary[1], xmax=boundary[2], ymax=boundary[3])
    # end1=time.clock()
    # print('legstart使用的时间')
    # print(end1-start1)
    # 这个时间一般都okay的

global legup
global myteampoint
global anamypoint
myteampoint=0
anamypoint=0
global i
i=2
def leg_end(msg):
    '''

    :param msg:
    {
        "msg_name" : "leg_end",
        "msg_data" : {
            "teams" : [
            {
                "id" : 1001,				#队ID
                "point" : 770             #本leg的各队所得点数
            },
            {
            "id" : 1002,
            "point" : 450
             }
            ]
        }
    }

    :return:
    '''
    global f
    global myteampoint
    global anamypoint
    legup=False


    # print('hello')

    print ("round over")
    teams = msg["msg_data"]['teams']


    for team in teams:
        print ("teams:%s" % team['id'])
        print ("point:%s" % team['point'])
        print ("\n\n")

        f.write('     半场' + '  ' + str(team['id']) + '分数:' + str(team['point']) + '\n')
        if team['id']==1515:
            myteampoint = myteampoint + team['point']
        else:
            anamypoint = anamypoint + team['point']


def game_over(msg):
    global f
    global myteampoint
    global anamypoint
    global epsi
    global roundcount
    f.write('   我方 的总分数:' + str(myteampoint) + '\n')
    f.write('   敌人 的总分数:' + str(anamypoint) + '\n')
    myteampoint=0
    anamypoint=0
    print ("game over!")
    epsi = epsi + 1
    f.write('roundstart:' + str(epsi) + '\n') #这个是为下一轮做准备
    roundcount=0


global playerworm
playerworm=None

global flag_initialworm
flag_initialworm=False

def round(msg):
    global powersetround

    global powersetin

    global powersetout

    global mapfeature

    global roundcount
    global boundary
    global maptype


    global playerworm
    global playerout
    global playerattackup
    global playerattackdown

    global wormwholetarget
    global  anamytarget

    global powersetA
    global powersetB
    global powersetC
    global powersetD
    global playerA
    global playerB
    global playerC
    global playerD

    '''

    :param msg: dict
    :return:
    return type: dict
    '''
    start=time.clock()


    roundcount = roundcount +1
    print ("round"+str(roundcount))
    # print(msg)

    ######################每局内容更新###################
    round_id = msg['msg_data']['round_id']
    players = msg['msg_data']['players']

    #这个函数是返回myplayers 和 anamyplayers
    myplayers,anamyplayers=update_players(players)

    # print('在前面打印一下我方player r')
    # print(myplayers)
    # print('在前面打印一下我敌方player')
    # print(anamyplayers)



    global Game_mode
    global Attack
    if msg['msg_data']['mode']==Game_mode and (roundcount>50 or roundcount>200):
        print('我们这个时候不用防守，也就不用考虑敌人的位置了')
        Attack=True
        updateanamypositionattackmode()
    else:
        Attack=False
        # print('我们正在防守模式')
        # updateanamypositionsimple(anamyplayers)
        # updateanamyposition(anamyplayers)
        updateanamypositionUpgrade(anamyplayers)
    print('敌人的情况  ',anamyplayers)
    # mapshow(mapfeature)
    # print('为什么没有A')
    # print('看一下敌人的位置有没有实际更新')

        ##########更新powerset
    try:
        powersetround = []
        powersetround = msg['msg_data']['power']
    except:
        powersetround = []
    update_powerset(myplayers, anamyplayers)

    if maptype==1:
        # print('map1 种类中')

        if len(myplayers) == 4:
            # z这个函数的作用是确定playerworm 和 out  wormwhole 等等   与之前的效果相同
            update_playerABCD(myplayers)  # 这个函数的作用是为了实现，对playerworm  playerout playerup playerdown的选择
            # print('我们还是满员四个人')
            playerA = playerworm
            playerB = playerout
            playerC = playerattackup
            playerD = playerattackdown
            if Attack:
                actionA = get_poweractionmap1(playerA, anamyplayers)
                actionB = get_poweractionmap1(playerB, anamyplayers)
                actionC = get_poweractionmap1(playerC, anamyplayers)
                actionD = get_poweractionmap1(playerD, anamyplayers)
            else:
                actionA = get_poweractionmap1(playerA, anamyplayers)
                actionB = get_poweractionmap1(playerB, anamyplayers)
                actionC = get_poweractionmap1(playerC, anamyplayers)
                actionD = get_poweractionmap1(playerD, anamyplayers)
        else:
            # z这个函数的作用是确定playerworm 和 out  wormwhole 等等   与之前的效果相同
            update_playerABCD(myplayers)  # get abcd
            try:
                playerA = myplayers[0]
            except:
                # print('playerA赋值异常')
                playerA = None
                pass
            try:
                playerB = myplayers[1]
            except:
                playerB = None
                # print('playerB赋值异常')
                pass
            try:
                playerC = myplayers[2]
            except:
                # print('playerC赋值异常')
                playerC = None
                pass
            try:

                playerD = myplayers[3]
            except:
                # print('playerD赋值异常')
                playerD = None
                pass
            try:
                # print('找到A路径')
                actionA = get_poweractionmap1(playerA, anamyplayers)
            except:
                # print('找A的路径异常')
                pass
            try:
                # print('找到B路径')
                actionB = get_poweractionmap1(playerB, anamyplayers)
            except:
                # print('找B的路径异常')
                pass
            try:
                # print('找到c路径')
                actionC = get_poweractionmap1(playerC, anamyplayers)
            except:
                # print('找C的路径异常')
                pass
            try:
                # print('找到D路径')
                actionD = get_poweractionmap1(playerD, anamyplayers)
            except:
                # print('找D的路径异常')/
                pass

    elif maptype==2:
        # print('we are in maptype2 situation')
        if len(myplayers)==4:
            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = myplayers[2]
            playerD = myplayers[3]
        elif len(myplayers)==3:
            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = myplayers[2]
            playerD = None
        elif len(myplayers)==2:
            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = None
            playerD = None
        elif len(myplayers)==1:
            playerA = myplayers[0]
            playerB = None
            playerC = None
            playerD = None
        global flag_get_Attackanamy
        flag_get_Attackanamy=False
        dividepowerset(myplayers) #这个函数分别得到了各个player对应要吃的power
        if Attack:
            # actionA = get_attackactionmap2Upgrade_parta(playerA, powersetA,anamyplayers)
            # actionB = get_attackactionmap2Upgrade_parta(playerB, powersetB,anamyplayers)
            # actionC = get_attackactionmap2Upgrade_parta(playerC, powersetC,anamyplayers)
            # actionD = get_attackactionmap2Upgrade_parta(playerD, powersetD,anamyplayers)

            # actionA = get_poweractionmap2UpgradeV2(playerA, powersetA,anamyplayers)
            # actionB = get_poweractionmap2UpgradeV2(playerB, powersetB,anamyplayers)
            # actionC = get_poweractionmap2UpgradeV2(playerC, powersetC,anamyplayers)
            # actionD = get_poweractionmap2UpgradeV2(playerD, powersetD,anamyplayers)
            actionA = get_poweractionmap2(playerA, powersetA, anamyplayers)
            actionB = get_poweractionmap2(playerB, powersetB, anamyplayers)
            actionC = get_poweractionmap2(playerC, powersetC, anamyplayers)
            actionD = get_poweractionmap2(playerD, powersetD, anamyplayers)

        else:
            actionA = get_poweractionmap2(playerA, powersetA, anamyplayers)
            actionB = get_poweractionmap2(playerB, powersetB, anamyplayers)
            actionC = get_poweractionmap2(playerC, powersetC, anamyplayers)
            actionD = get_poweractionmap2(playerD, powersetD, anamyplayers)


    elif maptype==3:
        pass


   # / print('打印一下playerABCD')
# print(playerA)
    # print(playerB)
    # print(playerC)

    ####找到对应的路径


    direction = {1: 'up', 2: 'down', 3: 'left', 4: 'right', 5: 'up', 6: 'up', 7: 'right', 8: 'right'}
    result = {
        "msg_name": "action",
        "msg_data": {
            "round_id": round_id
        }
    }
    action = []


    if Attack:

        for player in players:
            if player['team'] == constants.team_id:
                try:
                    if player == playerA:
                        action.append({"team": player['team'], "player_id": player['id'],
                                       "move": [direction[actionA]]})
                except:
                    pass

                try:
                    if player == playerB:
                        action.append({"team": player['team'], "player_id": player['id'], "move": [direction[actionB]]})

                except:
                    pass
                try:
                    if player == playerC:
                        action.append({"team": player['team'], "player_id": player['id'], "move": [direction[actionC]]})

                except:
                    pass
                try:
                    if player == playerD:
                        action.append({"team": player['team'], "player_id": player['id'],
                                       "move": [direction[actionD]]})

                except:
                    pass
    else:

        action = []
        # print('we need to avoid')
        # mapshow(mapfeature)
        if playerA is None:
            # print('playerA 是空的')
            pass
        else:

            # a = player_avoidaction(playerA, anamyplayers,actionA)
            # a = player_avoidactionNew1(playerA, anamyplayers, actionA)
            # a = player_avoidactionNew2(playerA, anamyplayers, actionA)
            a = player_avoidactionNew3(playerA, anamyplayers, actionA)

            # print('PlayerA: ' + str(a))
            # print('playerA的内容： ', playerA)
            if a is None:  #我们认为返回0是可以选择不动的，这个时候我们就返回别的可以动的东西就好了

                pass
            else:
                action.append({"team": playerA['team'], "player_id": playerA['id'],"move": [direction[a]]})

            ###################################
        if playerB is None:
            # print('playerB 是空的')
            pass
        else:
            # a = player_avoidaction(playerB, anamyplayers,actionB)
            # a = player_avoidactionNew1(playerB, anamyplayers, actionB)
            # a = player_avoidactionNew2(playerB, anamyplayers, actionB)
            a = player_avoidactionNew3(playerB, anamyplayers, actionB)

            # print('PlayerB: ' + str(a))
            # print('playerB的内容： ', playerB)

            if a is None: #我们认为返回0是可以选择不动的，这个时候我们就返回别的可以动的东西就好了
                pass
            else:
             action.append({"team": playerB['team'], "player_id": playerB['id'],"move": [direction[a]]})
#####################################
        if playerC is None:
            # print('oplayerC 是空的')
            pass
        else:
            # a = player_avoidaction(playerC, anamyplayers,actionC)
            # a = player_avoidactionNew1(playerC, anamyplayers,actionC)

            # a = player_avoidactionNew2(playerC, anamyplayers,actionC)
            a = player_avoidactionNew3(playerC, anamyplayers,actionC)

            # print('PlayerC: ' + str(a))
            # print('playerC的内容： ', playerC)

            if a is None: #我们认为返回0是可以选择不动的，这个时候我们就返回别的可以动的东西就好了
                pass
            else:
                 action.append({"team": playerC['team'], "player_id": playerC['id'],"move": [direction[a]]})

#############################################

        if playerD is None:

            # print('playerd shi kong de ')
            pass
        else:
            # a = player_avoidaction(playerD, anamyplayers,actionD)
            # a = player_avoidactionNew1(playerD, anamyplayers,actionD)
            # a = player_avoidactionNew2(playerD, anamyplayers,actionD)
            a = player_avoidactionNew3(playerD, anamyplayers,actionD)

            # print('PlayerD: ' + str(a))
            # print('playerD的内容： ', playerD)
            if a is None: #我们认为返回0是可以选择不动的，这个时候我们就返回别的可以动的东西就好了
                pass
            else:
                action.append({"team": playerD['team'], "player_id": playerD['id'],"move": [direction[a]]})




    # print(action)
    # for player in players:
    #     if player['team'] == constants.team_id:
    #         actionold.append({"team": player['team'], "player_id": player['id'],
    #                        "move": [direction[random.randint(1, 4)]]})
    # print(actionold)
    result['msg_data']['actions'] = action

    #
    # end = time.clock()
    # print('打印用了多长的时间')
    # print(end - start)
    return result




#给定长 宽
#metoer位置
#tunnel位置
#敌方位置
#
def mapinittialization():
    global mapfeature
    global map_height
    global map_width
    global meteors
    global  tunnels
    global  wormholes


    mapfeature = []


    # print('mapheight:'+str(map_height))
    # print('mapheight:' + str(map_width))
    h=map_height
    w=map_width

    # print('ok1')
    for x in range(w):
        mapfeature += [[]]
        for y in range(50):
            mapfeature[x].append(astarpath.Grid(x, y, h, w))
        pass
    # print('ok2')

    # print('ok3')
    # print(len(meteor))
    # print('###########menotr######')
    for i in range(len(meteors)):
        mapfeature[meteors[i]['x']][meteors[i]['y']].wall=True
        mapfeature[meteors[i]['x']][meteors[i]['y']].context='*'
   #     print('x'+str(meteor[i]['x'])+'y'+str(meteor[i]['y']))
  #  mapshow(mapfeature)
    for tunnel in (tunnels):
        mapfeature[tunnel['x']][tunnel['y']].wall = False
        # mapfeature[tunnel['x']][tunnel['y']].context = '*'

        mapfeature[tunnel['x']][tunnel['y']].tunnel= tunnel['direction']
        # mapfeature[tunnel['x']][tunnel['y']].tunnel = 'no'  #使用了这句话 就表示不使用neibour作为路径规划了
        mapfeature[tunnel['x']][tunnel['y']].context =tunnel['direction'][0]



    # mapfeature[1][1].context='aa'
    # print('找到当前的wormhole')
    # print(wormholes)
    for wormhole in wormholes:
        mapfeature[wormhole['x']][wormhole['y']].wormhole = True
        # mapfeature[tunnel['x']][tunnel['y']].context = '*'
        # print('wormhole name : ',wormhole['name'])
        mapfeature[wormhole['x']][wormhole['y']].wormholecontext = wormhole['name']

        mapfeature[wormhole['x']][wormhole['y']].context = wormhole['name']



    for x in range(w):
        for y in range(h):
            # addneighboursnew(mapfeature[x][y])
            addneighboursnewupdate(mapfeature[x][y])
            #addneighbourssimple(mapfeature[x][y])
    global tunnelsneighbours
    # print('打印一下当前的tunnelsneighbours的情况  ', tunnelsneighbours)
    # for tunnelsneighbour in  tunnelsneighbours:
        # print('实际的坐标的情况   x',tunnelsneighbour.x,'   y:', tunnelsneighbour.y)
    # mapshow(mapfeature)
#program control
#判断是否需要使用boundary ，如果不使用boundary 我们也就不需要找到一个可以进入内部的player了

#这个函数用来判断是否地图的基本特点。

def  boundary_get():
    global mapfeature
    global tunnels
    global meteors
    global maptype
    global map_width
    global map_height
    global PointPrority
##如果我们需要boundary
    #首先要判断所有的player都是不是在内部
    x = []
    y = []
    #这个地方用于判断我的所有的player中是否有已经在内部的
    for tunnel in (tunnels):
        # print(tunnel)
        x.append(tunnel['x'])
        y.append(tunnel['y'])

    xmax = max(x)
    xmin = min(x)
    ymax = max(y)
    ymin = min(y)

    xmax=14
    xmin=4
    ymax=14
    ymin=4
    maptype=2

    #我们这个时候要判断是否需要使用虫洞吗？？？
    startx=3
    starty=10

    endx=5
    endy=4
    mapshow(mapfeature)
    maptype=2
    start=mapfeature[startx][starty]
    end = mapfeature[endx][endy]
    global path
    path=[]
    if start.tunnel == 'no' and not start.wall and end.tunnel=='no' and not end.wall:
        path1=getpath(start,end)
        # get_actionfrompathold()
        ac=get_actionfrompath()
        if  flag_getsolution:
            print('我们找到了到内部的情况哦哦哦')

            print('实际路径')
            for pa in path1:
                print('走的坐标，x:',pa.x,'  y:', pa.y)
            maptype=2
        else:
            print('我们真的找不到到内部的情况啊')
            maptype=1
    maptype=2

    #如果石头或者tunnel处于很多的状态，我们设定我们吃敌人优先，否则我们设定吃豆子优先
    barriaer=len(meteors)+len(tunnels)
    if barriaer<=0.2*map_width*map_height:

        PointPrority=True
    else:
        PointPrority=False



    #如果我们发现中间是进不去的时候怎么办，我们实际上，就应当记录下来powerset的位置


    return [xmin,ymin,xmax,ymax],maptype


global tunnelsneighbours
tunnelsneighbours=[]
def addneighboursnewupdate(a):
    global map_height
    global map_width

    # print('我的坐标x:' + str(a.x) + '  y:' + str(a.y))

    i = 0
    if a.x > 0:
        # print('找左邻居')
        if mapfeature[a.x - 1][a.y].tunnel == 'no':
            if mapfeature[a.x-1][a.y].wormhole==True:
                a.neighbours.append(mapfeature[a.x-1][a.y])
                c=findwormpair(x=a.x-1,y=a.y) #将当前是wormhole的坐标传入下去

                a.neighbours.append(mapfeature[c['x']][c['y']])
            else:

                a.neighbours.append(mapfeature[a.x - 1][a.y])
        else:
            a.neighbours.append(mapfeature[a.x - 1][a.y])
            # c = findgoodneighbour(mapfeature[a.x - 1][a.y])
            c = findgoodneighbourV2(mapfeature[a.x - 1][a.y])
            if (c.x == a.x) and (c.y == a.y):
                # print('me没有')
                pass
            else:
                # print('我们准备在ntunnelsneighbours 中添加tunnelsneighbour是的情况',c)
                if c not  in tunnelsneighbours:
                    tunnelsneighbours.append(c)
                a.neighbours.append(c)
    if a.x < map_width - 1:
        # print('找右邻居')
        if mapfeature[a.x + 1][a.y].tunnel == 'no':
            if mapfeature[a.x + 1][a.y].wormhole == True:
                a.neighbours.append(mapfeature[a.x + 1][a.y])
                c = findwormpair(x=a.x + 1,y=a.y)  # 将当前是wormhole的坐标传入下去

                a.neighbours.append(mapfeature[c['x']][c['y']])
            else:
                a.neighbours.append(mapfeature[a.x + 1][a.y])
        else:
            a.neighbours.append(mapfeature[a.x + 1][a.y])
            c = findgoodneighbourV2(mapfeature[a.x + 1][a.y])
            if (c.x == a.x) and (c.y == a.y):
                # print('me没有')
                pass
            else:
                # print('我们准备在ntunnelsneighbours 中添加tunnelsneighbour是的情况',c)
                if c not  in tunnelsneighbours:
                    tunnelsneighbours.append(c)
                a.neighbours.append(c)
    if a.y > 0:
        # print('找上邻居')

        if mapfeature[a.x][a.y - 1].tunnel == 'no':
            if mapfeature[a.x][a.y-1].wormhole == True:
                a.neighbours.append(mapfeature[a.x][a.y - 1])
                c = findwormpair(x=a.x , y=a.y-1)  # 将当前是wormhole的坐标传入下去

                a.neighbours.append(mapfeature[c['x']][c['y']])
            else:
                a.neighbours.append(mapfeature[a.x][a.y - 1])
        else:
            a.neighbours.append(mapfeature[a.x][a.y - 1])
            c = findgoodneighbourV2(mapfeature[a.x][a.y - 1])
            if (c.x == a.x) and (c.y == a.y):
                # print('me没有')
                pass
            else:
                # print('我们准备在ntunnelsneighbours 中添加tunnelsneighbour是的情况',c)
                if c not  in tunnelsneighbours:
                    tunnelsneighbours.append(c)

                a.neighbours.append(c)
    if a.y < map_height - 1:
        # print('找下邻居')
        if mapfeature[a.x][a.y + 1].tunnel == 'no':
            if mapfeature[a.x ][a.y+1].wormhole == True:
                a.neighbours.append(mapfeature[a.x][a.y + 1])
                c = findwormpair(x=a.x, y=a.y+1)  # 将当前是wormhole的坐标传入下去

                a.neighbours.append(mapfeature[c['x']][c['y']])
            else:
                a.neighbours.append(mapfeature[a.x][a.y + 1])
        else:
            a.neighbours.append(mapfeature[a.x][a.y + 1])
            c = findgoodneighbourV2(mapfeature[a.x][a.y + 1])
            if (c.x == a.x) and (c.y == a.y):
                # print('me没有')
                pass
            else:
                # print('我们准备在ntunnelsneighbours 中添加tunnelsneighbour是的情况',c)
                if c not  in tunnelsneighbours:
                    tunnelsneighbours.append(c)

                a.neighbours.append(c)

def findwormpair(x,y):

    global wormholes

    # print('开始找对应的wormhole了')
    for wormhole in wormholes:
        if wormhole['x']==x and wormhole['y']==y:
            name=wormhole['name']


    # print('打印之前的名字。name   ',name)
    if name.isupper():

        name=name.lower()
        # print('打印变成小写后的的name   ', name)
        for wormhole in wormholes:
            if wormhole['name']==name:
                # print('打印找到返回的wormhole',wormhole)
                return wormhole
    else:
        name=name.upper()
        # print('打印变成大写后的字母  ， ', name)
        for wormhole in wormholes:
            if wormhole['name']==name:
                # print('打印返回的wormhole，' ,wormhole)
                return wormhole



def addneighboursnew(a):
    global map_height
    global map_width

    print('我的坐标x:' + str(a.x) + '  y:' + str(a.y))


    i=0
    if a.x > 0:
        print('找左邻居')
        if mapfeature[a.x - 1][a.y].tunnel == 'no':
            a.neighbours.append(mapfeature[a.x - 1][a.y])
        else:
            c=findgoodneighbour(mapfeature[a.x - 1][a.y])
            if (c.x == a.x) and (c.y == a.y):
                print('me没有')
                pass
            else:

                a.neighbours.append(c)
    if a.x < map_width- 1:
        print('找右邻居')
        if mapfeature[a.x + 1][a.y].tunnel =='no':
            a.neighbours.append(mapfeature[a.x + 1][a.y])
        else:
            c=findgoodneighbour(mapfeature[a.x +1][a.y])
            if (c.x == a.x) and (c.y == a.y):
                print('me没有')
                pass
            else:

                a.neighbours.append(c)
    if a.y> 0:
        print('找上邻居')

        if mapfeature[a.x ][a.y-1].tunnel == 'no':

            a.neighbours.append(mapfeature[a.x ][a.y-1])
        else:
            c=findgoodneighbour(mapfeature[a.x][a.y - 1])
            if (c.x==a.x) and (c.y==a.y):
                print('me没有')
                pass
            else:

                a.neighbours.append(c)
    if a.y < map_height - 1:
        print('找下邻居')
        if mapfeature[a.x][a.y+1].tunnel == 'no':


            a.neighbours.append(mapfeature[a.x][a.y+1])
        else:
            c=findgoodneighbour(mapfeature[a.x][a.y+1])
            if (c.x==a.x) and (c.y==a.y):
                print('me没有')
                pass
            else:

                a.neighbours.append(c)

def addneighbourssimple(a):
    global map_height
    global map_width

    # print('我的坐标x:' + str(a.x) + '  y:' + str(a.y))


    if a.x > 0:

            a.neighbours.append(mapfeature[a.x - 1][a.y])

    if a.x < map_width- 1:

            a.neighbours.append(mapfeature[a.x + 1][a.y])

    if a.y> 0:

            a.neighbours.append(mapfeature[a.x ][a.y-1])

    if a.y < map_height - 1:

            a.neighbours.append(mapfeature[a.x][a.y+1])

#findgoodneighbour()是仅仅对tunnel一个方向的邻居进行了规划
#即→↑这种连续的没有进行计算
def findgoodneighbour(b):
    i = 0

    # print('实际传过来的b的坐标的情况x'+str(b.x)+'  y:'+str(b.y))

    if mapfeature[b.x][b.y].tunnel == 'up':

        while mapfeature[b.x][b.y - i].tunnel == 'up':
            # print('实际的i'+str(i))
            i = i + 1

        # print('实际的up邻居坐标x:'+str(b.x)+'  y:'+str(b.y-i))
        return mapfeature[b.x][b.y - i]
    elif mapfeature[b.x][b.y].tunnel == 'down':
        while mapfeature[b.x][b.y + i].tunnel == 'down':
            # print('实际的i' + str(i))
            i = i + 1
        # print('实际的down邻居坐标x:' + str(b.x) + '  y:' + str(b.y + i))
        return mapfeature[b.x][b.y + i]
    elif mapfeature[b.x][b.y].tunnel == 'left':
        while mapfeature[b.x - i][b.y].tunnel == 'left':
            # print('实际的i' + str(i))
            i = i + 1
        # print('实际的left邻居坐标x:' + str(b.x-i) + '  y:' + str(b.y))
        return mapfeature[b.x - i][b.y]
    elif mapfeature[b.x][b.y].tunnel == 'right':
        while mapfeature[b.x + i][b.y].tunnel == 'right':
            # print('实际的i' + str(i))
            i = i + 1
        # print('实际的right邻居坐标x:' + str(b.x+i) + '  y:' + str(b.y))
        return mapfeature[b.x+i][b.y]
#findgoodneighbourV1(oldb)是仅仅对tunnel一个方向的邻居进行了规划
#采用递归的方式进行确定下一步的neighbours是谁
def findgoodneighbourV1(oldb):
    global mapfeature
    mapfeaturecopy=copy.deepcopy(mapfeature)
    goodneighbour=mapfeaturecopy[oldb.x][oldb.y]
    b=goodneighbour
    print('实际传过来的b的坐标的情况x'+str(b.x)+'  y:'+str(b.y))
    while b.tunnel != 'no':
        print('当前的b的位置','x  ',b.x,' y   :',b.y)
        print('当前b的tunnel的情况', b.tunnel)
        print('当前b的tunnel的情况', b.tunnel)
        if mapfeaturecopy[b.x][b.y].tunnel == 'up':
            i = 0
            while mapfeaturecopy[b.x][b.y-i].tunnel == 'up':
                # print('实际的i'+str(i))
                i = i + 1
                goodneighbour=mapfeaturecopy[b.x][b.y-i]
            print('实际的up邻居坐标x:'+str(b.x)+'  y:'+str(b.y-i))
            b=goodneighbour
            # return mapfeature[b.x][b.y-i]
        elif mapfeaturecopy[b.x][b.y].tunnel == 'down':
            i = 0
            while mapfeaturecopy[b.x][b.y + i].tunnel == 'down':
                # print('实际的i' + str(i))
                i = i + 1
                goodneighbour=mapfeaturecopy[b.x][b.y+i]
            print('实际的down邻居坐标x:' + str(b.x) + '  y:' + str(b.y + i))
            b=goodneighbour
        elif mapfeaturecopy[b.x][b.y].tunnel == 'left':
            i = 0
            while mapfeaturecopy[b.x-i][b.y].tunnel == 'left':
                print('实际的i' + str(i))
                i = i + 1
                goodneighbour=mapfeaturecopy[b.x-i][b.y]

            print('实际的left邻居坐标x:' + str(b.x-i) + '  y:' + str(b.y))
            b=goodneighbour
            # return mapfeature[b.x-i][b.y]
        elif mapfeaturecopy[b.x][b.y].tunnel == 'right':
            i = 0
            while mapfeaturecopy[b.x+i][b.y].tunnel == 'right':
                # print('实际的i' + str(i))
                i = i + 1
                goodneighbour=mapfeaturecopy[b.x+i][b.y]
            print('实际的right邻居坐标x:' + str(b.x+i) + '  y:' + str(b.y))
            b=goodneighbour

    return b
#findgoodneighbourV2(b)是仅仅对tunnel一个方向的邻居进行了规划
#采用递归的方式进行确定下一步的neighbours是谁
def findgoodneighbourV2(b):
    # global mapfeature
    # mapfeaturecopy=copy.deepcopy(mapfeature)
    # goodneighbour=mapfeaturecopy[oldb.x][oldb.y]
    goodneighbour=b
    # print('实际传过来的b的坐标的情况x'+str(b.x)+'  y:'+str(b.y))
    if mapfeature[b.x][b.y].tunnel == 'up':
        i = 0
        while mapfeature[b.x][b.y - i].tunnel == 'up':
            # print('实际的i'+str(i))
            i = i + 1
            goodneighbour = mapfeature[b.x][b.y - i]
        # print('实际的up邻居坐标x:' + str(b.x) + '  y:' + str(b.y - i))
        if goodneighbour.tunnel == 'no':
            # print('的确是no')
            return goodneighbour
        else:
            a = findgoodneighbourV2(goodneighbour)
            return a


        # return mapfeature[b.x][b.y-i]
    elif mapfeature[b.x][b.y].tunnel == 'down':
        i = 0
        while mapfeature[b.x][b.y + i].tunnel == 'down':
            # print('实际的i' + str(i))
            i = i + 1
            goodneighbour = mapfeature[b.x][b.y + i]
        # print('实际的down邻居坐标x:' + str(b.x) + '  y:' + str(b.y + i))
        if goodneighbour.tunnel == 'no':
            # print('的确是no')
            return goodneighbour
        else:
            a = findgoodneighbourV2(goodneighbour)
            return a
    elif mapfeature[b.x][b.y].tunnel == 'left':
        i = 0
        while mapfeature[b.x - i][b.y].tunnel == 'left':
            # print('实际的i' + str(i))
            i = i + 1
            goodneighbour = mapfeature[b.x - i][b.y]

        # print('实际的left邻居坐标x:' + str(b.x - i) + '  y:' + str(b.y))
        # print('Actual good neightbour', goodneighbour.tunnel)
        # print('Actual good neighbours的postions',goodneighbour.x,'  ', goodneighbour.y)
        if goodneighbour.tunnel == 'no':
            # print('的确是no')
            return goodneighbour
        else:
            a=findgoodneighbourV2(goodneighbour)
            return a
        # return mapfeature[b.x-i][b.y]
    elif mapfeature[b.x][b.y].tunnel == 'right':
        i = 0
        while mapfeature[b.x + i][b.y].tunnel == 'right':
            # print('实际的i' + str(i))
            i = i + 1
            goodneighbour = mapfeature[b.x + i][b.y]
        # print('实际的right邻居坐标x:' + str(b.x + i) + '  y:' + str(b.y))
        if goodneighbour.tunnel == 'no':
            # print('的确是no')
            return goodneighbour
        else:
            a = findgoodneighbourV2(goodneighbour)
            return a





#这个函数的作用是将attackmode 切换成为防守模式的时候,还是会记录下敌人的位置.在最后有可能造成我们得到no solution的情况
#这个函数的作用是将敌人本身的目标设定为空气了
def updateanamypositionattackmode():
    global mapfeature
    global oldanamyposition

    for i in range(len(oldanamyposition)):
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].anamy = False  # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].trueanamy = False  # 敌人的位置

        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].context = '0'  # 敌人的位置

    oldanamyposition=[]


#通过这个函数实现地方位置的判断
#这个函数是为了实现敌人周围相邻的地方设定为anmy的性质
oldanamyposition = []
def updateanamyposition(anamyplayers):
    global mapfeature
    global oldanamyposition
    global map_width
    global map_height

    # print('我们正在更新敌人的位置')



    # print('old position的情况',oldanamyposition)

    for i in range(len(oldanamyposition)):
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].trueanamy = False # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].anamy = False  # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].context = '0'  # 敌人的位置


    oldanamyposition = []
    # print('anamyplayers情况', oldanamyposition)
    for i in range(len(anamyplayers)):
        # print('我们正在内部更新敌人的位置')
        # print('打印一下我方的teamid',constants.team_id)
        # if anamyplayers[i]['team']==constants.team_id:
            oldanamyposition.append({'x':anamyplayers[i]['x'],'y':anamyplayers[i]['y']})
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].anamy=True #敌人的位置
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].trueanamy = True  # 敌人的位置
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].context= 'TA'  # 敌人的位置
            # print(anamyplayers[i]['x'])
            # print(anamyplayers[i]['y'])
            # print(anamyplayers[i]['x'] > 0)
            # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].wall )
            # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].tunnel == 'no')
            if anamyplayers[i]['x'] > 0 and not mapfeature[anamyplayers[i]['x']-1][anamyplayers[i]['y']].wall  and \
                    mapfeature[anamyplayers[i]['x']-1][anamyplayers[i]['y']].tunnel in  'no':
                mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].anamy = True  # 敌人的位置
                mapfeature[anamyplayers[i]['x']-1][anamyplayers[i]['y']].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x':anamyplayers[i]['x']-1,'y':anamyplayers[i]['y']})


            if anamyplayers[i]['x'] < map_width-1 and not mapfeature[anamyplayers[i]['x']+1][anamyplayers[i]['y']].wall and \
                    mapfeature[anamyplayers[i]['x']+1][anamyplayers[i]['y']].tunnel in 'no':
                mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].anamy = True   # 敌人的位置
                mapfeature[anamyplayers[i]['x']+1][anamyplayers[i]['y']].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x':anamyplayers[i]['x']+1,'y':anamyplayers[i]['y']})

            if anamyplayers[i]['y'] > 0 and not mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']-1].wall  and \
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']-1].tunnel in 'no':
                mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].anamy=True  # 敌人的位置
                mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']-1].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x':anamyplayers[i]['x'],'y':anamyplayers[i]['y']-1})

            if anamyplayers[i]['y'] < map_height-1 and not mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']+1].wall and \
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']+1].tunnel in 'no':
                mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].anamy=True
                mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']+1].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x':anamyplayers[i]['x'],'y':anamyplayers[i]['y']+1})


#通过这个函数实现地方位置的判断
#这个函数是为了更好的实现周围相邻敌人设置成anamy属性的情况。
#如果经过了tunnel或者是经过了wormhole也会计算出来得到的
def updateanamypositionUpgrade(anamyplayers):
    global mapfeature
    global oldanamyposition
    global map_width
    global map_height


    # print('我们正在更新敌人的位置')

    # print('old position的情况',oldanamyposition)

    for i in range(len(oldanamyposition)):
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].trueanamy = False  # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].anamy = False  # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].context = '0'  # 敌人的位置


    oldanamyposition = []
    # print('anamyplayers情况', oldanamyposition)
    for i in range(len(anamyplayers)):
        # print('我们正在内部更新敌人的位置')
        # print('打印一下我方的teamid',constants.team_id)
        # if anamyplayers[i]['team']==constants.team_id:
        oldanamyposition.append({'x': anamyplayers[i]['x'], 'y': anamyplayers[i]['y']})
        mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].anamy = True  # 敌人的位置
        mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].trueanamy = True  # 敌人的位置
        mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].context = 'TA'  # 敌人的位置
        # print(anamyplayers[i]['x'])
        # print(anamyplayers[i]['y'])
        # print(anamyplayers[i]['x'] > 0)
        # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].wall )
        # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].tunnel == 'no')
        if anamyplayers[i]['x'] > 0 and not mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].wall:
            # and \
            if  mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].tunnel not in 'no':
                a=findgoodneighbour(mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']])
                if (a.x == anamyplayers[i]['x']) and (a.y == anamyplayers[i]['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})


            else:
                if mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].wormhole:
                    newworm=findwormpair(anamyplayers[i]['x'] - 1,anamyplayers[i]['y'])
                    mapfeature[newworm['x']][newworm['y']].anamy=True
                    mapfeature[newworm['x']][newworm['y']].context='A'
                    oldanamyposition.append({'x': newworm['x']-1, 'y': newworm['y']})

                else:
                    mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].anamy = True  # 敌人的位置
                    mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayers[i]['x']-1, 'y': anamyplayers[i]['y']})

        if anamyplayers[i]['x'] < map_width - 1 and not mapfeature[anamyplayers[i]['x'] + 1][
            anamyplayers[i]['y']].wall:

            if mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].tunnel not in 'no':
                a=findgoodneighbour(mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']])
                if (a.x == anamyplayers[i]['x']) and (a.y == anamyplayers[i]['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})

            else:
                if   mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].wormhole:
                    newworm = findwormpair(anamyplayers[i]['x'] + 1,anamyplayers[i]['y'])
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x']+1, 'y': newworm['y']})

                else:

                    mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].anamy = True  # 敌人的位置
                    mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayers[i]['x']+1, 'y': anamyplayers[i]['y']})


        if anamyplayers[i]['y'] > 0 and not mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].wall:
            if mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].tunnel not in 'no':
                a=findgoodneighbour(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1])

                if (a.x == anamyplayers[i]['x']) and (a.y == anamyplayers[i]['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].wormhole:
                    newworm = findwormpair(anamyplayers[i]['x'],anamyplayers[i]['y'] - 1)
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']-1})

                else:
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].anamy = True  # 敌人的位置
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayers[i]['x'], 'y': anamyplayers[i]['y']-1})


        if anamyplayers[i]['y'] < map_height - 1 and not mapfeature[anamyplayers[i]['x']][
            anamyplayers[i]['y'] + 1].wall:
            if mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].tunnel not in 'no':
                a=findgoodneighbour(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1])
                if (a.x == anamyplayers[i]['x']) and (a.y == anamyplayers[i]['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].wormhole:
                    newworm = findwormpair(anamyplayers[i]['x'],anamyplayers[i]['y'] + 1)
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']+1})

                else:
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].anamy = True  # 敌人的位置
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayers[i]['x'], 'y': anamyplayers[i]['y']+1})


    pass

def updateanamypositionsimple(anamyplayers):
    global mapfeature
    global oldanamyposition
    global map_width
    global map_height

    for i in range(len(oldanamyposition)):
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].anamy = False  # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].trueanamy = False  # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].context = '0'  # 敌人的位置

    oldanamyposition = []
    for i in range(len(anamyplayers)):
        # if anamyplayers[i]['team']==1111:
            oldanamyposition.append({'x':anamyplayers[i]['x'],'y':anamyplayers[i]['y']})
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].trueanamy=True #敌人的位置
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].anamy=True #敌人的位置
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].context= 'TA'  # 敌人的位置


#这个函数是将新看到pwoer加入powersetall 当中，并且根据player当前的位置，进行更新是否已经有player已经被吃掉了 什么的
#用来更新得到的powerset 分成powersetin 和  powersetout   或者分成powerseta b c d  这样以便更加均衡的吃豆子
def update_powerset(myplayers,anamyplayers):
    global powersetout
    global powersetin
    global powersetround
    global powersetall


    # 当前的的最大的范围是x 5 - 14  y  5 -14
    for i in range(len(powersetround)):
        if powersetround[i]['x'] >= boundary[0] and powersetround[i]['x'] <= boundary[2] and powersetround[i]['y'] >= boundary[1] and \
                powersetround[i]['y'] <=  boundary[3]:
            if powersetround[i] in powersetin:

                pass
            else:
                # powersetall.append(powersetround[i])
                powersetin.append(powersetround[i])
        else:
            if powersetround[i] in powersetout:
                pass
            else:
                # powersetall.append(powersetround[i])
                powersetout.append(powersetround[i])
    # powersetall.extend(powersetround)
    # powersetout.extend(powersetround)
    # powersetin.extend(powersetround)
    for i in range(len(myplayers)):

        try:
            for power in (powersetout):

                if myplayers[i]['x'] == power['x'] and myplayers[i]['y'] == power['y']:
                    powersetout.remove(power)
                    # powersetall.remove(power)




            for power in (powersetin):
                if myplayers[i]['x'] == power['x'] and myplayers[i]['y'] == power['y']:
                    powersetin.remove(power)
                    # powersetall.remove(power)

        except:
            print('error in updatepowerset')
            pass

    for i in range(len(anamyplayers)):


        try:
            for power in (powersetout):

                    if anamyplayers[i]['x'] == power['x'] and anamyplayers[i]['y'] == power['y']:
                        powersetout.remove(power)
                        # powersetall.remove(power)

                    pass


            for  power in (powersetin):
                if anamyplayers[i]['x'] == power['x'] and anamyplayers[i]['y'] == power['y']:
                    powersetin.remove(power)
                    # powersetall.remove(power)

        except:
            print('error in updatepowerset')
    powersetall=[]
    powersetall.extend(powersetout)
    powersetall.extend(powersetin)
    powerset_positionrecord()
    # print('在updatepowerset中打印一下 powersetall ',powersetall)
    # print('在updatepowerset中打印一下 powersetin ',powersetin)
    # print('在updatepowerset中打印一下 powersetout ',powersetout)

#这个函数的作用就是实现根据powersetall的情况将其分成每个player去吃powerA B　C　Ｄ
def dividepowerset(myplayers):
    global  powersetall
    global powersetA
    global powersetB
    global powersetC
    global powersetD
    global playerA
    global playerB
    global playerC
    global playerD
    powersetA = []
    powersetB = []
    powersetC = []
    powersetD = []

    # print('在dividied中打印powersetall',powersetall)

    for power in powersetall:
        if findnearestplayer(power, myplayers) == playerA:
            powersetA.append(power)
        if findnearestplayer(power, myplayers) == playerB:
            powersetB.append(power)
        if findnearestplayer(power, myplayers) == playerC:
            powersetC.append(power)
        if findnearestplayer(power, myplayers) == playerD:
            powersetD.append(power)

    #

    # print('我们分别打印一下当前的ABCD的powerset中给的情况')
    # print('A',powersetA)
    # print('B',powersetB)
    # print('C', powersetC)
    # print('D', powersetD)
    pass
#这个函数是为了将我们的这些powerset 分成很多组---分别对应到我们各自player
def findnearestplayer(power,myplayers):
    playerbest=[]

    dis = 10000000000000
    # print('在寻找距离最近的powerout的情况下，我们打印一下powerserout以便更好判断我们得到的是不是最好的')
    # print(powersetout)
    for player in myplayers:
        tempdis=abs(player['x']-power['x'])+abs(player['y']-power['y'])
        if tempdis<dis:
            dis=tempdis
            playerbest=player
    return playerbest
global powersetPos
powersetPos=[]
global lengthofpowersetPos
lengthofpowersetPos=-1
global CangobestPos
CangobestPos=False

def powerset_positionrecord():
    global powersetout
    global powersetin
    global powersetround
    global powersetall
    global powersetPos
    global lengthofpowersetPos
    global bestPos1,bestPos2,bestPos3,bestPos4

    for power in powersetround:
        powerpos=[power['x'],power['y']]
        if powerpos not in powersetPos:
            powersetPos.append(powerpos)


    # print('我们看一下更新的powerset的实际的位置',powersetPos)
    # print('我们来看一下，实际的powerset的位置，总共有多少个？',len(powersetPos))

    #使用一种聚类的算法找到最密集的区域，然后记录其中的一个位置，然后能过够开始吃豆子
    #采用聚类算法--Kmeans， 这个地方不能采用= 号，因为后面随着中心点的变化 会变化的很大，所以，容易造成抖动，所以我们需要不能使用等号，
    #为了避免同时宣导相同的点？？？？
    if len(powersetPos)>lengthofpowersetPos :

        lengthofpowersetPos = len(powersetPos)

        dataSet = np.array(powersetPos)
        # print(dataSet)
        # 执行keams 算法
        bestPos1, bestPos2, bestPos3, bestPos4 = kmeans.KMeans(dataSet, 4)
        CangobestPos = True
    elif len(powersetPos)==lengthofpowersetPos and random.random()<0.2:
        dataSet = np.array(powersetPos)
        # print(dataSet)
        # 执行keams 算法
        bestPos1, bestPos2, bestPos3, bestPos4 = kmeans.KMeans(dataSet, 4)


        #
        print('bestpos1', bestPos1)
        print('bestpos2', bestPos2)
        print('bestpos3', bestPos3)
        print('bestpos4', bestPos4)
        # print('best4的情况',bestPos4[0])
        # print('')
        # if np.isnan(bestPos4[0].all()):
        #     print('best4isnnanananananananannanananan a')





# This function is to update  the actual position
# to the map
#更新实际的powerset对应的map的位置的context
#
global oldpowerposition
oldpowerposition=[]

def updatepowersetposition():

    global powersetin
    global powersetout
    global mapfeature
    global playerworm
    global map_height
    global map_width
    global oldpowerposition



    # 默认是power for则我们用别的符号去代替，然后将能够使用context去表示这个东西到底是不是power
    # 每次更新的时候，都可以将所有的power都恢复默认，然后重新根据当前的powersetout 和powetsetin 分别
    # 重新更新当前的datasset，所以
    # 要想更新map，我们还需要进行每一个层级都进行更新
    # 更细你的顺序就是
    # 1、powerset
    # 2、tunne
    # 3、annamyset

    # print('进入更新powerset的函数')





    for i in range(len(oldpowerposition)):
        mapfeature[oldpowerposition[i]['x']][oldpowerposition[i]['y']].power = '0'  #
        mapfeature[oldpowerposition[i]['x']][oldpowerposition[i]['y']].context = '0'  #

    oldpowerposition = []
    for i in range(len(powersetin)):

        # print('打印powerset')
        # print(powersetin[i])
        oldpowerposition.append({'x': powersetin[i]['x'], 'y': powersetin[i]['y']})
        mapfeature[powersetin[i]['x']][powersetin[i]['y']].power = '$'  #
        mapfeature[powersetin[i]['x']][powersetin[i]['y']].context = 'S'  #

    for i in range(len(powersetout)):

        print('打印powersetout')
        print(powersetout[i])
        oldpowerposition.append({'x': powersetout[i]['x'], 'y': powersetout[i]['y']})
        mapfeature[powersetout[i]['x']][powersetout[i]['y']].power = '$'  #
        mapfeature[powersetout[i]['x']][powersetout[i]['y']].context = 'S'  #

    # print('已经更新powerset的地图信息了')


def mapshow(mapfeature):
    global map_height
    global map_width
    for y in range(map_height):
        b = ''
        for x in range(map_width):
            b += mapfeature[x][y].context + '   '
        print(b)




def update_playerABCD(myplayers):
    global playerworm
    global playerout
    global playerattackup
    global playerattackdown
#这个函数是用来判断player是否已经在tunnel内部了
    global flag_playerinworm  # 这个变量判断是否有player已经进入到内部
    # 判断playerworm 是否进入到了 tunnel 内部  这个函数的奇纳提我们已经找到了playerworm
    # 这个就是为了判断当前给的playworm是否进入到了wormhole当中去
    global flag_initialworm
    if playerworm is None:
        if not flag_playerinworm:  # 如果玩家A还没在洞中
            # 这个就是为了判断当前给的playworm是否进入到了wormhole当中去
            update_playerAandwormhole(myplayers)  # playerworm,playerwormtarget 这个函数全局更新这两个全局变量
            flag_initialworm = True
        # 我们首先更新了playerworm的直实际的位置
        # 然后实际位置的情况下，再来判断这个player是否再tunnel内部
        myplayerscopy = copy.deepcopy(myplayers)
        # print('my actual copy:  ', myplayerscopy)
        if len(myplayerscopy) == 4:
            for player in (myplayers):
                if player['id'] == playerworm['id']:
                    # 我们进行更新playerworm
                    playerworm = player

            myplayerscopy.remove(playerworm)
            playerout=myplayerscopy[0]
            # print('溢出之后的copy    ', myplayerscopy)
            playerattackup = myplayerscopy[1]
            playerattackdown = myplayerscopy[2]
            # print('plaeyrattckup的情况    ', playerattackup)
    else:
        # 我们首先更新了playerworm的直实际的位置
        # 然后实际位置的情况下，再来判断这个player是否再tunnel内部
        myplayerscopy = copy.deepcopy(myplayers)
        # print('my actual copy:  ', myplayerscopy)

        if len(myplayers)==4:
            for player in (myplayers):
                if player['id'] == playerworm['id']:
                    # 我们进行更新playerworm
                    playerworm = player
                else:
                    playerout = player
            myplayerscopy.remove(playerworm)
            playerout = myplayerscopy[0]
            # print('溢出之后的copy    ', myplayerscopy)
            playerattackup = myplayerscopy[1]
            playerattackdown = myplayerscopy[2]



        elif len(myplayerscopy) == 3:
            for player in (myplayers):
                if player['id'] == playerworm['id']:
                    # 我们进行更新playerworm
                    playerworm = player
            print('我们能移出playerworm吗？')
            print('playerworm 是多少', playerworm)
            print('myplayers    ',myplayers)
            print('myplayers copy',myplayerscopy)

            if playerworm in myplayerscopy:
                myplayerscopy.remove(playerworm)
            else:
                update_playerAandwormhole(myplayers)

                whetherplayerAin(xmin=boundary[0], ymin=boundary[1], xmax=boundary[2], ymax=boundary[3])
                for player in (myplayers):
                    if player['id'] == playerworm['id']:
                        # 我们进行更新playerworm
                        playerworm = player
                myplayerscopy.remove(playerworm)

            playerout = myplayerscopy[0]
                # print('溢出之后的copy    ', myplayerscopy)
            playerattackup = myplayerscopy[1]
                # playerattackdown = myplayerscopy[2]



        elif len(myplayerscopy) == 2:
            for player in (myplayers):
                if player['id'] == playerworm['id']:
                    # 我们进行更新playerworm
                    playerworm = player

            if playerworm in myplayerscopy:
                myplayerscopy.remove(playerworm)
            else:
                update_playerAandwormhole(myplayers)

                whetherplayerAin(xmin=boundary[0], ymin=boundary[1], xmax=boundary[2], ymax=boundary[3])
                for player in (myplayers):
                    if player['id'] == playerworm['id']:
                        # 我们进行更新playerworm
                        playerworm = player
                myplayerscopy.remove(playerworm)
            playerout = myplayerscopy[0]


            # print('plaeyrattckup的情况    ', playerattackup)
        # 这个东西判断的前提是要更新playerworm
        whetherplayerAin(xmin=boundary[0], ymin=boundary[1], xmax=boundary[2], ymax=boundary[3])
        if not flag_playerinworm:  # and not flag_initialworm:  # 如果玩家A还没在洞中
            # 这个就是为了判断当前给的playworm是否进入到了wormhole当中去
            # print('玩家还不在洞中2')
            update_playerAandwormhole(myplayers)  # playerworm,playerwormtarget 这个函数全局更新这两个全局变量

def update_playerAandwormhole(myplayers):
    # myplayers data
    # {'id': 0, 'score': 0, 'sleep': 0, 'team': 2222, 'x': 0, 'y': 7}
    #
    # {'id': 1, 'score': 0, 'sleep': 0, 'team': 2222, 'x': 19, 'y': 7}
    #
    # {'id': 2, 'score': 0, 'sleep': 0, 'team': 2222, 'x': 0, 'y': 12}
    #
    # {'id': 3, 'score': 0, 'sleep': 0, 'team': 2222, 'x': 19, 'y': 12}
    global playerworm
    global wormwholetarget



    global playerwormtarget

    ibest = 0;
    jbest = 0;

    disbest = mindistancebetweenwormandplayer(myplayers[0], wormwholetarget[0])
    for i in range(len(myplayers)):
        for j in range(len(wormwholetarget)):
            tempdis = mindistancebetweenwormandplayer(myplayers[i], wormwholetarget[j])
            if tempdis <= disbest:
                disbest = tempdis
                ibest = i
                jbest = j

    playerworm = myplayers[ibest]

    playerwormtarget = wormwholetarget[jbest]


global flag_playerinworm
flag_playerinworm=False
def whetherplayerAin(xmin,ymin,xmax,ymax):

    global wormholetarget
    global playerworm
    global playerwormtarget
    global flag_playerinworm
    global flagplayerinworm
    global flaggetAplayer




    if playerworm['x'] > xmin and playerworm['x'] < xmax and playerworm['y'] > ymin and playerworm['y'] < ymax:
        # print('我们的那个需要的player已经进入了tunnel内部了')
        flag_playerinworm = True
    else:
        # print('我们的那个需要的player已经进不在tunnel内部了')
        flag_playerinworm=False


#计算wormwhole 和
def mindistancebetweenwormandplayer(player,worm):
    dis=abs(player['x']-worm['x'])+abs(player['y']-worm['y'])
    return dis


#we are in the tunnel已经进入了tunnel 内部
#默认我们没有在tunnnel内部的情况
#我们通过这个返回能够进入内部的wormwhole
global flag_findwormwholein
flag_findwormwholein=False
#这个函数的作用是找到wormhole，
#如果没有东西进去对的话就找到一个wormhole
def find_wormhole(xmin,ymin,xmax,ymax):
    global powerset
    global tunnels
    global wormholes
    global mapfeature
    global flagfindwormwholein
    global wormwholetarget
    wormholetemp = []
    wormwholetarget = []
    wormholescopy=copy.deepcopy(wormholes)

    for i in range(len(wormholes)):
        if wormholes[i]['x'] > xmin and wormholes[i]['x'] < xmax and wormholes[i]['y'] > ymin and wormholes[i]['y'] < ymax:
            wormholetemp.append(wormholes[i])

    for i in range(len(wormholetemp)):
        wormholes.remove(wormholetemp[i])

    wormwholetarget = wormholes
    wormholes=wormholescopy
    # print(wormhole)
    flagfindwormwholein = True
    return wormwholetarget


#this function is to tell it is a wormhole or not
def iswormhole(x,y):
    global wormholes

    for wormhole in wormholes:
        if wormhole['x']==x and wormhole['y']==y:
            return True

    return False
#这个函数给定目标的坐标
def istunnelneighbour(startx,starty,endx,endy):
    # global tunnels
    global tunnelsneighbours
    # print('当前的tunnelneighbours',tunnelsneighbours)
    for tunnelsneighbour in tunnelsneighbours:
        if tunnelsneighbour.x==endx and tunnelsneighbour.y==endy and distancecalculate(startx,starty,endx,endy )>1:
            return True

    return False
def viatunnelnewaction(startx,starty,endx,endy):
        global tunnels
        global mapfeature

        if startx > 0:
            # print('找左邻居')
            if mapfeature[startx - 1][starty].tunnel == 'no':

                # a.neighbours.append(mapfeature[a.x - 1][a.y])
                # print('左面的方块是居然不是tunnel')
                pass
            else:
                c = findgoodneighbourV2(mapfeature[startx - 1][starty])
                if (c.x == endx) and (c.y == endy):
                    # print('我们的左边的邻居导致了最终end情况')
                    newendx=startx-1
                    newendy=starty
                    return newendx,newendy

        if startx < map_width - 1:
            # print('找右邻居')
            if mapfeature[startx + 1][starty].tunnel == 'no':
                # a.neighbours.append(mapfeature[a.x + 1][a.y])
                # print('右面的方块是居然不是tunnel')

                pass
            else:
                c = findgoodneighbourV2(mapfeature[startx + 1][starty])
                if (c.x == endx) and (c.y == endy):

                    # print('我们的右边的邻居导致了最终end的情况')
                    newendx = startx +1
                    newendy = starty
                    return newendx, newendy

        if starty > 0:
            # print('找上邻居')

            if mapfeature[startx][starty - 1].tunnel == 'no':
                # print('上面的方块是居然不是tunnel')

                pass
                # a.neighbours.append(mapfeature[a.x][a.y - 1])
            else:
                c = findgoodneighbourV2(mapfeature[startx][starty - 1])
                if (c.x == endx) and (c.y == endy):
                    # print('我们的上边的邻居导致了最终end的情况')
                    newendx = startx
                    newendy = starty-1
                    return newendx, newendy


        if starty < map_height - 1:
            # print('找下邻居')
            if mapfeature[startx][starty + 1].tunnel == 'no':
                # print('下面的方块是居然不是tunnel')

                pass
                # a.neighbours.append(mapfeature[a.x][a.y + 1])
            else:
                c = findgoodneighbourV2(mapfeature[startx][starty + 1])
                if (c.x == endx) and (c.y == endy):
                    # print('me没有')
                    # print('我们的下边的邻居导致了最终end的情况')
                    newendx = startx
                    newendy = starty+1
                    return newendx, newendy
def get_poweractionmap2(playerX,powersetX,anamyplayers):
    global playerA
    global playerB
    global playerC
    global playerD

    global powersetin
    global powersetout
    global powersetall
    global mapfeature
    global flag_getsolution
    global path
    global Attack

    global Intera  # 惯性概念


    path = []

    if len(powersetX) == 0:  # 如果已经空了 则根据模式，如果是攻击模式，则进行攻击。如果不是攻击模式，则尽量原远离自己的伙伴和墙壁，是否可以采用
        # 还需要再继续再进行修改
        # print('这个时候根本不会执行这个代码')
        # defaultposition=[]
        if Attack:  #这个可以加入养猪计划
            # return get_attackactionmap2(playerX=playerX,anamyplayers=anamyplayers,powersetX=powersetX)
            if playerX==None:
                pass
            else:

                # return get_poweractionmap2UpgradeV2(playerX=playerX, anamyplayers=anamyplayers, powersetX=powersetX)

                #实时更短的计算敌人的聚类的
                return get_attackactionmap2Upgrade_parta(playerX=playerX, anamyplayers=anamyplayers, powersetX=powersetX)

        else:
            # print('我们再防守模式下，powerset中啥都没有')
            #这个时候，实际上，我们可以返回None --这个时候我也建议返回None
            print('在防守模式中，powerset为空，应当返回None才对')
            return None
            # return random.randint(0,4)

    else:
        # print('打印一下当前的powersetX',powersetX)
        powersettemp = findnearestpowerX(playerX,powersetX)  # 实际上，我们寻找power的方式要是基于power的才行
        # print(player)
        # print(powersettemp)
        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[powersettemp['x']][powersettemp['y']]

        # print('playerX   ',playerX['id'],' 运动路径')
        # print('起始的位置')
        # print('x' + str(start.x) + 'y' + str(start.y))
        # print('终止的位置')
        # print('x' + str(end.x) + 'y' + str(end.y))
        #
        path = getpath(start, end)
        # print('传回来的flaggetsolution是否有用呢', flag_getsolution)
        if flag_getsolution:
            # print('flag_getsolution 是ok的')
            # powersetall.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            ac = get_actionfrompath()
            return ac
        else:
            print('吃豆子的情况下没有找到solution，不应该出现这种情况把')
            if Attack:
                print('吃豆子的情况下没有找到solution，最不该出现的情况')
                # print('攻击模式下,我们是没有用的,进行的是随机运动,')
                # 后面要修改为攻击敌人的情况
                ac = random.randint(1, 4)
                return ac
            else:
                print('吃豆子的情况下没有找到solution，敌人堵住了的情况下')

                print('我们在逃跑模式下,但是返回None')
                # w我们要逃跑，所以留给后面的逃跑的情况给出action
                # return random.randint(1, 4)
                return None
def get_attackactionmap2(playerX,powersetX,anamyplayers):  #最原始的攻击的版本
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1,bestPos2,bestPos3,bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global path
    path = []
    action = []
    if len(anamyplayers) == 0:
        if len(powersetX)==0:  #这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
            #在这种情况下我们进行敌人的搜素和寻找豆子
            defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
            # print('向四个角随机运动')

            if playerX == playerB:
                # print('得到的bestpos的结果',bestPos1)


                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[bestPos1[0]][bestPos1[1]]
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))

                if start.x==end.x and start.y == end.y:
                    return random.randint(1,4)
                path = getpath(start, end)
                if flag_getsolution:
                    ac = get_actionfrompath()
                    return ac
                else:
                    return defaultmove[0][random.randint(0, 1)]
            elif playerX == playerC :
                # print('得到的bestpos的结果',bestPos2)
                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos2[0]][bestPos2[1]]
                    # print('起始的位置')
                    # print('x' + str(start.x) + 'y' + str(start.y))
                    # print('终止的位置')
                    # print('x' + str(end.x) + 'y' + str(end.y))
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[1][random.randint(0, 1)]
                except:
                    return defaultmove[1][random.randint(0, 1)]

            elif playerX == playerD:
                # print('得到的bestpos的结果',bestPos3)
                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos3[0]][bestPos3[1]]

                    if start.x==end.x and start.y == end.y:
                        #我们进行了随机的运动
                        return random.randint(1,4)
                    # print('起始的位置')
                    # print('x' + str(start.x) + 'y' + str(start.y))
                    # print('终止的位置')
                    # print('x' + str(end.x) + 'y' + str(end.y))
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[2][random.randint(0, 1)]
                except:
                    return defaultmove[2][random.randint(0, 1)]

            elif playerX == playerA:
                # print('得到的bestpos的结果',bestPos4)


                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos4[0]][bestPos4[1]]

                    if start.x==end.x and start.y == end.y:
                        return random.randint(1,4)
                    # print('起始的位置')
                    # print('x' + str(start.x) + 'y' + str(start.y))
                    # print('终止的位置')
                    # print('x' + str(end.x) + 'y' + str(end.y))
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[3][random.randint(0, 1)]
                except:
                    return defaultmove[3][random.randint(0, 1)]

        else:
            #这个情况下 就要进行吃豆子
            # print('应该根本不会调用到当前的这个代码把？？？？？')
            return get_poweractionmap2(playerX ,powersetX,anamyplayers)

            #还是继续进行吃豆子
    else:
        # print('打印一下所有的敌人',anamyplayers)
        #这种情况下就要指导有敌人的情况下，我们就要找出最好攻击哪个敌人
        anamytarget=findbestanamytarget(anamyplayers)
        #定位选择吃哪个player


        attack_positionA,attack_positionB,attack_positionC,attack_positionD= get_attackanamyposition2(anamytarget)


    if playerX==playerA and playerX is not None:

        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[attack_positionA['x']][attack_positionA['y']]

        # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
        # print('起始的位置')
        # print('x' + str(start.x) + 'y' + str(start.y))
        # print('终止的位置')
        # print('x' + str(end.x) + 'y' + str(end.y))
        path = getpath(start, end)
        if flag_getsolution:
            # print('在攻击的时候playerUp,flag_getsolution 是ok的')
            # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac


    if playerX==playerB and playerX is not None:
        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[attack_positionB['x']][attack_positionB['y']]

        # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
        # print('起始的位置')
        # print('x' + str(start.x) + 'y' + str(start.y))
        # print('终止的位置')
        # print('x' + str(end.x) + 'y' + str(end.y))
        path = getpath(start, end)
        if flag_getsolution:
            # print('在攻击的时候playerUp,flag_getsolution 是ok的')
            # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac

        pass
    if playerX==playerC and playerX is not None:
        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[attack_positionC['x']][attack_positionC['y']]

        # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
        # print('起始的位置')
        # print('x' + str(start.x) + 'y' + str(start.y))
        # print('终止的位置')
        # print('x' + str(end.x) + 'y' + str(end.y))
        path = getpath(start, end)
        if flag_getsolution:
            # print('在攻击的时候playerUp,flag_getsolution 是ok的')
            # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac


    if playerX==playerD and playerX is not None     :
        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[attack_positionD['x']][attack_positionD['y']]

        # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
        # print('起始的位置')
        # print('x' + str(start.x) + 'y' + str(start.y))
        # print('终止的位置')
        # print('x' + str(end.x) + 'y' + str(end.y))
        path = getpath(start, end)
        if flag_getsolution:
            # print('在攻击的时候playerUp,flag_getsolution 是ok的')
            # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac
def findbestanamytarget(anamyplayers):
    pointbest = -1
    pointtemp = 0
    anamyttarget = []

    for anamyplayer in anamyplayers:
        pointtemp = anamyplayer['score']
        if pointtemp > pointbest:
            pointbest = pointtemp
            anamyttarget = anamyplayer
            # print('打印一下当前要追的敌人',anamyttarget)
    return anamyttarget
global flag_get_Attackanamy
def get_poweractionmap2UpgradeV2(playerX,powersetX,anamyplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1, bestPos2, bestPos3, bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global path
    global flag_get_Attackanamy
    global  attack_positionA, attack_positionB, attack_positionC, attack_positionD


    if playerX is None:
        return None


    seeanamys = []
    if len(anamyplayers)==0:
        pass
    else:
        for anamyplayer in anamyplayers:
            if anamyplayer['x'] <= playerX['x'] + visionrange and anamyplayer['x'] >= playerX['x'] - visionrange and \
                    anamyplayer['y'] <= playerX['y'] + visionrange and anamyplayer['y'] >= playerX['y'] - visionrange:
                seeanamys.append(anamyplayer)

    path = []
    action = []
    if len(anamyplayers) == 0:
        if len(seeanamys) == 0:
            if len(powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
                # 在这种情况下我们进行敌人的搜素和寻找豆子
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # print('向默认的pos位置跑去')
                if playerX == playerB:
                    # print('得到的bestpos的结果',bestPos1)

                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos1[0]][bestPos1[1]]
                    # print('起始的位置')
                    # print('x' + str(start.x) + 'y' + str(start.y))
                    # print('终止的位置')
                    # print('x' + str(end.x) + 'y' + str(end.y))

                    if start.x == end.x and start.y == end.y:
                        return random.randint(1, 4)
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[0][random.randint(0, 1)]
                elif playerX == playerC:
                    # print('得到的bestpos的结果',bestPos2)
                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos2[0]][bestPos2[1]]
                        # print('起始的位置')
                        # print('x' + str(start.x) + 'y' + str(start.y))
                        # print('终止的位置')
                        # print('x' + str(end.x) + 'y' + str(end.y))
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return defaultmove[1][random.randint(0, 1)]
                    except:
                        return defaultmove[1][random.randint(0, 1)]

                elif playerX == playerD:
                    # print('得到的bestpos的结果',bestPos3)
                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos3[0]][bestPos3[1]]

                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)
                        # print('起始的位置')
                        # print('x' + str(start.x) + 'y' + str(start.y))
                        # print('终止的位置')
                        # print('x' + str(end.x) + 'y' + str(end.y))
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return defaultmove[2][random.randint(0, 1)]
                    except:
                        return defaultmove[2][random.randint(0, 1)]

                elif playerX == playerA:
                    # print('得到的bestpos的结果',bestPos4)

                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos4[0]][bestPos4[1]]

                        if start.x == end.x and start.y == end.y:
                            return random.randint(1, 4)
                        # print('起始的位置')
                        # print('x' + str(start.x) + 'y' + str(start.y))
                        # print('终止的位置')
                        # print('x' + str(end.x) + 'y' + str(end.y))
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return defaultmove[3][random.randint(0, 1)]
                    except:
                        return defaultmove[3][random.randint(0, 1)]


            else:
                # 这个情况下 就要进行吃豆子
                # print('应该根本不会调用到当前的这个代码把？？？？？')
                return get_poweractionmap2(playerX, powersetX, anamyplayers)

        else:
            print('这些也应该不会执行的把')
            if flag_get_Attackanamy:
                pass
            else:

                anamytarget = findbestanamytarget(anamyplayers)
                    # 定位选择吃哪个player
                # 这个是之前的，根据敌人的具体的位置，我们将其向墙上挤
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD ,org= get_attackanamyposition2(anamytarget)

                #这个仅仅考虑了敌人的下一步的运动的可能性的位置
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD ,org= get_anamynextmoveposition(anamytarget)
                #这个函数是包含了上面两个函数的综合的考虑
                attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(anamytarget)

                flag_get_Attackanamy=True

            # 还是继续进行吃豆子
    else:
        # print('打印一下所有的敌人',anamyplayers)
        # 这种情况下就要指导有敌人的情况下，我们就要找出最好攻击哪个敌人
        if flag_get_Attackanamy:
            pass
        else:

            anamytarget = findbestanamytarget(anamyplayers)
            # 定位选择吃哪个player
            # 这个是之前的，根据敌人的具体的位置，我们将其向墙上挤
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD ,org= get_attackanamyposition2(anamytarget)

            # 这个仅仅考虑了敌人的下一步的运动的可能性的位置
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD ,org= get_anamynextmoveposition(anamytarget)
            # 这个函数是包含了上面两个函数的综合的考虑
            attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(anamytarget)

            flag_get_Attackanamy = True

    if playerX == playerA:
        if attack_positionA is None:
            if len(powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
                # 在这种情况下我们进行敌人的搜素和寻找豆子
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # print('向默认的pos位置跑去')
                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos4[0]][bestPos4[1]]

                    if start.x == end.x and start.y == end.y:
                        return random.randint(1, 4)
                    # print('起始的位置')
                    # print('x' + str(start.x) + 'y' + str(start.y))
                    # print('终止的位置')
                    # print('x' + str(end.x) + 'y' + str(end.y))
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[3][random.randint(0, 1)]
                except:
                    return defaultmove[3][random.randint(0, 1)]
            else:
                # 这个情况下 就要进行吃豆子
                # print('应该根本不会调用到当前的这个代码把？？？？？')
                return get_poweractionmap2(playerX, powersetX, anamyplayers)

        else:

            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionA['x']][attack_positionA['y']]

        # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
        # print('起始的位置')
        # print('x' + str(start.x) + 'y' + str(start.y))
        # print('终止的位置')
        # print('x' + str(end.x) + 'y' + str(end.y))
        path = getpath(start, end)
        if flag_getsolution:
            # print('在攻击的时候playerUp,flag_getsolution 是ok的')
            # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac

    if playerX == playerB :
        if attack_positionB is None:
            if len(powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
                # 在这种情况下我们进行敌人的搜素和寻找豆子
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # print('向默认的pos位置跑去')
                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos1[0]][bestPos1[1]]
                    # print('起始的位置')
                    # print('x' + str(start.x) + 'y' + str(start.y))
                    # print('终止的位置')
                    # print('x' + str(end.x) + 'y' + str(end.y))

                    if start.x == end.x and start.y == end.y:
                        return random.randint(1, 4)
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[0][random.randint(0, 1)]
                except:
                    return defaultmove[0][random.randint(0, 1)]
            else:
                # 这个情况下 就要进行吃豆子
                # print('应该根本不会调用到当前的这个代码把？？？？？')
                return get_poweractionmap2(playerX, powersetX, anamyplayers)

        else:

            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionB['x']][attack_positionB['y']]



        # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
        # print('起始的位置')
        # print('x' + str(start.x) + 'y' + str(start.y))
        # print('终止的位置')
        # print('x' + str(end.x) + 'y' + str(end.y))
        path = getpath(start, end)
        if flag_getsolution:
            # print('在攻击的时候playerUp,flag_getsolution 是ok的')
            # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac

        pass
    if playerX == playerC:
        if attack_positionC is None:
            if len(powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
                # 在这种情况下我们进行敌人的搜素和寻找豆子
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # print('向默认的pos位置跑去')
                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos2[0]][bestPos2[1]]
                    # print('起始的位置')
                    # print('x' + str(start.x) + 'y' + str(start.y))
                    # print('终止的位置')
                    # print('x' + str(end.x) + 'y' + str(end.y))
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[1][random.randint(0, 1)]
                except:
                    return defaultmove[1][random.randint(0, 1)]
            else:
                # 这个情况下 就要进行吃豆子
                # print('应该根本不会调用到当前的这个代码把？？？？？')
                return get_poweractionmap2(playerX, powersetX, anamyplayers)

        else:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionC['x']][attack_positionC['y']]

        # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
        # print('起始的位置')
        # print('x' + str(start.x) + 'y' + str(start.y))
        # print('终止的位置')
        # print('x' + str(end.x) + 'y' + str(end.y))
        path = getpath(start, end)
        if flag_getsolution:
            # print('在攻击的时候playerUp,flag_getsolution 是ok的')
            # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac

    if playerX == playerD:
        if attack_positionD is None:
            if len(powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
                # 在这种情况下我们进行敌人的搜素和寻找豆子
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # print('向默认的pos位置跑去')
                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos3[0]][bestPos3[1]]

                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)
                    # print('起始的位置')
                    # print('x' + str(start.x) + 'y' + str(start.y))
                    # print('终止的位置')
                    # print('x' + str(end.x) + 'y' + str(end.y))
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[2][random.randint(0, 1)]
                except:
                    return defaultmove[2][random.randint(0, 1)]
            else:
                # 这个情况下 就要进行吃豆子
                # print('应该根本不会调用到当前的这个代码把？？？？？')
                return get_poweractionmap2(playerX, powersetX, anamyplayers)

        else:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionD['x']][attack_positionD['y']]

        # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
        # print('起始的位置')
        # print('x' + str(start.x) + 'y' + str(start.y))
        # print('终止的位置')
        # print('x' + str(end.x) + 'y' + str(end.y))
        path = getpath(start, end)
        if flag_getsolution:
            # print('在攻击的时候playerUp,flag_getsolution 是ok的')
            # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac

global flag_get_Attackanamy
flag_get_Attackanamy=False
def get_attackactionmap2Upgrade_parta(playerX,powersetX,anamyplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1,bestPos2,bestPos3,bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global flag_get_Attackanamy
    global path
    global attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal,targetnearestplayer
    global visionrange
    seeanamys=[]

    if playerX is None:
        return None

    for anamyplayer in anamyplayers:
        if anamyplayer['x']<= playerX['x']+visionrange and anamyplayer['x']>= playerX['x']-visionrange and anamyplayer['y']<= playerX['y']+visionrange and anamyplayer['y']>= playerX['y']-visionrange:
            seeanamys.append(anamyplayer)

    path = []
    action = []
    if len(anamyplayers) == 0:
        if len(seeanamys) == 0:
            # flag_get_Attackanamy=False
            if len(powersetX)==0:  #这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
                #在这种情况下我们进行敌人的搜素和寻找豆子
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # # print('向四个角随机运动')

                if playerX == playerB:
                    # print('得到的bestpos的结果',bestPos1)
                    try:

                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos1[0]][bestPos1[1]]
                        # print('起始的位置')
                        # print('x' + str(start.x) + 'y' + str(start.y))
                        # print('终止的位置')
                        # print('x' + str(end.x) + 'y' + str(end.y))

                        if start.x==end.x and start.y == end.y:
                            return random.randint(1,4)
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return defaultmove[0][random.randint(0, 1)]
                    except:
                        return defaultmove[0][random.randint(0, 1)]
                elif playerX == playerC :
                    # print('得到的bestpos的结果',bestPos2)
                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos2[0]][bestPos2[1]]
                        # print('起始的位置')
                        # print('x' + str(start.x) + 'y' + str(start.y))
                        # print('终止的位置')
                        # print('x' + str(end.x) + 'y' + str(end.y))
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return defaultmove[1][random.randint(0, 1)]
                    except:
                        return defaultmove[1][random.randint(0, 1)]

                elif playerX == playerD:
                    # print('得到的bestpos的结果',bestPos3)
                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos3[0]][bestPos3[1]]

                        if start.x==end.x and start.y == end.y:
                            #我们进行了随机的运动
                            return random.randint(1,4)
                        # print('起始的位置')
                        # print('x' + str(start.x) + 'y' + str(start.y))
                        # print('终止的位置')
                        # print('x' + str(end.x) + 'y' + str(end.y))
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return defaultmove[2][random.randint(0, 1)]
                    except:
                        return defaultmove[2][random.randint(0, 1)]

                elif playerX == playerA:
                    # print('得到的bestpos的结果',bestPos4)


                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos4[0]][bestPos4[1]]

                        if start.x==end.x and start.y == end.y:
                            return random.randint(1,4)
                        # print('起始的位置')
                        # print('x' + str(start.x) + 'y' + str(start.y))
                        # print('终止的位置')
                        # print('x' + str(end.x) + 'y' + str(end.y))
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return defaultmove[3][random.randint(0, 1)]
                    except:
                        return defaultmove[3][random.randint(0, 1)]

            else:
                #这个情况下 就要进行吃豆子
                print('应该根本不会调用到当前的这个代码把？？？？？')
                return get_poweractionmap2(playerX ,powersetX,anamyplayers)
        else:
            pass
                #还是继续进行吃豆子
    else:
        if flag_get_Attackanamy:
            return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)
        else:
            # print('打印一下所有的敌人',anamyplayers)
            #这种情况下就要指导有敌人的情况下，我们就要找出最好攻击哪个敌人
            # print('出现敌人scorekey错误，查看问题,打印敌人日志111111',anamyplayers)
            anamytarget=findbestanamytarget(anamyplayers)
            #定位选择吃哪个player


            # attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal=get_anamynextmoveposition(anamytarget)
            attack_positionA, attack_positionB, attack_positionC, attack_positionD=get_attackanamyposition2V2(anamytarget)
            attack_positionOriginal={'x':anamytarget['x'],'y':anamytarget['y']}
            targetnearestplayer=get_nearestanamy_player()
            flag_get_Attackanamy=True
            print('Go eat anamy')
            return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)


    # flag_get_Attackanamy=True
def get_attackactionmap2Upgrade_partb(playerX,anamyplayers,powersetX):
    global playerA
    global playerB
    global playerC
    global playerD
    global path
    global mapfeature
    global flag_getsolution
    global attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal,targetnearestplayer
    path=[]
    print('向敌人的位置进行攻击')
    if playerX==playerA :
        #是不是距离敌人的原点最近
        if playerX==targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                print('找到路径')
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos=get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX==playerB:
        #是不是距离敌人的原点最近
        if playerX==targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos=get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                # print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX==playerC :
        #是不是距离敌人的原点最近
        if playerX==targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos=get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                # print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX==playerD:
        #是不是距离敌人的原点最近
        if playerX==targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos=get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac

def get_nearestanamyposition(playerX):
    global attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal,targetnearestplayer
    bestpos=None
    disbest=100
    if attack_positionA is not None:
        disA=stepdistance(playerX,attack_positionA)
        disbest=disA
        bestpos = attack_positionA
    if attack_positionB is not None:
        disB= stepdistance(playerX, attack_positionB)
        if disB<disbest:
            disbest = disB
            bestpos = attack_positionB
    if attack_positionC is not None:
        disC= stepdistance(playerX, attack_positionC)
        if disC<disbest:
            disbest = disC
            bestpos = attack_positionC
    if attack_positionD is not None:
        disD= stepdistance(playerX, attack_positionD)
        if disD<disbest:
            disbest = disD
            bestpos = attack_positionD
    if bestpos is not None:
        if bestpos==attack_positionA:
            attack_positionA=None
        elif bestpos==attack_positionB:
            attack_positionB=None
        elif bestpos==attack_positionC:
            attack_positionC=None
        elif bestpos==attack_positionD:
            attack_positionD=None
        # print('打印当前actionABCD的情况')
        # print('attack_positionA:',attack_positionA)
        # print('attack_positionB:',attack_positionB)
        # print('attack_positionC:',attack_positionC)
        # print('attack_positionD:',attack_positionD)
    else:
        # print('返回原始的位置')
        bestpos=attack_positionOriginal

    return bestpos

def get_nearestanamy_player():
    global playerA
    global playerB
    global playerC
    global playerD
    global attack_positionOriginal
    bestplayer=[]
    disbest=100
    if playerA is not None:
        disA=stepdistance(playerA,attack_positionOriginal)
        disbest=disA
        bestplayer = playerA
    if playerB is not None:
        disB= stepdistance(playerB, attack_positionOriginal)
        if disB<disbest:
            disbest = disA
            bestplayer = playerB

    if playerC is not None:
        disC = stepdistance(playerC, attack_positionOriginal)
        disbest = disC
        if disC<disbest:
            disbest = disC
            bestplayer = playerC
    if playerD is not None:
        disD = stepdistance(playerD, attack_positionOriginal)
        disbest = disD
        if disD<disbest:
            disbest = disD
            bestplayer = playerD
    return bestplayer

#这个函数的作用是得到敌人将来能够移动的未来的可能的位置
def get_anamynextmoveposition(anamyplayer):
    global mapfeature
    global map_height
    global map_width
    x=anamyplayer['x']
    y=anamyplayer['y']
    tar_pos={'x':x,'y':y}
    #找它的上邻居
    NextmovePos=[]
    if y>0 and not mapfeature[x][y-1].wall:
        a=mapfeature[x][y-1]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x':a.x,'y':a.y})
        elif a.tunnel != 'no':
            c=findgoodneighbourV2(a)
            if a.x==c.x and a.x==c.y:
               print('same point')
            else:
                NextmovePos.append({'x':c.x,'y':c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if y<map_height-1 and not mapfeature[x][y+1].wall:
        a=mapfeature[x][y+1]
        # print('敌人是存在下邻居')
        if a.wormhole:
            NextmovePos.append({'x':a.x,'y':a.y})
        elif a.tunnel != 'no':
            c=findgoodneighbourV2(a)
            if a.x==c.x and a.x==c.y:
               print('same point')
            else:
                NextmovePos.append({'x':c.x,'y':c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x>0 and not mapfeature[x-1][y].wall:
        a=mapfeature[x-1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x':a.x,'y':a.y})
        elif a.tunnel != 'no':
            c=findgoodneighbourV2(a)
            if a.x==c.x and a.x==c.y:
               print('same point')
            else:
                NextmovePos.append({'x':c.x,'y':c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x<map_width-1 and not mapfeature[x+1][y].wall:
        a=mapfeature[x+1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x':a.x,'y':a.y})
        elif a.tunnel != 'no':
            c=findgoodneighbourV2(a)
            if a.x==c.x and a.x==c.y:
               print('same point')
            else:
                NextmovePos.append({'x':c.x,'y':c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})

    num=len(NextmovePos)
    if num==4:
        Pos_A=NextmovePos[0]
        Pos_B=NextmovePos[1]
        Pos_C=NextmovePos[2]
        Pos_D=NextmovePos[3]
        Pos_or=tar_pos
    elif num==3:
        Pos_A=NextmovePos[0]
        Pos_B=NextmovePos[1]
        Pos_C=NextmovePos[2]
        Pos_D=tar_pos
        Pos_or=tar_pos

    elif num==2:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = tar_pos
        Pos_D = tar_pos
        Pos_or=tar_pos

    elif num==1:
        Pos_A = NextmovePos[0]
        Pos_B = tar_pos
        Pos_C = tar_pos
        Pos_D = tar_pos
        Pos_or=tar_pos

    elif num==0:
        Pos_A = None
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or=tar_pos

    # print('这个敌人的下一次移动的位置',NextmovePos)
    return Pos_A,Pos_B,Pos_C,Pos_D,Pos_or

def get_attackanamyposition2(anamytarget):
    global map_width
    global map_height

    # 判断敌人所在位置范围
    x = anamytarget['x']
    y = anamytarget ['y']

#根据敌人的位置，减少下部追击敌人的方式

    if x <= map_width / 2 and y <= map_height / 2 and x <= y:  # 如果其本身就在左上角 ,从下逼到上  #加入额外判断能否追死的情况

        Target_Ax = x  # 目标位置设定为 右侧
        Target_Ay = y
        Target_Bx = x + 1  # 目标位置设定右下
        Target_By = y
        Target_Cx = x - 1
        Target_Cy = y
        Target_Dx = x + 1
        Target_Dy = y - 1

    if x <= map_width / 2 and y <= map_height / 2 and x >= y:  # 如果其本身就在左上角 ,从右逼到左
        Target_Ax = x  # 目标位置设定为 下侧
        Target_Ay = y
        Target_Bx = x   # 目标位置设定左下
        Target_By = y + 1
        Target_Cx = x
        Target_Cy = y - 1
        Target_Dx = x - 1
        Target_Dy = y + 1

    if x >= map_width / 2 and y <= map_height / 2 and x / 2 >= y:  # 如果其本身就在右上角 ,从左逼到右
        Target_Ax = x  # 目标位置设定为 下侧
        Target_Ay = y
        Target_Bx = x  # 目标位置设定右下
        Target_By = y + 1
        Target_Cx=x
        Target_Cy=y-1
        Target_Dx = x + 1
        Target_Dy = y + 1
    if x >= map_width / 2 and y <= map_height / 2 and x / 2 <= y:  # 如果其本身就在右上角 ,从下逼到上
        Target_Ax = x  # 目标位置设定为 左侧
        Target_Ay = y
        Target_Bx = x - 1  # 目标位置设定左下
        Target_By = y
        Target_Cx=x+1
        Target_Cy=y
        Target_Dx = x - 1
        Target_Dy = y - 1
        # 在地图下方的情况
    if x <= map_width / 2 and y >= map_height / 2 and x <= y / 2:  # 如果其本身就在左下角 ,上逼到下
        Target_Ax = x  # 目标位置设定为 左侧
        Target_Ay = y
        Target_Bx = x + 1  # 目标位置设定左下
        Target_By = y
        Target_Cx=x-1
        Target_Cy=y
        Target_Dx = x + 1
        Target_Dy = y + 1

    if x <= map_width / 2 and y >= map_height / 2 and x >= y / 2:  # 如果其本身就在左下角 ,从右逼到左
        Target_Ax = x  # 目标位置设定为 右侧
        Target_Ay = y
        Target_Bx = x  # 目标位置设定y右下
        Target_By = y - 1
        Target_Cx = x
        Target_Cy=y+1
        Target_Dx = x - 1
        Target_Dy = y - 1

    if x >= map_width / 2 and y >= map_height / 2 and x >= y:  # 如果其本身就在右下角 ,从左逼到右
        Target_Ax = x  # 目标位置设定为 右侧
        Target_Ay = y
        Target_Bx = x  # 目标位置设定左下
        Target_By = y - 1
        Target_Cx=x
        Target_Cy=y+1
        Target_Dx = x + 1
        Target_Dy = y - 1

    if x >= map_width / 2 and y >= map_height / 2 and x <= y:  # 如果其本身就在右下角 ,从上逼到下
        Target_Ax = x  # 目标位置设定为 右侧
        Target_Ay = y
        Target_Bx = x - 1  # 目标位置设定右下
        Target_By = y
        Target_Cx=x+1
        Target_Cy=y
        Target_Dx = x - 1
        Target_Dy = y + 1


    if Target_Bx < 0:
        Target_Bx = 0
    if Target_By < 0:
        Target_By = 0
    if Target_Bx >= map_width:
        Target_Bx = map_width - 1
    if Target_By >= map_height:
        Target_By = map_width - 1

    if Target_Cx < 0:
        Target_Cx = 0
    if Target_Cy < 0:
        Target_Cy = 0
    if Target_Cx >= map_width:
        Target_Cx = map_width - 1
    if Target_Cy >= map_height:
        Target_Cy = map_width - 1
    if Target_Dx < 0:
        Target_Dx = 0
    if Target_Dy < 0:
        Target_Dy = 0
    if Target_Dx >= map_width:
        Target_Dx = map_width - 1
    if Target_Dy >= map_height:
        Target_Dy = map_width - 1


    Target_A = {'x': Target_Ax, 'y': Target_Ay}

    Target_B = {'x': Target_Bx, 'y': Target_By}
    Target_C = {'x': Target_Cx, 'y': Target_Cy}
    Target_D = {'x': Target_Dx, 'y': Target_Dy}
    return Target_A,Target_B, Target_C,Target_D

    # 还要考虑敌人突然不在视野内的情况下
    # 这个时候还要考虑如果前面是虫洞的情况下,我们也要跟过去,这个时候需要利用的player自身的视野
         # 同样,如果我们逃跑,也要走向

def get_attackanamyposition2V2(anamytarget):
    global map_width
    global map_height

    # 判断敌人所在位置范围
    x = anamytarget['x']
    y = anamytarget['y']

    # 根据敌人的位置，减少下部追击敌人的方式

    if x <= map_width / 2 and y <= map_height / 2 and x <= y:  # 如果其本身就在左上角 ,从下逼到上  #加入额外判断能否追死的情况

        Target_Ax = x  # 目标位置
        Target_Ay = y

        Target_A = {'x': Target_Ax, 'y': Target_Ay}

        pos=get_anamynextDirMovePosition(x, y, 4)
        if pos is None:
            Target_B = None
        else:

            Target_Bx =pos['x']  # 目标位置设定右下
            Target_By =pos['y']
            if Target_Bx < 0:
                Target_Bx = 0
            if Target_By < 0:
                Target_By = 0
            if Target_Bx >= map_width:
                Target_Bx = map_width - 1
            if Target_By >= map_height:
                Target_By = map_width - 1
            Target_B = {'x': Target_Bx, 'y': Target_By}

        pos=get_anamynextDirMovePosition(x,y,1)
        if pos is None:
            Target_C = None
        else:
            pos=get_anamynextDirMovePosition(pos['x'],pos['y'],3)
            if pos is None:
                Target_C = None
            else:
                Target_Cx = pos['x']
                Target_Cy = pos['y']
                if Target_Cx < 0:
                    Target_Cx = 0
                if Target_Cy < 0:
                    Target_Cy = 0
                if Target_Cx >= map_width:
                    Target_Cx = map_width - 1
                if Target_Cy >= map_height:
                    Target_Cy = map_width - 1
                Target_C = {'x': Target_Cx, 'y': Target_Cy}

        pos = get_anamynextDirMovePosition(x,y,2)

        if pos is None:
            Target_D=None
        else:
            Target_Dx = pos['x']
            Target_Dy = pos['y']
            if Target_Dx < 0:
                Target_Dx = 0
            if Target_Dy < 0:
                Target_Dy = 0
            if Target_Dx >= map_width:
                Target_Dx = map_width - 1
            if Target_Dy >= map_height:
                Target_Dy = map_width - 1
            Target_D = {'x': Target_Dx, 'y': Target_Dy}




    if x <= map_width / 2 and y <= map_height / 2 and x >= y:  # 如果其本身就在左上角 ,从右逼到左
        Target_Ax = x  # 目标位置
        Target_Ay = y

        Target_A = {'x': Target_Ax, 'y': Target_Ay}

        pos = get_anamynextDirMovePosition(x, y, 2)
        if pos is None:
            Target_B = None
        else:

            Target_Bx = pos['x']  # 目标位置设定右下
            Target_By = pos['y']
            if Target_Bx < 0:
                Target_Bx = 0
            if Target_By < 0:
                Target_By = 0
            if Target_Bx >= map_width:
                Target_Bx = map_width - 1
            if Target_By >= map_height:
                Target_By = map_width - 1
            Target_B = {'x': Target_Bx, 'y': Target_By}

        pos = get_anamynextDirMovePosition(x, y, 3)
        if pos is None:
            Target_C = None
        else:
            pos = get_anamynextDirMovePosition(pos['x'], pos['y'], 2)
            if pos is None:
                Target_C = None
            else:
                Target_Cx = pos['x']
                Target_Cy = pos['y']
                if Target_Cx < 0:
                    Target_Cx = 0
                if Target_Cy < 0:
                    Target_Cy = 0
                if Target_Cx >= map_width:
                    Target_Cx = map_width - 1
                if Target_Cy >= map_height:
                    Target_Cy = map_width - 1
                Target_C = {'x': Target_Cx, 'y': Target_Cy}

        pos = get_anamynextDirMovePosition(x, y, 4)

        if pos is None:
            Target_D = None
        else:
            Target_Dx = pos['x']
            Target_Dy = pos['y']
            if Target_Dx < 0:
                Target_Dx = 0
            if Target_Dy < 0:
                Target_Dy = 0
            if Target_Dx >= map_width:
                Target_Dx = map_width - 1
            if Target_Dy >= map_height:
                Target_Dy = map_width - 1
            Target_D = {'x': Target_Dx, 'y': Target_Dy}

    if x >= map_width / 2 and y <= map_height / 2 and x / 2 >= y:  # 如果其本身就在右上角 ,从左逼到右
        Target_Ax = x  # 目标位置
        Target_Ay = y

        Target_A = {'x': Target_Ax, 'y': Target_Ay}

        pos = get_anamynextDirMovePosition(x, y, 2)
        if pos is None:
            Target_B = None
        else:

            Target_Bx = pos['x']  # 目标位置设定右下
            Target_By = pos['y']
            if Target_Bx < 0:
                Target_Bx = 0
            if Target_By < 0:
                Target_By = 0
            if Target_Bx >= map_width:
                Target_Bx = map_width - 1
            if Target_By >= map_height:
                Target_By = map_width - 1
            Target_B = {'x': Target_Bx, 'y': Target_By}

        pos = get_anamynextDirMovePosition(x, y, 4)
        if pos is None:
            Target_C = None
        else:
            pos = get_anamynextDirMovePosition(pos['x'], pos['y'], 2)
            if pos is None:
                Target_C = None
            else:
                Target_Cx = pos['x']
                Target_Cy = pos['y']
                if Target_Cx < 0:
                    Target_Cx = 0
                if Target_Cy < 0:
                    Target_Cy = 0
                if Target_Cx >= map_width:
                    Target_Cx = map_width - 1
                if Target_Cy >= map_height:
                    Target_Cy = map_width - 1
                Target_C = {'x': Target_Cx, 'y': Target_Cy}

        pos = get_anamynextDirMovePosition(x, y, 3)

        if pos is None:
            Target_D = None
        else:
            Target_Dx = pos['x']
            Target_Dy = pos['y']
            if Target_Dx < 0:
                Target_Dx = 0
            if Target_Dy < 0:
                Target_Dy = 0
            if Target_Dx >= map_width:
                Target_Dx = map_width - 1
            if Target_Dy >= map_height:
                Target_Dy = map_width - 1
            Target_D = {'x': Target_Dx, 'y': Target_Dy}
    if x >= map_width / 2 and y <= map_height / 2 and x / 2 <= y:  # 如果其本身就在右上角 ,从下逼到上
        Target_Ax = x  # 目标位置
        Target_Ay = y

        Target_A = {'x': Target_Ax, 'y': Target_Ay}

        pos = get_anamynextDirMovePosition(x, y, 3)
        if pos is None:
            Target_B = None
        else:

            Target_Bx = pos['x']  # 目标位置设定右下
            Target_By = pos['y']
            if Target_Bx < 0:
                Target_Bx = 0
            if Target_By < 0:
                Target_By = 0
            if Target_Bx >= map_width:
                Target_Bx = map_width - 1
            if Target_By >= map_height:
                Target_By = map_width - 1
            Target_B = {'x': Target_Bx, 'y': Target_By}

        pos = get_anamynextDirMovePosition(x, y, 1)
        if pos is None:
            Target_C = None
        else:
            pos = get_anamynextDirMovePosition(pos['x'], pos['y'], 3)
            if pos is None:
                Target_C = None
            else:
                Target_Cx = pos['x']
                Target_Cy = pos['y']
                if Target_Cx < 0:
                    Target_Cx = 0
                if Target_Cy < 0:
                    Target_Cy = 0
                if Target_Cx >= map_width:
                    Target_Cx = map_width - 1
                if Target_Cy >= map_height:
                    Target_Cy = map_width - 1
                Target_C = {'x': Target_Cx, 'y': Target_Cy}

        pos = get_anamynextDirMovePosition(x, y, 2)

        if pos is None:
            Target_D = None
        else:
            Target_Dx = pos['x']
            Target_Dy = pos['y']
            if Target_Dx < 0:
                Target_Dx = 0
            if Target_Dy < 0:
                Target_Dy = 0
            if Target_Dx >= map_width:
                Target_Dx = map_width - 1
            if Target_Dy >= map_height:
                Target_Dy = map_width - 1
            Target_D = {'x': Target_Dx, 'y': Target_Dy}
    if x <= map_width / 2 and y >= map_height / 2 and x <= y / 2:  # 如果其本身就在左下角 ,上逼到下
        Target_Ax = x  # 目标位置
        Target_Ay = y

        Target_A = {'x': Target_Ax, 'y': Target_Ay}

        pos = get_anamynextDirMovePosition(x, y, 4)
        if pos is None:
            Target_B = None
        else:

            Target_Bx = pos['x']  # 目标位置设定右下
            Target_By = pos['y']
            if Target_Bx < 0:
                Target_Bx = 0
            if Target_By < 0:
                Target_By = 0
            if Target_Bx >= map_width:
                Target_Bx = map_width - 1
            if Target_By >= map_height:
                Target_By = map_width - 1
            Target_B = {'x': Target_Bx, 'y': Target_By}

        pos = get_anamynextDirMovePosition(x, y, 2)
        if pos is None:
            Target_C = None
        else:
            pos = get_anamynextDirMovePosition(pos['x'], pos['y'], 3)
            if pos is None:
                Target_C = None
            else:
                Target_Cx = pos['x']
                Target_Cy = pos['y']
                if Target_Cx < 0:
                    Target_Cx = 0
                if Target_Cy < 0:
                    Target_Cy = 0
                if Target_Cx >= map_width:
                    Target_Cx = map_width - 1
                if Target_Cy >= map_height:
                    Target_Cy = map_width - 1
                Target_C = {'x': Target_Cx, 'y': Target_Cy}

        pos = get_anamynextDirMovePosition(x, y, 1)

        if pos is None:
            Target_D = None
        else:
            Target_Dx = pos['x']
            Target_Dy = pos['y']
            if Target_Dx < 0:
                Target_Dx = 0
            if Target_Dy < 0:
                Target_Dy = 0
            if Target_Dx >= map_width:
                Target_Dx = map_width - 1
            if Target_Dy >= map_height:
                Target_Dy = map_width - 1
            Target_D = {'x': Target_Dx, 'y': Target_Dy}

    if x <= map_width / 2 and y >= map_height / 2 and x >= y / 2:  # 如果其本身就在左下角 ,从右逼到左
        Target_Ax = x  # 目标位置
        Target_Ay = y

        Target_A = {'x': Target_Ax, 'y': Target_Ay}

        pos = get_anamynextDirMovePosition(x, y, 1)
        if pos is None:
            Target_B = None
        else:

            Target_Bx = pos['x']  # 目标位置设定右下
            Target_By = pos['y']
            if Target_Bx < 0:
                Target_Bx = 0
            if Target_By < 0:
                Target_By = 0
            if Target_Bx >= map_width:
                Target_Bx = map_width - 1
            if Target_By >= map_height:
                Target_By = map_width - 1
            Target_B = {'x': Target_Bx, 'y': Target_By}

        pos = get_anamynextDirMovePosition(x, y, 3)
        if pos is None:
            Target_C = None
        else:
            pos = get_anamynextDirMovePosition(pos['x'], pos['y'], 1)
            if pos is None:
                Target_C = None
            else:
                Target_Cx = pos['x']
                Target_Cy = pos['y']
                if Target_Cx < 0:
                    Target_Cx = 0
                if Target_Cy < 0:
                    Target_Cy = 0
                if Target_Cx >= map_width:
                    Target_Cx = map_width - 1
                if Target_Cy >= map_height:
                    Target_Cy = map_width - 1
                Target_C = {'x': Target_Cx, 'y': Target_Cy}

        pos = get_anamynextDirMovePosition(x, y, 4)

        if pos is None:
            Target_D = None
        else:
            Target_Dx = pos['x']
            Target_Dy = pos['y']
            if Target_Dx < 0:
                Target_Dx = 0
            if Target_Dy < 0:
                Target_Dy = 0
            if Target_Dx >= map_width:
                Target_Dx = map_width - 1
            if Target_Dy >= map_height:
                Target_Dy = map_width - 1
            Target_D = {'x': Target_Dx, 'y': Target_Dy}
    if x >= map_width / 2 and y >= map_height / 2 and x >= y:  # 如果其本身就在右下角 ,从左逼到右
        Target_Ax = x  # 目标位置
        Target_Ay = y

        Target_A = {'x': Target_Ax, 'y': Target_Ay}

        pos = get_anamynextDirMovePosition(x, y, 1)
        if pos is None:
            Target_B = None
        else:

            Target_Bx = pos['x']  # 目标位置设定右下
            Target_By = pos['y']
            if Target_Bx < 0:
                Target_Bx = 0
            if Target_By < 0:
                Target_By = 0
            if Target_Bx >= map_width:
                Target_Bx = map_width - 1
            if Target_By >= map_height:
                Target_By = map_width - 1
            Target_B = {'x': Target_Bx, 'y': Target_By}

        pos = get_anamynextDirMovePosition(x, y, 4)
        if pos is None:
            Target_C = None
        else:
            pos = get_anamynextDirMovePosition(pos['x'], pos['y'], 2)
            if pos is None:
                Target_C = None
            else:
                Target_Cx = pos['x']
                Target_Cy = pos['y']
                if Target_Cx < 0:
                    Target_Cx = 0
                if Target_Cy < 0:
                    Target_Cy = 0
                if Target_Cx >= map_width:
                    Target_Cx = map_width - 1
                if Target_Cy >= map_height:
                    Target_Cy = map_width - 1
                Target_C = {'x': Target_Cx, 'y': Target_Cy}

        pos = get_anamynextDirMovePosition(x, y, 3)

        if pos is None:
            Target_D = None
        else:
            Target_Dx = pos['x']
            Target_Dy = pos['y']
            if Target_Dx < 0:
                Target_Dx = 0
            if Target_Dy < 0:
                Target_Dy = 0
            if Target_Dx >= map_width:
                Target_Dx = map_width - 1
            if Target_Dy >= map_height:
                Target_Dy = map_width - 1
            Target_D = {'x': Target_Dx, 'y': Target_Dy}

    if x >= map_width / 2 and y >= map_height / 2 and x <= y:  # 如果其本身就在右下角 ,从上逼到下
        Target_Ax = x  # 目标位置
        Target_Ay = y

        Target_A = {'x': Target_Ax, 'y': Target_Ay}

        pos = get_anamynextDirMovePosition(x, y, 3)
        if pos is None:
            Target_B = None
        else:

            Target_Bx = pos['x']  # 目标位置设定右下
            Target_By = pos['y']
            if Target_Bx < 0:
                Target_Bx = 0
            if Target_By < 0:
                Target_By = 0
            if Target_Bx >= map_width:
                Target_Bx = map_width - 1
            if Target_By >= map_height:
                Target_By = map_width - 1
            Target_B = {'x': Target_Bx, 'y': Target_By}

        pos = get_anamynextDirMovePosition(x, y, 2)
        if pos is None:
            Target_C = None
        else:
            pos = get_anamynextDirMovePosition(pos['x'], pos['y'], 3)
            if pos is None:
                Target_C = None
            else:
                Target_Cx = pos['x']
                Target_Cy = pos['y']
                if Target_Cx < 0:
                    Target_Cx = 0
                if Target_Cy < 0:
                    Target_Cy = 0
                if Target_Cx >= map_width:
                    Target_Cx = map_width - 1
                if Target_Cy >= map_height:
                    Target_Cy = map_width - 1
                Target_C = {'x': Target_Cx, 'y': Target_Cy}

        pos = get_anamynextDirMovePosition(x, y, 1)

        if pos is None:
            Target_D = None
        else:
            Target_Dx = pos['x']
            Target_Dy = pos['y']
            if Target_Dx < 0:
                Target_Dx = 0
            if Target_Dy < 0:
                Target_Dy = 0
            if Target_Dx >= map_width:
                Target_Dx = map_width - 1
            if Target_Dy >= map_height:
                Target_Dy = map_width - 1
            Target_D = {'x': Target_Dx, 'y': Target_Dy}




    return Target_A, Target_B, Target_C, Target_D

def get_anamynextDirMovePosition(x,y,direction):
    global mapfeature
    global map_height
    global map_width

    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    if direction==1:
        if y > 0 and not mapfeature[x][y - 1].wall:
            a = mapfeature[x][y - 1]
            # print('敌人是存在上邻居')
            if a.wormhole:
                PosUp = {'x': a.x, 'y': a.y}
                return PosUp
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None
                    print('same point')
                else:
                    PosUp = {'x': c.x, 'y': c.y}
                    return PosUp

            else:
                PosUp = {'x': a.x, 'y': a.y}
                return PosUp
        else:
            return None
    if direction==2:
        if y < map_height - 1 and not mapfeature[x][y + 1].wall:
            a = mapfeature[x][y + 1]
            # print('敌人是存在下邻居')
            if a.wormhole:
                PosDown = {'x': a.x, 'y': a.y}
                return PosDown
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None
                    print('same point')
                else:
                    PosDown = {'x': c.x, 'y': c.y}
                    return PosDown

            else:
                PosDown = {'x': a.x, 'y': a.y}
                return PosDown
        else:
            return None
    if direction==3:
        if x > 0 and not mapfeature[x - 1][y].wall:
            a = mapfeature[x - 1][y]
            # print('敌人是存在左邻居')
            if a.wormhole:
                PosLeft = {'x': a.x, 'y': a.y}
                return PosLeft
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None
                    print('same point')
                else:
                    PosLeft = {'x': c.x, 'y': c.y}
                    return PosLeft

            else:
                PosLeft = {'x': a.x, 'y': a.y}
                return PosLeft
        else:
            return None


    if direction==4:
        if x < map_width - 1 and not mapfeature[x + 1][y].wall:
            a = mapfeature[x+1][y]
            # print('敌人是存在上邻居')
            if a.wormhole:
                PosRight = {'x': a.x, 'y': a.y}
                return PosRight
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None
                    print('same point')
                else:
                    PosRight = {'x': c.x, 'y': c.y}
                    return PosRight

            else:
                PosRight = {'x': a.x, 'y': a.y}
                return PosRight
        else:
            return None

def findnearestpowerX(playerX,powersetX):
    powerbest=[]

    dis = 10000000000000
    # print('在寻找距离最近的powerout的情况下，我们打印一下powerserout以便更好判断我们得到的是不是最好的')
    # print(powersetout)
    for power in powersetX:

        tempdis=abs(playerX['x']-power['x'])+abs(playerX['y']-power['y'])
        if tempdis<dis:
            dis=tempdis

            powerbest=power
    return powerbest

def get_poweractionmap1(playerX,anamyplayers):
    import  random
    global  powersetin
    global powersetout
    global playerworm
    global playerout
    global playerattackup
    global playerattackdown
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD,attack_positionOriginal,targetnearestplayer,flag_get_Attackanamy

    global mapfeature

    global playerwormtarget
    global flag_playerinworm
    global flag_getsolution
    global  path

    global Intera #惯性概念

    # flag_playerinworm=True
    path=[]
    action=[]
    if playerX == playerworm:
        # print('我们在actionfind当中，应当首先进行的就是要判断这个player是不是已经进入到了我们的tunnel内部了')
        if flag_playerinworm:  #如果我们已经在wormhole里面了
            # 这个函数保证的是能够返回距离当前player最近的power
            # print('这个时候我已经能够进入到player进入虫洞内部了')
            if len(powersetin)==0:
                print('这个时候已经没有powersetin了')
                #这个时候就去到外面去抓人吗？？还是到外面去吃

                # print('pwoersetin是空的,导致目前的动作是空的')  #这个时候，理论上应该能够
                return random.randint(1,4)
            else:

                powersettemp = findnearestpoweri(playerX)
                # print(player)
                # print(powersettemp)
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[powersettemp['x']][powersettemp['y']]
                # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))

                path = getpath(start, end)

                #这个时候我们打印出path的位置
                # for i in range(len(path)):
                #     print('path的实际的位置','  x :',path[i].x,'y  :',path[i].y)
                # print('传回来的flaggetsolution是否有用呢', flag_getsolution)
                if flag_getsolution:
                    for i in range(len(path)):
                        print('path的实际的位置','  x :',path[i].x,'y  :',path[i].y)
                    powersetin.remove(powersettemp)
                    # print('flag_getsolution 是ok的')
                    ac=get_actionfrompath()
                    return ac
                else:
                    if Attack:
                        # print('攻击模式下,我们是没有用的,进行额是随机运动,')
                        #后面要修改为攻击敌人的情况，顺带的攻击敌人
                        ac = random.randint(1, 4)
                        return ac
                    else:
                        # print('我们准备在计划躲避的时候 action的给出None的情况')
                        #w我们要逃跑，所以留给后面的逃跑的情况给出action
                        return None

                    # print('打印一下当前坤的路径')
                    # mapshow(mapfeature)
        else:#这个时候我们的player 还没有进入到wormwhole 内部
            print('这个是要进入虫洞的一个player，正在努力进入到虫洞内部的路径')
            # print(player)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[playerwormtarget['x']][playerwormtarget['y']]
            # print('起始的位置')
            # print('x' + str(start.x) + 'y' + str(start.y))
            # print('终止的位置')
            # print('x' + str(end.x) + 'y' + str(end.y))

            path = getpath(start, end)

            # for i in range(len(path)):
            #     print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
            # # print('传回来的flaggetsolution是否有用呢', flag_getsolution)
            # print('传回来的flaggetsolution是否有用呢',flag_getsolution)
            if flag_getsolution:
                for i in range(len(path)):
                    print('path的实际的位置','  x :',path[i].x,'y  :',path[i].y)
                print('flag_getsolution 是ok的')
                ac = get_actionfrompath()
                return ac
            else:
                if Attack:
                    # print('攻击模式下,我们是没有用的,进行额是随机运动,')
                    # 后面要修改为攻击敌人的情况
                    ac = random.randint(1, 4)
                    return ac
                else:
                    # print('我们在逃跑模式下,但是返回None,我们返回None了')
                    # w我们要逃跑，所以留给后面的逃跑的情况给出action
                    return random.randint(1,4)

    else:  #这个时候的player实际上,是为playerout 专门吃外面的分数的 #########powersetout 外面的player去找到路径                            #这个敌方我希望如果能够看到敌方的player的情况下; 我们就进行直接的追击
        # 这个函数保证的是能够返回距离当前player最近的power                    #实际上也一样，我们应当对player的action进行交集操作以达到最优的情况
        # print('打印一下当前需要虚招路径的player的信息bcd')
        # print(player)
        if  len(powersetout) == 0:#如果已经空了 则根据模式，如果是攻击模式，则进行攻击。如果不是攻击模式，则尽量原远离自己的伙伴和墙壁，是否可以采用
            #还需要再继续再进行修改


            anamytarget = findbestanamytarget(anamyplayers)
            # 定位选择吃哪个player

            # attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal=get_anamynextmoveposition(anamytarget)
            attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(anamytarget)
            attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
            targetnearestplayer = get_nearestanamy_player()
            flag_get_Attackanamy = True
            print('Go eat anamy')
            powersetX=[]
            return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)



        else:
            powersettemp = findnearestpowero(playerX)  #实际上，我们寻找power的方式要是基于power的才行
            # print(player)
            # print(powersettemp)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[powersettemp['x'] ][powersettemp['y'] ]

            # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
            # print('起始的位置')
            # print('x' + str(start.x) + 'y' + str(start.y))
            # print('终止的位置')
            # print('x' + str(end.x) + 'y' + str(end.y))

            # 我们要判断下一步是不是虫洞
            # 如果下一步是虫洞并且该虫洞距离当前的位置是 1  那么我们就继续 否则我们重新定位虫洞


            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))

            path = getpath(start, end)
            # print('传回来的flaggetsolution是否有用呢', flag_getsolution)
            if flag_getsolution:
                # print('flag_getsolution 是ok的')
                powersetout.remove(powersettemp)   #移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
                for i in range(len(path)):
                    print('path的实际的位置','  x :',path[i].x,'y  :',path[i].y)
                ac = get_actionfrompath()
                return ac
            else:
                if Attack:
                    # print('攻击模式下,我们是没有用的,进行额是随机运动,')
                    # 后面要修改为攻击敌人的情况
                    ac = random.randint(1, 4)
                    return ac
                else:
                    # print('我们在逃跑模式下,但是返回None')
                    # w我们要逃跑，所以留给后面的逃跑的情况给出action
                    return random.randint(1, 4)

#这个函数作用是希望能够通过player对powerset进行吃
#追击敌人的情况下，我们还是需要两个player进行追击，
#如果我们的player被吃掉了也就不足四个玩家的情况呢？？？（后面再考虑好了）
#get_attackaction 的主要的作用就吃敌人的作用的，这个函数的直接的作用就是对给定的player进行攻击规划
def get_attackaction(player,anamyplayers):
    import  random
    global  powersetin
    global powersetout
    global playerworm
    global playerout
    global playerattackup
    global playerattackdown

    global mapfeature
    global flaggetAplayer
    global flagplayerinworm
    global flag_getsolution
    global  path
    path=[]
    action = []

    if playerattackup == player:
        if len(anamyplayers) == 0:
            return get_poweractionmap1(player,anamyplayers)

        else:
            Uptarget, Downtarget = get_attacktargetposiontV1(anamyplayers)
            # if Uptarget==Downtarget:
            #     start = mapfeature[player['x']][player['y']]
            #     end = mapfeature[Uptarget['x']+random.randint(-1,1)][Uptarget['y']+random.randint(-1,1)]
            # else:
            #     start = mapfeature[player['x']][player['y']]
            #     end = mapfeature[Uptarget['x']][Uptarget['y']]
            start = mapfeature[player['x']][player['y']]
            end = mapfeature[Uptarget['x']][Uptarget['y']]

            # print('playerworm的位置，和下一步的运动，希望能够找到为什么出现抖动')
            # print('起始的位置')
            # print('x' + str(start.x) + 'y' + str(start.y))
            # print('终止的位置')
            # print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                # print('在攻击的时候playerUp,flag_getsolution 是ok的')
                # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
                for i in range(len(path)):
                    print('path的实际的位置','  x :',path[i].x,'y  :',path[i].y)
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')
                    return
                    ac = random.randint(1, 4)
                    return ac

    if playerattackdown == player:
        if len(anamyplayers)==0:
            return get_poweractionmap1(player,anamyplayers)

        else:
            Uptarget, Downtarget = get_attacktargetposiontV1(anamyplayers)
            # if Uptarget==Downtarget:
            #     start = mapfeature[player['x']][player['y']]
            #     end = mapfeature[Downtarget['x']+random.randint(-1,1)][Downtarget['y']+random.randint(-1,1)]
            # else:
            #     start = mapfeature[player['x']][player['y']]
            #     end = mapfeature[Downtarget['x']][Downtarget['y']]
            start = mapfeature[player['x']][player['y']]
            end = mapfeature[Downtarget['x']][Downtarget['y']]


            # print('起始的位置')
            # print('x' + str(start.x) + 'y' + str(start.y))
            # print('终止的位置')
            # print('x' + str(end.x) + 'y' + str(end.y))

            path = getpath(start, end)
            if flag_getsolution:
                # print('在攻击的时候playerDown,flag_getsolution 是ok的')
                # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
                for i in range(len(path)):
                    print('path的实际的位置','  x :',path[i].x,'y  :',path[i].y)
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get


                    # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')
                    return
                    ac = random.randint(1, 4)
                    return ac

def additional_attackV1(player,Uptarget,Downtarget):

    global powersetin
    global powersetout
    global playerworm
    global playerout
    global playerattackup
    global playerattackdown

    global mapfeature
    global flaggetAplayer
    global flagplayerinworm
    global flag_getsolution
    global path


    addtionalup,additionaldown= get_Updownposion(Uptarget)

    start = mapfeature[player['x']][player['y']]
    end = mapfeature[addtionalup['x']][additionaldown['y']]
    print('起始的位置')
    print('x' + str(start.x) + 'y' + str(start.y))
    print('终止的位置')
    print('x' + str(end.x) + 'y' + str(end.y))
    path = getpath(start, end)
    if flag_getsolution:
        print('player的额外攻击的模式，这个时候我们需要设定的攻击的路线')
        # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
        # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
        for i in range(len(path)):
            print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
        ac = get_actionfrompath()
        return ac
    else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

        print('player的额外攻击模式下 我们是没有找到合适的路线,进行的是随机运动,')
        ac = random.randint(1, 4)
        return ac


#函数：能够优化找到最好攻击的敌人
#需要考虑：
#1、# 能够看到的敌人的位置
#2、跑到距离敌人更加靠近中心的地方。
#3、判断我方的人数，如果我方包含3个人，则额外出来一个player走wormhole 进行进攻这样的路线。
#  需要选择距离要抓的敌人最近的三个人
#得到希望攻击的敌人,发返回要追击的敌人,这个是在主函数中进行调用确定. 只要给出目标位置的坐标 两个坐标
global oldUptarget
global oldDowntarget
def get_attacktargetposiontV1(anamyplayers):
    global anamy
    global playerattackup
    global playerattackdown
    global oldUptarget
    global oldDowntarget
    global flag_anamycirclefind
    flag_anamycirclefind=False
    if len(anamyplayers)==0:
        if not flag_anamycirclefind:      #防止每次都要循环发现敌人的位置，这个时候我们就只有当我们再次丢了的时候我们才再次进行敌方player的寻找
            Uptargetx, Uptargety, Downtargetx, Downtargety=find_anamy()  #这个函数作用就是
            Uptarget = {'x': Uptargetx, 'y': Uptargety}
            Downtarget = {'x': Downtargetx, 'y': Downtargety}
            oldUptarget=Uptarget
            oldDowntarget=Downtarget
            flag_anamycirclefind=True
            return Uptarget, Downtarget
        else:

            Uptarget=oldUptarget
            Downtarget=oldDowntarget
            return Uptarget,Downtarget
    else:

        ##找到的情况下
        targetanamy=anamyplayers[0]
        # print('打印一下敌人的情况.    ',targetanamy)
        # print('打印一下我方的情况  playerattackup  '  ,playerattackup)
        # print('打印一下我方的情况  playerattackup  ', playerattackdown)

        distanceUp = stepdistance(playerattackup, targetanamy)
        distanceDown = stepdistance(playerattackdown, targetanamy)
        dismin=distanceUp+distanceDown
        for anamyplayer in anamyplayers:
            distanceUp = stepdistance(playerattackup, anamyplayer)
            distanceDown = stepdistance(playerattackdown, anamyplayer)
            dis = distanceUp + distanceDown
            if dis < dismin:
                dismin=dis
                targetanamy=anamyplayer

        Uptarget, Downtarget= get_Updownposion(targetanamy)

        # 表示我们找到了不需要重新找,如果再次丢了可以再找
        if dismin<=4:
            flag_anamycirclefind = False

        return Uptarget, Downtarget


#This function 的目标是希望能够找到敌人
#得到的是下一步的运动的坐标,也即是我们向那边找
def find_anamy():
    global playerattackup
    global playerattackdown
    global map_width
    global map_height

    factor_inside=2

    x=playerattackup['x']
    y=playerattackup['y']
    if  x <map_width/2 and y<map_height/2: #如果其本身就在左上角
        Uptargetx=map_width-factor_inside#将其移动到右下角
        Uptargety=map_height-factor_inside
    elif x > map_width/2 and y<map_height/2: #如果本身在右上角
        Uptargetx = factor_inside  #则将其移动到左下
        Uptargety = map_height-factor_inside
    elif x < map_width/2 and y>map_height/2:  #如果本身在左下角
        Uptargetx = map_width -factor_inside  # 则将其移动到右上角
        Uptargety = factor_inside
    else:                                    #本身在右下角
        Uptargetx = factor_inside  # 将其移动到左上脚
        Uptargety = factor_inside

    x = playerattackdown['x']
    y = playerattackdown['y']
    if  x <= map_width/2 and y<=map_height/2: #如果其本身就在左上角
        Downtargetx=map_width-factor_inside#将其移动到右下角
        Downtargety=map_height-factor_inside
    elif x > map_width/2 and y<map_height/2: #如果本身在右上角
        Downtargetx = factor_inside  #则将其移动到左下
        Downtargety = map_height-factor_inside
    elif x < map_width/2 and y>map_height/2:  #如果本身在左下角
        Downtargetx = map_width -factor_inside  # 则将其移动到右上角
        Downtargety = factor_inside
    else:                                    #本身在右下角
        Downtargetx = factor_inside  # 将其移动到左上脚
        Downtargety = factor_inside



    return  Uptargetx,Uptargety,Downtargetx,Downtargety


#this function 的作用是根据攻击的敌人的目标得到这两个playerUP 和 down 的各自的作用
def get_Updownposion(targetanmay):
    global map_width
    global map_height

    # print('打印一下targetanamay 的情况   ', targetanmay )

    #判断敌人所在位置范围
    x=targetanmay['x']
    y=targetanmay['y']
    # if  x <= map_width/2 and y<=map_height/2 and x<=y: #如果其本身就在左上角 ,从下逼到上  #加入额外判断能否追死的情况
    #     Uptargetx=x+1#目标位置设定为 右侧
    #     Uptargety=y
    #     Downtargetx=x+1 # 目标位置设定右下
    #     Downtargety=y+1
    #     Uptarget = {'x': Uptargetx, 'y': Uptargety}
    #     Downtarget = {'x': Downtargetx, 'y': Downtargety}
    #
    # if x <= map_width / 2 and y <= map_height / 2 and x >= y:  # 如果其本身就在左上角 ,从右逼到左
    #     Uptargetx = x  # 目标位置设定为 下侧
    #     Uptargety = y+1
    #     Downtargetx = x + 1  # 目标位置设定左下
    #     Downtargety = y + 1
    #     Uptarget = {'x': Uptargetx, 'y': Uptargety}
    #     Downtarget = {'x': Downtargetx, 'y': Downtargety}
    #
    # if x >= map_width / 2 and y <= map_height / 2 and  x/2 >= y:  # 如果其本身就在右上角 ,从左逼到右
    #     Uptargetx = x  # 目标位置设定为 下侧
    #     Uptargety = y+1
    #     Downtargetx = x -1  # 目标位置设定右下
    #     Downtargety = y +1
    #     Uptarget = {'x': Uptargetx, 'y': Uptargety}
    #     Downtarget = {'x': Downtargetx, 'y': Downtargety}
    #
    # if x >= map_width / 2 and y <= map_height / 2 and  x/2 <= y:  # 如果其本身就在右上角 ,从下逼到上
    #     Uptargetx = x-1  # 目标位置设定为 左侧
    #     Uptargety = y
    #     Downtargetx = x - 1  # 目标位置设定左下
    #     Downtargety = y +1
    #     Uptarget = {'x': Uptargetx, 'y': Uptargety}
    #     Downtarget = {'x': Downtargetx, 'y': Downtargety}
    #
    # #在地图下方的情况
    # if x <= map_width / 2 and y >= map_height / 2 and  x <= y/2:  # 如果其本身就在左下角 ,从下逼到下
    #     Uptargetx = x  # 目标位置设定为 左侧
    #     Uptargety = y+1
    #     Downtargetx = x - 1  # 目标位置设定左下
    #     Downtargety = y - 1
    #     Uptarget = {'x': Uptargetx, 'y': Uptargety}
    #     Downtarget = {'x': Downtargetx, 'y': Downtargety}
    #
    # if x <= map_width / 2 and y >= map_height / 2 and  x >= y/2:  # 如果其本身就在左下角 ,从右逼到左
    #     Uptargetx = x  # 目标位置设定为 右侧
    #     Uptargety = y-1
    #     Downtargetx = x + 1  # 目标位置设定y右下
    #     Downtargety = y - 1
    #     Uptarget = {'x': Uptargetx, 'y': Uptargety}
    #     Downtarget = {'x': Downtargetx, 'y': Downtargety}
    #
    #
    # if x >= map_width / 2 and y >= map_height / 2 and  x >= y:  # 如果其本身就在右下角 ,从左逼到右
    #     Uptargetx = x  # 目标位置设定为 右侧
    #     Uptargety = y-1
    #     Downtargetx = x - 1  # 目标位置设定左下
    #     Downtargety = y - 1
    #     Uptarget = {'x': Uptargetx, 'y': Uptargety}
    #     Downtarget = {'x': Downtargetx, 'y': Downtargety}
    #
    #
    # if x >=map_width / 2 and y >= map_height / 2 and  x <= y:  # 如果其本身就在右下角 ,从上逼到下
    #     Uptargetx = x-1  # 目标位置设定为 右侧
    #     Uptargety = y
    #     Downtargetx = x - 1  # 目标位置设定右下
    #     Downtargety = y - 1
    #     Uptarget = {'x': Uptargetx, 'y': Uptargety}
    #     Downtarget = {'x': Downtargetx, 'y': Downtargety}
    if x <= map_width / 2 and y <= map_height / 2 and x <= y:  # 如果其本身就在左上角 ,从下逼到上  #加入额外判断能否追死的情况

        Uptargetx = x   # 目标位置设定为 右侧
        Uptargety = y
        Downtargetx = x+1  # 目标位置设定右下
        Downtargety = y


    if x <= map_width / 2 and y <= map_height / 2 and x >= y:  # 如果其本身就在左上角 ,从右逼到左
        Uptargetx = x  # 目标位置设定为 下侧
        Uptargety = y
        Downtargetx = x   # 目标位置设定左下
        Downtargety = y+1


    if x >= map_width / 2 and y <= map_height / 2 and x / 2 >= y:  # 如果其本身就在右上角 ,从左逼到右
        Uptargetx = x  # 目标位置设定为 下侧
        Uptargety = y
        Downtargetx = x  # 目标位置设定右下
        Downtargety = y+1

    if x >= map_width / 2 and y <= map_height / 2 and x / 2 <= y:  # 如果其本身就在右上角 ,从下逼到上
        Uptargetx =  x # 目标位置设定为 左侧
        Uptargety = y
        Downtargetx = x -1  # 目标位置设定左下
        Downtargety = y


        # 在地图下方的情况
    if x <= map_width / 2 and y >= map_height / 2 and x <= y / 2:  # 如果其本身就在左下角 ,上逼到下
        Uptargetx = x  # 目标位置设定为 左侧
        Uptargety = y
        Downtargetx = x+1   # 目标位置设定左下
        Downtargety = y
        Uptarget = {'x': Uptargetx, 'y': Uptargety}
        Downtarget = {'x': Downtargetx, 'y': Downtargety}

    if x <= map_width / 2 and y >= map_height / 2 and x >= y / 2:  # 如果其本身就在左下角 ,从右逼到左
        Uptargetx = x  # 目标位置设定为 右侧
        Uptargety = y
        Downtargetx = x   # 目标位置设定y右下
        Downtargety = y-1


    if x >= map_width / 2 and y >= map_height / 2 and x >= y:  # 如果其本身就在右下角 ,从左逼到右
        Uptargetx = x  # 目标位置设定为 右侧
        Uptargety = y
        Downtargetx = x  # 目标位置设定左下
        Downtargety = y-1


    if x >= map_width / 2 and y >= map_height / 2 and x <= y:  # 如果其本身就在右下角 ,从上逼到下
        Uptargetx = x   # 目标位置设定为 右侧
        Uptargety = y
        Downtargetx = x-1  # 目标位置设定右下
        Downtargety = y


    if Downtargetx<0:
        Downtargetx=0
    if Downtargety<0:
        Downtargety=0
    if Downtargetx >= map_width:
        Downtargetx = map_width-1
    if Downtargety >= map_height:
        Downtargety = map_width-1

    Uptarget = {'x': Uptargetx, 'y': Uptargety}
    Downtarget = {'x': Downtargetx, 'y': Downtargety}
    return Uptarget, Downtarget

    #还要考虑敌人突然不在视野内的情况下
     #这个时候还要考虑如果前面是虫洞的情况下,我们也要跟过去,这个时候需要利用的player自身的视野
    #同样,如果我们逃跑,也要走向



#这个函数的作用是在我们得到了一个某条path的情况下，得出下一条路径path
def get_actionfrompath():
    global path
    global Attack
    global map_height
    global map_width


    currentspot = path[len(path) - 1]

    nextspot = path[len(path) - 2]
    startx=currentspot.x
    starty=currentspot.y
    endx=nextspot.x
    endy=nextspot.y
    # print('执行wormhole前')
    # print('单步走的时候，currentsopt的位置  x',startx,'  y:',starty)
    # print('单步走的时候，nextsopt的位置  x',endx,'  y:',endy)
    if iswormhole(endx, endy):
        # print('下一步是虫洞')
        if distancecalculate(x1=endx, y1=endy, x2=startx, y2=starty) == 1:

            print('下一步的虫洞的距离是1')
            pass
        elif distancecalculate(x1=endx, y1=endy, x2=startx, y2=starty) == 0:
            # 得到当前可以移动的范围内
            # print('当前的距离是00000')
            movaableaction=[]
            x=startx
            y=starty
            if y > 0:  # 向上

                if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][y - 1].tunnel == 'down'):
                    movaableaction.append(1)
            if y < map_height - 1:  # 向下
                if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][y + 1].tunnel == 'up'):
                    movaableaction.append(2)
            if x > 0:  # 向左移动
                if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][y].tunnel == 'right'):
                    movaableaction.append(3)
            if x < map_width - 1:  # 向右移动
                if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                    y].tunnel == 'left'):
                    movaableaction.append(4)
            print('我们当前的这一步就在想要进入的wormhole当中呢！')   #这个时候，我们应当在可移动的范围内，随机动一下咯

            return movaableaction[random.randint(0,len(movaableaction)-1)]

        else:
            print('下一步的虫洞的距离并不是 1， 我们需要进行额外的操作，所以，我们要进行更新新的end.x,end.y')
            newend = findwormpair(endx, endy)
            endx = newend['x']
            endy = newend['y']
    # print('执行istunnel 前')
    # print('单步走的时候，currentsopt的位置  x', startx, '  y:', starty)
    # print('单步走的时候，nextsopt的位置  x', endx, '  y:', endy)

    #这句话用来判断下一步是不是tunnel的终点，如果是的我们就不走这个
    if istunnelneighbour(startx=startx,starty=starty,endx=endx, endy=endy):
        endx,endy = viatunnelnewaction(startx=startx, starty=starty, endx=endx, endy=endy)


    if startx == endx:
        if starty > endy:  # 向上移动
            # action.append({"team": player['team'], "player_id": player['id'],
            #                "move": [1]})
            print('mvoe up')
            return 1
        else:
            # action.append({"team": player['team'], "player_id": player['id'],
            #                "move": [2]})
            print('move down')
            return 2
    else:
        if startx > endx:
            # action.append({"team": player['team'], "player_id": player['id'],
            #                "move": [3]})
            print('mvoe left')
            return 3
        else:
            # action.append({"team": player['team'], "player_id": player['id'],
            #                "move": [4]})
            print('move right')
            return 4

def get_actionfrompathold():
    global path
    global Attack

    currentspot = path[len(path) - 1]

    nextspot = path[len(path) - 2]
    startx=currentspot.x
    starty=currentspot.y
    endx=nextspot.x
    endy=nextspot.y


    if startx == endx:
        if starty > endy:  # 向上移动
            # action.append({"team": player['team'], "player_id": player['id'],
            #                "move": [1]})
            # print('mvoe up')
            return 1
        else:
            # action.append({"team": player['team'], "player_id": player['id'],
            #                "move": [2]})
            # print('move down')
            return 2
    else:
        if startx > endx:
            # action.append({"team": player['team'], "player_id": player['id'],
            #                "move": [3]})
            # print('mvoe left')
            return 3
        else:
            # action.append({"team": player['team'], "player_id": player['id'],
            #                "move": [4]})
            # print('move right')
            return 4



def findnearestpowero(player):
    global powersetout
    global powersetin
    global playerworm

    powerbest=[]

    dis = 10000000000000
    # print('在寻找距离最近的powerout的情况下，我们打印一下powerserout以便更好判断我们得到的是不是最好的')
    # print(powersetout)
    for power in (powersetout):

        tempdis=abs(player['x']-power['x'])+abs(player['y']-power['y'])
        if tempdis<dis:
            dis=tempdis

            powerbest=power
    return powerbest




def findnearestpoweri(player):
    global powersetout
    global powersetin
    global playerworm
    global flagp_layerinworm

    powerbest=[]

    dis = 1000000000
    #这个player已经进入了wormwhole里面并且进入了tunnel内部
    if flag_playerinworm:
        if player==playerworm:
            for power in (powersetin):
                tempdis=abs(player['x']-power['x'])+abs(player['y']-power['y'])
                if tempdis<dis:
                    dis = tempdis
                    powerbest=power
            return powerbest
    else:
        pass



#我们将给定的player作为start 起点
#我们将给定的powet 作为end  终点
#其中start 和  end 都是grid 类型的对象
global path
path =[]
def getpath(start,end):
    global mapfeature
    global  flag
    global flag_getsolution
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    flag_getsolution=False
    openSet=[]
    closedSet=[]
    openSet.append(start)

    # print('进入时候的openset')
    # print(openSet)


    #进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous=[]

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
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag=1
                #确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou=100
                while temp.previous:
                    cou = cou -1
                    path.append(temp.previous)
                    temp = temp.previous

                flag_getsolution = True
                # print('flag_getsolution' , flag_getsolution)
                return path

              #  gridshow(grid)

                break

                # find the path

            ##将该节点移出openset
            openSet.remove(current)
            ##将该节点移入closedset
            closedSet.append(current)

            #理论上直接就右neighbours
            neighbours=current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            #循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):


                neighbour = neighbours[i]

             #   print(type(neighbour))

                #当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or  (neighbour.context=='*') or (neighbour.anamy) or (neighbour.tunnel!='no'):
                #    print('就在这里')
                    pass
                else:
                #当前的邻居不在closedset中

                    tempG = current.g + 1
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


        else:
            flag_getsolution=False
            print('no solution')
            break



#这个函数是为了判断当前地图所处在的类型。
#我们应当判断出地图中是否存在死区的这种情况
def getpathmapdecide(start,end):
    global mapfeature
    global  flag
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    openSet=[]
    closedSet=[]
    openSet.append(start)

    print('进入时候的openset')
    print(openSet)
    #进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous=[]

    while True:
     #   print('uiiiiiiiiiiiiiiiiiiiiiiiiiiii')
    #    print(openSet)
      #  print(closedSet)

        if len(openSet) > 0:
            winner = 0

            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            #current 是最小的节点
            current = openSet[winner]

            #判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag=1

                #确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou=100
                while temp.previous:
                    cou = cou -1
                    path.append(temp.previous)
                    temp = temp.previous

                #    print(' we  have out of the path')
                #    print(' we  have out of the path')
                for i in range(len(path)):
                    #   print('x' + str(path[i].i) + 'y' + str(path[i].j))
                    path[i].context = '-'

                #mapshow(mapfeature)
                return path
              #  gridshow(grid)

                break

                # find the path




            ##将该节点移出openset
            openSet.remove(current)
            ##将该节点移入closedset
            closedSet.append(current)

            #理论上直接就右neighbours
            neighbours=current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            #循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):


                neighbour = neighbours[i]

             #   print(type(neighbour))

                #当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or  (neighbour.context=='*') or (neighbour.anamy) or neighbour.tunnel != 'no'  or  neighbour.wormhole:
                #    print('就在这里')
                    pass
                else:
                #当前的邻居不在closedset中

                    tempG = current.g + 1
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


def heuristic(a,b):

    #d=math.sqrt((a.i-b.i)*(a.i-b.i)+(a.j-b.j)*(a.j-b.j))
    d=abs(a.x-b.x)+abs((a.y-b.y))
  #  print(d)
    return  d

def stepdistance(playerA,playerB):
    d = abs(playerA['x'] - playerB['x']) + abs(playerA['y'] - playerB['y'])
    return d
def distancecalculate(x1,y1,x2,y2):
    d = abs(x1 - x2) + abs(y1 - y2)
    return d






#这个函数，采用从少的移动方向到多的移动情况进行退化，这样就可以能够比较完美的使用deadmove了。
def player_avoidactionNew3(player,anamyplayers,actionpower):
    global visionrange
    global mapfeature
    global map_width
    global map_height
    global playerworm
    global visionrange
    x = player['x']
    y = player['y']
    # print('实际坐标x：' + str(x) + '    y' + str(y))
    movaableactiona = []
    # print('筛选动作前，看一下敌人的位置')
    # print('敌人的情况',anamyplayers)
    # mapshow(mapfeature)
    '''第一轮筛选：使用更加严格的条件，然后采用deadmove'''
    if y > 0:  # 向上
        if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y-1]) or wormholeanamylimit(mapfeature[x][y-1])):
            movaableactiona.append(1)
    if y < map_height - 1:  # 向下
        if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y+1]) or wormholeanamylimit(mapfeature[x][y+1])):
            movaableactiona.append(2)
    if x > 0:  # 向左移动
        if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][y].tunnel == 'right' or tunnelanamylimit(mapfeature[x-1][y]) or wormholeanamylimit(mapfeature[x-1][y])):
            movaableactiona.append(3)
    if x < map_width - 1:  # 向右移动
        if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][y].tunnel == 'left' or tunnelanamylimit(mapfeature[x+1][y]) or wormholeanamylimit(mapfeature[x+1][y])):
            movaableactiona.append(4)
    movaableaction=movaableactiona
    # print('第一轮筛选后的内容',movaableaction)
    # mapshow(mapfeature)

    #实际情况下，这个地方并不应该要是整体视野内的敌人的情况，而是某一个自身的playerx的情况，这个时候，我们是否要重复计算每一个player啊
    seeanamys = []

    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= player['x'] + visionrange and anamyplayer['x'] >= player['x'] - visionrange and  anamyplayer['y'] <= player['y'] + visionrange and anamyplayer['y'] >= player['y'] - visionrange:
                seeanamys.append(anamyplayer)

    if len(seeanamys) == 0:
        if actionpower in movaableaction:  #在上面的严苛的条件下，至少是安全的但是似乎没有考虑到field limit的情况
            return actionpower
        else: #这个时候我们应当尽量分散逃跑咯
            # 这个时候表示的是上面返回的是None,这个时候我们尽量对逃跑准则进行一定的规划 分散规划 对于不同的player朝着不同的方向进行跑去吗？？在前面power的规划的过程中，我们就已经进行了一定目标位置的规划的情况
            #对于聚类的分析，我们是否有更好的分类的方式。是到底要分成几类也是很有关系的

            if len(movaableaction) > 1:
                movaableaction2 = fieldlimit(player, movaableaction)
                # print('经过tunnel筛选的动作：'+str(movaableaction2))
                if len(movaableaction2) == 0:
                    pass
                else:
                    movaableaction = movaableaction2
            #
            # defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
            # # # print('向四个角随机运动')
            #
            # if player == playerB:
            #         ac= defaultmove[0][random.randint(0, 1)]
            # elif player == playerC:
            #     # print('得到的bestpos的结果',bestPos2)
            #     ac = defaultmove[1][random.randint(0, 1)]
            #
            # elif player == playerD:
            #     ac = defaultmove[2][random.randint(0, 1)]
            # elif player == playerA:
            #     ac = defaultmove[3][random.randint(0, 1)]
            #
            # if ac in movaableaction:
            #     return ac
            # else:
            a = random.randint(0, len(movaableaction) - 1)
            # print('打印一下，我们将要选择执行哪些动作，没有敌人的情况下----' + str(movaableaction[a]))
            return movaableaction[a]
    else:
        # print('这个时候打印一下当前可移动的i情况 和本身的位置')
        # print(movaableaction)
        # print('anaamyplayes 的情况',anamyplayers )
        if len(movaableaction) == 0:  # 如果没有可以移动的距离了，就选择不移动了
            # 这个时候就应该根据记录的敌人的情况进行规律探讨,然后得到移动的规律.
            # 具体规律可以设定如果最近的敌人上一次的移动方向是向下,并且上上次的移动方向是向下,我们就认为我们就可以进行反向的运动,这样有可能
            # 这个时候根据敌人的实际位置进行跑动
            ac = deadmoveNew3(player, anamyplayers)
            # print('打印一下，我们将要选择执行哪些动作，死亡移动----' + str(ac))
            return ac

        else:
            # 尽量不要贴边走否则容易被吃
            # 也就是x如果小于1


                if len(movaableaction) > 1:
                    print('我们准备使用fieldlimit')
                    movaableaction2 = fieldlimit(player, movaableaction)
                    # print('经过tunnel筛选的动作：'+str(movaableaction2))
                    if len(movaableaction2) == 0:
                        pass
                    else:
                        movaableaction = movaableaction2

                    # print('打印一下经过筛选的action' + str(movaableaction1))
                if actionpower in movaableaction:
                    return actionpower
                else:

                    if len(movaableaction) > 1:
                        print('我们使用centrogtravity')
                        movaableaction3 = center_gravity(player, movaableaction)  #实际上，这个也在一定程度上防止了他还回到虫洞去
                        # print('经过gravity筛选的动作 '+str(movaableaction3))

                        if len(movaableaction3) == 0:
                            pass
                        else:
                            movaableaction = movaableaction3
                        # 这个敌方选择好了
                        # print('这个时候我们看一下可以执行的action有多长：len(movaableaction)：'+str(len(movaableaction)))
                        a = random.randint(0, len(movaableaction) - 1)
                        # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                        return movaableaction[a]
                    else:
                        return movaableaction[0]


#更新了敌人的位置的i情况，从多的的移动的方向到移动多的情况 不能使用deadmove了
def player_avoidactionNew2(player,anamyplayers,actionpower):
    global visionrange
    global mapfeature
    global map_width
    global map_height
    global playerworm

    x = player['x']
    y = player['y']
    # print('实际坐标x：' + str(x) + '    y' + str(y))
    movaableactiona = []
    # print('筛选动作前，看一下敌人的位置')
    # mapshow(mapfeature)
    '''第一轮筛选：不能走的有石头，真实的敌人的位置，走过tunnel之后敌人的只是的位置'''
    if y > 0:  # 向上
        if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 1].wall or mapfeature[x][
            y - 1].tunnel == 'down'):
            movaableactiona.append(1)
    if y < map_height - 1:  # 向下
        if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 1].wall or mapfeature[x][
            y + 1].tunnel == 'up'):
            movaableactiona.append(2)
    if x > 0:  # 向左移动
        if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
            y].tunnel == 'right' ):
            movaableactiona.append(3)
    if x < map_width - 1:  # 向右移动
        if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
            y].tunnel == 'left'):
            movaableactiona.append(4)
    movaableaction=movaableactiona
    print('第一轮筛选后的内容',movaableaction)
    updateanamyposition(anamyplayers) #这个刷新了敌人的位置不包含，走了tunnel之后的终点
    '''第二轮筛选：放宽敌人位置的限制，敌人的位置经过tunnel之后的扩大一圈'''
    # print('筛选动作前，看一下敌人的位置')
    # mapshow(mapfeature)
    if len(movaableaction)>=2:
        movaableactionb=[]
        # 得到当前可以移动的范围内
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1])):
                movaableactionb.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1])):
                movaableactionb.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y])):
                movaableactionb.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y])):
                movaableactionb.append(4)
        if len(movaableactionb)>0:

            movaableaction=movaableactionb
            print('第二轮筛选后的内容',movaableactionb)

        else:

            print('第二轮筛选后的内容',movaableactionb)

    '''第三轮筛选：放宽敌人位置的限制，敌人的位置所有的都扩大一圈'''
    updateanamypositionUpgrade(anamyplayers)#这个是最真实的，都有可能不能走箭头了
    # print('筛选动作前，看一下敌人的位置')
    # mapshow(mapfeature)
    if len(movaableaction)>=2:
        movaableactionc=[]
        # 得到当前可以移动的范围内
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' ):
                movaableactionc.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up'):
                movaableactionc.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right'):
                movaableactionc.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' ):
                movaableactionc.append(4)
        if len(movaableactionc)>0:

            movaableaction=movaableactionc
            print('第二轮筛选后的内容',movaableactionc)

        else:

            print('第二轮筛选后的内容',movaableactionc)



    if len(anamyplayers) == 0:
        if actionpower in movaableaction:
            return actionpower
        else: #这个时候我们应当尽量分散逃跑咯
            # 这个时候表示的是上面返回的是None,这个时候我们尽量对逃跑准则进行一定的规划 分散规划

            a = random.randint(0, len(movaableaction) - 1)
            # print('打印一下，我们将要选择执行哪些动作，没有敌人的情况下----' + str(movaableaction[a]))
            return movaableaction[a]
    else:
        # print('这个时候打印一下当前可移动的i情况 和本身的位置')
        # print(movaableaction)
        # print('anaamyplayes 的情况',anamyplayers )
        if len(movaableaction) == 0:  # 如果没有可以移动的距离了，就选择不移动了
            # 这个时候就应该根据记录的敌人的情况进行规律探讨,然后得到移动的规律.
            # 具体规律可以设定如果最近的敌人上一次的移动方向是向下,并且上上次的移动方向是向下,我们就认为我们就可以进行反向的运动,这样有可能
            # 这个时候根据敌人的实际位置进行跑动
            ac = deadmove(player, anamyplayers)
            # print('打印一下，我们将要选择执行哪些动作，死亡移动----' + str(ac))
            return ac

        else:
            # 尽量不要贴边走否则容易被吃
            # 也就是x如果小于1

            # print('action 有多长'+str(len(movaableaction)))
            # print('打印一下可以执行的动作'+str(movaableaction))
            if player == playerworm:
                # mapshow(mapfeature)
                # print('这个时候打印一下当前可移动的i情况 和本身的位置',player)
                # print(movaableaction)
                # print('anaamyplayes 的情况', anamyplayers)
                # print('action power 是多少：'+str(actionpower))
                if actionpower in movaableaction:
                    # print('playerworm action power 是在这个内部')
                    return actionpower
                else:
                    # 这个敌方选择好了
                    # print('这个时候我们看一下可以执行的action有多长：len(movaableaction)：'+str(len(movaableaction)))
                    a = random.randint(0, len(movaableaction) - 1)
                    # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                    return movaableaction[a]
                # 这个时候就不需要有敌人
                pass
            else:
                if len(movaableaction) > 1:
                    movaableaction2 = fieldlimit(player, movaableaction)
                    # print('经过tunnel筛选的动作：'+str(movaableaction2))
                    if len(movaableaction2) == 0:
                        pass
                    else:
                        movaableaction = movaableaction2

                    # print('打印一下经过筛选的action' + str(movaableaction1))
                if actionpower in movaableaction:
                    return actionpower
                else:

                    if len(movaableaction) > 1:
                        movaableaction3 = center_gravity(player, movaableaction)  #实际上，这个也在一定程度上防止了他还回到虫洞去
                        # print('经过gravity筛选的动作 '+str(movaableaction3))

                        if len(movaableaction3) == 0:
                            pass
                        else:
                            movaableaction = movaableaction3
                        # 这个敌方选择好了
                        # print('这个时候我们看一下可以执行的action有多长：len(movaableaction)：'+str(len(movaableaction)))
                        a = random.randint(0, len(movaableaction) - 1)
                        # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                        return movaableaction[a]
                    else:
                        return movaableaction[0]

#下面是未将敌人的邻居进行更新到帧是邻居的情况，进行从多个移动方向到少的移动方向的选择
def player_avoidactionNew1(player,anamyplayers,actionpower):
    global visionrange
    global mapfeature
    global map_width
    global map_height
    global playerworm

    x = player['x']
    y = player['y']
    # print('实际坐标x：' + str(x) + '    y' + str(y))
    movaableaction = []

    '''第一轮筛选：不能走的有石头，真实的敌人的位置，走过tunnel之后敌人的只是的位置'''
    if y > 0:  # 向上
        if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 1].wall or mapfeature[x][
            y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1])):
            movaableaction.append(1)
    if y < map_height - 1:  # 向下
        if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 1].wall or mapfeature[x][
            y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1])):
            movaableaction.append(2)
    if x > 0:  # 向左移动
        if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
            y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y])):
            movaableaction.append(3)
    if x < map_width - 1:  # 向右移动
        if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
            y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y])):
            movaableaction.append(4)
    # print('第一轮筛选后的内容',movaableaction)
    '''第二轮筛选：放宽敌人位置的限制，敌人的位置经过tunnel之后的扩大一圈'''
    if len(movaableaction)>=2:
        movaableaction=[]
        # 得到当前可以移动的范围内
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1])):
                movaableaction.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1])):
                movaableaction.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y])):
                movaableaction.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y])):
                movaableaction.append(4)
        # print('第二轮筛选后的内容',movaableaction)

    '''第三轮筛选：放宽敌人位置的限制，敌人的位置所有的都扩大一圈'''

    if len(movaableaction)>=2:
        movaableaction=[]
        # 得到当前可以移动的范围内
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1])):
                movaableaction.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1])):
                movaableaction.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y])):
                movaableaction.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y])):
                movaableaction.append(4)
        # print('第一轮筛选后的内容', movaableaction)

    '''第四轮筛选：考虑敌人走tunnel之后的下一步，对未来的某一个情况进行限制'''
    # if len(movaableaction)>=2:
    #     movaableaction=[]
    #     # 得到当前可以移动的范围内
    #     if y > 0:  # 向上
    #         if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
    #             y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1])):
    #             movaableaction.append(1)
    #     if y < map_height - 1:  # 向下
    #         if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
    #             y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1])):
    #             movaableaction.append(2)
    #     if x > 0:  # 向左移动
    #         if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
    #             y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y])):
    #             movaableaction.append(3)
    #     if x < map_width - 1:  # 向右移动
    #         if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
    #             y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y])):
    #             movaableaction.append(4)
    #
    # if len(movaableaction)>=2:
    #     movaableaction = []
    #     # 得到当前可以移动的范围内
    #     if y > 0:  # 向上
    #         if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
    #             y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1])):
    #             movaableaction.append(1)
    #     if y < map_height - 1:  # 向下
    #         if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
    #             y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1])):
    #             movaableaction.append(2)
    #     if x > 0:  # 向左移动
    #         if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
    #             y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y])):
    #             movaableaction.append(3)
    #     if x < map_width - 1:  # 向右移动
    #         if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
    #             y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y])):
    #             movaableaction.append(4)


    if len(anamyplayers) == 0:
        if actionpower in movaableaction:
            return actionpower
        else: #这个时候我们应当尽量分散逃跑咯
            # 这个时候表示的是上面返回的是None,这个时候我们尽量对逃跑准则进行一定的规划 分散规划

            a = random.randint(0, len(movaableaction) - 1)
            # print('打印一下，我们将要选择执行哪些动作，没有敌人的情况下----' + str(movaableaction[a]))
            return movaableaction[a]
    else:
        # print('这个时候打印一下当前可移动的i情况 和本身的位置')
        # print(movaableaction)
        # print('anaamyplayes 的情况',anamyplayers )
        if len(movaableaction) == 0:  # 如果没有可以移动的距离了，就选择不移动了
            # 这个时候就应该根据记录的敌人的情况进行规律探讨,然后得到移动的规律.
            # 具体规律可以设定如果最近的敌人上一次的移动方向是向下,并且上上次的移动方向是向下,我们就认为我们就可以进行反向的运动,这样有可能
            # 这个时候根据敌人的实际位置进行跑动
            ac = deadmove(player, anamyplayers)
            # print('打印一下，我们将要选择执行哪些动作，死亡移动----' + str(ac))
            return ac

        else:
            # 尽量不要贴边走否则容易被吃
            # 也就是x如果小于1

            # print('action 有多长'+str(len(movaableaction)))
            # print('打印一下可以执行的动作'+str(movaableaction))
            if player == playerworm:
                # mapshow(mapfeature)
                # print('这个时候打印一下当前可移动的i情况 和本身的位置',player)
                # print(movaableaction)
                # print('anaamyplayes 的情况', anamyplayers)
                # print('action power 是多少：'+str(actionpower))
                if actionpower in movaableaction:
                    # print('playerworm action power 是在这个内部')
                    return actionpower
                else:
                    # 这个敌方选择好了
                    # print('这个时候我们看一下可以执行的action有多长：len(movaableaction)：'+str(len(movaableaction)))
                    a = random.randint(0, len(movaableaction) - 1)
                    # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                    return movaableaction[a]
                # 这个时候就不需要有敌人
                pass
            else:
                if len(movaableaction) > 1:
                    movaableaction0= anamynexttunnelmovelimit(player,movaableaction)
                    if len(movaableaction0)==0:
                        pass
                    else:
                        movaableaction=movaableaction0
                        if len(movaableaction)>1:


                            movaableaction1 = tunnellimit(player, movaableaction)
                            # print('未经过筛选的动作：'+str(movaableaction))
                            # print('经过field筛选的动作：'+str(movaableaction1))
                            if len(movaableaction1) == 0:
                                pass
                            else:
                                movaableaction = movaableaction1

                                if len(movaableaction) > 1:
                                    movaableaction2 = fieldlimit(player, movaableaction)
                                    # print('经过tunnel筛选的动作：'+str(movaableaction2))
                                    if len(movaableaction2) == 0:
                                        pass
                                    else:
                                        movaableaction = movaableaction2

                    # print('打印一下经过筛选的action' + str(movaableaction1))
                if actionpower in movaableaction:
                    return actionpower
                else:

                    if len(movaableaction) > 1:
                        movaableaction3 = center_gravity(player, movaableaction)  #实际上，这个也在一定程度上防止了他还回到虫洞去
                        # print('经过gravity筛选的动作 '+str(movaableaction3))

                        if len(movaableaction3) == 0:
                            pass
                        else:
                            movaableaction = movaableaction3
                        # 这个敌方选择好了
                        # print('这个时候我们看一下可以执行的action有多长：len(movaableaction)：'+str(len(movaableaction)))
                        a = random.randint(0, len(movaableaction) - 1)
                        # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                        return movaableaction[a]
                    else:
                        return movaableaction[0]


def anamynexttunnelmovelimit(player,movaableaction,anamplayers):
    global tunnelsneighbours
    global mapfeature
    x = player['x']
    y = player['y']


    '''针对只走一步是tunnel终点的情况，防止敌人直接走tunnel吃我，但是又不能杜绝不走这个'''
    newmovableactiion = []
    for moveaction in movaableaction:
        if moveaction == 1 and mapfeature[x][y - 1] not in tunnelsneighbours :
            newmovableactiion.append(moveaction)
        if moveaction == 2 and mapfeature[x][y + 1] not in tunnelsneighbours :
            newmovableactiion.append(moveaction)
        if moveaction == 3 and mapfeature[x - 1][y] not in tunnelsneighbours:
            newmovableactiion.append(moveaction)
        if moveaction == 4 and mapfeature[x + 1][y] not in tunnelsneighbours:
            newmovableactiion.append(moveaction)
    return newmovableactiion



    pass





#这个函数的目的就希望能够根据地方的player的位置躲着
def player_avoidaction(player, anamyplayers,actionpower):
    global visionrange
    global mapfeature
    global map_width
    global map_height
    global playerworm

    # print('打印一下当前player的信息')
    # print(player)
    x = player['x']
    y = player['y']
    # print('实际坐标x：' + str(x) + '    y' + str(y))
    movaableaction = []


    #得到当前可以移动的范围内
    if y > 0:  # 向上
        if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y-1])):
            movaableaction.append(1)
    if y < map_height - 1:  # 向下
        if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y+1])):
            movaableaction.append(2)
    if x > 0:  # 向左移动
        if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][y].tunnel == 'right' or tunnelanamylimit(mapfeature[x-1][y])):
            movaableaction.append(3)
    if x < map_width - 1:  # 向右移动
        if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][y].tunnel == 'left' or tunnelanamylimit(mapfeature[x+1][y])):
            movaableaction.append(4)

    if len(anamyplayers)==0:
        # 分程两种，一种是在内部的豆子，一种是不在内部的豆子
        #如果敌人都不在哦我们的视野内的时候，我们也要吃豆子啊
        #吃豆子成俗
        # movaableaction=[1,2,3,4]
        # print('我们正在进行随机 逃跑')  #并不应该进行完全的逃跑.
        # if len(movaableaction) > 1:
        #     movaableaction1 = fieldlimit(player, movaableaction)
        #     # print('未经过筛选的动作：'+str(movaableaction))
        #     # print('打印一下经过筛选的action' + str(movaableaction1))
        #     if len(movaableaction1) == 0:
        #         print('经过筛选后的动作是空的')
        #         pass
        #     else:
        #         movaableaction = movaableaction1

        # print('这个时候打印一下当前可移动的i情况 和本身的位置')
        # print(movaableaction)
        # print('anaamyplayes 的情况',anamyplayers )
        if actionpower in movaableaction:
            return   actionpower
        else:
            #这个时候表示的是上面返回的是None,这个时候我们尽量对逃跑准则进行一定的规划 分散规划


            a = random.randint(0, len(movaableaction) - 1)
            # print('打印一下，我们将要选择执行哪些动作，没有敌人的情况下----'+str(movaableaction[a]))
            return movaableaction[a]
    else:
        # print('这个时候打印一下当前可移动的i情况 和本身的位置')
        # print(movaableaction)
        # print('anaamyplayes 的情况',anamyplayers )
        if len(movaableaction)==0:  #如果没有可以移动的距离了，就选择不移动了
            #这个时候就应该根据记录的敌人的情况进行规律探讨,然后得到移动的规律.
            #具体规律可以设定如果最近的敌人上一次的移动方向是向下,并且上上次的移动方向是向下,我们就认为我们就可以进行反向的运动,这样有可能
            #这个时候根据敌人的实际位置进行跑动
            ac=deadmove(player,anamyplayers)
            # print('打印一下，我们将要选择执行哪些动作，死亡移动----'+str(ac))
            return ac

        else:
            #尽量不要贴边走否则容易被吃
            #也就是x如果小于1

            # print('action 有多长'+str(len(movaableaction)))
            # print('打印一下可以执行的动作'+str(movaableaction))
            if player==playerworm:
                # mapshow(mapfeature)
                # print('这个时候打印一下当前可移动的i情况 和本身的位置',player)
                # print(movaableaction)
                # print('anaamyplayes 的情况', anamyplayers)
                # print('action power 是多少：'+str(actionpower))
                if actionpower in movaableaction:
                    # print('playerworm action power 是在这个内部')
                    return actionpower
                else:
                    # 这个敌方选择好了
                    # print('这个时候我们看一下可以执行的action有多长：len(movaableaction)：'+str(len(movaableaction)))
                    a = random.randint(0, len(movaableaction) - 1)
                    # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                    return movaableaction[a]
                #这个时候就不需要有敌人
                pass
            else:
                if len(movaableaction)>1:

                    movaableaction1=fieldlimit(player,movaableaction)
                    # print('未经过筛选的动作：'+str(movaableaction))
                    # print('经过field筛选的动作：'+str(movaableaction1))
                    if  len(movaableaction1)==0:
                        pass
                    else:
                        movaableaction=movaableaction1

                        if len(movaableaction)>1:
                            movaableaction2=tunnellimit(player,movaableaction)
                            # print('经过tunnel筛选的动作：'+str(movaableaction2))
                            if len(movaableaction2)==0:
                                pass
                            else:
                                movaableaction=movaableaction2

                    # print('打印一下经过筛选的action' + str(movaableaction1))
                if actionpower in movaableaction:
                   return actionpower
                else:

                    if len(movaableaction)>1:
                        movaableaction3=center_gravity(player,movaableaction)
                        # print('经过gravity筛选的动作 '+str(movaableaction3))

                        if len(movaableaction3)==0:
                            pass
                        else:
                            movaableaction=movaableaction3
                        #这个敌方选择好了
                        # print('这个时候我们看一下可以执行的action有多长：len(movaableaction)：'+str(len(movaableaction)))
                        a=random.randint(0,len(movaableaction)-1)
                        # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                        return movaableaction[a]
                    else:
                        return movaableaction[0]


#这个function的作用就是为了实现在可行的路线中寻找最优的路线
def fieldlimit(player,movaableaction):
    global map_width
    global map_height
    field_factor=3
    x=player['x']
    y=player['y']
    newmovableactiion=[]
    for moveaction in movaableaction:
        if moveaction==1 and y>=field_factor:
            newmovableactiion.append(moveaction)
        if moveaction==2 and y<=map_height-field_factor:
            newmovableactiion.append(moveaction)
        if moveaction == 3 and x >= field_factor:
            newmovableactiion.append(moveaction)
        if moveaction==4 and x<=map_width-field_factor:
            newmovableactiion.append(moveaction)
    return newmovableactiion
    pass
def tunnellimit(player,movaableaction):
    global mapfeature
    x=player['x']
    y=player['y']

    newmovableactiion=[]
    for moveaction in movaableaction:
        if moveaction==1 and  mapfeature[x][y-1].tunnel == 'no':
            newmovableactiion.append(moveaction)
        if moveaction==2 and mapfeature[x][y+1].tunnel=='no':
            newmovableactiion.append(moveaction)
        if moveaction == 3 and mapfeature[x-1][y].tunnel=='no':
            newmovableactiion.append(moveaction)
        if moveaction==4 and mapfeature[x+1][y].tunnel=='no':
            newmovableactiion.append(moveaction)
    return newmovableactiion

def center_gravity(player,moveableaction):
    global map_width
    global map_height
    gravity_factor=4
    x=player['x']
    y=player['y']
    # print('打印出 实际的位置 x，y',x,'    ',y)
    y_away=abs(y- map_height/2)/map_height
    x_away = abs(x - map_width / 2) / map_width
    newmovableactiion=[]
    for moveaction in moveableaction:
        if moveaction == 1 and y>=map_height/2:
            newmovableactiion.append(moveaction)
        if moveaction == 2 and y<map_height/2:
            newmovableactiion.append(moveaction)
        if moveaction == 3 and x>=map_width/2:
            newmovableactiion.append(moveaction)
        if moveaction == 4 and x<map_width/2:
            newmovableactiion.append(moveaction)
    #这一段是用来选择走左还是走右的
    if len(newmovableactiion)==2:
        newmovableactiion1=[]
        for moveaction in moveableaction:
            if moveaction==1 and y_away>=x_away:
                newmovableactiion1.append(moveaction)
            if moveaction==2 and y_away>=x_away:
                newmovableactiion1.append(moveaction)
            if moveaction == 3 and x_away>=y_away:
                newmovableactiion1.append(moveaction)
            if moveaction==4 and x_away>=y_away:
                newmovableactiion1.append(moveaction)
        return newmovableactiion1
    else:
        return newmovableactiion
#这个函数作用是为了防止走完tunnel之后，终点就是敌人的情况
#我们需要得到移动的方向，然后终点是哪里
def tunnelanamylimit(neighbour):
    global mapfeature
    if neighbour.tunnel=='no':
        # print('我们的邻居是nonononono，也就不是tunnel了')
        return False  #表示不是敌人
        pass
    else:
        c=findgoodneighbour(neighbour) #给定mapfeature的一个对象，然后返回对应实际的neighbour。
        # print('这个时候返回走过tunnel之后的情况敌人的位置',c.anamy)
        return c.anamy


    pass

#这个函数是判断经过tunnel之后的是不是真实的敌人的位置
def tunneltrueanamylimit(neighbour):
    global mapfeature
    if neighbour.tunnel=='no':
        # print('我们的邻居是nonononono，也就不是tunnel了')
        return False  #表示不是敌人
        pass
    else:
        c=findgoodneighbour(neighbour) #给定mapfeature的一个对象，然后返回对应实际的neighbour。
        # print('这个时候返回走过tunnel之后，trueannamy的i情况',c.trueanamy)
        return c.trueanamy
def wormholeanamylimit(neighbour):
    global mapfeature
    if neighbour.wormhole:
        Anamyworm=findwormpair(neighbour.x,neighbour.y)
        # print('返回的worm对面的是不是敌人',mapfeature[Anamyworm['x']][Anamyworm['y']].anamy)
        return mapfeature[Anamyworm['x']][Anamyworm['y']].anamy
    else:
        return False

def wormholetrueanamylimit(neighbour):
    global mapfeature
    if neighbour.wormhole:
        anamyworm=findwormpair(neighbour.x,neighbour.y)
        # print('返回的worm对面的是不是敌人',mapfeature[anamyworm['x']][anamyworm['y']].anamy)
        return mapfeature[anamyworm['x']][anamyworm['y']].trueanamy
    else:
        return False

    pass


    pass


global anamy_moveU1
global anamy_moveU2

anamy_moveU1=[]
anamy_moveU2=[]
def get_trueanamymotionpatern(player,anamyplayers):
    import copy
    global mapfeature
    global lastmove
    global lastlastmove


    movableaction=[]
    x = player['x']
    y = player['y']
    print('实际坐标x：' + str(x) + '    y' + str(y))
    #这个时候实际记录一下敌人的移动方向。如果连续两次同一个方向，那么我们就反向移动
    mapfeaturecopy=copy.deepcopy(mapfeature)



    movaableaction = []
    # 得到当前可以移动的范围内
    if y > 0:  # 向上

        if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][y - 1].tunnel == 'down'):
            movableaction.append(1)
    if y < map_height - 1:  # 向下
        if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][y + 1].tunnel == 'up'):
            movableaction.append(2)
    if x > 0:  # 向左移动
        if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][y].tunnel == 'right'):
            movableaction.append(3)
    if x < map_width - 1:  # 向右移动
        if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][y].tunnel == 'left'):
            movableaction.append(4)



def update_players(players):
    # print(players)
    myplayers = []
    anamyplayers = []
    ##更新player的内容，设定为局部变量了，所以我们每次都会重新更新

    for i in range(len(players)):
        if players[i]['team'] == constants.team_id:
            myplayers.append(players[i])
        else:
            anamyplayers.append(players[i])
    return myplayers,anamyplayers
    ##############展示我方的player和地方的player
    # print('我方的player')
    # for i in range(len(myplayers)):
    #
    #     print(myplayers[i])
    # print('敌方的player')
    # for i in range(len(anamyplayers)):
    #     print(anamyplayers[i])
    #########更新当前的敌人的位置################

#
def deadmoveNew3(player,anamyplayers):
        #要找到分数最多的敌人。
        #攻击最近的敌人
    global mapfeature
    mindis=1000
    x=player['x']
    y=player['y']
    move_backplan=[]

    for anamyplayer in anamyplayers:
        x_dis= abs(player['x'] - anamyplayer['x'])
        y_dis=abs(player['y'] - anamyplayer['y'])
        tempdis=x_dis+y_dis
        if tempdis < mindis:
            mindis = tempdis
            # minanamy = anamyplayer
    if mindis==2 and  x_dis==1 and y_dis==1:

        return None
    elif mindis==1:  #这个时候的情况下也是有路走的啊，因为即使走tunnel也是没有路了啊，这个时候，我们就将敌人当成帧是的敌人，其他的位置是不考虑的哦~
        '''我们派出了敌人在我斜对角的情况，这样的情况下，我希望还能有路可以走，这个时候我就认为敌人不会穿过tunnel来找我'''
        # print('第一层放宽敌人限制')
        updateanamyposition(anamyplayers) #这个是将敌人的位置仅仅更新到不走过tunnel的情况
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1]) or wormholetrueanamylimit(mapfeature[x][y-1])):
                move_backplan.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1]) or wormholetrueanamylimit(mapfeature[x][y+1])):
                move_backplan.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y]) or wormholetrueanamylimit(mapfeature[x-1][y])):
                move_backplan.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y]) or wormholetrueanamylimit(mapfeature[x+1][y])):
                move_backplan.append(4)
        # print('放宽对敌人限制后的情况下的可运动的范围',move_backplan)
        if len(move_backplan)==0:
            '''这个时候需要再一次放松限制'''
            # print('第二层放宽敌人限制')
            # print('')

            # mapshow(mapfeature)
            movaableactionb=[]
            if y > 0:  # 向上
                if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 1].wall or mapfeature[x][
                    y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1]) or wormholetrueanamylimit(
                    mapfeature[x][y - 1])):
                    movaableactionb.append(1)
            if y < map_height - 1:  # 向下
                if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 1].wall or mapfeature[x][
                    y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1]) or wormholetrueanamylimit(
                    mapfeature[x][y + 1])):
                    movaableactionb.append(2)
            if x > 0:  # 向左移动
                if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                    y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y]) or wormholetrueanamylimit(
                    mapfeature[x - 1][y])):
                    movaableactionb.append(3)
            if x < map_width - 1:  # 向右移动
                if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                    y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y]) or wormholetrueanamylimit(
                    mapfeature[x + 1][y])):
                    movaableactionb.append(4)
            # print('第二次放宽对敌人的限制后的移动范围：', movaableactionb)
            if len(movaableactionb)==0:
                return random.randint(1,4)
            else:
                ac= movaableactionb[random.randint(0,len(movaableactionb)-1)]
                return ac

        else:
            ac=move_backplan[random.randint(0,len(move_backplan)-1)]
            return ac



#我们进行整体的规划
#通过对当前player要进行的action的运动的集合
#我们对敌人进行追击的策略就是包围策略
#
def deadmove(player,anamyplayers):
        #要找到分数最多的敌人。
        #攻击最近的敌人
    global mapfeature
    mindis=1000
    x=player['x']
    y=player['y']
    move_backplan=[]

    for anamyplayer in anamyplayers:
        x_dis= abs(player['x'] - anamyplayer['x'])
        y_dis=abs(player['y'] - anamyplayer['y'])
        tempdis=x_dis+y_dis
        if tempdis < mindis:
            mindis = tempdis
            # minanamy = anamyplayer
    if mindis==2 and  x_dis==1 and y_dis==1:
        return None
    elif mindis==1:  #这个时候的情况下也是有路走的啊，因为即使走tunnel也是没有路了啊，这个时候，我们就将敌人当成帧是的敌人，其他的位置是不考虑的哦~
        print('这个时候发现设定的条件太过精细，导致逃跑的情况下完全限制了路径，所以这个时候就放宽对敌人的位置的判断')
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1])):
                move_backplan.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1])):
                move_backplan.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y])):
                move_backplan.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y])):
                move_backplan.append(4)
        print('放宽对敌人限制后的情况下的可运动的范围',move_backplan)
        if len(move_backplan)==0:
            return random.randint(1,4)
        else:
            ac=move_backplan[random.randint(0,len(move_backplan)-1)]
            return ac



def getmindistance(player,anamyplayers):

    mindis = 10000000000000
    # print('在寻找距离最近的powerout的情况下，我们打印一下powerserout以便更好判断我们得到的是不是最好的')
    # print(powersetout)
    for anamyplayer in anamyplayers:

        tempdis = abs(player['x'] - anamyplayer['x']) + abs(player['y'] - anamyplayer['y'])
        if tempdis < mindis:
            mindis = tempdis

            minanamy = anamyplayer
    return minanamy






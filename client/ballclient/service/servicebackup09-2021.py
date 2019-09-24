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

global meteors  # 陨石坐标位置
global tunnel  # 隧道位置
global wormholes  # 虫洞位置 传送
global mode  # 强势还是弱势
global palyerposition  # 玩家位置
global visionrange

global powersetout
global powersetin
global powersetround
global powersetall
powersetin = []
powersetout = []
powersetround = []
powersetall = []

global playerworm
global playerwormtarget
global Game_mode
global Attack
Attack = True

global boundary
boundary = []

global roundcount
roundcount = 0
global f
f = open('test.txt', 'w')
global epsi
epsi = 0
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
    global wormholes
    global playerworm
    global Game_mode
    global boundary
    global maptype
    global visionrange
    global powersetPos
    global anamys_id
    global anamys_motionpatterns
    global flag_playerA_done, flag_playerB_done, flag_playerC_done, flag_playerD_done
    flag_playerA_done = False
    flag_playerB_done = False
    flag_playerC_done = False
    flag_playerD_done = False
    # print ("round start")
    # print(msg)
    # print('这个时候打印一下powersetin 和 powersetout看是否下半场有记录到',powersetPos)

    # print ("msg_name:%s" % msg['msg_name'])
    # print ("map_width:%s" % msg['msg_data']['map']['width'])
    # print ("map_height:%s" % msg['msg_data']['map']['height'])
    # print ("vision:%s" % msg['msg_data']['map']['vision'])
    # print ("meteor:%s" % msg['msg_data']['map']['meteor'])
    # # print ("cloud:%s" % msg['msg_data']['map']['cloud'])
    # print ("tunnel:%s" % msg['msg_data']['map']['tunnel'])
    # print ("wormhole:%s" % msg['msg_data']['map']['wormhole'])
    # print ("teams:%s" % msg['msg_data']['teams'])
    if msg['msg_data']['teams'][0]['id'] == constants.team_id:
        Game_mode = msg['msg_data']['teams'][0]['force']
        # 这个时候实际上也应应当记录一下我方的id和地方的id信息
        anamys_id = msg['msg_data']['teams'][1]['players']
        anamys_motionpatterns = [
            {'id': anamys_id[0], 'lastmove': 5, 'lastlastmove': 5, 'x': 0, 'y': 0, 'updatelast': False,
             'updatelastlast': False},
            {'id': anamys_id[1], 'lastmove': 5, 'lastlastmove': 5, 'x': 0, 'y': 0, 'updatelast': False,
             'updatelastlast': False},
            {'id': anamys_id[2], 'lastmove': 5, 'lastlastmove': 5, 'x': 0, 'y': 0, 'updatelast': False,
             'updatelastlast': False},
            {'id': anamys_id[3], 'lastmove': 5, 'lastlastmove': 5, 'x': 0, 'y': 0, 'updatelast': False,
             'updatelastlast': False}]
    else:
        Game_mode = msg['msg_data']['teams'][1]['force']
        anamys_id = msg['msg_data']['teams'][0]['players']
        anamys_motionpatterns = [
            {'id': anamys_id[0], 'lastmove': 5, 'lastlastmove': 5, 'x': 0, 'y': 0, 'updatelast': False,
             'updatelastlast': False},
            {'id': anamys_id[1], 'lastmove': 5, 'lastlastmove': 5, 'x': 0, 'y': 0, 'updatelast': False,
             'updatelastlast': False},
            {'id': anamys_id[2], 'lastmove': 5, 'lastlastmove': 5, 'x': 0, 'y': 0, 'updatelast': False,
             'updatelastlast': False},
            {'id': anamys_id[3], 'lastmove': 5, 'lastlastmove': 5, 'x': 0, 'y': 0, 'updatelast': False,
             'updatelastlast': False}]

    map_width = msg['msg_data']['map']['width']
    map_height = msg['msg_data']['map']['height']

    visionrange = msg['msg_data']['map']['vision']

    meteors = []
    for i in range(len(msg['msg_data']['map']['meteor'])):
        meteors.append(msg['msg_data']['map']['meteor'][i])
    #  print(msg['msg_data']['map']['meteor'][i])

    # print(meteors)

    ###########get tunnel data###################
    # {'direction': 'up', 'x': 5, 'y': 5}
    tunnels = []
    for i in range(len(msg['msg_data']['map']['tunnel'])):
        tunnels.append(msg['msg_data']['map']['tunnel'][i])
        # print(tunnel[i]0)
    # print('get tunnels')
    # print(tunnels)
    #########get wormhole data#################
    # teams:[{'force': 'beat', 'id': 2222, 'players': [0, 1, 2, 3]}, {'force': 'think', 'id': 1111, 'players': [4, 5, 6, 7]}]
    wormholes = []
    for i in range(len(msg['msg_data']['map']['wormhole'])):
        wormholes.append(msg['msg_data']['map']['wormhole'][i])

    mapinittialization()

    boundary, maptype = boundary_get()
    # wormwholetarget是表示可以有好几个有能够进入内部的虫洞
    find_wormhole(xmin=boundary[0], ymin=boundary[1], xmax=boundary[2], ymax=boundary[3])
    # end1=time.clock()
    # print('legstart使用的时间')
    # print(end1-start1)
    # 这个时间一般都okay的


global myteampoint
global anamypoint
myteampoint = 0
anamypoint = 0


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
    # legup=False

    global roundcount
    roundcount = 0
    # print('hello')

    print("round over")
    teams = msg["msg_data"]['teams']
    print(msg)

    for team in teams:
        print("teams:%s" % team['id'])
        print("point:%s" % team['point'])
        print("\n\n")

        f.write('     半场' + '  ' + str(team['id']) + '分数:' + str(team['point']) + '\n')
        if team['id'] == 1515:
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
    myteampoint = 0
    anamypoint = 0
    print("game over!")
    epsi = epsi + 1
    f.write('roundstart:' + str(epsi) + '\n')  # 这个是为下一轮做准备
    roundcount = 0


global playerworm
playerworm = None

global flag_initialworm
flag_initialworm = False

global flag_exploremapdone
flag_exploremapdone = False


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
    global anamytarget

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
    start = time.clock()

    roundcount = roundcount + 1
    print("round" + str(roundcount))

    # print(msg)

    ######################每局内容更新###################
    round_id = msg['msg_data']['round_id']
    players = msg['msg_data']['players']

    # 这个函数是返回myplayers 和 anamyplayers
    myplayers, anamyplayers = update_players(players)

    global partApos, partBpos, partCpos, partDpos, partABCDpos
    global centrolpartApos, centrolpartBpos, centrolpartCpos, centrolpartDpos
    global flag_exploremapdone
    if flag_exploremapdone:
        pass
    else:
        # print('partABCDpos',partABCDpos)
        if len(partABCDpos) >= 10:
            # print('四块待询问的点A', partApos)
            # print('四块待询问的点B', partBpos)
            # print('四块待询问的点C', partCpos)
            # print('四块待询问的点D', partDpos)

            centrolpartApos, partApos = getcentrolpos(partApos, myplayers)
            centrolpartBpos, partBpos = getcentrolpos(partBpos, myplayers)
            centrolpartCpos, partCpos = getcentrolpos(partCpos, myplayers)
            centrolpartDpos, partDpos = getcentrolpos(partDpos, myplayers)
            updatepartABCDpos(myplayers)
            if roundcount == 1:
                round1TogetDefaultline(myplayers)
        else:
            # print('complete view explore')
            flag_exploremapdone = True
            pass

    ######round1的动作，得到巡游动作的分配###

    if roundcount == 300:
        teams = msg['msg_data']['teams']
        print('当前的teams', teams)
        for team in teams:
            if team['id'] == 1515:
                f.write('我方死了' + str(8 - len(myplayers) - team['remain_life']) + '次' + '\n')
            else:
                f.write('敌方死了' + str(8 - 4 - team['remain_life']) + '次' + '\n')

    global Game_mode
    global Attack
    global PointPrority
    # PointPrority = True
    if msg['msg_data']['mode'] == Game_mode:
        updateanamypositionattackmode()

        Attack = True


    else:
        Attack = False
        # print('我们正在防守模式')
        # updateanamypositionsimple(anamyplayers)
        # updateanamyposition(anamyplayers)
        # updateanamypositionUpgradehardV1a(anamyplayers,myplayers)
        updateanamypositionUpgrade(anamyplayers)

    # print('敌人的情况  ',anamyplayers)
    get_trueanamymotionpattern(anamyplayers)

    # mapshow(mapfeature)

    ##########更新powerset
    try:
        powersetround = []
        powersetround = msg['msg_data']['power']
    except:
        powersetround = []
    update_powerset(myplayers, anamyplayers)
    global flag_get_Attackanamy
    flag_get_Attackanamy = False
    maptype = 2
    if maptype == 1:
        # print('map1 种类中')
        # z这个函数的作用是确定playerworm 和 out  wormwhole 等等   与之前的效果相同
        update_playerABCDV1(myplayers)  # 这个函数的作用是为了实现，对playerworm  playerout playerup playerdown的选择
        dividepowerset(myplayers)  # 这个函数分别得到了各个player对应要吃的power

        if Attack:
            # actionA = get_poweractionmap1(playerA, anamyplayers)
            # actionB = get_poweractionmap1(playerB, anamyplayers)
            # actionC = get_poweractionmap1(playerC, anamyplayers)
            # actionD = get_poweractionmap1(playerD, anamyplayers)
            actionA = get_poweractionmap1V2(playerA, anamyplayers, powersetA)
            actionB = get_poweractionmap1V2(playerB, anamyplayers, powersetB)
            actionC = get_poweractionmap1V2(playerC, anamyplayers, powersetC)
            actionD = get_poweractionmap1V2(playerD, anamyplayers, powersetD)

        else:
            actionA = get_poweractionmap1V2(playerA, anamyplayers, powersetA)
            actionB = get_poweractionmap1V2(playerB, anamyplayers, powersetB)
            actionC = get_poweractionmap1V2(playerC, anamyplayers, powersetC)
            actionD = get_poweractionmap1V2(playerD, anamyplayers, powersetD)


    elif maptype == 2:
        # print('we are in maptype2 situation')

        if len(myplayers) == 4:
            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = myplayers[2]
            playerD = myplayers[3]
        elif len(myplayers) == 3:
            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = myplayers[2]
            playerD = None
        elif len(myplayers) == 2:
            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = None
            playerD = None
        elif len(myplayers) == 1:
            playerA = myplayers[0]
            playerB = None
            playerC = None
            playerD = None

        dividepowerset(myplayers)  # 这个函数分别得到了各个player对应要吃的power
        if Attack:

            PointPrority = False
            if PointPrority:
                # 这个函数是进行的是吃分数优先的情况，具体攻击敌人的使用的情况，可以通过调用后面的函数进行改变
                actionA = get_poweractionmap2(playerA, powersetA, anamyplayers, myplayers)
                actionB = get_poweractionmap2(playerB, powersetB, anamyplayers, myplayers)
                actionC = get_poweractionmap2(playerC, powersetC, anamyplayers, myplayers)
                actionD = get_poweractionmap2(playerD, powersetD, anamyplayers, myplayers)
            else:
                # print('在哪里1')
                # 使用这个get_attackactionmap2Upgrade_parta 是采用优先吃敌人的方式，并且采用的是攻击敌人的postionV2
                # actionA = get_attackactionmap2Upgrade_parta(playerA, powersetA,anamyplayers,myplayers)
                # actionB = get_attackactionmap2Upgrade_parta(playerB, powersetB,anamyplayers,myplayers)
                # actionC = get_attackactionmap2Upgrade_parta(playerC, powersetC,anamyplayers,myplayers)
                # actionD = get_attackactionmap2Upgrade_parta(playerD, powersetD,anamyplayers,myplayers)

                # 这个函数进行的是吃敌人优先的策略，攻击敌人的位置是nextmove，然后敌人的默认的方向的位置是None??不是的，默认的方向敌人本身的位置
                # actionA = get_poweractionmap2UpgradeV2(playerA, powersetA,anamyplayers)
                # actionB = get_poweractionmap2UpgradeV2(playerB, powersetB,anamyplayers)
                # actionC = get_poweractionmap2UpgradeV2(playerC, powersetC,anamyplayers)
                # actionD = get_poweractionmap2UpgradeV2(playerD, powersetD,anamyplayers)

                # 这个函数是吃敌人优先的策略，但是会对吃敌人的额阈值进行一定的设定，还需要更好的完善，预测的是敌人的下一步
                # actionA = get_poweractionmap2UpgradeV3(playerA, powersetA, anamyplayers,myplayers)
                # actionB = get_poweractionmap2UpgradeV3(playerB, powersetB, anamyplayers,myplayers)
                # actionC = get_poweractionmap2UpgradeV3(playerC, powersetC, anamyplayers,myplayers)
                # actionD = get_poweractionmap2UpgradeV3  (playerD, powersetD, anamyplayers,myplayers)
                #

                # 在parta的基础上进行的修改，加入自主的巡游的策略
                # actionA = get_attackactionmap2Upgrade_partaV2(playerA, powersetA,anamyplayers,myplayers)
                # actionB = get_attackactionmap2Upgrade_partaV2(playerB, powersetB,anamyplayers,myplayers)
                # actionC = get_attackactionmap2Upgrade_partaV2(playerC, powersetC,anamyplayers,myplayers)
                # actionD = get_attackactionmap2Upgrade_partaV2(playerD, powersetD,anamyplayers,myplayers)

                # 这个是本来向走围堵的策略的发现比较复杂
                # actionAll = get_poweractionmap2UpgradeV4(playerA, powersetA, anamyplayers,myplayers)

                # 这个是在v3的基础上进行修改，然后通过限制我方的运动方向进行攻击
                '''将我们的player进行膨胀处理'''
                for pos in anamymakewallposition:
                    mapfeature[pos['x']][pos['y']].attackwall = False
                    mapfeature[pos['x']][pos['y']].context = '0'
                global flag_playerA_done, flag_playerB_done, flag_playerC_done, flag_playerD_done
                flag_playerA_done = False
                flag_playerB_done = False
                flag_playerC_done = False
                flag_playerD_done = False
                myplayerscopy = copy.deepcopy(myplayers)
                # myplayerscopy.remove(playerA)
                updatemyplayerspositionUpgrade(myplayerscopy, anamyplayers)  # 这个时候就把自己搞死了。所以，应该当去除自己更新myplayers
                # actionA = get_poweractionmap2UpgradeV5(playerA, powersetA, anamyplayers,myplayers)
                # actionB = get_poweractionmap2UpgradeV5(playerB, powersetB, anamyplayers,myplayers)
                # actionC = get_poweractionmap2UpgradeV5(playerC, powersetC, anamyplayers,myplayers)
                # actionD = get_poweractionmap2UpgradeV5(playerD, powersetD, anamyplayers,myplayers)
                # #
                actionA = get_poweractionmap2UpgradeV6(playerA, powersetA, anamyplayers, myplayers)
                actionB = get_poweractionmap2UpgradeV6(playerB, powersetB, anamyplayers, myplayers)
                actionC = get_poweractionmap2UpgradeV6(playerC, powersetC, anamyplayers, myplayers)
                actionD = get_poweractionmap2UpgradeV6(playerD, powersetD, anamyplayers, myplayers)

                # actionA = get_poweractionmap2UpgradeV7(playerA, powersetA, anamyplayers,myplayers)
                # actionB = get_poweractionmap2UpgradeV7(playerB, powersetB, anamyplayers,myplayers)
                # actionC = get_poweractionmap2UpgradeV7(playerC, powersetC, anamyplayers,myplayers)
                # actionD = get_poweractionmap2UpgradeV7(playerD, powersetD, anamyplayers,myplayers)

                for anamyplayer in anamyplayers:
                    mapfeature[anamyplayer['x']][anamyplayer['y']].trueanamyplayer = False

        else:
            actionA = get_poweractionmap2(playerA, powersetA, anamyplayers, myplayers)
            actionB = get_poweractionmap2(playerB, powersetB, anamyplayers, myplayers)
            actionC = get_poweractionmap2(playerC, powersetC, anamyplayers, myplayers)
            actionD = get_poweractionmap2(playerD, powersetD, anamyplayers, myplayers)


    elif maptype == 3:
        pass

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
            # a = player_avoidactionNew3(playerA, anamyplayers, actionA)
            a = player_avoidactionNew4(playerA, anamyplayers, actionA, myplayers)
            # a = player_avoidactionNew5(playerA, anamyplayers, actionA,myplayers)

            # print('PlayerA: ' + str(a))
            # print('playerA的内容： ', playerA)
            if a is None:  # 我们认为返回0是可以选择不动的，这个时候我们就返回别的可以动的东西就好了

                pass
            else:
                action.append({"team": playerA['team'], "player_id": playerA['id'], "move": [direction[a]]})

            ###################################
        if playerB is None:
            # print('playerB 是空的')
            pass
        else:
            # a = player_avoidaction(playerB, anamyplayers,actionB)
            # a = player_avoidactionNew1(playerB, anamyplayers, actionB)
            # a = player_avoidactionNew2(playerB, anamyplayers, actionB)
            # a = player_avoidactionNew3(playerB, anamyplayers, actionB)
            a = player_avoidactionNew4(playerB, anamyplayers, actionB, myplayers)
            # a = player_avoidactionNew5(playerB, anamyplayers, actionB,myplayers)
            #
            # print('PlayerB: ' + str(a))
            # print('playerB的内容： ', playerB)

            if a is None:  # 我们认为返回0是可以选择不动的，这个时候我们就返回别的可以动的东西就好了
                pass
            else:
                action.append({"team": playerB['team'], "player_id": playerB['id'], "move": [direction[a]]})
        #####################################
        if playerC is None:
            # print('oplayerC 是空的')
            pass
        else:
            # a = player_avoidaction(playerC, anamyplayers,actionC)
            # a = player_avoidactionNew1(playerC, anamyplayers,actionC)

            # a = player_avoidactionNew2(playerC, anamyplayers,actionC)
            # a = player_avoidactionNew3(playerC, anamyplayers,actionC)
            a = player_avoidactionNew4(playerC, anamyplayers, actionC, myplayers)
            # a = player_avoidactionNew5(playerC, anamyplayers,actionC,myplayers)
            #
            # print('PlayerC: ' + str(a))
            # print('playerC的内容： ', playerC)

            if a is None:  # 我们认为返回0是可以选择不动的，这个时候我们就返回别的可以动的东西就好了
                pass
            else:
                action.append({"team": playerC['team'], "player_id": playerC['id'], "move": [direction[a]]})

        #############################################

        if playerD is None:

            # print('playerd shi kong de ')
            pass
        else:
            # a = player_avoidaction(playerD, anamyplayers,actionD)
            # a = player_avoidactionNew1(playerD, anamyplayers,actionD)
            # a = player_avoidactionNew2(playerD, anamyplayers,actionD)
            # a = player_avoidactionNew3(playerD, anamyplayers,actionD)
            a = player_avoidactionNew4(playerD, anamyplayers, actionD, myplayers)
            # a = player_avoidactionNew5(playerD, anamyplayers,actionD,myplayers)

            # print('PlayerD: ' + str(a))
            # print('playerD的内容： ', playerD)
            if a is None:  # 我们认为返回0是可以选择不动的，这个时候我们就返回别的可以动的东西就好了
                pass
            else:
                action.append({"team": playerD['team'], "player_id": playerD['id'], "move": [direction[a]]})

    # print(action)
    # for player in players:
    #     if player['team'] == constants.team_id:
    #         actionold.append({"team": player['team'], "player_id": player['id'],
    #                        "move": [direction[random.randint(1, 4)]]})
    # print(actionold)
    result['msg_data']['actions'] = action

    #
    end = time.clock()
    print('打印用了多长的时间')
    print(end - start)
    return result


# 给定长 宽
# metoer位置
# tunnel位置
# 敌方位置
#
global partABCDpos
partABCDpos = []


def mapinittialization():
    global mapfeature
    global map_height
    global map_width
    global meteors
    global tunnels
    global wormholes
    global mapview
    global partApos, partBpos, partCpos, partDpos
    global defaultlineA, defaultlineB, defaultlineC, defaultlineD

    mapview = []
    mapfeature = []
    h = map_height
    w = map_width

    # print('ok1')
    for x in range(w):
        mapfeature += [[]]
        mapview += [[]]
        for y in range(h):
            mapfeature[x].append(astarpath.Grid(x, y, h, w))
            mapview[x].append(0)
        pass

    for i in range(len(meteors)):
        mapfeature[meteors[i]['x']][meteors[i]['y']].wall = True
        mapfeature[meteors[i]['x']][meteors[i]['y']].context = '*'

        mapview[meteors[i]['x']][meteors[i]['y']] = 1

    for tunnel in (tunnels):
        mapfeature[tunnel['x']][tunnel['y']].wall = False
        # mapfeature[tunnel['x']][tunnel['y']].context = '*'

        mapfeature[tunnel['x']][tunnel['y']].tunnel = tunnel['direction']
        # mapfeature[tunnel['x']][tunnel['y']].tunnel = 'no'  #使用了这句话 就表示不使用neibour作为路径规划了
        mapfeature[tunnel['x']][tunnel['y']].context = tunnel['direction'][0]

        mapview[tunnel['x']][tunnel['y']] = 1

    # mapfeature[1][1].context='aa'
    # print('找到当前的wormhole')
    # print(wormholes)
    for wormhole in wormholes:
        mapfeature[wormhole['x']][wormhole['y']].wormhole = True
        # mapfeature[tunnel['x']][tunnel['y']].context = '*'
        # print('wormhole name : ',wormhole['name'])
        mapfeature[wormhole['x']][wormhole['y']].wormholecontext = wormhole['name']

        mapfeature[wormhole['x']][wormhole['y']].context = wormhole['name']

        mapview[wormhole['x']][wormhole['y']] = 1

    global partABCDpos
    partApos = []
    partBpos = []
    partCpos = []
    partDpos = []

    # 找到一开始我的鲲想要去的敌方
    for x in range(visionrange + 1, w - visionrange):
        for y in range(visionrange + 1, h - visionrange):
            if x < int(w / 2) - visionrange and y < int(h / 2) - visionrange:
                # 这个时候找到这些地点的中心
                if not mapfeature[x][y].wall and mapfeature[x][y].tunnel == 'no' and not mapfeature[x][y].wormhole:
                    partApos.append({'x': x, 'y': y})


            elif x > int(w / 2) + visionrange and y < int(h / 2) - visionrange:
                # 这个时候找到这些地点的中心
                if not mapfeature[x][y].wall and mapfeature[x][y].tunnel == 'no' and not mapfeature[x][y].wormhole:
                    partBpos.append({'x': x, 'y': y})
            elif x < int(w / 2) - visionrange and y > int(h / 2) + visionrange:
                # 这个时候找到这些地点的中心
                if not mapfeature[x][y].wall and mapfeature[x][y].tunnel == 'no' and not mapfeature[x][y].wormhole:
                    partCpos.append({'x': x, 'y': y})
            elif x > int(w / 2) + visionrange and y > int(h / 2) + visionrange:
                # 这个时候找到这些地点的中心
                if not mapfeature[x][y].wall and mapfeature[x][y].tunnel == 'no' and not mapfeature[x][y].wormhole:
                    partDpos.append({'x': x, 'y': y})

    # print('四块待询问的点A',partApos)
    # print('四块待询问的点B',partBpos)
    # print('四块待询问的点C', partCpos)
    # print('四块待询问的点D',partDpos)
    partABCDpos.extend(partApos)
    partABCDpos.extend(partBpos)
    partABCDpos.extend(partCpos)
    partABCDpos.extend(partDpos)
    # print('zongdian ',partABCDpos)

    for x in range(w):
        for y in range(h):
            # addneighboursnew(mapfeature[x][y])
            addneighboursnewupdate(mapfeature[x][y])
            # addneighbourssimple(mapfeature[x][y])
    global tunnelsneighbours
    # print('打印一下当前的tunnelsneighbours的情况  ', tunnelsneighbours)
    # for tunnelsneighbour in  tunnelsneighbours:
    # print('实际的坐标的情况   x',tunnelsneighbour.x,'   y:', tunnelsneighbour.y)
    # mapshow(mapfeature)


# program control
# 判断是否需要使用boundary ，如果不使用boundary 我们也就不需要找到一个可以进入内部的player了

# 这个函数用来判断是否地图的基本特点。

def round1TogetDefaultline(myplayers):
    global mapfeature
    global partApos, partBpos, partCpos, partDpos
    global defaultlineA, defaultlineB, defaultlineC, defaultlineD
    global centrolpartDpos, centrolpartBpos, centrolpartCpos, centrolpartDpos
    global flag_getsolution
    defaultlineA = []
    defaultlineB = []
    defaultlineC = []
    defaultlineD = []

    print('centrolpartApos', centrolpartApos)
    print('centrolpartBpos', centrolpartBpos)
    print('centrolpartCpos', centrolpartCpos)
    print('centrolpartDpos', centrolpartDpos)

    myplayerscopy = copy.deepcopy(myplayers)
    player1 = findnearestplayertomapexplorepos(myplayerscopy, centrolpartApos)
    myplayerscopy.remove(player1)
    player2 = findnearestplayertomapexplorepos(myplayerscopy, centrolpartBpos)
    myplayerscopy.remove(player2)
    player3 = findnearestplayertomapexplorepos(myplayerscopy, centrolpartCpos)
    myplayerscopy.remove(player3)
    player4 = myplayerscopy[0]
    print('defaultplayer A', player1)
    print('defaultplayer B', player2)
    print('defaultplayer C', player3)
    print('defaultplayer D', player4)

    print('四块待询问的点A', partApos)
    print('四块待询问的点B', partBpos)
    print('四块待询问的点C', partCpos)
    print('四块待询问的点D', partDpos)
    x = player1['x']
    y = player1['y']
    partAposcopy = copy.deepcopy(partApos)
    partBposcopy = copy.deepcopy(partBpos)
    partCposcopy = copy.deepcopy(partCpos)
    partDposcopy = copy.deepcopy(partDpos)

    testposnum = len(partApos)
    for i in range(testposnum):
        startpos = {'x': x, 'y': y}
        print('startpos:', startpos)
        pos = get_nearestPosition(startpos, partAposcopy)
        start = mapfeature[x][y]
        end = mapfeature[pos['x']][pos['y']]
        path = getpathnoanamy(start, end)
        if flag_getsolution:
            x = pos['x']
            y = pos['y']
            # if len(path)==2:
            defaultlineA.append(pos)
            partAposcopy.remove(pos)
        else:
            partAposcopy.remove(pos)

    x = player2['x']
    y = player2['y']
    testposnum = len(partBpos)
    for i in range(testposnum):
        startpos = {'x': x, 'y': y}
        pos = get_nearestPosition(startpos, partBposcopy)
        start = mapfeature[x][y]
        end = mapfeature[pos['x']][pos['y']]
        path = getpathnoanamy(start, end)
        if flag_getsolution:
            x = pos['x']
            y = pos['y']
            # if len(path)==2:
            defaultlineB.append(pos)
            partBposcopy.remove(pos)

    x = player3['x']
    y = player3['y']

    testposnum = len(partCpos)
    for i in range(testposnum):
        startpos = {'x': x, 'y': y}
        pos = get_nearestPosition(startpos, partCposcopy)
        start = mapfeature[x][y]
        end = mapfeature[pos['x']][pos['y']]
        path = getpathnoanamy(start, end)
        if flag_getsolution:
            x = pos['x']
            y = pos['y']
            # if len(path)==2:
            defaultlineC.append(pos)
            partCposcopy.remove(pos)

    x = player4['x']
    y = player4['y']
    testposnum = len(partDpos)
    for i in range(testposnum):
        startpos = {'x': x, 'y': y}
        pos = get_nearestPosition(startpos, partDposcopy)
        start = mapfeature[x][y]
        end = mapfeature[pos['x']][pos['y']]
        path = getpathnoanamy(start, end)
        if flag_getsolution:
            x = pos['x']
            y = pos['y']
            # if len(path)==2:
            #     defaultlineD.append(pos)
            defaultlineD.append(pos)

            partDposcopy.remove(pos)

    print('default line A', defaultlineA)
    print('default line B', defaultlineB)
    print('default line C', defaultlineC)
    print('default line D', defaultlineD)
    global defaultlineAcopy, defaultlineBcopy, defaultlineCcopy, defaultlineDcopy
    defaultlineAcopy = copy.deepcopy(defaultlineA)
    defaultlineBcopy = copy.deepcopy(defaultlineB)
    defaultlineCcopy = copy.deepcopy(defaultlineC)
    defaultlineDcopy = copy.deepcopy(defaultlineD)


def get_nearestPosition(start, posset):
    dismin = 100

    if posset is None:
        return None
    # print()
    for pos in posset:

        distemp = stepdistance(start, pos)
        if distemp < dismin:
            dismin = distemp
            minpos = pos
    print('返回的最近的距离', dismin)
    print('返回的最近的位置', minpos)
    return minpos


def boundary_get():
    global mapfeature
    global tunnels
    global meteors
    global maptype
    global map_width
    global map_height
    global PointPrority
    global fieldlimitfactor
    global path
    fieldlimitfactor = 3
    ##如果我们需要boundary
    # 首先要判断所有的player都是不是在内部
    x = []
    y = []
    # 这个地方用于判断我的所有的player中是否有已经在内部的
    for tunnel in (tunnels):
        # print(tunnel)
        x.append(tunnel['x'])
        y.append(tunnel['y'])

    xmax = max(x)
    xmin = min(x)
    ymax = max(y)
    ymin = min(y)

    xmax = 14
    xmin = 4
    ymax = 14
    ymin = 4

    # #我们这个时候要判断是否需要使用虫洞吗？？？
    startx = 1
    starty = 0

    endx = 0
    endy = 1
    start = mapfeature[startx][starty]
    end = mapfeature[endx][endy]
    path = getpath(start, end)
    # path=getpath(start,end)
    # get_actionfrompathold()
    # ac=get_actionfrompath()
    if flag_getsolution:
        print('我们找到了到内部的情况哦哦哦')
        #
        print('实际路径')
        for pa in path:
            print('走的坐标，x:', pa.x, '  y:', pa.y)
        maptype = 2
    else:
        print('我们真的找不到到内部的情况啊')
        maptype = 1

    # mapshow(mapfeature)
    maptype = 2
    start = mapfeature[startx][starty]
    end = mapfeature[endx][endy]
    path = []
    if start.tunnel == 'no' and not start.wall and end.tunnel == 'no' and not end.wall and mapfeature[19][
        0].wormhole and mapfeature[0][19].wormhole:
        path = getpathmapdecide(start, end)
        # path=getpath(start,end)
        # get_actionfrompathold()
        # ac=get_actionfrompath()
        if flag_getsolution:
            print('我们找到了到内部的情况哦哦哦')
            #
            # print('实际路径')
            # for pa in path1:
            #     print('走的坐标，x:',pa.x,'  y:', pa.y)
            maptype = 2
        else:
            print('我们真的找不到到内部的情况啊')
            maptype = 1
    # maptype = 2
    # maptype=2
    # 如果石头或者tunnel处于很多的状态，我们设定我们吃敌人优先，否则我们设定吃豆子优先
    barriaer = len(meteors)
    if barriaer <= 0.15 * map_width * map_height:
        print('吃豆子优先')
        PointPrority = True
    else:
        print('进攻优先')

        PointPrority = False

    # PointPrority = False

    # 如果我们发现中间是进不去的时候怎么办，我们实际上，就应当记录下来powerset的位置

    return [xmin, ymin, xmax, ymax], maptype


global tunnelsneighbours
tunnelsneighbours = []


def addneighboursnewupdate(a):
    global map_height
    global map_width

    # print('我的坐标x:' + str(a.x) + '  y:' + str(a.y))

    i = 0
    if a.x > 0:
        # print('找左邻居')
        if mapfeature[a.x - 1][a.y].tunnel == 'no':
            if mapfeature[a.x - 1][a.y].wormhole == True:
                # a.neighbours.append(mapfeature[a.x-1][a.y])
                c = findwormpair(x=a.x - 1, y=a.y)  # 将当前是wormhole的坐标传入下去

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
                if c not in tunnelsneighbours:
                    tunnelsneighbours.append(c)
                a.neighbours.append(c)
    if a.x < map_width - 1:
        # print('找右邻居')
        if mapfeature[a.x + 1][a.y].tunnel == 'no':
            if mapfeature[a.x + 1][a.y].wormhole == True:
                # a.neighbours.append(mapfeature[a.x + 1][a.y])
                c = findwormpair(x=a.x + 1, y=a.y)  # 将当前是wormhole的坐标传入下去

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
                if c not in tunnelsneighbours:
                    tunnelsneighbours.append(c)
                a.neighbours.append(c)
    if a.y > 0:
        # print('找上邻居')

        if mapfeature[a.x][a.y - 1].tunnel == 'no':
            if mapfeature[a.x][a.y - 1].wormhole == True:
                # a.neighbours.append(mapfeature[a.x][a.y - 1])
                c = findwormpair(x=a.x, y=a.y - 1)  # 将当前是wormhole的坐标传入下去

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
                if c not in tunnelsneighbours:
                    tunnelsneighbours.append(c)

                a.neighbours.append(c)
    if a.y < map_height - 1:
        # print('找下邻居')
        if mapfeature[a.x][a.y + 1].tunnel == 'no':
            if mapfeature[a.x][a.y + 1].wormhole == True:
                # a.neighbours.append(mapfeature[a.x][a.y + 1])
                c = findwormpair(x=a.x, y=a.y + 1)  # 将当前是wormhole的坐标传入下去

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
                if c not in tunnelsneighbours:
                    tunnelsneighbours.append(c)

                a.neighbours.append(c)


def findwormpair(x, y):
    global wormholes

    # print('开始找对应的wormhole了')
    for wormhole in wormholes:
        if wormhole['x'] == x and wormhole['y'] == y:
            name = wormhole['name']

    # print('打印之前的名字。name   ',name)
    if name.isupper():

        name = name.lower()
        # print('打印变成小写后的的name   ', name)
        for wormhole in wormholes:
            if wormhole['name'] == name:
                # print('打印找到返回的wormhole',wormhole)
                return wormhole
    else:
        name = name.upper()
        # print('打印变成大写后的字母  ， ', name)
        for wormhole in wormholes:
            if wormhole['name'] == name:
                # print('打印返回的wormhole，' ,wormhole)
                return wormhole


def addneighboursnew(a):
    global map_height
    global map_width

    print('我的坐标x:' + str(a.x) + '  y:' + str(a.y))

    i = 0
    if a.x > 0:
        print('找左邻居')
        if mapfeature[a.x - 1][a.y].tunnel == 'no':
            a.neighbours.append(mapfeature[a.x - 1][a.y])
        else:
            c = findgoodneighbour(mapfeature[a.x - 1][a.y])
            if (c.x == a.x) and (c.y == a.y):
                print('me没有')
                pass
            else:

                a.neighbours.append(c)
    if a.x < map_width - 1:
        print('找右邻居')
        if mapfeature[a.x + 1][a.y].tunnel == 'no':
            a.neighbours.append(mapfeature[a.x + 1][a.y])
        else:
            c = findgoodneighbour(mapfeature[a.x + 1][a.y])
            if (c.x == a.x) and (c.y == a.y):
                print('me没有')
                pass
            else:

                a.neighbours.append(c)
    if a.y > 0:
        print('找上邻居')

        if mapfeature[a.x][a.y - 1].tunnel == 'no':

            a.neighbours.append(mapfeature[a.x][a.y - 1])
        else:
            c = findgoodneighbour(mapfeature[a.x][a.y - 1])
            if (c.x == a.x) and (c.y == a.y):
                print('me没有')
                pass
            else:

                a.neighbours.append(c)
    if a.y < map_height - 1:
        print('找下邻居')
        if mapfeature[a.x][a.y + 1].tunnel == 'no':

            a.neighbours.append(mapfeature[a.x][a.y + 1])
        else:
            c = findgoodneighbour(mapfeature[a.x][a.y + 1])
            if (c.x == a.x) and (c.y == a.y):
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

    if a.x < map_width - 1:
        a.neighbours.append(mapfeature[a.x + 1][a.y])

    if a.y > 0:
        a.neighbours.append(mapfeature[a.x][a.y - 1])

    if a.y < map_height - 1:
        a.neighbours.append(mapfeature[a.x][a.y + 1])


# findgoodneighbour()是仅仅对tunnel一个方向的邻居进行了规划
# 即→↑这种连续的没有进行计算
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
        return mapfeature[b.x + i][b.y]


# findgoodneighbourV1(oldb)是仅仅对tunnel一个方向的邻居进行了规划
# 采用递归的方式进行确定下一步的neighbours是谁
def findgoodneighbourV1(oldb):
    global mapfeature
    mapfeaturecopy = copy.deepcopy(mapfeature)
    goodneighbour = mapfeaturecopy[oldb.x][oldb.y]
    b = goodneighbour
    print('实际传过来的b的坐标的情况x' + str(b.x) + '  y:' + str(b.y))
    while b.tunnel != 'no':
        print('当前的b的位置', 'x  ', b.x, ' y   :', b.y)
        print('当前b的tunnel的情况', b.tunnel)
        print('当前b的tunnel的情况', b.tunnel)
        if mapfeaturecopy[b.x][b.y].tunnel == 'up':
            i = 0
            while mapfeaturecopy[b.x][b.y - i].tunnel == 'up':
                # print('实际的i'+str(i))
                i = i + 1
                goodneighbour = mapfeaturecopy[b.x][b.y - i]
            print('实际的up邻居坐标x:' + str(b.x) + '  y:' + str(b.y - i))
            b = goodneighbour
            # return mapfeature[b.x][b.y-i]
        elif mapfeaturecopy[b.x][b.y].tunnel == 'down':
            i = 0
            while mapfeaturecopy[b.x][b.y + i].tunnel == 'down':
                # print('实际的i' + str(i))
                i = i + 1
                goodneighbour = mapfeaturecopy[b.x][b.y + i]
            print('实际的down邻居坐标x:' + str(b.x) + '  y:' + str(b.y + i))
            b = goodneighbour
        elif mapfeaturecopy[b.x][b.y].tunnel == 'left':
            i = 0
            while mapfeaturecopy[b.x - i][b.y].tunnel == 'left':
                print('实际的i' + str(i))
                i = i + 1
                goodneighbour = mapfeaturecopy[b.x - i][b.y]

            print('实际的left邻居坐标x:' + str(b.x - i) + '  y:' + str(b.y))
            b = goodneighbour
            # return mapfeature[b.x-i][b.y]
        elif mapfeaturecopy[b.x][b.y].tunnel == 'right':
            i = 0
            while mapfeaturecopy[b.x + i][b.y].tunnel == 'right':
                # print('实际的i' + str(i))
                i = i + 1
                goodneighbour = mapfeaturecopy[b.x + i][b.y]
            print('实际的right邻居坐标x:' + str(b.x + i) + '  y:' + str(b.y))
            b = goodneighbour

    return b


# findgoodneighbourV2(b)是仅仅对tunnel一个方向的邻居进行了规划
# 采用递归的方式进行确定下一步的neighbours是谁
def findgoodneighbourV2(b):
    # global mapfeature
    # mapfeaturecopy=copy.deepcopy(mapfeature)
    # goodneighbour=mapfeaturecopy[oldb.x][oldb.y]
    goodneighbour = b
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
            a = findgoodneighbourV2(goodneighbour)
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


# 这个函数的作用是将attackmode 切换成为防守模式的时候,还是会记录下敌人的位置.在最后有可能造成我们得到no solution的情况
# 这个函数的作用是将敌人本身的目标设定为空气了
def updateanamypositionattackmode():
    global mapfeature
    global oldanamyposition

    for i in range(len(oldanamyposition)):
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].anamy = False  # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].trueanamy = False  # 敌人的位置

        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].context = '0'  # 敌人的位置

    oldanamyposition = []


# 通过这个函数实现地方位置的判断
# 这个函数是为了实现敌人周围相邻的地方设定为anmy的性质
oldanamyposition = []


def updateanamyposition(anamyplayers):
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
        if anamyplayers[i]['x'] > 0 and not mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].wall and \
                mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].tunnel in 'no':
            mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].anamy = True  # 敌人的位置
            mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].context = 'D'  # 敌人的位置
            oldanamyposition.append({'x': anamyplayers[i]['x'] - 1, 'y': anamyplayers[i]['y']})

        if anamyplayers[i]['x'] < map_width - 1 and not mapfeature[anamyplayers[i]['x'] + 1][
            anamyplayers[i]['y']].wall and \
                mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].tunnel in 'no':
            mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].anamy = True  # 敌人的位置
            mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].context = 'D'  # 敌人的位置
            oldanamyposition.append({'x': anamyplayers[i]['x'] + 1, 'y': anamyplayers[i]['y']})

        if anamyplayers[i]['y'] > 0 and not mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].wall and \
                mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].tunnel in 'no':
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].anamy = True  # 敌人的位置
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].context = 'D'  # 敌人的位置
            oldanamyposition.append({'x': anamyplayers[i]['x'], 'y': anamyplayers[i]['y'] - 1})

        if anamyplayers[i]['y'] < map_height - 1 and not mapfeature[anamyplayers[i]['x']][
            anamyplayers[i]['y'] + 1].wall and \
                mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].tunnel in 'no':
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].anamy = True
            mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].context = 'D'  # 敌人的位置
            oldanamyposition.append({'x': anamyplayers[i]['x'], 'y': anamyplayers[i]['y'] + 1})


# 通过这个函数实现地方位置的判断
# 这个函数是为了更好的实现周围相邻敌人设置成anamy属性的情况。
# 如果经过了tunnel或者是经过了wormhole也会计算出来得到的
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

        # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].wall )
        # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].tunnel == 'no')
        if anamyplayers[i]['x'] > 0 and not mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].wall:
            # and \
            if mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']])
                if (a.x == anamyplayers[i]['x']) and (a.y == anamyplayers[i]['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})


            else:
                if mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].wormhole:
                    newworm = findwormpair(anamyplayers[i]['x'] - 1, anamyplayers[i]['y'])
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:
                    mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].anamy = True  # 敌人的位置
                    mapfeature[anamyplayers[i]['x'] - 1][anamyplayers[i]['y']].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayers[i]['x'] - 1, 'y': anamyplayers[i]['y']})

        if anamyplayers[i]['x'] < map_width - 1 and not mapfeature[anamyplayers[i]['x'] + 1][
            anamyplayers[i]['y']].wall:

            if mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']])
                if (a.x == anamyplayers[i]['x']) and (a.y == anamyplayers[i]['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].wormhole:
                    newworm = findwormpair(anamyplayers[i]['x'] + 1, anamyplayers[i]['y'])
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:

                    mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].anamy = True  # 敌人的位置
                    mapfeature[anamyplayers[i]['x'] + 1][anamyplayers[i]['y']].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayers[i]['x'] + 1, 'y': anamyplayers[i]['y']})

        if anamyplayers[i]['y'] > 0 and not mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].wall:
            if mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1])

                if (a.x == anamyplayers[i]['x']) and (a.y == anamyplayers[i]['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].wormhole:
                    newworm = findwormpair(anamyplayers[i]['x'], anamyplayers[i]['y'] - 1)
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].anamy = True  # 敌人的位置
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] - 1].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayers[i]['x'], 'y': anamyplayers[i]['y'] - 1})

        if anamyplayers[i]['y'] < map_height - 1 and not mapfeature[anamyplayers[i]['x']][
            anamyplayers[i]['y'] + 1].wall:
            if mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1])
                if (a.x == anamyplayers[i]['x']) and (a.y == anamyplayers[i]['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].wormhole:
                    newworm = findwormpair(anamyplayers[i]['x'], anamyplayers[i]['y'] + 1)
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].anamy = True  # 敌人的位置
                    mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y'] + 1].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayers[i]['x'], 'y': anamyplayers[i]['y'] + 1})

    pass


# 通过这个函数实现地方位置的判断
# 这个函数是为了更好的实现周围相邻敌人设置成anamy属性的情况。
# 如果经过了tunnel或者是经过了wormhole也会计算出来得到的
def updateanamypositionUpgradehardV1a(anamyplayers, myplayers):
    global mapfeature
    global oldanamyposition
    global map_width
    global map_height

    for myplayer in myplayers:
        mapfeature[myplayer['x']][myplayer['y']].myplayer = True

    # print('我们正在更新敌人的位置')

    # print('old position的情况',oldanamyposition)

    for i in range(len(oldanamyposition)):
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].trueanamy = False  # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].anamy = False  # 敌人的位置
        mapfeature[oldanamyposition[i]['x']][oldanamyposition[i]['y']].context = '0'  # 敌人的位置

    oldanamyposition = []
    # print('anamyplayers情况', oldanamyposition)
    for anamyplayer in anamyplayers:
        # print('我们正在内部更新敌人的位置')
        # print('打印一下我方的teamid',constants.team_id)
        # if anamyplayers[i]['team']==constants.team_id:
        oldanamyposition.append({'x': anamyplayer['x'], 'y': anamyplayer['y']})
        mapfeature[anamyplayer['x']][anamyplayer['y']].anamy = True  # 敌人的位置
        mapfeature[anamyplayer['x']][anamyplayer['y']].trueanamy = True  # 敌人的位置
        mapfeature[anamyplayer['x']][anamyplayer['y']].context = 'TA'  # 敌人的位置

        # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].wall )
        # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].tunnel == 'no')
        if anamyplayer['x'] > 0 and not mapfeature[anamyplayer['x'] - 1][anamyplayer['y']].wall and not \
        mapfeature[anamyplayer['x'] - 1][anamyplayer['y']].myplayer:
            # and \
            if mapfeature[anamyplayer['x'] - 1][anamyplayer['y']].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[anamyplayer['x'] - 1][anamyplayer['y']])
                if (a.x == anamyplayer['x']) and (a.y == anamyplayer['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    if mapfeature[a.x][a.y].trueanamy:
                        pass
                    else:
                        mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})


            else:
                if mapfeature[anamyplayer['x'] - 1][anamyplayer['y']].wormhole:
                    newworm = findwormpair(anamyplayer['x'] - 1, anamyplayer['y'])
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    if mapfeature[newworm['x']][newworm['y']].trueanamy:
                        pass
                    else:
                        mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:
                    mapfeature[anamyplayer['x'] - 1][anamyplayer['y']].anamy = True  # 敌人的位置
                    if mapfeature[anamyplayer['x'] - 1][anamyplayer['y']].trueanamy:
                        pass
                    else:

                        mapfeature[anamyplayer['x'] - 1][anamyplayer['y']].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayer['x'] - 1, 'y': anamyplayer['y']})

                    updateanamypositionUpgradehardV1b(anamyplayer['x'] - 1, anamyplayer['y'])

        if anamyplayer['x'] < map_width - 1 and not mapfeature[anamyplayer['x'] + 1][anamyplayer['y']].wall and not \
        mapfeature[anamyplayer['x'] + 1][anamyplayer['y']].myplayer:

            if mapfeature[anamyplayer['x'] + 1][anamyplayer['y']].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[anamyplayer['x'] + 1][anamyplayer['y']])
                if (a.x == anamyplayer['x']) and (a.y == anamyplayer['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    if mapfeature[a.x][a.y].trueanamy:
                        pass
                    else:
                        mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[anamyplayer['x'] + 1][anamyplayer['y']].wormhole:
                    newworm = findwormpair(anamyplayer['x'] + 1, anamyplayer['y'])
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    if mapfeature[newworm['x']][newworm['y']].trueanamy:
                        pass
                    else:
                        mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:

                    mapfeature[anamyplayer['x'] + 1][anamyplayer['y']].anamy = True  # 敌人的位置
                    if mapfeature[anamyplayer['x'] + 1][anamyplayer['y']].trueanamy:
                        pass
                    else:
                        mapfeature[anamyplayer['x'] + 1][anamyplayer['y']].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayer['x'] + 1, 'y': anamyplayer['y']})
                    updateanamypositionUpgradehardV1b(anamyplayer['x'] + 1, anamyplayer['y'])

        if anamyplayer['y'] > 0 and not mapfeature[anamyplayer['x']][anamyplayer['y'] - 1].wall and not \
        mapfeature[anamyplayer['x']][anamyplayer['y'] - 1].myplayer:
            if mapfeature[anamyplayer['x']][anamyplayer['y'] - 1].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[anamyplayer['x']][anamyplayer['y'] - 1])

                if (a.x == anamyplayer['x']) and (a.y == anamyplayer['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    if mapfeature[a.x][a.y].trueanamy:
                        pass
                    else:
                        mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[anamyplayer['x']][anamyplayer['y'] - 1].wormhole:
                    newworm = findwormpair(anamyplayer['x'], anamyplayer['y'] - 1)
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    if mapfeature[newworm['x']][newworm['y']].trueanamy:
                        pass
                    else:
                        mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:
                    mapfeature[anamyplayer['x']][anamyplayer['y'] - 1].anamy = True  # 敌人的位置
                    if mapfeature[anamyplayer['x']][anamyplayer['y'] - 1].trueanamy:
                        pass
                    else:
                        mapfeature[anamyplayer['x']][anamyplayer['y'] - 1].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayer['x'], 'y': anamyplayer['y'] - 1})
                    updateanamypositionUpgradehardV1b(anamyplayer['x'], anamyplayer['y'] - 1)

        if anamyplayer['y'] < map_height - 1 and not mapfeature[anamyplayer['x']][anamyplayer['y'] + 1].wall and not \
        mapfeature[anamyplayer['x']][anamyplayer['y'] + 1].myplayer:
            if mapfeature[anamyplayer['x']][anamyplayer['y'] + 1].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[anamyplayer['x']][anamyplayer['y'] + 1])
                if (a.x == anamyplayer['x']) and (a.y == anamyplayer['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                    if mapfeature[a.x][a.y].trueanamy:
                        pass
                    else:
                        mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[anamyplayer['x']][anamyplayer['y'] + 1].wormhole:
                    newworm = findwormpair(anamyplayer['x'], anamyplayer['y'] + 1)
                    mapfeature[newworm['x']][newworm['y']].anamy = True
                    if mapfeature[newworm['x']][newworm['y']].trueanamy:
                        pass
                    else:
                        mapfeature[newworm['x']][newworm['y']].context = 'A'
                    oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:
                    mapfeature[anamyplayer['x']][anamyplayer['y'] + 1].anamy = True  # 敌人的位置
                    if mapfeature[anamyplayer['x']][anamyplayer['y'] + 1].trueanamy:
                        pass
                    else:
                        mapfeature[anamyplayer['x']][anamyplayer['y'] + 1].context = 'A'  # 敌人的位置
                    oldanamyposition.append({'x': anamyplayer['x'], 'y': anamyplayer['y'] + 1})
                    updateanamypositionUpgradehardV1b(anamyplayer['x'], anamyplayer['y'] + 1)

    for myplayer in myplayers:
        mapfeature[myplayer['x']][myplayer['y']].myplayer = False

    pass

    # mapshow(mapfeature)
    pass


def updateanamypositionUpgradehardV1b(x, y):
    global mapfeature
    global oldanamyposition
    global map_width
    global map_height

    # x=anamyplayer['x']
    # y=anamyplayer['y']
    # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].wall )
    # print(mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].tunnel == 'no')
    if x > 0 and not mapfeature[x - 1][y].wall:
        if mapfeature[x - 1][y].tunnel != 'no':
            a = findgoodneighbour(mapfeature[x - 1][y])
            if (a.x == x) and (a.y == y):
                pass
            else:
                mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                if mapfeature[a.x][a.y].trueanamy:
                    pass
                else:
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x': a.x, 'y': a.y})


        else:
            if mapfeature[x - 1][y].wormhole:
                newworm = findwormpair(x - 1, y)
                mapfeature[newworm['x']][newworm['y']].anamy = True
                if mapfeature[newworm['x']][newworm['y']].trueanamy:
                    pass
                else:
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

            else:
                mapfeature[x - 1][y].anamy = True  # 敌人的位置
                if mapfeature[x - 1][y].trueanamy:
                    pass
                else:
                    mapfeature[x - 1][y].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x': x - 1, 'y': y})

    if x < map_width - 1 and not mapfeature[x + 1][y].wall:

        if mapfeature[x + 1][y].tunnel not in 'no':
            a = findgoodneighbour(mapfeature[x + 1][y])
            if (a.x == x) and (a.y == y):

                pass
            else:
                mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                if mapfeature[a.x][a.y].trueanamy:
                    pass
                else:
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x': a.x, 'y': a.y})

        else:
            if mapfeature[x][y].wormhole:
                newworm = findwormpair(x + 1, y)
                mapfeature[newworm['x']][newworm['y']].anamy = True
                if mapfeature[newworm['x']][newworm['y']].trueanamy:
                    pass
                else:
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

            else:

                mapfeature[x + 1][y].anamy = True  # 敌人的位置
                if mapfeature[x + 1][y].trueanamy:
                    pass
                else:
                    mapfeature[x + 1][y].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x': x + 1, 'y': y})

    if y > 0 and not mapfeature[x][y - 1].wall:
        if mapfeature[x][y - 1].tunnel not in 'no':
            a = findgoodneighbour(mapfeature[x][y - 1])

            if (a.x == x) and (a.y == y):

                pass
            else:
                mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                if mapfeature[a.x][a.y].trueanamy:
                    pass
                else:
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x': a.x, 'y': a.y})

        else:
            if mapfeature[x][y - 1].wormhole:
                newworm = findwormpair(x, y - 1)
                mapfeature[newworm['x']][newworm['y']].anamy = True
                if mapfeature[newworm['x']][newworm['y']].trueanamy:
                    pass
                else:
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

            else:
                mapfeature[x][y - 1].anamy = True  # 敌人的位置
                if mapfeature[x][y - 1].trueanamy:
                    pass
                else:
                    mapfeature[x][y - 1].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x': x, 'y': y - 1})

    if y < map_height - 1 and not mapfeature[x][y + 1].wall:
        if mapfeature[x][y + 1].tunnel not in 'no':
            a = findgoodneighbour(mapfeature[x][y + 1])
            if (a.x == x) and (a.y == y):

                pass
            else:
                mapfeature[a.x][a.y].anamy = True  # 敌人的位置
                if mapfeature[a.x][a.y].trueanamy:
                    pass
                else:
                    mapfeature[a.x][a.y].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x': a.x, 'y': a.y})

        else:
            if mapfeature[x][y + 1].wormhole:
                newworm = findwormpair(x, y + 1)
                mapfeature[newworm['x']][newworm['y']].anamy = True
                if mapfeature[newworm['x']][newworm['y']].trueanamy:
                    pass
                else:
                    mapfeature[newworm['x']][newworm['y']].context = 'A'
                oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})
                oldanamyposition.append({'x': newworm['x'], 'y': newworm['y']})

            else:
                mapfeature[x][y + 1].anamy = True  # 敌人的位置
                if mapfeature[x][y + 1].trueanamy:
                    pass
                else:
                    mapfeature[x][y + 1].context = 'A'  # 敌人的位置
                oldanamyposition.append({'x': x, 'y': y + 1})

    pass


global oldmyplayersposition
oldmyplayersposition = []


def updatemyplayerspositionUpgrade(myplayers, anamyplayers):
    global mapfeature
    global oldmyplayersposition

    global map_width
    global map_height

    # print('我们正在更新敌人的位置')
    for anamyplayer in anamyplayers:
        mapfeature[anamyplayer['x']][anamyplayer['y']].trueanamyplayer = True

    for i in range(len(oldmyplayersposition)):
        mapfeature[oldmyplayersposition[i]['x']][oldmyplayersposition[i]['y']].truemyplayer = False  # 敌人的位置
        mapfeature[oldmyplayersposition[i]['x']][oldmyplayersposition[i]['y']].myplayer = False  # 敌人的位置
        mapfeature[oldmyplayersposition[i]['x']][oldmyplayersposition[i]['y']].context = '0'  # 敌人的位置

    oldmyplayersposition = []

    # print('打印一下当前我的player是多少',myplayers)
    for myplayer in myplayers:
        print('打印一下当前我的player是哪个', myplayer)

        oldmyplayersposition.append({'x': myplayer['x'], 'y': myplayer['y']})
        mapfeature[myplayer['x']][myplayer['y']].truemyplayer = True  # 敌人的位置
        mapfeature[myplayer['x']][myplayer['y']].myplayer = True  # 敌人的位置
        mapfeature[myplayer['x']][myplayer['y']].context = 'TM'  # 敌人的位置

        if myplayer['x'] > 0 and not mapfeature[myplayer['x'] - 1][myplayer['y']].wall and not \
                mapfeature[myplayer['x'] - 1][myplayer['y']].trueanamyplayer:
            # and \
            if mapfeature[myplayer['x'] - 1][myplayer['y']].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[myplayer['x'] - 1][myplayer['y']])
                if (a.x == myplayer['x']) and (a.y == myplayer['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].myplayer = True  # 敌人的位置
                    if mapfeature[a.x][a.y].truemyplayer:
                        pass
                    else:
                        mapfeature[a.x][a.y].context = 'M'  # 敌人的位置
                    oldmyplayersposition.append({'x': a.x, 'y': a.y})


            else:
                if mapfeature[myplayer['x'] - 1][myplayer['y']].wormhole:
                    newworm = findwormpair(myplayer['x'] - 1, myplayer['y'])
                    mapfeature[newworm['x']][newworm['y']].myplayer = True
                    if mapfeature[newworm['x']][newworm['y']].truemyplayer:
                        pass
                    else:
                        mapfeature[newworm['x']][newworm['y']].context = 'M'
                    oldmyplayersposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:
                    mapfeature[myplayer['x'] - 1][myplayer['y']].myplayer = True  # 敌人的位置
                    if mapfeature[myplayer['x'] - 1][myplayer['y']].truemyplayer:
                        pass
                    else:

                        mapfeature[myplayer['x'] - 1][myplayer['y']].context = 'M'  # 敌人的位置
                    oldmyplayersposition.append({'x': myplayer['x'] - 1, 'y': myplayer['y']})

                    # updateanamypositionUpgradehardV1b(myplayer['x'] - 1, myplayer['y'])

        if myplayer['x'] < map_width - 1 and not mapfeature[myplayer['x'] + 1][myplayer['y']].wall and not \
                mapfeature[myplayer['x'] + 1][myplayer['y']].trueanamyplayer:

            if mapfeature[myplayer['x'] + 1][myplayer['y']].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[myplayer['x'] + 1][myplayer['y']])
                if (a.x == myplayer['x']) and (a.y == myplayer['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].myplayer = True  # 敌人的位置
                    if mapfeature[a.x][a.y].truemyplayer:
                        pass
                    else:
                        mapfeature[a.x][a.y].context = 'M'  # 敌人的位置
                    oldmyplayersposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[myplayer['x'] + 1][myplayer['y']].wormhole:
                    newworm = findwormpair(myplayer['x'] + 1, myplayer['y'])
                    mapfeature[newworm['x']][newworm['y']].myplayer = True
                    if mapfeature[newworm['x']][newworm['y']].truemyplayer:
                        pass
                    else:
                        mapfeature[newworm['x']][newworm['y']].context = 'M'
                    oldmyplayersposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:

                    mapfeature[myplayer['x'] + 1][myplayer['y']].myplayer = True  # 敌人的位置
                    if mapfeature[myplayer['x'] + 1][myplayer['y']].truemyplayer:
                        pass
                    else:
                        mapfeature[myplayer['x'] + 1][myplayer['y']].context = 'M'  # 敌人的位置
                    oldmyplayersposition.append({'x': myplayer['x'] + 1, 'y': myplayer['y']})
                    # updateanamypositionUpgradehardV1b(myplayer['x'] + 1, myplayer['y'])

        if myplayer['y'] > 0 and not mapfeature[myplayer['x']][myplayer['y'] - 1].wall and not \
                mapfeature[myplayer['x']][myplayer['y'] - 1].trueanamyplayer:
            if mapfeature[myplayer['x']][myplayer['y'] - 1].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[myplayer['x']][myplayer['y'] - 1])

                if (a.x == myplayer['x']) and (a.y == myplayer['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].myplayer = True  # 敌人的位置
                    if mapfeature[a.x][a.y].truemyplayer:
                        pass
                    else:
                        mapfeature[a.x][a.y].context = 'M'  # 敌人的位置
                    oldmyplayersposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[myplayer['x']][myplayer['y'] - 1].wormhole:
                    newworm = findwormpair(myplayer['x'], myplayer['y'] - 1)
                    mapfeature[newworm['x']][newworm['y']].myplayer = True
                    if mapfeature[newworm['x']][newworm['y']].truemyplayer:
                        pass
                    else:
                        mapfeature[newworm['x']][newworm['y']].context = 'M'
                    oldmyplayersposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:
                    mapfeature[myplayer['x']][myplayer['y'] - 1].myplayer = True  # 敌人的位置
                    if mapfeature[myplayer['x']][myplayer['y'] - 1].truemyplayer:
                        pass
                    else:
                        mapfeature[myplayer['x']][myplayer['y'] - 1].context = 'M'  # 敌人的位置
                    oldmyplayersposition.append({'x': myplayer['x'], 'y': myplayer['y'] - 1})
                    # updateanamypositionUpgradehardV1b(myplayer['x'], myplayer['y'] - 1)

        if myplayer['y'] < map_height - 1 and not mapfeature[myplayer['x']][myplayer['y'] + 1].wall and not \
                mapfeature[myplayer['x']][myplayer['y'] + 1].trueanamyplayer:
            if mapfeature[myplayer['x']][myplayer['y'] + 1].tunnel not in 'no':
                a = findgoodneighbour(mapfeature[myplayer['x']][myplayer['y'] + 1])
                if (a.x == myplayer['x']) and (a.y == myplayer['y']):

                    pass
                else:
                    mapfeature[a.x][a.y].myplayer = True  # 敌人的位置
                    if mapfeature[a.x][a.y].truemyplayer:
                        pass
                    else:
                        mapfeature[a.x][a.y].context = 'M'  # 敌人的位置
                    oldmyplayersposition.append({'x': a.x, 'y': a.y})

            else:
                if mapfeature[myplayer['x']][myplayer['y'] + 1].wormhole:
                    newworm = findwormpair(myplayer['x'], myplayer['y'] + 1)
                    mapfeature[newworm['x']][newworm['y']].myplayer = True
                    if mapfeature[newworm['x']][newworm['y']].truemyplayer:
                        pass
                    else:
                        mapfeature[newworm['x']][newworm['y']].context = 'M'
                    oldmyplayersposition.append({'x': newworm['x'], 'y': newworm['y']})

                else:
                    mapfeature[myplayer['x']][myplayer['y'] + 1].myplayer = True  # 敌人的位置
                    if mapfeature[myplayer['x']][myplayer['y'] + 1].truemyplayer:
                        pass
                    else:
                        mapfeature[myplayer['x']][myplayer['y'] + 1].context = 'M'  # 敌人的位置
                    oldmyplayersposition.append({'x': myplayer['x'], 'y': myplayer['y'] + 1})
                    # updateanamypositionUpgradehardV1b(anamyplayer['x'], anamyplayer['y'] + 1)


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
        oldanamyposition.append({'x': anamyplayers[i]['x'], 'y': anamyplayers[i]['y']})
        mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].trueanamy = True  # 敌人的位置
        mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].anamy = True  # 敌人的位置
        mapfeature[anamyplayers[i]['x']][anamyplayers[i]['y']].context = 'TA'  # 敌人的位置


# 这个函数是将新看到pwoer加入powersetall 当中，并且根据player当前的位置，进行更新是否已经有player已经被吃掉了 什么的
# 用来更新得到的powerset 分成powersetin 和  powersetout   或者分成powerseta b c d  这样以便更加均衡的吃豆子

def update_powerset(myplayers, anamyplayers):
    global powersetout
    global powersetin
    global powersetround
    global powersetall

    # 当前的的最大的范围是x 5 - 14  y  5 -14

    for power in powersetround:
        if power['x'] >= boundary[0] and power['x'] <= boundary[2] and power['y'] >= boundary[1] and power['y'] <= \
                boundary[3]:
            if power in powersetin:

                pass
            else:
                # powersetall.append(powersetround[i])
                powersetin.append(power)
        else:
            if power in powersetout:
                pass
            else:
                # powersetall.append(powersetround[i])
                powersetout.append(power)
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

            for power in (powersetin):
                if anamyplayers[i]['x'] == power['x'] and anamyplayers[i]['y'] == power['y']:
                    powersetin.remove(power)
                    # powersetall.remove(power)

        except:
            print('error in updatepowerset')
    powersetall = []
    powersetall.extend(powersetout)
    powersetall.extend(powersetin)
    # if len(powersetall)==0:
    #     pass
    #     print(powersetall)
    # else:
    powerset_positionrecord()
    # print('在updatepowerset中打印一下 powersetall ',powersetall)
    # print('在updatepowerset中打印一下 powersetin ',powersetin)
    # print('在updatepowerset中打印一下 powersetout ',powersetout)


# 这个函数的作用就是实现根据powersetall的情况将其分成每个player去吃powerA B　C　Ｄ
def dividepowerset(myplayers):
    global powersetall
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


# 这个函数是为了将我们的这些powerset 分成很多组---分别对应到我们各自player
def findnearestplayer(power, myplayers):
    playerbest = []

    dis = 10000000000000
    # print('在寻找距离最近的powerout的情况下，我们打印一下powerserout以便更好判断我们得到的是不是最好的')
    # print(powersetout)
    for player in myplayers:
        tempdis = abs(player['x'] - power['x']) + abs(player['y'] - power['y'])
        if tempdis < dis:
            dis = tempdis
            playerbest = player
    return playerbest


global powersetPos
powersetPos = []
global lengthofpowersetPos
lengthofpowersetPos = -1
global CangobestPos
CangobestPos = False


def powerset_positionrecord():
    global powersetout
    global powersetin
    global powersetround
    global powersetall
    global powersetPos
    global lengthofpowersetPos
    global bestPos1, bestPos2, bestPos3, bestPos4

    for power in powersetround:
        powerpos = [power['x'], power['y']]
        if powerpos not in powersetPos:
            powersetPos.append(powerpos)

    # print('我们看一下更新的powerset的实际的位置',powersetPos)
    # print('我们来看一下，实际的powerset的位置，总共有多少个？',len(powersetPos))

    # 使用一种聚类的算法找到最密集的区域，然后记录其中的一个位置，然后能过够开始吃豆子
    # 采用聚类算法--Kmeans， 这个地方不能采用= 号，因为后面随着中心点的变化 会变化的很大，所以，容易造成抖动，所以我们需要不能使用等号，
    # 为了避免同时宣导相同的点？？？？

    if len(powersetPos) >= 1:
        if len(powersetPos) > lengthofpowersetPos:

            lengthofpowersetPos = len(powersetPos)

            dataSet = np.array(powersetPos)
            # print(dataSet)
            # 执行keams 算法
            bestPos1, bestPos2, bestPos3, bestPos4 = kmeans.KMeans(dataSet, 4)
            CangobestPos = True
            # print('bestpos1', bestPos1)
            # print('bestpos2', bestPos2)
            # print('bestpos3', bestPos3)
            # print('bestpos4', bestPos4)
        elif len(powersetPos) == lengthofpowersetPos and random.random() < 0.01:

            dataSet = np.array(powersetPos)
            # print(dataSet)
            # 执行keams 算法
            bestPos1, bestPos2, bestPos3, bestPos4 = kmeans.KMeans(dataSet, 4)

            # print('bestpos1', bestPos1)
            # print('bestpos2', bestPos2)
            # print('bestpos3', bestPos3)
            # print('bestpos4', bestPos4)
    else:
        pass


# This function is to update  the actual position
# to the map
# 更新实际的powerset对应的map的位置的context
#
global oldpowerpositin
oldpowerposition = []


def updatepowersetposition():
    global powersetin
    global powersetout
    global mapfeature
    global playerworm
    global map_height
    global map_width
    global oldpowerposition

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

    y_o = -1
    c = '    '
    # for num in range(20):
    #     c  +=str(num)+' '
    print('  0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19  ')
    for y in range(map_height):
        y_o += 1
        b = str(y_o) + ' '
        for x in range(map_width):
            b += mapfeature[x][y].context + '   '
        print(b)


def update_playerABCD(myplayers):
    global playerworm
    global playerout
    global playerattackup
    global playerattackdown
    # 这个函数是用来判断player是否已经在tunnel内部了
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
            playerout = myplayerscopy[0]
            # print('溢出之后的copy    ', myplayerscopy)
            playerattackup = myplayerscopy[1]
            playerattackdown = myplayerscopy[2]
            # print('plaeyrattckup的情况    ', playerattackup)
    else:
        # 我们首先更新了playerworm的直实际的位置
        # 然后实际位置的情况下，再来判断这个player是否再tunnel内部
        myplayerscopy = copy.deepcopy(myplayers)
        # print('my actual copy:  ', myplayerscopy)

        if len(myplayers) == 4:
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
            print('myplayers    ', myplayers)
            print('myplayers copy', myplayerscopy)

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


def update_playerABCDV1(myplayers):
    global playerworm
    global playerout
    global playerattackup
    global playerattackdown
    global playerA, playerB, playerC, playerD
    # 这个函数是用来判断player是否已经在tunnel内部了
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

        # print('my actual copy:  ', myplayerscopy)
        if len(myplayers) == 4:
            for player in (myplayers):
                if player['id'] == playerworm['id']:
                    # 我们进行更新playerworm
                    playerworm = player
            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = myplayers[2]
            playerD = myplayers[3]

            # print('plaeyrattckup的情况    ', playerattackup)
    else:

        # print('my actual copy:  ', myplayerscopy)

        if len(myplayers) == 4:
            for player in (myplayers):
                if player['id'] == playerworm['id']:
                    # 我们进行更新playerworm
                    playerworm = player
                else:
                    playerout = player
            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = myplayers[2]
            playerD = myplayers[3]



        elif len(myplayers) == 3:
            for player in (myplayers):
                if player['id'] == playerworm['id']:
                    # 我们进行更新playerworm
                    playerworm = player

            if playerworm in myplayers:
                pass
            else:
                update_playerAandwormhole(myplayers)

                whetherplayerAin(xmin=boundary[0], ymin=boundary[1], xmax=boundary[2], ymax=boundary[3])
                for player in (myplayers):
                    if player['id'] == playerworm['id']:
                        # 我们进行更新playerworm
                        playerworm = player

            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = myplayers[2]
            playerD = None
            # playerattackdown = myplayerscopy[2]



        elif len(myplayers) == 2:
            for player in (myplayers):
                if player['id'] == playerworm['id']:
                    # 我们进行更新playerworm
                    playerworm = player

            if playerworm in myplayers:
                pass
            else:
                update_playerAandwormhole(myplayers)

                whetherplayerAin(xmin=boundary[0], ymin=boundary[1], xmax=boundary[2], ymax=boundary[3])
                for player in (myplayers):
                    if player['id'] == playerworm['id']:
                        # 我们进行更新playerworm
                        playerworm = player

            playerA = myplayers[0]
            playerB = myplayers[1]
            playerC = None
            playerD = None
        elif len(myplayers) == 1:
            playerA = myplayers[0]
            playerB = None
            playerC = None
            playerD = None

            # print('plaeyrattckup的情况    ', playerattackup)
        # 这个东西判断的前提是要更新playerworm
        whetherplayerAin(xmin=boundary[0], ymin=boundary[1], xmax=boundary[2], ymax=boundary[3])
        if not flag_playerinworm:  # and not flag_initialworm:  # 如果玩家A还没在洞中
            # 这个就是为了判断当前给的playworm是否进入到了wormhole当中去

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
flag_playerinworm = False


def whetherplayerAin(xmin, ymin, xmax, ymax):
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
        flag_playerinworm = False


# 计算wormwhole 和
def mindistancebetweenwormandplayer(player, worm):
    dis = abs(player['x'] - worm['x']) + abs(player['y'] - worm['y'])
    return dis


# we are in the tunnel已经进入了tunnel 内部
# 默认我们没有在tunnnel内部的情况
# 我们通过这个返回能够进入内部的wormwhole
global flag_findwormwholein
flag_findwormwholein = False


# 这个函数的作用是找到wormhole，
# 如果没有东西进去对的话就找到一个wormhole
def find_wormhole(xmin, ymin, xmax, ymax):
    global powerset
    global tunnels
    global wormholes
    global mapfeature
    global flagfindwormwholein
    global wormwholetarget
    wormholetemp = []
    wormwholetarget = []
    wormholescopy = copy.deepcopy(wormholes)

    for i in range(len(wormholes)):
        if wormholes[i]['x'] > xmin and wormholes[i]['x'] < xmax and wormholes[i]['y'] > ymin and wormholes[i][
            'y'] < ymax:
            wormholetemp.append(wormholes[i])

    for i in range(len(wormholetemp)):
        wormholes.remove(wormholetemp[i])

    wormwholetarget = wormholes
    wormholes = wormholescopy
    # print(wormhole)
    flagfindwormwholein = True
    return wormwholetarget


# this function is to tell it is a wormhole or not
def iswormhole(x, y):
    global wormholes

    for wormhole in wormholes:
        if wormhole['x'] == x and wormhole['y'] == y:
            return True

    return False


# 这个函数给定目标的坐标
def istunnelneighbour(startx, starty, endx, endy):
    # global tunnels
    global tunnelsneighbours
    # print('当前的tunnelneighbours',tunnelsneighbours)
    for tunnelsneighbour in tunnelsneighbours:
        if tunnelsneighbour.x == endx and tunnelsneighbour.y == endy and distancecalculate(startx, starty, endx,
                                                                                           endy) > 1:
            return True

    return False


def viatunnelnewaction(startx, starty, endx, endy):
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
                newendx = startx - 1
                newendy = starty
                return newendx, newendy

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
                newendx = startx + 1
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
                newendy = starty - 1
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
                newendy = starty + 1
                return newendx, newendy


# 吃豆子优先的情况
def get_poweractionmap2(playerX, powersetX, anamyplayers, myplayers):
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
    global flag_exploremapdone

    global Intera  # 惯性概念

    path = []
    if playerX == None:
        pass

    if len(powersetX) == 0:  # 如果已经空了 则根据模式，如果是攻击模式，则进行攻击。如果不是攻击模式，则尽量原远离自己的伙伴和墙壁，是否可以采用
        # 还需要再继续再进行修改
        # print('这个时候根本不会执行这个代码')
        # defaultposition=[]
        if Attack:  # 这个可以加入养猪计划
            # 这个敌方的函数是22-4 使用的版本，采用的是绝对位置的攻击敌人的方式，吃豆子，也是采用的有排序的方式，而且到最好就不排序了
            # return get_attackactionmap2(playerX=playerX,anamyplayers=anamyplayers,powersetX=powersetX)

            #     return get_poweractionmap2UpgradeV2(playerX=playerX, anamyplayers=anamyplayers, powersetX=powersetX)
            # 实时更短的计算敌人的聚类的
            return get_attackactionmap2Upgrade_parta(playerX=playerX, anamyplayers=anamyplayers, powersetX=powersetX,
                                                     myplayers=myplayers)
        else:
            # 这个时候我们也应该尝试着去走到默认的位置
            global centrolpartApos, centrolpartBpos, centrolpartCpos, centrolpartDpos
            if playerX == playerB:
                if flag_exploremapdone:
                    # print('得到的bestpos的结果',bestPos1)
                    try:

                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos1[0]][bestPos1[1]]

                        if start.x == end.x and start.y == end.y:
                            return random.randint(1, 4)
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return None
                    except:
                        return None
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerB:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerB:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerB:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerB:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return None
                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        try:

                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos1[0]][bestPos1[1]]

                            if start.x == end.x and start.y == end.y:
                                return random.randint(1, 4)
                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return None
                        except:
                            return None


            elif playerX == playerC:
                if flag_exploremapdone:
                    # print('得到的bestpos的结果',bestPos2)
                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos2[0]][bestPos2[1]]

                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return None
                    except:
                        return None
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerC:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerC:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerC:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerC:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return None

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        try:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos2[0]][bestPos2[1]]

                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return None
                        except:
                            return None

            elif playerX == playerD:
                # print('得到的bestpos的结果',bestPos3)
                if flag_exploremapdone:
                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos3[0]][bestPos3[1]]

                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return None
                    except:
                        return None
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerD:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerD:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerD:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerD:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return None

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:

                        ac = get_actionfrompath()
                        return ac
                    else:
                        try:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos3[0]][bestPos3[1]]

                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return None
                        except:
                            return None

            elif playerX == playerA:
                # print('得到的bestpos的结果',bestPos4)
                if flag_exploremapdone:
                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos3[0]][bestPos3[1]]

                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return None
                    except:
                        return None
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerA:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerA:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerA:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerA:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return None

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:

                        ac = get_actionfrompath()
                        return ac
                    else:
                        try:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos4[0]][bestPos4[1]]

                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return None
                        except:
                            return None

            return None

    else:
        # print('打印一下当前的powersetX',powersetX)
        powersettemp = findnearestpowerX(playerX, powersetX)  # 实际上，我们寻找power的方式要是基于power的才行
        # print(player)
        # print(powersettemp)
        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[powersettemp['x']][powersettemp['y']]

        path = getpath(start, end)
        # print('传回来的flaggetsolution是否有用呢', flag_getsolution)
        if flag_getsolution:

            ac = get_actionfrompath()
            return ac
        else:
            # print('吃豆子的情况下没有找到solution，不应该出现这种情况把')
            if Attack:

                ac = random.randint(1, 4)
                return ac
            else:

                return None


# 目前已经不使用attackactionmap2
def get_attackactionmap2(playerX, powersetX, anamyplayers):  # 最原始的攻击的版本
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
    path = []
    action = []
    if playerX is None:
        return None
    if len(anamyplayers) == 0:
        if len(
                powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
            # 在这种情况下我们进行敌人的搜素和寻找豆子
            defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
            # print('向四个角随机运动')

            if playerX == playerB:
                # print('得到的bestpos的结果',bestPos1)

                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[bestPos1[0]][bestPos1[1]]

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

            # 还是继续进行吃豆子
    else:
        # print('打印一下所有的敌人',anamyplayers)
        # 这种情况下就要指导有敌人的情况下，我们就要找出最好攻击哪个敌人
        anamytarget = findbestanamytarget(anamyplayers)
        # 定位选择吃哪个player

        attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2(anamytarget)

    if playerX == playerA and playerX is not None:

        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[attack_positionA['x']][attack_positionA['y']]

        path = getpath(start, end)
        if flag_getsolution:

            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            ac = random.randint(1, 4)
            return ac

    if playerX == playerB and playerX is not None:
        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[attack_positionB['x']][attack_positionB['y']]

        path = getpath(start, end)
        if flag_getsolution:

            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac

        pass
    if playerX == playerC and playerX is not None:
        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[attack_positionC['x']][attack_positionC['y']]

        path = getpath(start, end)
        if flag_getsolution:

            ac = get_actionfrompath()
            return ac
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

            # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')

            ac = random.randint(1, 4)
            return ac

    if playerX == playerD and playerX is not None:
        start = mapfeature[playerX['x']][playerX['y']]
        end = mapfeature[attack_positionD['x']][attack_positionD['y']]

        path = getpath(start, end)
        if flag_getsolution:

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
    # if pointbest>=20:
    #     return anamyttarget
    # else:
    #     return None


def findbestanamytargetNearthewall(anamyplayers):
    disbest = -1
    anamyttarget = []

    for anamyplayer in anamyplayers:
        x = anamyplayer['x'] - 10
        y = anamyplayer['y'] - 10
        distemp = x * x + y * y

        if distemp > disbest:
            disbest = distemp
            anamyttarget = anamyplayer
            # print('打印一下当前要追的敌人',anamyttarget)
    return anamyttarget


def findbestanamytargetV4(anamyplayers, myplayers):
    dismin = 1000
    distemp = 0
    for anamyplayer in anamyplayers:
        num, nextposes = get_anamynextmovepositionV3(anamyplayer)
        for myplayer in myplayers:

            for nextpos in nextposes:
                distemp = distemp + stepdistance(myplayer, nextpos)
        # 可以根据敌人所在棋盘的位置，然后得到相应的结果
        # absolutepos=anamyplayer
        if distemp < dismin:
            dismin = distemp
            minanamy = anamyplayer
    return minanamy


def get_poweractionmap2UpgradeV4(playerX, powersetX, anamyplayers, myplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1, bestPos2, bestPos3, bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global flag_get_Attackanamy
    global path
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    global attack_direc1, attack_direc2, basedirec
    global anamytarget
    global visionrange
    global attack_thresheoldfar
    global centrolpartApos, centrolpartBpos, centrolpartCpos, centrolpartDpos
    global defaultlineA, defaultlineB, defaultlineC, defaultlineD
    global defaultlineAcopy, defaultlineBcopy, defaultlineCcopy, defaultlineDcopy
    attack_thresheoldfar = 10
    attack_thresheoldnear = 1
    pre_aboutstep = -3

    if playerX is None:
        return None
    seeanamys = []
    # 来判断敌人是否在我当前的player的视野内
    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= playerX['x'] + visionrange and anamyplayer['x'] >= playerX['x'] - visionrange and \
                anamyplayer['y'] <= playerX['y'] + visionrange and anamyplayer['y'] >= playerX['y'] - visionrange:
            seeanamys.append(anamyplayer)

    path = []
    action = []
    if len(anamyplayers) == 0:
        return 1
        # 还是继续进行吃豆子
    else:
        # 我们来判断当前自己有多少个player，采用什么样的进攻的测策略
        if flag_get_Attackanamy:
            pass
        else:
            # 这个时候线采用敌人分数最多的
            # anamytarget = findbestanamytargetNearthewall(anamyplayers)#选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            anamytarget = findbestanamytargetV4(anamyplayers, myplayers)  # 选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数

            attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
            targetnearestplayer = get_nearestanamy_player(attack_positionOriginal)

            flag_get_Attackanamy = True
            # return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)
    direction = {1: 'up', 2: 'down', 3: 'left', 4: 'right', 5: 'up', 6: 'up', 7: 'right', 8: 'right'}

    actionAll = []
    myplayerscopy = copy.deepcopy(myplayers)

    # get_anamynextmovepositionV4(anamytarget)

    for pos in anamymakewallposition:
        mapfeature[pos['x']][pos['y']].attackwall = False
        mapfeature[pos['x']][pos['y']].context = '0'

    playerorg = getmyplayersordered(myplayerscopy, anamytarget)

    myplayerscopy.remove(playerorg)
    if True:
        print('我们进入了anamyplayer的情况')
        start = mapfeature[playerorg['x']][playerorg['y']]
        end = mapfeature[anamytarget['x']][anamytarget['y']]
        path = getpathnoattackwallnotruemyplayer(start, end)

        if flag_getsolution:
            attackmakepathwall(path, anamytarget)
            mapshow(mapfeature)

            ac = get_actionfrompath()
            actionAll.append({"team": playerorg['team'], "player_id": playerorg['id'],
                              "move": [direction[ac]]})
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
            print('目标是敌人的player应该不会没有路径走的吧')
            ac = random.randint(1, 4)
            actionAll.append({"team": playerorg['team'], "player_id": playerorg['id'],
                              "move": [direction[ac]]})
    playerorg = getmyplayersordered(myplayerscopy, anamytarget)

    myplayerscopy.remove(playerorg)
    if True:
        print('我们进入了anamyplayer的情况')
        start = mapfeature[playerorg['x']][playerorg['y']]
        end = mapfeature[anamytarget['x']][anamytarget['y']]
        path = getpathnoattackwallnotruemyplayer(start, end)

        if flag_getsolution:
            attackmakepathwall(path, anamytarget)

            ac = get_actionfrompath()
            actionAll.append({"team": playerorg['team'], "player_id": playerorg['id'],
                              "move": [direction[ac]]})
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
            print('目标是敌人的player应该不会没有路径走的吧')
            ac = random.randint(1, 4)
            actionAll.append({"team": playerorg['team'], "player_id": playerorg['id'],
                              "move": [direction[ac]]})
    playerorg = getmyplayersordered(myplayerscopy, anamytarget)

    myplayerscopy.remove(playerorg)
    if True:
        print('我们进入了anamyplayer的情况')
        start = mapfeature[playerorg['x']][playerorg['y']]
        end = mapfeature[anamytarget['x']][anamytarget['y']]
        path = getpathnoattackwallnotruemyplayer(start, end)

        if flag_getsolution:
            attackmakepathwall(path, anamytarget)

            ac = get_actionfrompath()
            actionAll.append({"team": playerorg['team'], "player_id": playerorg['id'],
                              "move": [direction[ac]]})
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
            print('目标是敌人的player应该不会没有路径走的吧')
            ac = random.randint(1, 4)
            actionAll.append({"team": playerorg['team'], "player_id": playerorg['id'],
                              "move": [direction[ac]]})

    playerorg = getmyplayersordered(myplayerscopy, anamytarget)

    myplayerscopy.remove(playerorg)
    if True:
        print('我们进入了anamyplayer的情况')
        start = mapfeature[playerorg['x']][playerorg['y']]
        end = mapfeature[anamytarget['x']][anamytarget['y']]
        path = getpathnoattackwallnotruemyplayer(start, end)

        if flag_getsolution:
            attackmakepathwall(path, anamytarget)

            ac = get_actionfrompath()
            actionAll.append({"team": playerorg['team'], "player_id": playerorg['id'],
                              "move": [direction[ac]]})
        else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
            print('目标是敌人的player应该不会没有路径走的吧')
            ac = random.randint(1, 4)
            actionAll.append({"team": playerorg['team'], "player_id": playerorg['id'],
                              "move": [direction[ac]]})

    return actionAll

    #
    # absolutepostion={'LU','RU','LD','RD'}
    # print('要攻击的敌人的位置x:',anamytarget['x'],'y:',anamytarget['y'])
    # for player in myplayers:
    #     seeanamys = []
    #     #来判断敌人是否在我当前的player的视野内
    #     for anamyplayer in anamyplayers:
    #         if anamyplayer['x'] <= player['x'] + visionrange and anamyplayer['x'] >= player['x'] - visionrange and \
    #                 anamyplayer['y'] <= player['y'] + visionrange and anamyplayer['y'] >= player['y'] - visionrange:
    #             seeanamys.append(anamyplayer)
    #     if anamytarget in seeanamys:
    #         print('敌人在视野内，保持压迫形状')
    #         print('absolutepostion',absolutepostion)
    #         absolutepos=getabsoluteposition(player,anamytarget,absolutepostion)
    #         end = getendpos(absolutepos,anamytarget)
    #         start = mapfeature[player['x']][player['y']]
    #         print('我的位置x:',start.x,'y:',start.y)
    #         print('期望位置x:',end.x,'y:',end.y)
    #         print('')
    #         path = getpath(start, end)
    #         if flag_getsolution:
    #             ac = get_actionfrompath()
    #
    #             actionAll.append({"team": player['team'], "player_id": player['id'],
    #                               "move": [direction[ac]]})
    #         else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
    #             print('目标是敌人的player应该不会没有路径走的吧')
    #             ac = random.randint(1, 4)
    #             actionAll.append({"team": player['team'], "player_id": player['id'],
    #                               "move": [direction[ac]]})
    #
    #     else:
    #         print('敌人不在视野内直接进攻敌人')
    #         #目标设定为某个位置去压迫
    #         start = mapfeature[player['x']][player['y']]
    #         end = mapfeature[anamytarget['x']][anamytarget['y']]
    #         path = getpathnoattackwallnotruemyplayer(start, end)
    #
    #         if flag_getsolution:
    #
    #             attackmakepathwall(path, anamytarget)
    #             mapshow(mapfeature)
    #
    #             ac = get_actionfrompath()
    #
    #             actionAll.append({"team": player['team'], "player_id": player['id'],
    #                               "move": [direction[ac]]})
    #         else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
    #             print('目标是敌人的player应该不会没有路径走的吧')
    #             ac = random.randint(1, 4)
    #             actionAll.append({"team": player['team'], "player_id": player['id'],
    #                               "move": [direction[ac]]})
    #
    # mapshow(mapfeature)
    # return actionAll
    # playerorg=getmyplayersordered(myplayerscopy,anamytarget)
    # myplayerscopy.remove(playerorg)
    #
    #
    #
    # player2= getmyplayersordered(myplayerscopy,anamytarget)
    #
    # myplayerscopy.remove(player2)
    # if True:
    #     print('我们进入了anamyplayer的情况')
    #     start = mapfeature[player2['x']][player2['y']]
    #     end = mapfeature[anamytarget['x']][anamytarget['y']]
    #     path = getpathnoattackwallnotruemyplayer(start, end)
    #
    #     if flag_getsolution:
    #         attackmakepathwall(path,anamytarget)
    #
    #         ac = get_actionfrompath()
    #         actionAll.append({"team": player2['team'], "player_id": player2['id'],
    #                           "move": [direction[ac]]})
    #     else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
    #         print('目标是敌人的player应该不会没有路径走的吧')
    #         ac = random.randint(1, 4)
    #         actionAll.append({"team": player2['team'], "player_id": player2['id'],
    #                           "move": [direction[ac]]})
    # player3= getmyplayersordered(myplayerscopy, anamytarget)
    #
    # myplayerscopy.remove(player3)
    # if True:
    #     print('我们进入了anamyplayer的情况')
    #     start = mapfeature[player3['x']][player3['y']]
    #     end = mapfeature[anamytarget['x']][anamytarget['y']]
    #     path = getpathnoattackwallnotruemyplayer(start, end)
    #
    #     if flag_getsolution:
    #         ac = get_actionfrompath()
    #         actionAll.append({"team": player3['team'], "player_id": player3['id'],
    #                           "move": [direction[ac]]})
    #     else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
    #         print('目标是敌人的player应该不会没有路径走的吧')
    #         ac = random.randint(1, 4)
    #         actionAll.append({"team": player3['team'], "player_id": player3['id'],
    #                           "move": [direction[ac]]})
    # player4 = getmyplayersordered(myplayerscopy, anamytarget)
    #
    # myplayerscopy.remove(player4)
    # if True:
    #     print('我们进入了anamyplayer的情况')
    #     start = mapfeature[player4['x']][player4['y']]
    #     end = mapfeature[anamytarget['x']][anamytarget['y']]
    #     path = getpathnoattackwallnotruemyplayer(start, end)
    #
    #     if flag_getsolution:
    #         ac = get_actionfrompath()
    #         actionAll.append({"team": player4['team'], "player_id": player4['id'],
    #                           "move": [direction[ac]]})
    #     else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
    #         print('目标是敌人的player应该不会没有路径走的吧')
    #         ac = random.randint(1, 4)
    #         actionAll.append({"team": player4['team'], "player_id": player4['id'],
    #                           "move": [direction[ac]]})
    #
    # return actionAll
    #
    #
    # path=[]
    # if playerX==playerA :
    #     #是不是距离敌人的原点最近
    #     if playerX==targetnearestplayer:
    #         start = mapfeature[playerX['x']][playerX['y']]
    #         end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
    #         # print('起始的位置')
    #         # print('x' + str(start.x) + 'y' + str(start.y))
    #         # print('终止的位置')
    #         # print('x' + str(end.x) + 'y' + str(end.y))
    #         path = getpath(start, end)
    #         if flag_getsolution:
    #             ac = get_actionfrompath()
    #             return ac
    #         else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
    #             ac = random.randint(1, 4)
    #             return ac
    #     else:
    #
    #         # playertemp=get_nearestanamy_player(attack_positionA)
    #         pos = get_nearestanamyposition(playerX)
    #
    #         disX=stepdistance(playerX,pos)
    #
    #         if disX > attack_thresheoldfar and len(powersetX)!=0:
    #             return get_poweractionmap2(playerX, powersetX, anamyplayers,myplayers)
    #         elif disX<=attack_thresheoldnear:
    #             start = mapfeature[playerX['x']][playerX['y']]
    #             end = mapfeature[pos['x']][pos['y']]
    #             # print('起始的位置')
    #             # print('x' + str(start.x) + 'y' + str(start.y))
    #             # print('终止的位置')
    #             # print('x' + str(end.x) + 'y' + str(end.y))
    #             if start.x==end.x and start.y == end.y:
    #                 return None
    #             path = getpath(start, end)
    #             if flag_getsolution:
    #
    #                 ac = get_actionfrompath()
    #                 return ac
    #             else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
    #                 ac = random.randint(1, 4)
    #             return ac
    #
    #         else:
    #
    #             if pos==attack_positionA:
    #                 for i in range(disX-pre_aboutstep):
    #
    #                     postemp=get_anamynextDirMovePosition(pos['x'],pos['y'],1)
    #                     if postemp is None:
    #                         break
    #                     else:
    #                         pos=postemp
    #             elif pos==attack_positionB:
    #                 for i in range(disX-pre_aboutstep):
    #
    #                     postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 2)
    #                     if postemp is None:
    #                         break
    #                     else:
    #                         pos = postemp
    #             elif pos==attack_positionC:
    #                 for i in range(disX-pre_aboutstep):
    #
    #                     postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 3)
    #                     if postemp is None:
    #                         break
    #                     else:
    #                         pos = postemp
    #             elif pos == attack_positionD:
    #                 for i in range(disX-pre_aboutstep):
    #
    #                     postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 4)
    #                     if postemp is None:
    #                         break
    #                     else:
    #                         pos = postemp
    #             start = mapfeature[playerX['x']][playerX['y']]
    #             end = mapfeature[pos['x']][pos['y']]
    #             # print('起始的位置')
    #             # print('x' + str(start.x) + 'y' + str(start.y))
    #             # print('终止的位置')
    #             # print('x' + str(end.x) + 'y' + str(end.y))
    #             if start.x==end.x and start.y == end.y:
    #                 return None
    #             path = getpath(start, end)
    #             if  flag_getsolution:
    #                 ac = get_actionfrompath()
    #                 return ac
    #             else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
    #
    #                 ac = random.randint(1, 4)
    #                 return ac


def get_poweractionmap2UpgradeV5(playerX, powersetX, anamyplayers, myplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1, bestPos2, bestPos3, bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global flag_get_Attackanamy
    global path
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    global attack_direc1, attack_direc2, basedirec
    global anamytarget
    global visionrange
    global attack_thresheoldfar
    global defaultlineA, defaultlineB, defaultlineC, defaultlineD
    global defaultlineAcopy, defaultlineBcopy, defaultlineCcopy, defaultlineDcopy
    global flag_playerA_done, flag_playerB_done, flag_playerC_done, flag_playerD_done

    attack_thresheoldfar = 10
    attack_thresheoldnear = 1
    pre_aboutstep = -3
    seeanamys = []
    if playerX is None:
        return None

    # 来判断敌人是否在我当前的player的视野内
    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= playerX['x'] + visionrange and anamyplayer['x'] >= playerX['x'] - visionrange and \
                anamyplayer['y'] <= playerX['y'] + visionrange and anamyplayer['y'] >= playerX['y'] - visionrange:
            seeanamys.append(anamyplayer)

    path = []
    action = []
    print('anamyplayers不是空的吧', anamyplayers)
    if len(anamyplayers) == 0:

        # flag_get_Attackanamy=False
        if len(
                powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
            # 在这种情况下我们进行敌人的搜素和寻找豆子

            if playerX == playerA:

                if flag_exploremapdone:
                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineAcopy:
                        if len(defaultlineAcopy) == 1:
                            defaultlineAcopy = copy.deepcopy(defaultlineA)
                        else:
                            defaultlineAcopy.remove(playerpos)

                        end = mapfeature[defaultlineAcopy[0]['x']][defaultlineAcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineAcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]

                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        print('routine walking2')

                        return ac
                    else:
                        return random.randint(1, 4)

                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerA:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerA:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerA:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerA:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        print('explore map')
                        ac = get_actionfrompath()
                        return ac
                    else:
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineAcopy:
                            if len(defaultlineAcopy) == 1:
                                defaultlineAcopy = copy.deepcopy(defaultlineA)
                            else:
                                defaultlineAcopy.remove(playerpos)

                            end = mapfeature[defaultlineAcopy[0]['x']][defaultlineAcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineAcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)

                # # print('向四个角随机运动')
            elif playerX == playerB:
                # print('得到的bestpos的结果',bestPos4)

                if flag_exploremapdone:
                    print('routine walking1')
                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineBcopy:
                        if len(defaultlineBcopy) == 1:
                            defaultlineBcopy = copy.deepcopy(defaultlineB)
                        else:
                            defaultlineBcopy.remove(playerpos)

                        end = mapfeature[defaultlineBcopy[0]['x']][defaultlineBcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineBcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        print('routine walking2')

                        return ac
                    else:
                        return random.randint(1, 4)

                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerB:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerB:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerB:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerB:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        print('explore map')

                        ac = get_actionfrompath()
                        return ac
                    else:
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineBcopy:
                            if len(defaultlineBcopy) == 1:
                                defaultlineBcopy = copy.deepcopy(defaultlineB)
                            else:
                                defaultlineBcopy.remove(playerpos)

                            end = mapfeature[defaultlineBcopy[0]['x']][defaultlineBcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineBcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)



            elif playerX == playerC:
                if flag_exploremapdone:
                    print('routine walking1')

                    # print('得到的bestpos的结果',bestPos2)
                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineCcopy:
                        if len(defaultlineCcopy) == 1:
                            defaultlineCcopy = copy.deepcopy(defaultlineC)
                        else:
                            defaultlineCcopy.remove(playerpos)

                        end = mapfeature[defaultlineCcopy[0]['x']][defaultlineCcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineCcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        print('routine walking2')

                        ac = get_actionfrompath()
                        return ac
                    else:
                        return random.randint(1, 4)
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerC:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerC:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerC:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerC:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)

                    if flag_getsolution:
                        print('explore map')

                        ac = get_actionfrompath()
                        return ac
                    else:

                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineCcopy:
                            if len(defaultlineCcopy) == 1:
                                defaultlineCcopy = copy.deepcopy(defaultlineC)
                            else:
                                defaultlineCcopy.remove(playerpos)

                            end = mapfeature[defaultlineCcopy[0]['x']][defaultlineCcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineCcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)

            elif playerX == playerD:
                # print('得到的bestpos的结果',bestPos3)

                if flag_exploremapdone:
                    print('routine walking1')

                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineDcopy:
                        if len(defaultlineDcopy) == 1:
                            defaultlineDcopy = copy.deepcopy(defaultlineD)
                        else:
                            defaultlineDcopy.remove(playerpos)

                        end = mapfeature[defaultlineDcopy[0]['x']][defaultlineDcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineDcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        print('routine walking2')

                        ac = get_actionfrompath()
                        return ac
                    else:
                        return random.randint(1, 4)
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerD:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerD:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerD:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerD:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        print('explore map')

                        ac = get_actionfrompath()

                        return ac
                    else:

                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineDcopy:
                            if len(defaultlineDcopy) == 1:
                                defaultlineDcopy = copy.deepcopy(defaultlineD)
                            else:
                                defaultlineDcopy.remove(playerpos)

                            end = mapfeature[defaultlineDcopy[0]['x']][defaultlineDcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineDcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)

        else:
            # 这个情况下 就要进行吃豆子
            return get_poweractionmap2(playerX, powersetX, anamyplayers, myplayers)
            # 还是继续进行吃豆子
    else:
        # 我们来判断当前自己有多少个player，采用什么样的进攻的测策略

        playernum = len(myplayers)
        if flag_get_Attackanamy:

            pass
        else:
            # 这个时候线采用敌人分数最多的
            # anamytarget = findbestanamytargetNearthewall(anamyplayers)#选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            # anamytarget = findbestanamytarget(anamyplayers)  # 选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            anamytarget = findbestanamytargetV4(anamyplayers, myplayers)  # 选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            # findbestanamytargetV4
            # 定位选择吃哪个player
            print('准备吃哪个anamytargetplayer', anamytarget)

            # attack_direc1, attack_direc2, basedirec = get_attackdirectionV3(anamytarget)

            # attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal=get_anamynextmoveposition(anamytarget)
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(anamytarget)
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal = get_anamynextmoveposition(
            #     anamytarget)

            attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
            targetnearestplayer = get_nearestanamy_player(attack_positionOriginal)
            print('距离敌人最近的我的player', targetnearestplayer)

            flag_get_Attackanamy = True
            # return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)
    print('是哪个player', playerX)
    path = []
    thresold_attackwall = 3
    if playerX == playerA:
        print('对playerA进行的操作')
        flag_playerA_done = True
        if False:
            # #预测敌人周围可以走的路径
            # allposition=caulatepossibalmove(anamytarget)
            # allmyposition=get_myplayernextmoveposition(playerX)
            # getcloserposition(position)
            #

            pass
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置', allposi)
                        if len(allposi) == 1:
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                            end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                            end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                            end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                            end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                        else:
                            print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                anamytarget)
                            if len(allposi) == 1:
                                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                                end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                                end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                                end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                                end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                            else:
                                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                                    anamytarget)

                                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                #     anamytarget)  # 希望找到的是敌人对角的位置
                                pos = get_nearestanamyposition(playerX)
                                end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置', allposi)
                if len(allposi) == 1:
                    end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                    end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                    end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                    end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                    end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        anamytarget)
                    if len(allposi) == 1:
                        end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                        end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                        end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                        end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                        end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                    else:
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                        pos = get_nearestanamyposition(playerX)
                        end = mapfeature[pos['x']][pos['y']]

                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac
    if playerX == playerB:
        print('对playerB进行的操作')
        flag_playerB_done = True
        if False:
            # #预测敌人周围可以走的路径
            # allposition=caulatepossibalmove(anamytarget)
            # allmyposition=get_myplayernextmoveposition(playerX)
            # getcloserposition(position)
            #

            pass
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置', allposi)
                        if len(allposi) == 1:
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                            end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                            end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                            end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                            end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                        else:
                            print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                anamytarget)
                            if len(allposi) == 1:
                                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                                end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                                end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                                end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                                end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                            else:
                                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                                    anamytarget)

                                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                #     anamytarget)  # 希望找到的是敌人对角的位置
                                pos = get_nearestanamyposition(playerX)
                                end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置', allposi)
                if len(allposi) == 1:
                    end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                    end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                    end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                    end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                    end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        anamytarget)
                    if len(allposi) == 1:
                        end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                        end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                        end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                        end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                        end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                    else:
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                        pos = get_nearestanamyposition(playerX)
                        end = mapfeature[pos['x']][pos['y']]

                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac
    if playerX == playerC:
        print('对playerC进行的操作')
        flag_playerC_done = True
        if False:
            # #预测敌人周围可以走的路径
            # allposition=caulatepossibalmove(anamytarget)
            # allmyposition=get_myplayernextmoveposition(playerX)
            # getcloserposition(position)
            #

            pass
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置', allposi)
                        if len(allposi) == 1:
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                            end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                            end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                            end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                            end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                        else:
                            print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                anamytarget)
                            if len(allposi) == 1:
                                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                                end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                                end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                                end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                                end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                            else:
                                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                                    anamytarget)

                                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                #     anamytarget)  # 希望找到的是敌人对角的位置
                                pos = get_nearestanamyposition(playerX)
                                end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置', allposi)
                if len(allposi) == 1:
                    end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                    end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                    end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                    end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                    end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        anamytarget)
                    if len(allposi) == 1:
                        end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                        end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                        end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                        end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                        end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                    else:
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                        pos = get_nearestanamyposition(playerX)
                        end = mapfeature[pos['x']][pos['y']]

                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac
    if playerX == playerD:
        print('对playerD进行的操作')
        flag_playerD_done = True
        if False:
            # #预测敌人周围可以走的路径
            # allposition=caulatepossibalmove(anamytarget)
            # allmyposition=get_myplayernextmoveposition(playerX)
            # getcloserposition(position)
            #

            pass
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置', allposi)
                        if len(allposi) == 1:
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                            end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                            end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                            end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                            end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                        else:
                            print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                anamytarget)
                            if len(allposi) == 1:
                                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                                end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                                end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                                end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                                end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                            else:
                                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                                    anamytarget)

                                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                #     anamytarget)  # 希望找到的是敌人对角的位置
                                pos = get_nearestanamyposition(playerX)
                                end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置', allposi)
                if len(allposi) == 1:
                    end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                    end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                    end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                    end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                    end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        anamytarget)
                    if len(allposi) == 1:
                        end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                        end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                        end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                        end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                        end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                    else:
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                        pos = get_nearestanamyposition(playerX)
                        end = mapfeature[pos['x']][pos['y']]

                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac


def get_poweractionmap2UpgradeV6(playerX, powersetX, anamyplayers, myplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1, bestPos2, bestPos3, bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global flag_get_Attackanamy
    global path
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    global attack_direc1, attack_direc2, basedirec
    global anamytarget
    global visionrange
    global attack_thresheoldfar
    global defaultlineA, defaultlineB, defaultlineC, defaultlineD
    global defaultlineAcopy, defaultlineBcopy, defaultlineCcopy, defaultlineDcopy
    global flag_playerA_done, flag_playerB_done, flag_playerC_done, flag_playerD_done

    attack_thresheoldfar = 10
    attack_thresheoldnear = 1
    pre_aboutstep = -3
    seeanamys = []
    if playerX is None:
        return None

    # 来判断敌人是否在我当前的player的视野内
    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= playerX['x'] + visionrange and anamyplayer['x'] >= playerX['x'] - visionrange and \
                anamyplayer['y'] <= playerX['y'] + visionrange and anamyplayer['y'] >= playerX['y'] - visionrange:
            seeanamys.append(anamyplayer)

    path = []
    action = []
    print('anamyplayers不是空的吧', anamyplayers)
    if len(anamyplayers) == 0:

        # flag_get_Attackanamy=False
        if len(
                powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
            # 在这种情况下我们进行敌人的搜素和寻找豆子

            if playerX == playerA:

                if flag_exploremapdone:
                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineAcopy:
                        if len(defaultlineAcopy) == 1:
                            defaultlineAcopy = copy.deepcopy(defaultlineA)
                        else:
                            defaultlineAcopy.remove(playerpos)

                        end = mapfeature[defaultlineAcopy[0]['x']][defaultlineAcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineAcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]

                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        print('routine walking2')

                        return ac
                    else:
                        return random.randint(1, 4)

                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerA:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerA:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerA:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerA:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        print('explore map')
                        ac = get_actionfrompath()
                        return ac
                    else:
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineAcopy:
                            if len(defaultlineAcopy) == 1:
                                defaultlineAcopy = copy.deepcopy(defaultlineA)
                            else:
                                defaultlineAcopy.remove(playerpos)

                            end = mapfeature[defaultlineAcopy[0]['x']][defaultlineAcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineAcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)

                # # print('向四个角随机运动')
            elif playerX == playerB:
                # print('得到的bestpos的结果',bestPos4)

                if flag_exploremapdone:
                    print('routine walking1')
                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineBcopy:
                        if len(defaultlineBcopy) == 1:
                            defaultlineBcopy = copy.deepcopy(defaultlineB)
                        else:
                            defaultlineBcopy.remove(playerpos)

                        end = mapfeature[defaultlineBcopy[0]['x']][defaultlineBcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineBcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        print('routine walking2')

                        return ac
                    else:
                        return random.randint(1, 4)

                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerB:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerB:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerB:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerB:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        print('explore map')

                        ac = get_actionfrompath()
                        return ac
                    else:
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineBcopy:
                            if len(defaultlineBcopy) == 1:
                                defaultlineBcopy = copy.deepcopy(defaultlineB)
                            else:
                                defaultlineBcopy.remove(playerpos)

                            end = mapfeature[defaultlineBcopy[0]['x']][defaultlineBcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineBcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)



            elif playerX == playerC:
                if flag_exploremapdone:
                    print('routine walking1')

                    # print('得到的bestpos的结果',bestPos2)
                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineCcopy:
                        if len(defaultlineCcopy) == 1:
                            defaultlineCcopy = copy.deepcopy(defaultlineC)
                        else:
                            defaultlineCcopy.remove(playerpos)

                        end = mapfeature[defaultlineCcopy[0]['x']][defaultlineCcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineCcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        print('routine walking2')

                        ac = get_actionfrompath()
                        return ac
                    else:
                        return random.randint(1, 4)
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerC:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerC:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerC:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerC:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)

                    if flag_getsolution:
                        print('explore map')

                        ac = get_actionfrompath()
                        return ac
                    else:

                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineCcopy:
                            if len(defaultlineCcopy) == 1:
                                defaultlineCcopy = copy.deepcopy(defaultlineC)
                            else:
                                defaultlineCcopy.remove(playerpos)

                            end = mapfeature[defaultlineCcopy[0]['x']][defaultlineCcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineCcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)

            elif playerX == playerD:
                # print('得到的bestpos的结果',bestPos3)

                if flag_exploremapdone:
                    print('routine walking1')

                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineDcopy:
                        if len(defaultlineDcopy) == 1:
                            defaultlineDcopy = copy.deepcopy(defaultlineD)
                        else:
                            defaultlineDcopy.remove(playerpos)

                        end = mapfeature[defaultlineDcopy[0]['x']][defaultlineDcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineDcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        print('routine walking2')

                        ac = get_actionfrompath()
                        return ac
                    else:
                        return random.randint(1, 4)
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerD:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerD:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerD:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerD:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        print('explore map')

                        ac = get_actionfrompath()

                        return ac
                    else:

                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineDcopy:
                            if len(defaultlineDcopy) == 1:
                                defaultlineDcopy = copy.deepcopy(defaultlineD)
                            else:
                                defaultlineDcopy.remove(playerpos)

                            end = mapfeature[defaultlineDcopy[0]['x']][defaultlineDcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineDcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)

        else:
            # 这个情况下 就要进行吃豆子
            return get_poweractionmap2(playerX, powersetX, anamyplayers, myplayers)
            # 还是继续进行吃豆子
    else:
        # 我们来判断当前自己有多少个player，采用什么样的进攻的测策略

        playernum = len(myplayers)
        if flag_get_Attackanamy:

            pass
        else:
            # 这个时候线采用敌人分数最多的
            # anamytarget = findbestanamytargetNearthewall(anamyplayers)#选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            anamytarget = findbestanamytarget(anamyplayers)  # 选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            # anamytarget = findbestanamytargetV4(anamyplayers,myplayers)  # 选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            # findbestanamytargetV4
            # 定位选择吃哪个player
            print('准备吃哪个anamytargetplayer', anamytarget)

            # attack_direc1, attack_direc2, basedirec = get_attackdirectionV3(anamytarget)

            # attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal=get_anamynextmoveposition(anamytarget)
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(anamytarget)
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal = get_anamynextmoveposition(
            #     anamytarget)

            attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
            targetnearestplayer = get_nearestanamy_player(attack_positionOriginal)
            print('距离敌人最近的我的player', targetnearestplayer)

            flag_get_Attackanamy = True
            # return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)
    print('是哪个player', playerX)
    path = []
    thresold_attackwall = 3
    if playerX == playerA:
        print('对playerA进行的操作')
        flag_playerA_done = True
        positioindex = 0
        if False:
            # #预测敌人周围可以走的路径
            # allposition=caulatepossibalmove(anamytarget)
            # allmyposition=get_myplayernextmoveposition(playerX)
            # getcloserposition(position)
            #

            pass
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)  # 这个地方需要注意nextmove 并没有返回敌人的目标的位置
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置1', allposi)

                        e = getmostsuitabletargetposition(myplayers, allposi)
                        if e is not None:

                            pos = e[positioindex]
                        else:
                            pos = attack_positionOriginal
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[pos['x']][pos['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            # start = mapfeature[playerX['x']][playerX['y']]
                            # end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            path = getpathnoattackwall(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)  # 这个时候我们认为就让他一个人去吃就好了
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置1', allposi)

                e = getmostsuitabletargetposition(myplayers, allposi)
                if e is not None:

                    pos = e[positioindex]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制11')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        anamytarget)
                    # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                    #     anamytarget)  # 希望找到的是敌人对角的位置
                    # print('所有的攻击的位置2', allposi)
                    e = getmostsuitabletargetposition(myplayers, allposi)
                    if e is not None:

                        pos = e[positioindex]
                    else:
                        pos = attack_positionOriginal
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                end = mapfeature[pos['x']][pos['y']]
                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnoanamyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnoattackwall(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac
    if playerX == playerB:
        print('对playerA进行的操作')
        flag_playerB_done = True
        positioindex = 1
        if False:
            # #预测敌人周围可以走的路径
            # allposition=caulatepossibalmove(anamytarget)
            # allmyposition=get_myplayernextmoveposition(playerX)
            # getcloserposition(position)
            #

            pass
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)  # 这个地方需要注意nextmove 并没有返回敌人的目标的位置
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置1', allposi)

                        e = getmostsuitabletargetposition(myplayers, allposi)
                        if e is not None:

                            pos = e[positioindex]
                        else:
                            pos = attack_positionOriginal
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[pos['x']][pos['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            # start = mapfeature[playerX['x']][playerX['y']]
                            # end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            path = getpathnoattackwall(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)  # 这个时候我们认为就让他一个人去吃就好了
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置1', allposi)

                e = getmostsuitabletargetposition(myplayers, allposi)
                if e is not None:

                    pos = e[positioindex]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制11')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        anamytarget)
                    # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                    #     anamytarget)  # 希望找到的是敌人对角的位置
                    # print('所有的攻击的位置2', allposi)
                    e = getmostsuitabletargetposition(myplayers, allposi)
                    if e is not None:

                        pos = e[positioindex]
                    else:
                        pos = attack_positionOriginal
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                end = mapfeature[pos['x']][pos['y']]
                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnoanamyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnoattackwall(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac
    if playerX == playerC:
        print('对playerC进行的操作')
        flag_playerC_done = True
        positioindex = 2
        if False:
            # #预测敌人周围可以走的路径
            # allposition=caulatepossibalmove(anamytarget)
            # allmyposition=get_myplayernextmoveposition(playerX)
            # getcloserposition(position)
            #

            pass
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)  # 这个地方需要注意nextmove 并没有返回敌人的目标的位置
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置1', allposi)

                        e = getmostsuitabletargetposition(myplayers, allposi)
                        if e is not None:

                            pos = e[positioindex]
                        else:
                            pos = attack_positionOriginal
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[pos['x']][pos['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            # start = mapfeature[playerX['x']][playerX['y']]
                            # end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            path = getpathnoattackwall(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)  # 这个时候我们认为就让他一个人去吃就好了
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置1', allposi)

                e = getmostsuitabletargetposition(myplayers, allposi)
                if e is not None:

                    pos = e[positioindex]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制11')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        anamytarget)
                    # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                    #     anamytarget)  # 希望找到的是敌人对角的位置
                    # print('所有的攻击的位置2', allposi)
                    e = getmostsuitabletargetposition(myplayers, allposi)
                    if e is not None:

                        pos = e[positioindex]
                    else:
                        pos = attack_positionOriginal
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                end = mapfeature[pos['x']][pos['y']]
                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnoanamyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnoattackwall(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac

    if playerX == playerD:
        print('对playerD进行的操作')
        flag_playerD_done = True
        positioindex = 0
        if False:
            # #预测敌人周围可以走的路径
            # allposition=caulatepossibalmove(anamytarget)
            # allmyposition=get_myplayernextmoveposition(playerX)
            # getcloserposition(position)
            #

            pass
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)  # 这个地方需要注意nextmove 并没有返回敌人的目标的位置
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置1', allposi)

                        e = getmostsuitabletargetposition(myplayers, allposi)
                        if e is not None:

                            pos = e[positioindex]
                        else:
                            pos = attack_positionOriginal
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[pos['x']][pos['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            # start = mapfeature[playerX['x']][playerX['y']]
                            # end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            path = getpathnoattackwall(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)  # 这个时候我们认为就让他一个人去吃就好了
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置1', allposi)

                e = getmostsuitabletargetposition(myplayers, allposi)
                if e is not None:

                    pos = e[positioindex]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制11')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        anamytarget)
                    # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                    #     anamytarget)  # 希望找到的是敌人对角的位置
                    # print('所有的攻击的位置2', allposi)
                    e = getmostsuitabletargetposition(myplayers, allposi)
                    if e is not None:

                        pos = e[positioindex]
                    else:
                        pos = attack_positionOriginal
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                end = mapfeature[pos['x']][pos['y']]
                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnoanamyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnoattackwall(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac


# 7是目前 5，6 的结合
def get_poweractionmap2UpgradeV7(playerX, powersetX, anamyplayers, myplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1, bestPos2, bestPos3, bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global flag_get_Attackanamy
    global path
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    global attack_direc1, attack_direc2, basedirec
    global anamytarget
    global visionrange
    global attack_thresheoldfar
    global defaultlineA, defaultlineB, defaultlineC, defaultlineD
    global defaultlineAcopy, defaultlineBcopy, defaultlineCcopy, defaultlineDcopy
    global flag_playerA_done, flag_playerB_done, flag_playerC_done, flag_playerD_done

    attack_thresheoldfar = 10
    attack_thresheoldnear = 1
    pre_aboutstep = -3
    seeanamys = []
    if playerX is None:
        return None

    # 来判断敌人是否在我当前的player的视野内
    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= playerX['x'] + visionrange and anamyplayer['x'] >= playerX['x'] - visionrange and \
                anamyplayer['y'] <= playerX['y'] + visionrange and anamyplayer['y'] >= playerX['y'] - visionrange:
            seeanamys.append(anamyplayer)

    path = []
    action = []
    print('anamyplayers不是空的吧', anamyplayers)
    if len(anamyplayers) == 0:

        # flag_get_Attackanamy=False
        if len(
                powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
            # 在这种情况下我们进行敌人的搜素和寻找豆子

            if playerX == playerA:

                if flag_exploremapdone:
                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineAcopy:
                        if len(defaultlineAcopy) == 1:
                            defaultlineAcopy = copy.deepcopy(defaultlineA)
                        else:
                            defaultlineAcopy.remove(playerpos)

                        end = mapfeature[defaultlineAcopy[0]['x']][defaultlineAcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineAcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]

                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        print('routine walking2')

                        return ac
                    else:
                        return random.randint(1, 4)

                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerA:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerA:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerA:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerA:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        print('explore map')
                        ac = get_actionfrompath()
                        return ac
                    else:
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineAcopy:
                            if len(defaultlineAcopy) == 1:
                                defaultlineAcopy = copy.deepcopy(defaultlineA)
                            else:
                                defaultlineAcopy.remove(playerpos)

                            end = mapfeature[defaultlineAcopy[0]['x']][defaultlineAcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineAcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)

                # # print('向四个角随机运动')
            elif playerX == playerB:
                # print('得到的bestpos的结果',bestPos4)

                if flag_exploremapdone:
                    print('routine walking1')
                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineBcopy:
                        if len(defaultlineBcopy) == 1:
                            defaultlineBcopy = copy.deepcopy(defaultlineB)
                        else:
                            defaultlineBcopy.remove(playerpos)

                        end = mapfeature[defaultlineBcopy[0]['x']][defaultlineBcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineBcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        print('routine walking2')

                        return ac
                    else:
                        return random.randint(1, 4)

                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerB:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerB:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerB:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerB:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        print('explore map')

                        ac = get_actionfrompath()
                        return ac
                    else:
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineBcopy:
                            if len(defaultlineBcopy) == 1:
                                defaultlineBcopy = copy.deepcopy(defaultlineB)
                            else:
                                defaultlineBcopy.remove(playerpos)

                            end = mapfeature[defaultlineBcopy[0]['x']][defaultlineBcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineBcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)



            elif playerX == playerC:
                if flag_exploremapdone:
                    print('routine walking1')

                    # print('得到的bestpos的结果',bestPos2)
                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineCcopy:
                        if len(defaultlineCcopy) == 1:
                            defaultlineCcopy = copy.deepcopy(defaultlineC)
                        else:
                            defaultlineCcopy.remove(playerpos)

                        end = mapfeature[defaultlineCcopy[0]['x']][defaultlineCcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineCcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        print('routine walking2')

                        ac = get_actionfrompath()
                        return ac
                    else:
                        return random.randint(1, 4)
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerC:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerC:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerC:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerC:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)

                    if flag_getsolution:
                        print('explore map')

                        ac = get_actionfrompath()
                        return ac
                    else:

                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineCcopy:
                            if len(defaultlineCcopy) == 1:
                                defaultlineCcopy = copy.deepcopy(defaultlineC)
                            else:
                                defaultlineCcopy.remove(playerpos)

                            end = mapfeature[defaultlineCcopy[0]['x']][defaultlineCcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineCcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)

            elif playerX == playerD:
                # print('得到的bestpos的结果',bestPos3)

                if flag_exploremapdone:
                    print('routine walking1')

                    playerpos = {'x': playerX['x'], 'y': playerX['y']}

                    if playerpos in defaultlineDcopy:
                        if len(defaultlineDcopy) == 1:
                            defaultlineDcopy = copy.deepcopy(defaultlineD)
                        else:
                            defaultlineDcopy.remove(playerpos)

                        end = mapfeature[defaultlineDcopy[0]['x']][defaultlineDcopy[0]['y']]

                    else:
                        pos = get_nearestPosition(playerpos, defaultlineDcopy)
                        end = mapfeature[pos['x']][pos['y']]

                    start = mapfeature[playerX['x']][playerX['y']]
                    print('起始的位置')
                    print('x' + str(start.x) + 'y' + str(start.y))
                    print('终止的位置')
                    print('x' + str(end.x) + 'y' + str(end.y))
                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        print('routine walking2')

                        ac = get_actionfrompath()
                        return ac
                    else:
                        return random.randint(1, 4)
                else:
                    if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerD:
                        end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerD:
                        end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                    elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerD:
                        end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                    elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerD:
                        end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                    else:
                        return random.randint(1, 4)

                    start = mapfeature[playerX['x']][playerX['y']]
                    path = getpath(start, end)
                    if flag_getsolution:
                        print('explore map')

                        ac = get_actionfrompath()

                        return ac
                    else:

                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineDcopy:
                            if len(defaultlineDcopy) == 1:
                                defaultlineDcopy = copy.deepcopy(defaultlineD)
                            else:
                                defaultlineDcopy.remove(playerpos)

                            end = mapfeature[defaultlineDcopy[0]['x']][defaultlineDcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineDcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)

        else:
            # 这个情况下 就要进行吃豆子
            return get_poweractionmap2(playerX, powersetX, anamyplayers, myplayers)
            # 还是继续进行吃豆子
    else:
        # 我们来判断当前自己有多少个player，采用什么样的进攻的测策略

        playernum = len(myplayers)
        if flag_get_Attackanamy:

            pass
        else:
            # 这个时候线采用敌人分数最多的
            # anamytarget = findbestanamytargetNearthewall(anamyplayers)#选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            # anamytarget = findbestanamytarget(anamyplayers)  # 选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            anamytarget = findbestanamytargetV4(anamyplayers, myplayers)  # 选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            # findbestanamytargetV4
            # 定位选择吃哪个player
            print('准备吃哪个anamytargetplayer', anamytarget)

            # attack_direc1, attack_direc2, basedirec = get_attackdirectionV3(anamytarget)

            # attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal=get_anamynextmoveposition(anamytarget)
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(anamytarget)
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal = get_anamynextmoveposition(
            #     anamytarget)

            attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
            targetnearestplayer = get_nearestanamy_player(attack_positionOriginal)
            print('距离敌人最近的我的player', targetnearestplayer)

            flag_get_Attackanamy = True
            # return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)
    print('是哪个player', playerX)
    path = []
    thresold_attackwall = 3
    if playerX == playerA:
        positioindex = 0
        print('对playerA进行的操作')
        flag_playerA_done = True
        if anamytarget in seeanamys:
            print('敌人在我的视野内,调用v6')
            return get_poweractionmap2UpgradeV6(playerX, powersetX, anamyplayers, myplayers)
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置', allposi)
                        if get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                            end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                            end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                            end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                            end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                        else:
                            print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                                anamytarget)
                            # if len(allposi) == 1:
                            #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            # el
                            if get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                                end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                                end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                                end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                                end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                            else:

                                pos = get_nearestanamyposition(playerX)
                                end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置', allposi)
                if get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                    end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                    end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                    end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                    end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        anamytarget)
                    # if len(allposi) == 1:
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    # el
                    if get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                        end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                        end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                        end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                        end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                    else:
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                        pos = get_nearestanamyposition(playerX)
                        end = mapfeature[pos['x']][pos['y']]

                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnoattackwall(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac
    if playerX == playerB:
        positioindex = 1
        print('对playerB进行的操作')
        flag_playerB_done = True
        if anamytarget in seeanamys:
            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                anamytarget)  # 希望找到的是敌人对角的位置
            print('所有的攻击的位置1', allposi)

            e = getmostsuitabletargetposition(myplayers, allposi)
            if e is not None:

                pos = e[positioindex]
            else:
                print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制11')
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                # print('所有的攻击的位置2', allposi)
                e = getmostsuitabletargetposition(myplayers, allposi)
                if e is not None:

                    pos = e[positioindex]
                else:
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        anamytarget)
                    e = getmostsuitabletargetposition(myplayers, allposi)
                    if e is not None:

                        pos = e[positioindex]
                    else:
                        pos = attack_positionOriginal
                    # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                    #     anamytarget)

            end = mapfeature[pos['x']][pos['y']]
            start = mapfeature[playerX['x']][playerX['y']]
            print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
            if start.x == end.x and start.y == end.y:
                return None
            path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
            if flag_getsolution:

                # return ac
                ac = get_actionfrompath()

                attackmakepathwallyapo(playerX, ac, anamytarget)

                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    ac = get_actionfrompath()
                    # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                    attackmakepathwallyapo(playerX, ac, anamytarget)
                    return ac
                else:
                    print('没有找到路径，走随机')
                    ac = random.randint(1, 4)
                    return ac
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置', allposi)
                        if len(allposi) == 1:
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                            end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                            end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                            end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                            end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                        else:
                            print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                anamytarget)
                            if len(allposi) == 1:
                                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                                end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                                end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                                end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                                end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                            else:
                                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                                    anamytarget)

                                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                #     anamytarget)  # 希望找到的是敌人对角的位置
                                pos = get_nearestanamyposition(playerX)
                                end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置', allposi)
                if len(allposi) == 1:
                    end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                    end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                    end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                    end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                    end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        anamytarget)
                    if len(allposi) == 1:
                        end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                        end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                        end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                        end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                        end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                    else:
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                        pos = get_nearestanamyposition(playerX)
                        end = mapfeature[pos['x']][pos['y']]

                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac
    if playerX == playerC:
        positioindex = 2
        print('对playerC进行的操作')
        flag_playerC_done = True
        if anamytarget in seeanamys:
            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                anamytarget)  # 希望找到的是敌人对角的位置
            print('所有的攻击的位置1', allposi)

            e = getmostsuitabletargetposition(myplayers, allposi)
            if e is not None:

                pos = e[positioindex]
            else:
                print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制11')
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                # print('所有的攻击的位置2', allposi)
                e = getmostsuitabletargetposition(myplayers, allposi)
                if e is not None:

                    pos = e[positioindex]
                else:
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        anamytarget)
                    e = getmostsuitabletargetposition(myplayers, allposi)
                    if e is not None:

                        pos = e[positioindex]
                    else:
                        pos = attack_positionOriginal
                    # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                    #     anamytarget)

            end = mapfeature[pos['x']][pos['y']]
            start = mapfeature[playerX['x']][playerX['y']]
            print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
            if start.x == end.x and start.y == end.y:
                return None
            path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
            if flag_getsolution:

                # return ac
                ac = get_actionfrompath()

                attackmakepathwallyapo(playerX, ac, anamytarget)

                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    ac = get_actionfrompath()
                    # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                    attackmakepathwallyapo(playerX, ac, anamytarget)
                    return ac
                else:
                    print('没有找到路径，走随机')
                    ac = random.randint(1, 4)
                    return ac
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置', allposi)
                        if len(allposi) == 1:
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                            end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                            end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                            end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                            end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                        else:
                            print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                anamytarget)
                            if len(allposi) == 1:
                                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                                end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                                end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                                end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                                end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                            else:
                                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                                    anamytarget)

                                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                #     anamytarget)  # 希望找到的是敌人对角的位置
                                pos = get_nearestanamyposition(playerX)
                                end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置', allposi)
                if len(allposi) == 1:
                    end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                    end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                    end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                    end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                    end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        anamytarget)
                    if len(allposi) == 1:
                        end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                        end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                        end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                        end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                        end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                    else:
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                        pos = get_nearestanamyposition(playerX)
                        end = mapfeature[pos['x']][pos['y']]

                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac
    if playerX == playerD:
        positioindex = 3
        print('对playerB进行的操作')
        flag_playerD_done = True
        if anamytarget in seeanamys:
            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                anamytarget)  # 希望找到的是敌人对角的位置
            print('所有的攻击的位置1', allposi)

            e = getmostsuitabletargetposition(myplayers, allposi)
            if e is not None:

                pos = e[positioindex]
            else:
                print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制11')
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                # print('所有的攻击的位置2', allposi)
                e = getmostsuitabletargetposition(myplayers, allposi)
                if e is not None:

                    pos = e[positioindex]
                else:
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        anamytarget)
                    e = getmostsuitabletargetposition(myplayers, allposi)
                    if e is not None:

                        pos = e[positioindex]
                    else:
                        pos = attack_positionOriginal
                    # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                    #     anamytarget)

            end = mapfeature[pos['x']][pos['y']]
            start = mapfeature[playerX['x']][playerX['y']]
            print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
            if start.x == end.x and start.y == end.y:
                return None
            path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
            if flag_getsolution:

                # return ac
                ac = get_actionfrompath()

                attackmakepathwallyapo(playerX, ac, anamytarget)

                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    ac = get_actionfrompath()
                    # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                    attackmakepathwallyapo(playerX, ac, anamytarget)
                    return ac
                else:
                    print('没有找到路径，走随机')
                    ac = random.randint(1, 4)
                    return ac
        else:
            # 是不是距离敌人的原点最近
            if playerX == targetnearestplayer:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                if flag_getsolution:
                    if len(path) == 2:
                        print('距离敌人的位置是1，这时候不去吃敌人而是去围堵')
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                        #     anamytarget)  # 希望找到的是敌人对角的位置
                        print('所有的攻击的位置', allposi)
                        if len(allposi) == 1:
                            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                            end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                            end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                            end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                        elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                            end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                        else:
                            print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                anamytarget)
                            if len(allposi) == 1:
                                end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                                end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                                end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                                end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                            elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                                end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                            else:
                                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                                    anamytarget)

                                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                                #     anamytarget)  # 希望找到的是敌人对角的位置
                                pos = get_nearestanamyposition(playerX)
                                end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            return None
                        path = getpathnoattackwallnotruemyplayer(start,
                                                                 end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                        if flag_getsolution:
                            ac = get_actionfrompath()

                            attackmakepathwallyapo(playerX, ac, anamytarget)
                            return ac
                        else:
                            path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                            if flag_getsolution:
                                ac = get_actionfrompath()
                                attackmakepathwallyapo(playerX, ac, anamytarget)
                                return ac
                            else:
                                print('没有找到路径，走随机')
                                ac = random.randint(1, 4)
                                return ac
                    else:
                        ac = get_actionfrompath()
                        if len(path) <= thresold_attackwall:
                            attackmakepathwall(path, anamytarget)

                        attackmakepathwallyapo(playerX, ac, anamytarget)

                        return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    print('没有找到路径，走随机')

                    ac = random.randint(1, 4)
                    return ac
            else:

                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4(
                #     anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendpos(
                #     anamytarget)  # 希望找到的是敌人对角的位置
                print('所有的攻击的位置', allposi)
                if len(allposi) == 1:
                    end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                    end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                    end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                    end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                    end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                else:
                    print('敌人的直接的一步都被使用了，需要在对敌人的位置进行更严格的限制')
                    attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = getendposlesslimit(
                        anamytarget)
                    if len(allposi) == 1:
                        end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionA) == playerX:
                        end = mapfeature[attack_positionA['x']][attack_positionA['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionB) == playerX:
                        end = mapfeature[attack_positionB['x']][attack_positionB['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionC) == playerX:
                        end = mapfeature[attack_positionC['x']][attack_positionC['y']]
                    elif get_nearestanamy_playernoviatruemyplayer(attack_positionD) == playerX:
                        end = mapfeature[attack_positionD['x']][attack_positionD['y']]
                    else:
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                            anamytarget)
                        # attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, allposi = get_anamynextmovepositionV4lesslimit(
                        #     anamytarget)

                        pos = get_nearestanamyposition(playerX)
                        end = mapfeature[pos['x']][pos['y']]

                start = mapfeature[playerX['x']][playerX['y']]
                print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                if flag_getsolution:
                    # if len(path)==2 and (path[0].x == path[2].x or path[0].y==path[2].y):
                    #     print('距离敌人的位置是横向或者竖向两格')
                    #     start = mapfeature[playerX['x']][playerX['y']]
                    #     end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
                    #     print('player起始的位置', 'x' + str(start.x) + 'y' + str(start.y))
                    #     print('终止的位置', 'x' + str(end.x) + 'y' + str(end.y))
                    #     if start.x == end.x and start.y == end.y:
                    #         return None
                    #     path = getpathnoattackwallnotruemyplayer(start, end)  # 这个走路是尽量避开最近那个鲲所制造的wall 并且避开自己的trueplayer的位置
                    #     if flag_getsolution:
                    #         ac = get_actionfrompath()
                    #
                    #         attackmakepathwallyapo(playerX, ac, anamytarget)
                    #
                    #         return ac
                    # else:
                    #     ac = get_actionfrompath()
                    #
                    #     attackmakepathwallyapo(playerX,ac,anamytarget)

                    # return ac
                    ac = get_actionfrompath()

                    # if len(path) <= thresold_attackwall:

                    attackmakepathwallyapo(playerX, ac, anamytarget)

                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    path = getpathnotruemyplayer(start, end)  # 这个是攻击敌人的目标位置，这个命令避开了我方的trueplayer的真实的位置，
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        # if len(path) <= thresold_attackwall: #比较近的时候才实现压迫，也就是不希望敌人的下一步，与我们相撞
                        attackmakepathwallyapo(playerX, ac, anamytarget)
                        return ac
                    else:
                        print('没有找到路径，走随机')
                        ac = random.randint(1, 4)
                        return ac


def getmostsuitabletargetposition(myplayers, allposi):
    global playerA, playerB, playerC, playerD
    global flag_getsolution
    global player_targetpos_index
    player_targetpos_index = []
    playerA_distance = []
    playerB_distance = []
    playerC_distance = []
    playerD_distance = []
    if allposi is None:
        return None
    print('打印一下allpos的情况', allposi)

    numplayers = len(myplayers)
    numtargetpositions = len(allposi)
    print('打印一下allpos的情况', allposi)
    print('allpos的个数', numtargetpositions)

    min = 1000
    if numplayers == 4:
        for i in range(numtargetpositions):
            player_targetpos_index.append(0)
        for pos in allposi:
            start = mapfeature[playerA['x']][playerA['y']]
            end = mapfeature[pos['x']][pos['y']]
            # path = getpathnotruemyplayer(start, end)  # 这个仅仅不能走myplayer的真实的位置
            path = getpathnotrueanamyplayer(start, end)
            if flag_getsolution:
                distemp = len(path) - 1
                playerA_distance.append(distemp)
            else:
                distemp = 10
                playerA_distance.append(distemp)
        for pos in allposi:
            start = mapfeature[playerB['x']][playerB['y']]
            end = mapfeature[pos['x']][pos['y']]
            path = getpathnotrueanamyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
            if flag_getsolution:
                distemp = len(path) - 1
                playerB_distance.append(distemp)
            else:
                distemp = 10
                playerB_distance.append(distemp)
        for pos in allposi:
            start = mapfeature[playerC['x']][playerC['y']]
            end = mapfeature[pos['x']][pos['y']]
            path = getpathnotrueanamyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
            if flag_getsolution:
                distemp = len(path) - 1
                playerC_distance.append(distemp)
            else:
                distemp = 10
                playerC_distance.append(distemp)
        for pos in allposi:
            start = mapfeature[playerD['x']][playerD['y']]
            end = mapfeature[pos['x']][pos['y']]
            path = getpathnotrueanamyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
            if flag_getsolution:
                distemp = len(path) - 1
                playerD_distance.append(distemp)
            else:
                distemp = 10
                playerD_distance.append(distemp)

        for l in range(numtargetpositions):
            for m in range(numtargetpositions):
                for n in range(numtargetpositions):
                    for o in range(numtargetpositions):
                        if not (l != m and l != n and l != o and m != n and m != o and n != o):
                            continue
                        else:
                            d = playerA_distance[l] + playerB_distance[m] + playerC_distance[n] + playerD_distance[o]
                            if d < min:
                                min = d
                                player_targetpos_index = [l, m, n, o]
                                # x+=1



    elif numplayers == 3:
        for i in range(numtargetpositions):
            player_targetpos_index.append(0)
        for pos in allposi:
            start = mapfeature[playerA['x']][playerA['y']]
            end = mapfeature[pos['x']][pos['y']]
            path = getpathnotruemyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
            if flag_getsolution:
                distemp = len(path) - 1
                playerA_distance.append(distemp)
            else:
                distemp = 10
                playerA_distance.append(distemp)
        for pos in allposi:
            start = mapfeature[playerB['x']][playerB['y']]
            end = mapfeature[pos['x']][pos['y']]
            path = getpathnotrueanamyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
            if flag_getsolution:
                distemp = len(path) - 1
                playerB_distance.append(distemp)
            else:
                distemp = 10
                playerB_distance.append(distemp)
        for pos in allposi:
            start = mapfeature[playerC['x']][playerC['y']]
            end = mapfeature[pos['x']][pos['y']]
            path = getpathnotrueanamyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
            if flag_getsolution:
                distemp = len(path) - 1
                playerC_distance.append(distemp)
            else:
                distemp = 10
                playerC_distance.append(distemp)
        for pos in allposi:
            start = mapfeature[playerD['x']][playerD['y']]
            end = mapfeature[pos['x']][pos['y']]
            path = getpathnotrueanamyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
            if flag_getsolution:
                distemp = len(path) - 1
                playerD_distance.append(distemp)
            else:
                distemp = 10
                playerD_distance.append(distemp)
        for l in range(numtargetpositions):
            for m in range(numtargetpositions):
                for n in range(numtargetpositions):
                    if not (l != m and l != n and l != o and m != n):
                        continue
                    else:
                        d = playerA_distance[l] + playerB_distance[m] + playerC_distance[n]
                        if d < min:
                            min = d
                            player_targetpos_index = [l, m, n]
        return player_targetpos_index

    else:
        return None


def getmyplayersordered(myplayers, anamytarget):
    global mapfeature

    print('调用getordered')
    print('myplayers', myplayers)
    print('anamytaeget', anamytarget)

    playersnum = len(myplayers)
    if playersnum == 4:
        disA = stepdistance(myplayers[0], anamytarget)
        disB = stepdistance(myplayers[1], anamytarget)
        disC = stepdistance(myplayers[2], anamytarget)
        disD = stepdistance(myplayers[3], anamytarget)
    elif playersnum == 3:
        disA = stepdistance(myplayers[0], anamytarget)
        disB = stepdistance(myplayers[1], anamytarget)
        disC = stepdistance(myplayers[2], anamytarget)
        disD = 1000
    elif playersnum == 2:
        disA = stepdistance(myplayers[0], anamytarget)
        disB = stepdistance(myplayers[1], anamytarget)
        disC = 1000
        disD = 1000
    else:
        disA = stepdistance(myplayers[0], anamytarget)
        disB = 1000
        disC = 1000
        disD = 1000

    if disA < disB:
        if disA < disC:
            if disA < disD:
                return myplayers[0]
            else:
                return myplayers[3]
        else:
            if disC < disD:
                return myplayers[2]
            else:
                return myplayers[3]
    else:
        if disB < disC:
            if disB < disD:
                return myplayers[1]
            else:
                return myplayers[3]
        else:
            if disC < disD:
                return myplayers[2]
            else:
                return myplayers[3]


def getabsoluteposition(player, anamytarget, absoluteposition):
    Ax = player['x']
    Ay = player['y']
    Bx = anamytarget['x']
    By = anamytarget['y']

    if Ax <= Bx and Ay <= By:
        # absoluteposition.remove('LU')
        return 'LU'
    elif Ax >= Bx and Ay <= By:
        # absoluteposition.remove('RU')
        return 'RU'
    elif Ax <= Bx and Ay >= By:
        # absoluteposition.remove('LD')
        return 'LD'
    elif Ax >= Bx and Ay >= By:
        # absoluteposition.remove('RD')
        return 'RD'


def caulatepossibalmove(anamytarget):
    anamyposibleposition = []

    anamyposibleposition.append({'x': anamytarget['x'], 'y': anamytarget['y']})
    anamynextposition1 = get_anamynextmovepositionV4(anamytarget)
    print('准备开始计算敌人可行的位置')
    for anamyposibleposition1i in anamynextposition1:
        if anamyposibleposition1i not in anamyposibleposition:
            anamyposibleposition.append(anamyposibleposition1i)
        else:
            pass
        anamyposibleposition2 = get_anamynextmovepositionV4(anamyposibleposition1i)
        for anamyposibleposition2i in anamyposibleposition2:
            if anamyposibleposition2i not in anamyposibleposition:
                anamyposibleposition.append(anamyposibleposition2i)
            else:
                pass
            anamyposibleposition3 = get_anamynextmovepositionV4(anamyposibleposition2i)
            for anamyposibleposition3i in anamyposibleposition3:
                if anamyposibleposition3i not in anamyposibleposition:
                    anamyposibleposition.append(anamyposibleposition3i)
                else:
                    pass
                anamyposibleposition4 = get_anamynextmovepositionV4(anamyposibleposition3i)
            for anamyposibleposition4i in anamyposibleposition4:
                if anamyposibleposition4i not in anamyposibleposition:
                    anamyposibleposition.append(anamyposibleposition4i)
                else:
                    pass
                anamyposibleposition5 = get_anamynextmovepositionV4(anamyposibleposition4i)
                if anamyposibleposition5 is None:
                    pass
                else:
                    for anamyposibleposition5i in anamyposibleposition5:

                        if anamyposibleposition5i not in anamyposibleposition5:
                            anamyposibleposition.append(anamyposibleposition5i)
                        else:
                            pass

    print('打印一下当前player的可行的路径有多少？', anamyposibleposition)
    print('打印一下当前player的可行的路径有多少？', len(anamyposibleposition))
    return anamyposibleposition


def getendpos(anamytarget):
    global mapfeature
    NextmovePos = []
    tar_pos = {'x': anamytarget['x'], 'y': anamytarget['y']}

    print('找左上')
    pos1 = get_anamynextDirMovePositionV5(anamytarget['x'], anamytarget['y'], 1)
    if pos1 is None:
        pos1 = get_anamynextDirMovePositionV5(anamytarget['x'], anamytarget['y'], 3)
        if pos1 is None:
            pass

        else:
            pos2 = get_anamynextDirMovePositionV5(pos1['x'], pos1['y'], 1)
            if pos2 is None:
                pass
            else:
                NextmovePos.append(pos2)
    else:
        pos2 = get_anamynextDirMovePositionV5(pos1['x'], pos1['y'], 3)
        if pos2 is None:
            pass
        else:
            NextmovePos.append(pos2)

    print('找右上')

    pos1 = get_anamynextDirMovePositionV5(anamytarget['x'], anamytarget['y'], 1)
    if pos1 is None:
        pos1 = get_anamynextDirMovePositionV5(anamytarget['x'], anamytarget['y'], 4)
        if pos1 is None:
            pass

        else:
            pos2 = get_anamynextDirMovePositionV5(pos1['x'], pos1['y'], 1)
            if pos2 is None:
                pass

            else:
                NextmovePos.append(pos2)
    else:
        pos2 = get_anamynextDirMovePositionV5(pos1['x'], pos1['y'], 4)
        if pos2 is None:
            pass
        else:
            if pos2 in NextmovePos:
                pass
            else:
                NextmovePos.append(pos2)
    print('找左下')

    pos1 = get_anamynextDirMovePositionV5(anamytarget['x'], anamytarget['y'], 2)
    if pos1 is None:
        pos1 = get_anamynextDirMovePositionV5(anamytarget['x'], anamytarget['y'], 3)
        if pos1 is None:
            pass

        else:
            pos2 = get_anamynextDirMovePositionV5(pos1['x'], pos1['y'], 2)
            if pos2 is None:
                pass
            else:
                NextmovePos.append(pos2)
    else:
        pos2 = get_anamynextDirMovePositionV5(pos1['x'], pos1['y'], 3)
        if pos2 is None:
            pass
        else:
            NextmovePos.append(pos2)

    print('找右下')
    pos1 = get_anamynextDirMovePositionV5(anamytarget['x'], anamytarget['y'], 2)
    if pos1 is None:
        pos1 = get_anamynextDirMovePositionV5(anamytarget['x'], anamytarget['y'], 4)
        if pos1 is None:
            pass

        else:
            pos2 = get_anamynextDirMovePositionV5(pos1['x'], pos1['y'], 2)
            if pos2 is None:
                pass
            else:
                NextmovePos.append(pos2)
    else:
        pos2 = get_anamynextDirMovePositionV5(pos1['x'], pos1['y'], 4)
        if pos2 is None:
            pass
        else:
            NextmovePos.append(pos2)

    num = len(NextmovePos)
    if num == 4:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = NextmovePos[3]
        Pos_or = tar_pos
    elif num == 3:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = None
        Pos_or = tar_pos

    elif num == 2:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 1:
        Pos_A = NextmovePos[0]
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 0:
        Pos_A = None
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    print
    return Pos_A, Pos_B, Pos_C, Pos_D, Pos_or, NextmovePos


def getendposlesslimit(anamytarget):
    global mapfeature
    NextmovePos = []
    tar_pos = {'x': anamytarget['x'], 'y': anamytarget['y']}

    print('找左上')
    pos1 = get_anamynextDirMovePositionV5lesslimit(anamytarget['x'], anamytarget['y'], 1)
    if pos1 is None:
        pos1 = get_anamynextDirMovePositionV5lesslimit(anamytarget['x'], anamytarget['y'], 3)
        if pos1 is None:
            pass

        else:
            pos2 = get_anamynextDirMovePositionV5lesslimit(pos1['x'], pos1['y'], 1)
            if pos2 is None:
                NextmovePos.append(pos1)
            else:
                NextmovePos.append(pos2)
    else:
        pos2 = get_anamynextDirMovePositionV5lesslimit(pos1['x'], pos1['y'], 3)
        if pos2 is None:
            NextmovePos.append(pos1)
        else:
            NextmovePos.append(pos2)

    print('找右上')

    pos1 = get_anamynextDirMovePositionV5lesslimit(anamytarget['x'], anamytarget['y'], 1)
    if pos1 is None:
        pos1 = get_anamynextDirMovePositionV5lesslimit(anamytarget['x'], anamytarget['y'], 4)
        if pos1 is None:
            pass

        else:
            pos2 = get_anamynextDirMovePositionV5lesslimit(pos1['x'], pos1['y'], 1)
            if pos2 is None:
                if pos1 in NextmovePos:
                    pass
                else:
                    NextmovePos.append(pos1)
            else:
                if pos2 in NextmovePos:
                    pass
                else:
                    NextmovePos.append(pos2)
    else:
        pos2 = get_anamynextDirMovePositionV5lesslimit(pos1['x'], pos1['y'], 4)
        if pos2 is None:
            if pos1 in NextmovePos:
                pass
            else:
                NextmovePos.append(pos1)
        else:
            if pos2 in NextmovePos:
                pass
            else:
                NextmovePos.append(pos2)
    print('找左下')

    pos1 = get_anamynextDirMovePositionV5lesslimit(anamytarget['x'], anamytarget['y'], 2)
    if pos1 is None:
        pos1 = get_anamynextDirMovePositionV5lesslimit(anamytarget['x'], anamytarget['y'], 3)
        if pos1 is None:
            pass

        else:
            pos2 = get_anamynextDirMovePositionV5lesslimit(pos1['x'], pos1['y'], 2)
            if pos2 is None:
                if pos1 in NextmovePos:
                    pass
                else:
                    NextmovePos.append(pos1)
            else:
                if pos2 in NextmovePos:
                    pass
                else:
                    NextmovePos.append(pos2)
    else:
        pos2 = get_anamynextDirMovePositionV5lesslimit(pos1['x'], pos1['y'], 3)
        if pos2 is None:
            if pos1 in NextmovePos:
                pass
            else:
                NextmovePos.append(pos1)
        else:
            if pos2 in NextmovePos:
                pass
            else:
                NextmovePos.append(pos2)

    print('找右下')
    pos1 = get_anamynextDirMovePositionV5lesslimit(anamytarget['x'], anamytarget['y'], 2)
    if pos1 is None:
        pos1 = get_anamynextDirMovePositionV5lesslimit(anamytarget['x'], anamytarget['y'], 4)
        if pos1 is None:
            pass

        else:
            pos2 = get_anamynextDirMovePositionV5lesslimit(pos1['x'], pos1['y'], 2)
            if pos2 is None:
                if pos1 in NextmovePos:
                    pass
                else:
                    NextmovePos.append(pos1)
            else:
                if pos2 in NextmovePos:
                    pass
                else:
                    NextmovePos.append(pos2)
    else:
        pos2 = get_anamynextDirMovePositionV5(pos1['x'], pos1['y'], 4)
        if pos2 is None:
            if pos1 in NextmovePos:
                pass
            else:
                NextmovePos.append(pos1)
        else:
            if pos2 in NextmovePos:
                pass
            else:
                NextmovePos.append(pos2)
    num = len(NextmovePos)
    if num == 4:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = NextmovePos[3]
        Pos_or = tar_pos
    elif num == 3:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = None
        Pos_or = tar_pos

    elif num == 2:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 1:
        Pos_A = NextmovePos[0]
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 0:
        Pos_A = None
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    return Pos_A, Pos_B, Pos_C, Pos_D, Pos_or, NextmovePos


global anamymakewallposition
anamymakewallposition = []


def attackmakepathwall(path, anamytarget):
    global mapfeature

    for pathi in path:
        print('pathd的位置x:', pathi.x, 'y:', pathi.y)

        if pathi.x == anamytarget['x'] and pathi.y == anamytarget['y']:
            pass

        pathi.attackwall = True
        pathi.context = 'W'
        anamymakewallposition.append({'x': pathi.x, 'y': pathi.y})
        # for i in range(1,5):
        #     pos= get_anamynextDirMovePosition(pathi.x,pathi.y,i)
        #     if pos is None:
        #         pass
        #     else:
        #         if pos['x'] == anamytarget['x'] and pos['y'] == anamytarget['y']:
        #             pass
        #         else:
        #
        #             mapfeature[pos['x']][pos['y']].attackwall = True
        #             mapfeature[pos['x']][pos['y']].context = 'W'
        #             anamymakewallposition.append(pos)


def attackmakepathwallyapo(playerX, ac, anamytarget):
    global mapfeature

    # 这个paht 实际上就是我们的grid类型的呢

    x = playerX['x']
    y = playerX['y']
    pos = get_anamynextDirMovePosition(x, y, ac)
    if pos is None:
        return 0
    else:
        print(pos)

        mapfeature[pos['x']][pos['y']].attackwall = True
        mapfeature[pos['x']][pos['y']].context = 'W'
        anamymakewallposition.append(pos)

    # poses=get_anamynextmoveposition(playerX)
    #
    # for pos in poses:
    #     if pos is None:
    #         pass
    #     else:
    #         if pos['x']==anamytarget['x'] and pos['y']==anamytarget['y']:
    #             pass
    #         else:
    #             if pos['x'] == anamytarget['x'] and pos['y'] == anamytarget['y']:
    #                 pass
    #             else:
    #
    #                 mapfeature[pos['x']][pos['y']].attackwall = True
    #                 mapfeature[pos['x']][pos['y']].context = 'W'
    #                 anamymakewallposition.append(pos)


# 加入权重因子
def get_poweractionmap2UpgradeV3(playerX, powersetX, anamyplayers, myplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1, bestPos2, bestPos3, bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global flag_get_Attackanamy
    global path
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    global attack_direc1, attack_direc2, basedirec
    global anamytarget
    global visionrange
    global attack_thresheoldfar
    attack_thresheoldfar = 10
    attack_thresheoldnear = 1
    pre_aboutstep = -3
    seeanamys = []
    if playerX is None:
        return None

    # 来判断敌人是否在我当前的player的视野内
    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= playerX['x'] + visionrange and anamyplayer['x'] >= playerX['x'] - visionrange and \
                anamyplayer['y'] <= playerX['y'] + visionrange and anamyplayer['y'] >= playerX['y'] - visionrange:
            seeanamys.append(anamyplayer)

    path = []
    action = []
    if len(anamyplayers) == 0:

        # flag_get_Attackanamy=False
        if len(
                powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
            # 在这种情况下我们进行敌人的搜素和寻找豆子
            defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
            # # print('向四个角随机运动')

            if playerX == playerB:
                # print('得到的bestpos的结果',bestPos1)
                try:

                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos1[0]][bestPos1[1]]

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
            elif playerX == playerC:
                # print('得到的bestpos的结果',bestPos2)
                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos2[0]][bestPos2[1]]

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

                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[2][random.randint(0, 1)]
                except:
                    return defaultmove[2][random.randint(0, 1)]

            elif playerX == playerA:

                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos4[0]][bestPos4[1]]

                    if start.x == end.x and start.y == end.y:
                        return random.randint(1, 4)

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
            return get_poweractionmap2(playerX, powersetX, anamyplayers, myplayers)
            # 还是继续进行吃豆子
    else:
        # 我们来判断当前自己有多少个player，采用什么样的进攻的测策略
        playernum = len(myplayers)
        if flag_get_Attackanamy:
            pass
        else:
            # 这个时候线采用敌人分数最多的
            # anamytarget = findbestanamytargetNearthewall(anamyplayers)#选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数
            anamytarget = findbestanamytarget(anamyplayers)  # 选择敌人的时候以一个权重的因子去衡量敌人的下几步可以运动的位置和分数

            # 定位选择吃哪个player

            attack_direc1, attack_direc2, basedirec = get_attackdirectionV3(anamytarget)

            # attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal=get_anamynextmoveposition(anamytarget)
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(anamytarget)
            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal = get_anamynextmoveposition(
                anamytarget)

            attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
            targetnearestplayer = get_nearestanamy_player(attack_positionOriginal)

            flag_get_Attackanamy = True
            # return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)

    path = []
    if playerX == playerA:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
            # print('起始的位置')
            # print('x' + str(start.x) + 'y' + str(start.y))
            # print('终止的位置')
            # print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:

            # playertemp=get_nearestanamy_player(attack_positionA)
            pos = get_nearestanamyposition(playerX)

            disX = stepdistance(playerX, pos)

            if disX > attack_thresheoldfar and len(powersetX) != 0:
                return get_poweractionmap2(playerX, powersetX, anamyplayers, myplayers)
            elif disX <= attack_thresheoldnear:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpath(start, end)
                if flag_getsolution:

                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    ac = random.randint(1, 4)
                return ac

            else:

                if pos == attack_positionA:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 1)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionB:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 2)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionC:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 3)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionD:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 4)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpath(start, end)
                if flag_getsolution:
                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    ac = random.randint(1, 4)
                    return ac
    if playerX == playerB:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
            # print('起始的位置')
            # print('x' + str(start.x) + 'y' + str(start.y))
            # print('终止的位置')
            # print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:

            pos = get_nearestanamyposition(playerX)

            disX = stepdistance(playerX, pos)

            if disX > attack_thresheoldfar and len(powersetX) != 0:
                return get_poweractionmap2(playerX, powersetX, anamyplayers)
            elif disX <= attack_thresheoldnear:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))
                path = getpath(start, end)
                if flag_getsolution:

                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    ac = random.randint(1, 4)
                return ac

            else:

                if pos == attack_positionA:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 1)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionB:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 2)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionC:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 3)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionD:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 4)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpath(start, end)
                if flag_getsolution:

                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    ac = random.randint(1, 4)
                    return ac
    if playerX == playerC:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
            # print('起始的位置')
            # print('x' + str(start.x) + 'y' + str(start.y))
            # print('终止的位置')
            # print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:

            pos = get_nearestanamyposition(playerX)

            disX = stepdistance(playerX, pos)

            if disX > attack_thresheoldfar and len(powersetX) != 0:
                return get_poweractionmap2(playerX, powersetX, anamyplayers)
            elif disX <= attack_thresheoldnear:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))
                path = getpath(start, end)
                if flag_getsolution:

                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    ac = random.randint(1, 4)
                return ac

            else:

                if pos == attack_positionA:
                    for i in range(disX - pre_aboutstep):
                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 1)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionB:
                    for i in range(disX - pre_aboutstep):
                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 2)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionC:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 3)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionD:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 4)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))
                if start.x == end.x and start.y == end.y:
                    return None
                path = getpath(start, end)
                if flag_getsolution:

                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    ac = random.randint(1, 4)
                    return ac
    if playerX == playerD:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]
            # print('起始的位置')
            # print('x' + str(start.x) + 'y' + str(start.y))
            # print('终止的位置')
            # print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:

            pos = get_nearestanamyposition(playerX)

            if pos is None:
                return get_poweractionmap2(playerX, powersetX, anamyplayers)

            disX = stepdistance(playerX, pos)

            if disX > attack_thresheoldfar and len(powersetX) != 0:
                return get_poweractionmap2(playerX, powersetX, anamyplayers)
            elif disX <= attack_thresheoldnear:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))
                path = getpath(start, end)
                if flag_getsolution:
                    print('找到路径')

                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    ac = random.randint(1, 4)
                return ac

            else:

                if pos == attack_positionA:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 1)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionB:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 2)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionC:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 3)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                elif pos == attack_positionD:
                    for i in range(disX - pre_aboutstep):

                        postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], 4)
                        if postemp is None:
                            break
                        else:
                            pos = postemp
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]
                # print('起始的位置')
                # print('x' + str(start.x) + 'y' + str(start.y))
                # print('终止的位置')
                # print('x' + str(end.x) + 'y' + str(end.y))
                path = getpath(start, end)
                if flag_getsolution:
                    print('找到路径')
                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    ac = random.randint(1, 4)
                    return ac


global flag_get_Attackanamy


# 这个getpoweractionmap2UpgradeV2 是进攻优先的把呢不能
def get_poweractionmap2UpgradeV2(playerX, powersetX, anamyplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1, bestPos2, bestPos3, bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global flag_get_Attackanamy
    global path
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    global visionrange
    seeanamys = []

    if playerX is None:
        return None

    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= playerX['x'] + visionrange and anamyplayer['x'] >= playerX['x'] - visionrange and \
                anamyplayer['y'] <= playerX['y'] + visionrange and anamyplayer['y'] >= playerX['y'] - visionrange:
            seeanamys.append(anamyplayer)

    path = []
    action = []
    if len(anamyplayers) == 0:
        if len(seeanamys) == 0:
            # flag_get_Attackanamy=False
            if len(
                    powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
                # 在这种情况下我们进行敌人的搜素和寻找豆子
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # # print('向四个角随机运动')

                if playerX == playerB:
                    # print('得到的bestpos的结果',bestPos1)
                    try:

                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos1[0]][bestPos1[1]]

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
                elif playerX == playerC:
                    # print('得到的bestpos的结果',bestPos2)
                    try:
                        start = mapfeature[playerX['x']][playerX['y']]
                        end = mapfeature[bestPos2[0]][bestPos2[1]]

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

                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            return defaultmove[3][random.randint(0, 1)]
                    except:
                        return defaultmove[3][random.randint(0, 1)]

            else:

                return get_poweractionmap2(playerX, powersetX, anamyplayers)
        else:
            pass
            # 还是继续进行吃豆子
    else:
        if flag_get_Attackanamy:
            pass
            # return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)
        else:
            # print('打印一下所有的敌人',anamyplayers)
            # 这种情况下就要指导有敌人的情况下，我们就要找出最好攻击哪个敌人
            # print('出现敌人scorekey错误，查看问题,打印敌人日志111111',anamyplayers)
            anamytarget = findbestanamytarget(anamyplayers)
            # 定位选择吃哪个player

            attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal = get_anamynextmoveposition(
                anamytarget)
            # attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(
            #     anamytarget)
            attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
            targetnearestplayer = get_nearestanamy_player(attack_positionOriginal)
            flag_get_Attackanamy = True
            # return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)

    path = []
    if playerX == playerA:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:
                print('找到路径')
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:
                print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX == playerB:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:
                print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:
                # print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX == playerC:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:
                # print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX == playerD:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac


global flag_get_Attackanamy
flag_get_Attackanamy = False


def get_attackactionmap2Upgrade_parta(playerX, powersetX, anamyplayers, myplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1, bestPos2, bestPos3, bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global flag_get_Attackanamy
    global path
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    global visionrange
    global centrolpartApos, centrolpartBpos, centrolpartCpos, centrolpartDpos

    seeanamys = []

    if playerX is None:
        return None

    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= playerX['x'] + visionrange and anamyplayer['x'] >= playerX['x'] - visionrange and \
                anamyplayer['y'] <= playerX['y'] + visionrange and anamyplayer['y'] >= playerX['y'] - visionrange:
            seeanamys.append(anamyplayer)

    path = []
    action = []
    if len(anamyplayers) == 0:
        if len(seeanamys) == 0:
            # flag_get_Attackanamy=False
            if len(
                    powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
                # 在这种情况下我们进行敌人的搜素和寻找豆子
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]

                # # print('向四个角随机运动')
                if playerX == playerB:
                    if flag_exploremapdone:
                        # print('得到的bestpos的结果',bestPos1)
                        try:

                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos1[0]][bestPos1[1]]

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
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerB:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerB:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerB:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerB:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return defaultmove[0][random.randint(0, 1)]
                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            try:

                                start = mapfeature[playerX['x']][playerX['y']]
                                end = mapfeature[bestPos1[0]][bestPos1[1]]

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


                elif playerX == playerC:
                    if flag_exploremapdone:
                        # print('得到的bestpos的结果',bestPos2)
                        try:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos2[0]][bestPos2[1]]

                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return defaultmove[1][random.randint(0, 1)]
                        except:
                            return defaultmove[1][random.randint(0, 1)]
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerC:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerC:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerC:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerC:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return defaultmove[1][random.randint(0, 1)]

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            try:
                                start = mapfeature[playerX['x']][playerX['y']]
                                end = mapfeature[bestPos2[0]][bestPos2[1]]

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
                    if flag_exploremapdone:
                        try:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos3[0]][bestPos3[1]]

                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return defaultmove[2][random.randint(0, 1)]
                        except:
                            return defaultmove[2][random.randint(0, 1)]
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerD:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerD:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerD:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerD:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return defaultmove[2][random.randint(0, 1)]

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:

                            ac = get_actionfrompath()
                            return ac
                        else:
                            try:
                                start = mapfeature[playerX['x']][playerX['y']]
                                end = mapfeature[bestPos3[0]][bestPos3[1]]

                                if start.x == end.x and start.y == end.y:
                                    # 我们进行了随机的运动
                                    return random.randint(1, 4)

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
                    if flag_exploremapdone:
                        try:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos3[0]][bestPos3[1]]

                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return defaultmove[3][random.randint(0, 1)]
                        except:
                            return defaultmove[3][random.randint(0, 1)]
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerA:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerA:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerA:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerA:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return defaultmove[3][random.randint(0, 1)]

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:

                            ac = get_actionfrompath()
                            return ac
                        else:
                            try:
                                start = mapfeature[playerX['x']][playerX['y']]
                                end = mapfeature[bestPos4[0]][bestPos4[1]]

                                if start.x == end.x and start.y == end.y:
                                    # 我们进行了随机的运动
                                    return random.randint(1, 4)

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
                return get_poweractionmap2(playerX, powersetX, anamyplayers, myplayers)
        else:
            pass
            # 还是继续进行吃豆子
    else:
        if flag_get_Attackanamy:
            # return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)
            return get_attackactionmap2Upgrade_partbV0_1(playerX, anamyplayers, powersetX)

        else:
            # print('打印一下所有的敌人',anamyplayers)
            # 这种情况下就要指导有敌人的情况下，我们就要找出最好攻击哪个敌人
            # print('出现敌人scorekey错误，查看问题,打印敌人日志111111',anamyplayers)
            anamytarget = findbestanamytarget(anamyplayers)
            # 定位选择吃哪个player
            if anamytarget is None:
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # # print('向四个角随机运动')
                if playerX == playerB:
                    if flag_exploremapdone:
                        # print('得到的bestpos的结果',bestPos1)
                        try:

                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos1[0]][bestPos1[1]]

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
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerB:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerB:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerB:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerB:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return defaultmove[0][random.randint(0, 1)]
                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            try:

                                start = mapfeature[playerX['x']][playerX['y']]
                                end = mapfeature[bestPos1[0]][bestPos1[1]]

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


                elif playerX == playerC:
                    if flag_exploremapdone:
                        # print('得到的bestpos的结果',bestPos2)
                        try:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos2[0]][bestPos2[1]]

                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return defaultmove[1][random.randint(0, 1)]
                        except:
                            return defaultmove[1][random.randint(0, 1)]
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerC:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerC:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerC:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerC:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return defaultmove[1][random.randint(0, 1)]

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            return ac
                        else:
                            try:
                                start = mapfeature[playerX['x']][playerX['y']]
                                end = mapfeature[bestPos2[0]][bestPos2[1]]

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
                    if flag_exploremapdone:
                        try:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos3[0]][bestPos3[1]]

                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return defaultmove[2][random.randint(0, 1)]
                        except:
                            return defaultmove[2][random.randint(0, 1)]
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerD:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerD:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerD:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerD:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return defaultmove[2][random.randint(0, 1)]

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:

                            ac = get_actionfrompath()
                            return ac
                        else:
                            try:
                                start = mapfeature[playerX['x']][playerX['y']]
                                end = mapfeature[bestPos3[0]][bestPos3[1]]

                                if start.x == end.x and start.y == end.y:
                                    # 我们进行了随机的运动
                                    return random.randint(1, 4)

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
                    if flag_exploremapdone:
                        try:
                            start = mapfeature[playerX['x']][playerX['y']]
                            end = mapfeature[bestPos3[0]][bestPos3[1]]

                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return defaultmove[3][random.randint(0, 1)]
                        except:
                            return defaultmove[3][random.randint(0, 1)]
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerA:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerA:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerA:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerA:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return defaultmove[3][random.randint(0, 1)]

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:

                            ac = get_actionfrompath()
                            return ac
                        else:
                            try:
                                start = mapfeature[playerX['x']][playerX['y']]
                                end = mapfeature[bestPos4[0]][bestPos4[1]]

                                if start.x == end.x and start.y == end.y:
                                    # 我们进行了随机的运动
                                    return random.randint(1, 4)

                                path = getpath(start, end)
                                if flag_getsolution:

                                    ac = get_actionfrompath()
                                    return ac
                                else:
                                    return defaultmove[3][random.randint(0, 1)]
                            except:
                                return defaultmove[3][random.randint(0, 1)]




            else:

                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal = get_anamynextmoveposition(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD=get_attackanamyposition2V2(anamytarget)
                attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
                targetnearestplayer = get_nearestanamy_player(attack_positionOriginal)
                flag_get_Attackanamy = True
                return get_attackactionmap2Upgrade_partbV0_1(playerX, anamyplayers, powersetX)

    # flag_get_Attackanamy=True


def get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX):
    global playerA
    global playerB
    global playerC
    global playerD
    global path
    global mapfeature
    global flag_getsolution
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    path = []
    if playerX == playerA:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX == playerB:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:
                # print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX == playerC:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:
                # print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX == playerD:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac


# 在partb的基础之上加入了如果敌人距离的比较远的情况，我们就不进行追击
def get_attackactionmap2Upgrade_partbV0_1(playerX, anamyplayers, powersetX):
    global playerA
    global playerB
    global playerC
    global playerD
    global path
    global mapfeature
    global flag_getsolution
    global bestPos1, bestPos2, bestPos3, bestPos4
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    dislimit = 3
    path = []
    if playerX == playerA:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            disX = stepdistance(playerX, pos)
            if disX <= dislimit:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]

                path = getpath(start, end)
                if flag_getsolution:
                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    ac = random.randint(1, 4)
                    return ac
            else:
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # # print('向四个角随机运动')
                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos4[0]][bestPos4[1]]

                    if start.x == end.x and start.y == end.y:
                        return random.randint(1, 4)
                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[3][random.randint(0, 1)]
                except:
                    return defaultmove[3][random.randint(0, 1)]

    if playerX == playerB:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            disX = stepdistance(playerX, pos)
            if disX <= dislimit:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]

                path = getpath(start, end)
                if flag_getsolution:
                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    ac = random.randint(1, 4)
                    return ac
            else:
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # # print('向四个角随机运动')

                try:

                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos1[0]][bestPos1[1]]

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

    if playerX == playerC:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            disX = stepdistance(playerX, pos)
            if disX <= dislimit:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]

                path = getpath(start, end)
                if flag_getsolution:
                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    ac = random.randint(1, 4)
                    return ac
            else:
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # # print('向四个角随机运动')
                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos2[0]][bestPos2[1]]

                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[1][random.randint(0, 1)]
                except:
                    return defaultmove[1][random.randint(0, 1)]

    if playerX == playerD:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            disX = stepdistance(playerX, pos)
            if disX <= dislimit:
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[pos['x']][pos['y']]

                path = getpath(start, end)
                if flag_getsolution:
                    ac = get_actionfrompath()
                    return ac
                else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                    ac = random.randint(1, 4)
                    return ac
            else:
                defaultmove = [[1, 3], [1, 4], [2, 3], [2, 4]]
                # # print('向四个角随机运动')

                try:
                    start = mapfeature[playerX['x']][playerX['y']]
                    end = mapfeature[bestPos3[0]][bestPos3[1]]

                    if start.x == end.x and start.y == end.y:
                        # 我们进行了随机的运动
                        return random.randint(1, 4)

                    path = getpath(start, end)
                    if flag_getsolution:
                        ac = get_actionfrompath()
                        return ac
                    else:
                        return defaultmove[2][random.randint(0, 1)]
                except:
                    return defaultmove[2][random.randint(0, 1)]


def get_attackactionmap2Upgrade_partaV2(playerX, powersetX, anamyplayers, myplayers):
    global playerA
    global playerB
    global playerC
    global playerD
    global bestPos1, bestPos2, bestPos3, bestPos4
    global powersetin
    global powersetout
    global mapfeature
    global flag_getsolution
    global flag_get_Attackanamy
    global path
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    global visionrange
    global centrolpartApos, centrolpartBpos, centrolpartCpos, centrolpartDpos
    global defaultlineA, defaultlineB, defaultlineC, defaultlineD
    global defaultlineAcopy, defaultlineBcopy, defaultlineCcopy, defaultlineDcopy
    seeanamys = []

    if playerX is None:
        return None

    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= playerX['x'] + visionrange and anamyplayer['x'] >= playerX['x'] - visionrange and \
                anamyplayer['y'] <= playerX['y'] + visionrange and anamyplayer['y'] >= playerX['y'] - visionrange:
            seeanamys.append(anamyplayer)

    path = []
    action = []
    if len(anamyplayers) == 0:
        if len(seeanamys) == 0:
            # flag_get_Attackanamy=False
            if len(
                    powersetX) == 0:  # 这地方的代码如果跳进来了是肯定是执行的，所以个分本不会执行那个地方的代码，我们应当将round 分为几个地方，第一个就是吃敌人的情况，这个时候，我们可以很多的时候是寻找power是在哪个位置
                # 在这种情况下我们进行敌人的搜素和寻找豆子

                if playerX == playerA:

                    if flag_exploremapdone:
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineAcopy:
                            if len(defaultlineAcopy) == 1:
                                defaultlineAcopy = copy.deepcopy(defaultlineA)
                            else:
                                defaultlineAcopy.remove(playerpos)

                            end = mapfeature[defaultlineAcopy[0]['x']][defaultlineAcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineAcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]

                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            print('routine walking2')

                            return ac
                        else:
                            return random.randint(1, 4)

                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerA:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerA:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerA:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerA:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return random.randint(1, 4)

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            print('explore map')
                            ac = get_actionfrompath()
                            return ac
                        else:
                            playerpos = {'x': playerX['x'], 'y': playerX['y']}

                            if playerpos in defaultlineAcopy:
                                if len(defaultlineAcopy) == 1:
                                    defaultlineAcopy = copy.deepcopy(defaultlineA)
                                else:
                                    defaultlineAcopy.remove(playerpos)

                                end = mapfeature[defaultlineAcopy[0]['x']][defaultlineAcopy[0]['y']]

                            else:
                                pos = get_nearestPosition(playerpos, defaultlineAcopy)
                                end = mapfeature[pos['x']][pos['y']]

                            start = mapfeature[playerX['x']][playerX['y']]
                            print('起始的位置')
                            print('x' + str(start.x) + 'y' + str(start.y))
                            print('终止的位置')
                            print('x' + str(end.x) + 'y' + str(end.y))
                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:
                                print('routine walking')

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return random.randint(1, 4)

                    # # print('向四个角随机运动')
                elif playerX == playerB:
                    # print('得到的bestpos的结果',bestPos4)

                    if flag_exploremapdone:
                        print('routine walking1')
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineBcopy:
                            if len(defaultlineBcopy) == 1:
                                defaultlineBcopy = copy.deepcopy(defaultlineB)
                            else:
                                defaultlineBcopy.remove(playerpos)

                            end = mapfeature[defaultlineBcopy[0]['x']][defaultlineBcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineBcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            print('routine walking2')

                            return ac
                        else:
                            return random.randint(1, 4)

                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerB:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerB:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerB:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerB:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return random.randint(1, 4)

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            print('explore map')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            playerpos = {'x': playerX['x'], 'y': playerX['y']}

                            if playerpos in defaultlineBcopy:
                                if len(defaultlineBcopy) == 1:
                                    defaultlineBcopy = copy.deepcopy(defaultlineB)
                                else:
                                    defaultlineBcopy.remove(playerpos)

                                end = mapfeature[defaultlineBcopy[0]['x']][defaultlineBcopy[0]['y']]

                            else:
                                pos = get_nearestPosition(playerpos, defaultlineBcopy)
                                end = mapfeature[pos['x']][pos['y']]

                            start = mapfeature[playerX['x']][playerX['y']]
                            print('起始的位置')
                            print('x' + str(start.x) + 'y' + str(start.y))
                            print('终止的位置')
                            print('x' + str(end.x) + 'y' + str(end.y))
                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:
                                print('routine walking')
                                ac = get_actionfrompath()
                                return ac
                            else:
                                return random.randint(1, 4)



                elif playerX == playerC:
                    if flag_exploremapdone:
                        print('routine walking1')

                        # print('得到的bestpos的结果',bestPos2)
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineCcopy:
                            if len(defaultlineCcopy) == 1:
                                defaultlineCcopy = copy.deepcopy(defaultlineC)
                            else:
                                defaultlineCcopy.remove(playerpos)

                            end = mapfeature[defaultlineCcopy[0]['x']][defaultlineCcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineCcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking2')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerC:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerC:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerC:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerC:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return random.randint(1, 4)

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)

                        if flag_getsolution:
                            print('explore map')

                            ac = get_actionfrompath()
                            return ac
                        else:

                            playerpos = {'x': playerX['x'], 'y': playerX['y']}

                            if playerpos in defaultlineCcopy:
                                if len(defaultlineCcopy) == 1:
                                    defaultlineCcopy = copy.deepcopy(defaultlineC)
                                else:
                                    defaultlineCcopy.remove(playerpos)

                                end = mapfeature[defaultlineCcopy[0]['x']][defaultlineCcopy[0]['y']]

                            else:
                                pos = get_nearestPosition(playerpos, defaultlineCcopy)
                                end = mapfeature[pos['x']][pos['y']]

                            start = mapfeature[playerX['x']][playerX['y']]
                            print('起始的位置')
                            print('x' + str(start.x) + 'y' + str(start.y))
                            print('终止的位置')
                            print('x' + str(end.x) + 'y' + str(end.y))
                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:
                                print('routine walking')

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return random.randint(1, 4)

                elif playerX == playerD:
                    # print('得到的bestpos的结果',bestPos3)

                    if flag_exploremapdone:
                        print('routine walking1')

                        playerpos = {'x': playerX['x'], 'y': playerX['y']}

                        if playerpos in defaultlineDcopy:
                            if len(defaultlineDcopy) == 1:
                                defaultlineDcopy = copy.deepcopy(defaultlineD)
                            else:
                                defaultlineDcopy.remove(playerpos)

                            end = mapfeature[defaultlineDcopy[0]['x']][defaultlineDcopy[0]['y']]

                        else:
                            pos = get_nearestPosition(playerpos, defaultlineDcopy)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking2')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerD:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerD:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerD:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerD:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return random.randint(1, 4)

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            print('explore map')

                            ac = get_actionfrompath()

                            return ac
                        else:

                            playerpos = {'x': playerX['x'], 'y': playerX['y']}

                            if playerpos in defaultlineDcopy:
                                if len(defaultlineDcopy) == 1:
                                    defaultlineDcopy = copy.deepcopy(defaultlineD)
                                else:
                                    defaultlineDcopy.remove(playerpos)

                                end = mapfeature[defaultlineDcopy[0]['x']][defaultlineDcopy[0]['y']]

                            else:
                                pos = get_nearestPosition(playerpos, defaultlineDcopy)
                                end = mapfeature[pos['x']][pos['y']]

                            start = mapfeature[playerX['x']][playerX['y']]
                            print('起始的位置')
                            print('x' + str(start.x) + 'y' + str(start.y))
                            print('终止的位置')
                            print('x' + str(end.x) + 'y' + str(end.y))
                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:
                                print('routine walking')

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return random.randint(1, 4)

            else:
                # 这个情况下 就要进行吃豆子
                return get_poweractionmap2(playerX, powersetX, anamyplayers, myplayers)
        else:
            pass
            # 还是继续进行吃豆子
    else:
        if flag_get_Attackanamy:
            # return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)
            return get_attackactionmap2Upgrade_partbV2(playerX, anamyplayers, powersetX)

        else:
            # print('打印一下所有的敌人',anamyplayers)
            # 这种情况下就要指导有敌人的情况下，我们就要找出最好攻击哪个敌人
            # print('出现敌人scorekey错误，查看问题,打印敌人日志111111',anamyplayers)
            anamytarget = findbestanamytarget(anamyplayers)
            # 定位选择吃哪个player
            if anamytarget is None:
                if playerX == playerA:

                    if flag_exploremapdone:
                        print('routine walking1')
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}
                        if playerpos in defaultlineA:
                            posindex = defaultlineA.index(playerpos)
                            if posindex == len(defaultlineA) - 1:
                                end = mapfeature[defaultlineA[0]['x']][defaultlineA[0]['y']]
                            else:
                                end = mapfeature[defaultlineA[posindex + 1]['x']][defaultlineA[posindex + 1]['y']]
                        else:
                            pos = get_nearestPosition(playerpos, defaultlineA)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]

                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            print('routine walking2')

                            return ac
                        else:
                            return random.randint(1, 4)

                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerA:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerA:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerA:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerA:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return random.randint(1, 4)

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            print('explore map')
                            ac = get_actionfrompath()
                            return ac
                        else:
                            playerpos = {'x': playerX['x'], 'y': playerX['y']}
                            if playerpos in defaultlineA:
                                posindex = defaultlineA.index(playerpos)
                                if posindex == len(defaultlineA) - 1:
                                    end = mapfeature[defaultlineA[0]['x']][defaultlineA[0]['y']]
                                else:
                                    end = mapfeature[defaultlineA[posindex + 1]['x']][defaultlineA[posindex + 1]['y']]
                            else:
                                pos = get_nearestPosition(playerpos, defaultlineA)
                                end = mapfeature[pos['x']][pos['y']]

                            start = mapfeature[playerX['x']][playerX['y']]
                            print('起始的位置')
                            print('x' + str(start.x) + 'y' + str(start.y))
                            print('终止的位置')
                            print('x' + str(end.x) + 'y' + str(end.y))
                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:
                                print('routine walking')

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return random.randint(1, 4)

                    # # print('向四个角随机运动')
                elif playerX == playerB:
                    # print('得到的bestpos的结果',bestPos4)

                    if flag_exploremapdone:
                        print('routine walking1')
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}
                        if playerpos in defaultlineB:
                            posindex = defaultlineB.index(playerpos)
                            if posindex == len(defaultlineB) - 1:
                                end = mapfeature[defaultlineB[0]['x']][defaultlineB[0]['y']]
                            else:
                                end = mapfeature[defaultlineB[posindex + 1]['x']][defaultlineB[posindex + 1]['y']]
                        else:
                            pos = get_nearestPosition(playerpos, defaultlineB)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            ac = get_actionfrompath()
                            print('routine walking2')

                            return ac
                        else:
                            return random.randint(1, 4)

                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerB:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerB:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerB:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerB:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return random.randint(1, 4)

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            print('explore map')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            playerpos = {'x': playerX['x'], 'y': playerX['y']}
                            if playerpos in defaultlineB:
                                posindex = defaultlineB.index(playerpos)
                                if posindex == len(defaultlineB) - 1:
                                    end = mapfeature[defaultlineB[0]['x']][defaultlineB[0]['y']]
                                else:
                                    end = mapfeature[defaultlineB[posindex + 1]['x']][defaultlineB[posindex + 1]['y']]
                            else:
                                pos = get_nearestPosition(playerpos, defaultlineB)
                                end = mapfeature[pos['x']][pos['y']]

                            start = mapfeature[playerX['x']][playerX['y']]
                            print('起始的位置')
                            print('x' + str(start.x) + 'y' + str(start.y))
                            print('终止的位置')
                            print('x' + str(end.x) + 'y' + str(end.y))
                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:
                                print('routine walking')
                                ac = get_actionfrompath()
                                return ac
                            else:
                                return random.randint(1, 4)



                elif playerX == playerC:
                    if flag_exploremapdone:
                        print('routine walking1')

                        # print('得到的bestpos的结果',bestPos2)
                        playerpos = {'x': playerX['x'], 'y': playerX['y']}
                        if playerpos in defaultlineC:
                            posindex = defaultlineC.index(playerpos)
                            if posindex == len(defaultlineC) - 1:
                                end = mapfeature[defaultlineC[0]['x']][defaultlineC[0]['y']]
                            else:
                                end = mapfeature[defaultlineC[posindex + 1]['x']][defaultlineC[posindex + 1]['y']]
                        else:
                            pos = get_nearestPosition(playerpos, defaultlineC)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking2')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerC:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerC:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerC:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerC:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return random.randint(1, 4)

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)

                        if flag_getsolution:
                            print('explore map')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            playerpos = {'x': playerX['x'], 'y': playerX['y']}
                            if playerpos in defaultlineC:
                                posindex = defaultlineC.index(playerpos)
                                if posindex == len(defaultlineC) - 1:
                                    end = mapfeature[defaultlineC[0]['x']][defaultlineC[0]['y']]
                                else:
                                    end = mapfeature[defaultlineC[posindex + 1]['x']][defaultlineC[posindex + 1]['y']]
                            else:
                                pos = get_nearestPosition(playerpos, defaultlineC)
                                end = mapfeature[pos['x']][pos['y']]

                            start = mapfeature[playerX['x']][playerX['y']]
                            print('起始的位置')
                            print('x' + str(start.x) + 'y' + str(start.y))
                            print('终止的位置')
                            print('x' + str(end.x) + 'y' + str(end.y))
                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:
                                print('routine walking')

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return random.randint(1, 4)

                elif playerX == playerD:
                    # print('得到的bestpos的结果',bestPos3)

                    if flag_exploremapdone:
                        print('routine walking1')

                        playerpos = {'x': playerX['x'], 'y': playerX['y']}
                        if playerpos in defaultlineD:
                            posindex = defaultlineD.index(playerpos)
                            if posindex == len(defaultlineD) - 1:
                                end = mapfeature[defaultlineD[0]['x']][defaultlineD[0]['y']]
                            else:
                                end = mapfeature[defaultlineD[posindex + 1]['x']][defaultlineD[posindex + 1]['y']]
                        else:
                            pos = get_nearestPosition(playerpos, defaultlineD)
                            end = mapfeature[pos['x']][pos['y']]

                        start = mapfeature[playerX['x']][playerX['y']]
                        print('起始的位置')
                        print('x' + str(start.x) + 'y' + str(start.y))
                        print('终止的位置')
                        print('x' + str(end.x) + 'y' + str(end.y))
                        if start.x == end.x and start.y == end.y:
                            # 我们进行了随机的运动
                            return random.randint(1, 4)

                        path = getpath(start, end)
                        if flag_getsolution:
                            print('routine walking2')

                            ac = get_actionfrompath()
                            return ac
                        else:
                            return random.randint(1, 4)
                    else:
                        if findnearestplayertomapexplorepos(myplayers, centrolpartApos) == playerD:
                            end = mapfeature[centrolpartApos['x']][centrolpartApos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartBpos) == playerD:
                            end = mapfeature[centrolpartBpos['x']][centrolpartBpos['y']]

                        elif findnearestplayertomapexplorepos(myplayers, centrolpartCpos) == playerD:
                            end = mapfeature[centrolpartCpos['x']][centrolpartCpos['y']]
                        elif findnearestplayertomapexplorepos(myplayers, centrolpartDpos) == playerD:
                            end = mapfeature[centrolpartDpos['x']][centrolpartDpos['y']]
                        else:
                            return random.randint(1, 4)

                        start = mapfeature[playerX['x']][playerX['y']]
                        path = getpath(start, end)
                        if flag_getsolution:
                            print('explore map')

                            ac = get_actionfrompath()

                            return ac
                        else:
                            playerpos = {'x': playerX['x'], 'y': playerX['y']}
                            if playerpos in defaultlineD:
                                posindex = defaultlineD.index(playerpos)
                                if posindex == len(defaultlineD) - 1:
                                    end = mapfeature[defaultlineD[0]['x']][defaultlineD[0]['y']]
                                else:
                                    end = mapfeature[defaultlineD[posindex + 1]['x']][defaultlineD[posindex + 1]['y']]
                            else:
                                pos = get_nearestPosition(playerpos, defaultlineD)
                                end = mapfeature[pos['x']][pos['y']]

                            start = mapfeature[playerX['x']][playerX['y']]
                            print('起始的位置')
                            print('x' + str(start.x) + 'y' + str(start.y))
                            print('终止的位置')
                            print('x' + str(end.x) + 'y' + str(end.y))
                            if start.x == end.x and start.y == end.y:
                                # 我们进行了随机的运动
                                return random.randint(1, 4)

                            path = getpath(start, end)
                            if flag_getsolution:
                                print('routine walking')

                                ac = get_actionfrompath()
                                return ac
                            else:
                                return random.randint(1, 4)


            else:

                attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal = get_anamynextmoveposition(
                    anamytarget)
                # attack_positionA, attack_positionB, attack_positionC, attack_positionD=get_attackanamyposition2V2(anamytarget)
                attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
                targetnearestplayer = get_nearestanamy_player(attack_positionOriginal)
                flag_get_Attackanamy = True
                return get_attackactionmap2Upgrade_partbV2(playerX, anamyplayers, powersetX)

    # flag_get_Attackanamy=True


def get_attackactionmap2Upgrade_partbV2(playerX, anamyplayers, powersetX):
    global playerA
    global playerB
    global playerC
    global playerD
    global path
    global mapfeature
    global flag_getsolution
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    path = []
    if playerX == playerA:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX == playerB:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:
                # print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX == playerC:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:
                # print('找到路径')

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
    if playerX == playerD:
        # 是不是距离敌人的原点最近
        if playerX == targetnearestplayer:
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[attack_positionOriginal['x']][attack_positionOriginal['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac
        else:
            pos = get_nearestanamyposition(playerX)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[pos['x']][pos['y']]

            path = getpath(start, end)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get
                ac = random.randint(1, 4)
                return ac


def get_nearestanamyposition(playerX):
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer
    bestpos = None
    disbest = 100
    if attack_positionA is not None:
        disA = stepdistance(playerX, attack_positionA)
        disbest = disA
        bestpos = attack_positionA
    if attack_positionB is not None:
        disB = stepdistance(playerX, attack_positionB)
        if disB < disbest:
            disbest = disB
            bestpos = attack_positionB
    if attack_positionC is not None:
        disC = stepdistance(playerX, attack_positionC)
        if disC < disbest:
            disbest = disC
            bestpos = attack_positionC
    if attack_positionD is not None:
        disD = stepdistance(playerX, attack_positionD)
        if disD < disbest:
            disbest = disD
            bestpos = attack_positionD
    if bestpos is not None:
        if bestpos == attack_positionA:
            attack_positionA = None
        elif bestpos == attack_positionB:
            attack_positionB = None
        elif bestpos == attack_positionC:
            attack_positionC = None
        elif bestpos == attack_positionD:
            attack_positionD = None

    else:
        # print('返回原始的位置')
        bestpos = attack_positionOriginal
        # return None #这个地方是因为如果我们返回的位置不是默认的位置，这个时候每个鲲的运动就会不知往哪里走

    return bestpos


def get_nearestanamy_player(attack_position):
    global playerA
    global playerB
    global playerC
    global playerD
    # global attack_positionOriginal
    if attack_position is None:
        return None
    bestplayer = []
    disbest = 100
    if playerA is not None:
        disA = stepdistance(playerA, attack_position)
        disbest = disA
        bestplayer = playerA
    if playerB is not None:
        disB = stepdistance(playerB, attack_position)
        if disB < disbest:
            disbest = disA
            bestplayer = playerB

    if playerC is not None:
        disC = stepdistance(playerC, attack_position)
        if disC < disbest:
            disbest = disC
            bestplayer = playerC
    if playerD is not None:
        disD = stepdistance(playerD, attack_position)
        if disD < disbest:
            disbest = disD
            bestplayer = playerD
    return bestplayer


def get_nearestanamy_playernoviatruemyplayer(attack_position):
    global playerA
    global playerB
    global playerC
    global playerD
    global flag_playerA_done, flag_playerB_done, flag_playerC_done, flag_playerD_done
    # global attack_positionOriginal
    if attack_position is None:
        return None

    bestplayer = []
    disbest = 100
    if playerA is not None and not flag_playerA_done:
        start = mapfeature[playerA['x']][playerA['y']]
        end = mapfeature[attack_position['x']][attack_position['y']]
        path = getpathnotruemyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
        if start.x == end.x and start.y == end.y:
            disA = 0

        else:
            path = getpath(start, end)
            if flag_getsolution:
                disA = len(path) - 1
            else:
                disA = 20

        disbest = disA
        bestplayer = playerA
    if playerB is not None and not flag_playerB_done:
        start = mapfeature[playerB['x']][playerB['y']]
        end = mapfeature[attack_position['x']][attack_position['y']]
        path = getpathnotruemyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
        if start.x == end.x and start.y == end.y:
            disB = 0
        else:
            path = getpath(start, end)
            if flag_getsolution:
                disB = len(path) - 1
            else:
                disB = 20
        if disB < disbest:
            disbest = disB
            bestplayer = playerB

    if playerC is not None and not flag_playerC_done:
        start = mapfeature[playerC['x']][playerC['y']]
        end = mapfeature[attack_position['x']][attack_position['y']]
        path = getpathnotruemyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
        if start.x == end.x and start.y == end.y:
            disC = 0
        else:
            path = getpath(start, end)
            if flag_getsolution:
                disC = len(path) - 1
            else:
                disC = 20

        if disC < disbest:
            disbest = disC
            bestplayer = playerC
    if playerD is not None and not flag_playerD_done:
        start = mapfeature[playerD['x']][playerD['y']]
        end = mapfeature[attack_position['x']][attack_position['y']]
        path = getpathnotruemyplayer(start, end)  # 这个仅仅受到敌人真实的位置的限制
        if start.x == end.x and start.y == end.y:
            disD = 0
        else:
            path = getpath(start, end)
            if flag_getsolution:
                disD = len(path) - 1
            else:
                disD = 20

        if disD < disbest:
            disbest = disD
            bestplayer = playerD
    return bestplayer


def get_anamynextmovepositionV3(anamyplayer):
    global mapfeature
    global map_height
    global map_width
    x = anamyplayer['x']
    y = anamyplayer['y']
    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    if y > 0 and not mapfeature[x][y - 1].wall:
        a = mapfeature[x][y - 1]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if y < map_height - 1 and not mapfeature[x][y + 1].wall:
        a = mapfeature[x][y + 1]
        # print('敌人是存在下邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x > 0 and not mapfeature[x - 1][y].wall:
        a = mapfeature[x - 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x < map_width - 1 and not mapfeature[x + 1][y].wall:
        a = mapfeature[x + 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})

    num = len(NextmovePos)
    if num == 4:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = NextmovePos[3]
        Pos_or = tar_pos
    elif num == 3:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = tar_pos
        Pos_or = tar_pos

    elif num == 2:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = tar_pos
        Pos_D = tar_pos
        Pos_or = tar_pos

    elif num == 1:
        Pos_A = NextmovePos[0]
        Pos_B = tar_pos
        Pos_C = tar_pos
        Pos_D = tar_pos
        Pos_or = tar_pos

    elif num == 0:
        Pos_A = None
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    # print('这个敌人的下一次移动的位置',NextmovePos)
    return num, NextmovePos


def get_attackdirectionV3(anamytarget):
    global map_width
    global map_height

    # 判断敌人所在位置范围
    x = anamytarget['x']
    y = anamytarget['y']

    # 根据敌人的位置，减少下部追击敌人的方式

    global map_width
    global map_height

    # 判断敌人所在位置范围
    x = anamytarget['x']
    y = anamytarget['y']

    # 根据敌人的位置，减少下部追击敌人的方式

    if x <= map_width / 2 and y <= map_height / 2 and x <= y:  # 如果其本身就在左上角 ,从下逼到上  #加入额外判断能否追死的情况

        return 2, 4, 1

    if x <= map_width / 2 and y <= map_height / 2 and x >= y:  # 如果其本身就在左上角 ,从右逼到左
        return 2, 4, 3

    if x >= map_width / 2 and y <= map_height / 2 and x / 2 >= y:  # 如果其本身就在右上角 ,从左逼到右
        return 2, 3, 4
    if x >= map_width / 2 and y <= map_height / 2 and x / 2 <= y:  # 如果其本身就在右上角 ,从下逼到上
        return 2, 3, 1
    if x <= map_width / 2 and y >= map_height / 2 and x <= y / 2:  # 如果其本身就在左下角 ,上逼到下
        return 1, 4, 2

    if x <= map_width / 2 and y >= map_height / 2 and x >= y / 2:  # 如果其本身就在左下角 ,从右逼到左
        return 1, 4, 3
    if x >= map_width / 2 and y >= map_height / 2 and x >= y:  # 如果其本身就在右下角 ,从左逼到右
        return 1, 3, 4

    if x >= map_width / 2 and y >= map_height / 2 and x <= y:  # 如果其本身就在右下角 ,从上逼到下
        return 1, 3, 2


def get_nearestanamydirection(playerX, anamytarget):
    pass


def get_anamynextDirMovePositionXXXV3(playerX, anamytarget, times, basedirec):
    global attack_direc1, attack_direc2
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer

    if attack_direc1 == 0 and attack_direc2 == 0:
        return get_nearestanamyposition(playerX)

    elif attack_direc1 == 0:
        pos = {'x': playerX['x'], 'y': playerX['y']}

        for i in range(times):
            postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], attack_direc2)
            if postemp is None:
                return pos
            else:
                pos = postemp
        attack_direc2 = 0
        return pos


    elif attack_direc2 == 0:
        pos = {'x': playerX['x'], 'y': playerX['y']}
        for i in range(times):

            postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], attack_direc1)
            if postemp is None:
                return pos
            else:
                pos = postemp
        attack_direc1 = 0
        return pos

    else:
        anamytargetpos = get_anamynextDirMovePosition(anamytarget['x'], anamytarget['y'], basedirec)
        if anamytargetpos is None:
            return get_nearestanamyposition(playerX)
        else:
            posa = get_anamynextDirMovePosition(anamytargetpos['x'], anamytargetpos['y'], attack_direc1)
            posb = get_anamynextDirMovePosition(anamytargetpos['x'], anamytargetpos['y'], attack_direc2)

    if posa is None or posb is None:
        return get_nearestanamyposition(playerX)
    else:
        a = stepdistance(playerX, posa)
        b = stepdistance(playerX, posb)
        if a > b:
            pos = {'x': playerX['x'], 'y': playerX['y']}
            for i in range(times):
                postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], attack_direc1)
                if postemp is None:
                    return pos
                else:
                    pos = postemp
            attack_direc1 = 0
            return pos
        else:
            pos = {'x': playerX['x'], 'y': playerX['y']}

            for i in range(times):
                postemp = get_anamynextDirMovePosition(pos['x'], pos['y'], attack_direc2)
                if postemp is None:
                    return pos
                else:
                    pos = postemp
            attack_direc1 = 2

            return pos


# 这个函数的作用是得到敌人将来能够移动的未来的可能的位置
def get_anamynextmoveposition(anamyplayer):
    global mapfeature
    global map_height
    global map_width
    x = anamyplayer['x']
    y = anamyplayer['y']
    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    Pos_A = None
    Pos_B = None
    Pos_C = None
    Pos_D = None
    if y > 0 and not mapfeature[x][y - 1].wall:
        a = mapfeature[x][y - 1]
        # print('敌人是存在上邻居')
        if a.wormhole:
            Pos_A = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                Pos_A = {'x': c.x, 'y': c.y}
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            Pos_A = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})

    if y < map_height - 1 and not mapfeature[x][y + 1].wall:
        a = mapfeature[x][y + 1]
        # print('敌人是存在下邻居')
        if a.wormhole:
            Pos_B = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                Pos_B = {'x': c.x, 'y': c.y}
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            Pos_B = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})

    if x > 0 and not mapfeature[x - 1][y].wall:
        a = mapfeature[x - 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            Pos_C = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                Pos_C = {'x': c.x, 'y': c.y}
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            Pos_C = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})

    if x < map_width - 1 and not mapfeature[x + 1][y].wall:
        a = mapfeature[x + 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            Pos_D = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                Pos_D = {'x': c.x, 'y': c.y}
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            Pos_D = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})

    #
    # num=len(NextmovePos)
    # if num==4:
    #     Pos_A=NextmovePos[0]
    #     Pos_B=NextmovePos[1]
    #     Pos_C=NextmovePos[2]
    #     Pos_D=NextmovePos[3]
    #     Pos_or=tar_pos
    # elif num==3:
    #     Pos_A=NextmovePos[0]
    #     Pos_B=NextmovePos[1]
    #     Pos_C=NextmovePos[2]
    #     Pos_D=None
    #     Pos_or=tar_pos
    #
    # elif num==2:
    #     Pos_A = NextmovePos[0]
    #     Pos_B = NextmovePos[1]
    #     Pos_C = None
    #     Pos_D = None
    #     Pos_or=tar_pos
    #
    # elif num==1:
    #     Pos_A = NextmovePos[0]
    #     Pos_B = None
    #     Pos_C = None
    #     Pos_D = None
    #     Pos_or=tar_pos
    #
    # elif num==0:
    #     Pos_A = None
    #     Pos_B = None
    #     Pos_C = None
    #     Pos_D = None
    Pos_or = tar_pos

    # print('这个敌人的下一次移动的位置',NextmovePos)
    return Pos_A, Pos_B, Pos_C, Pos_D, Pos_or


def get_myplayernextmoveposition(myplayer):
    global mapfeature
    global map_height
    global map_width
    x = myplayer['x']
    y = myplayer['y']
    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    Pos_A = None
    Pos_B = None
    Pos_C = None
    Pos_D = None
    if y > 0 and not mapfeature[x][y - 1].wall:
        a = mapfeature[x][y - 1]
        # print('敌人是存在上邻居')
        if a.wormhole:
            Pos_A = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                Pos_A = {'x': c.x, 'y': c.y}
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            Pos_A = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})

    if y < map_height - 1 and not mapfeature[x][y + 1].wall:
        a = mapfeature[x][y + 1]
        # print('敌人是存在下邻居')
        if a.wormhole:
            Pos_B = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                Pos_B = {'x': c.x, 'y': c.y}
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            Pos_B = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})

    if x > 0 and not mapfeature[x - 1][y].wall:
        a = mapfeature[x - 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            Pos_C = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                Pos_C = {'x': c.x, 'y': c.y}
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            Pos_C = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})

    if x < map_width - 1 and not mapfeature[x + 1][y].wall:
        a = mapfeature[x + 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            Pos_D = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                Pos_D = {'x': c.x, 'y': c.y}
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            Pos_D = {'x': a.x, 'y': a.y}
            NextmovePos.append({'x': a.x, 'y': a.y})

    #
    # num=len(NextmovePos)
    # if num==4:
    #     Pos_A=NextmovePos[0]
    #     Pos_B=NextmovePos[1]
    #     Pos_C=NextmovePos[2]
    #     Pos_D=NextmovePos[3]
    #     Pos_or=tar_pos
    # elif num==3:
    #     Pos_A=NextmovePos[0]
    #     Pos_B=NextmovePos[1]
    #     Pos_C=NextmovePos[2]
    #     Pos_D=None
    #     Pos_or=tar_pos
    #
    # elif num==2:
    #     Pos_A = NextmovePos[0]
    #     Pos_B = NextmovePos[1]
    #     Pos_C = None
    #     Pos_D = None
    #     Pos_or=tar_pos
    #
    # elif num==1:
    #     Pos_A = NextmovePos[0]
    #     Pos_B = None
    #     Pos_C = None
    #     Pos_D = None
    #     Pos_or=tar_pos
    #
    # elif num==0:
    #     Pos_A = None
    #     Pos_B = None
    #     Pos_C = None
    #     Pos_D = None
    Pos_or = tar_pos

    # print('这个敌人的下一次移动的位置',NextmovePos)
    return Pos_A, Pos_B, Pos_C, Pos_D, Pos_or


def get_anamynextmovepositionV4(anamyplayer):
    global mapfeature
    global map_height
    global map_width
    x = anamyplayer['x']
    y = anamyplayer['y']
    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    if y > 0 and not mapfeature[x][y - 1].wall and not mapfeature[x][y - 1].myplayer and not mapfeature[x][
        y - 1].attackwall:
        a = mapfeature[x][y - 1]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if y < map_height - 1 and not mapfeature[x][y + 1].wall and not mapfeature[x][y + 1].myplayer and not mapfeature[x][
        y + 1].attackwall:
        a = mapfeature[x][y + 1]
        # print('敌人是存在下邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x > 0 and not mapfeature[x - 1][y].wall and not mapfeature[x - 1][y].myplayer and not mapfeature[x - 1][
        y].attackwall:
        a = mapfeature[x - 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x < map_width - 1 and not mapfeature[x + 1][y].wall and not mapfeature[x + 1][y].myplayer and not \
    mapfeature[x + 1][y].attackwall:
        a = mapfeature[x + 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    num = len(NextmovePos)
    if num == 4:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = NextmovePos[3]
        Pos_or = tar_pos
    elif num == 3:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = None
        Pos_or = tar_pos

    elif num == 2:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 1:
        Pos_A = NextmovePos[0]
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 0:
        Pos_A = None
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    return Pos_A, Pos_B, Pos_C, Pos_D, Pos_or, NextmovePos


def get_anamynextmovepositionV4lesslimit(anamyplayer):
    global mapfeature
    global map_height
    global map_width
    x = anamyplayer['x']
    y = anamyplayer['y']
    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    if y > 0 and not mapfeature[x][y - 1].wall and not mapfeature[x][y - 1].truemyplayer and not mapfeature[x][
        y - 1].attackwall:
        a = mapfeature[x][y - 1]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if y < map_height - 1 and not mapfeature[x][y + 1].wall and not mapfeature[x][y + 1].truemyplayer and not \
    mapfeature[x][y + 1].attackwall:
        a = mapfeature[x][y + 1]
        # print('敌人是存在下邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x > 0 and not mapfeature[x - 1][y].wall and not mapfeature[x - 1][y].truemyplayer and not mapfeature[x - 1][
        y].attackwall:
        a = mapfeature[x - 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x < map_width - 1 and not mapfeature[x + 1][y].wall and not mapfeature[x + 1][y].truemyplayer and not \
    mapfeature[x + 1][y].attackwall:
        a = mapfeature[x + 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    num = len(NextmovePos)

    if num == 4:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = NextmovePos[3]
        Pos_or = tar_pos
    elif num == 3:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = None
        Pos_or = tar_pos

    elif num == 2:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 1:
        Pos_A = NextmovePos[0]
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 0:
        Pos_A = None
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    return Pos_A, Pos_B, Pos_C, Pos_D, Pos_or, NextmovePos


def get_anamynextmovepositionV5(anamyplayer):
    global mapfeature
    global map_height
    global map_width
    x = anamyplayer['x']
    y = anamyplayer['y']
    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    if y > 0 and not mapfeature[x][y - 1].wall and not mapfeature[x][y - 1].truemyplayer and not mapfeature[x][
        y - 1].attackwall:
        a = mapfeature[x][y - 1]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if y < map_height - 1 and not mapfeature[x][y + 1].wall and not mapfeature[x][y + 1].truemyplayer and not \
    mapfeature[x][y + 1].attackwall:
        a = mapfeature[x][y + 1]
        # print('敌人是存在下邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x > 0 and not mapfeature[x - 1][y].wall and not mapfeature[x - 1][y].truemyplayer and not mapfeature[x - 1][
        y].attackwall:
        a = mapfeature[x - 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    if x < map_width - 1 and not mapfeature[x + 1][y].wall and not mapfeature[x + 1][y].truemyplayer and not \
    mapfeature[x + 1][y].attackwall:
        a = mapfeature[x + 1][y]
        # print('敌人是存在上邻居')
        if a.wormhole:
            NextmovePos.append({'x': a.x, 'y': a.y})
        elif a.tunnel != 'no':
            c = findgoodneighbourV2(a)
            if a.x == c.x and a.x == c.y:
                pass
            else:
                NextmovePos.append({'x': c.x, 'y': c.y})
        else:
            NextmovePos.append({'x': a.x, 'y': a.y})
    num = len(NextmovePos)
    if num == 4:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = NextmovePos[3]
        Pos_or = tar_pos
    elif num == 3:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = NextmovePos[2]
        Pos_D = None
        Pos_or = tar_pos

    elif num == 2:
        Pos_A = NextmovePos[0]
        Pos_B = NextmovePos[1]
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 1:
        Pos_A = NextmovePos[0]
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    elif num == 0:
        Pos_A = None
        Pos_B = None
        Pos_C = None
        Pos_D = None
        Pos_or = tar_pos

    return Pos_A, Pos_B, Pos_C, Pos_D, Pos_or, NextmovePos


def get_attackanamyposition2(anamytarget):
    global map_width
    global map_height

    # 判断敌人所在位置范围
    x = anamytarget['x']
    y = anamytarget['y']

    # 根据敌人的位置，减少下部追击敌人的方式

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
        Target_Bx = x  # 目标位置设定左下
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
        Target_Cx = x
        Target_Cy = y - 1
        Target_Dx = x + 1
        Target_Dy = y + 1
    if x >= map_width / 2 and y <= map_height / 2 and x / 2 <= y:  # 如果其本身就在右上角 ,从下逼到上
        Target_Ax = x  # 目标位置设定为 左侧
        Target_Ay = y
        Target_Bx = x - 1  # 目标位置设定左下
        Target_By = y
        Target_Cx = x + 1
        Target_Cy = y
        Target_Dx = x - 1
        Target_Dy = y - 1
        # 在地图下方的情况
    if x <= map_width / 2 and y >= map_height / 2 and x <= y / 2:  # 如果其本身就在左下角 ,上逼到下
        Target_Ax = x  # 目标位置设定为 左侧
        Target_Ay = y
        Target_Bx = x + 1  # 目标位置设定左下
        Target_By = y
        Target_Cx = x - 1
        Target_Cy = y
        Target_Dx = x + 1
        Target_Dy = y + 1

    if x <= map_width / 2 and y >= map_height / 2 and x >= y / 2:  # 如果其本身就在左下角 ,从右逼到左
        Target_Ax = x  # 目标位置设定为 右侧
        Target_Ay = y
        Target_Bx = x  # 目标位置设定y右下
        Target_By = y - 1
        Target_Cx = x
        Target_Cy = y + 1
        Target_Dx = x - 1
        Target_Dy = y - 1

    if x >= map_width / 2 and y >= map_height / 2 and x >= y:  # 如果其本身就在右下角 ,从左逼到右
        Target_Ax = x  # 目标位置设定为 右侧
        Target_Ay = y
        Target_Bx = x  # 目标位置设定左下
        Target_By = y - 1
        Target_Cx = x
        Target_Cy = y + 1
        Target_Dx = x + 1
        Target_Dy = y - 1

    if x >= map_width / 2 and y >= map_height / 2 and x <= y:  # 如果其本身就在右下角 ,从上逼到下
        Target_Ax = x  # 目标位置设定为 右侧
        Target_Ay = y
        Target_Bx = x - 1  # 目标位置设定右下
        Target_By = y
        Target_Cx = x + 1
        Target_Cy = y
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
    return Target_A, Target_B, Target_C, Target_D

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


def get_anamynextDirMovePosition(x, y, direction):
    global mapfeature
    global map_height
    global map_width

    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    if direction == 1:
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

                else:
                    PosUp = {'x': c.x, 'y': c.y}
                    return PosUp

            else:
                PosUp = {'x': a.x, 'y': a.y}
                return PosUp
        else:
            return None
    if direction == 2:
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

                else:
                    PosDown = {'x': c.x, 'y': c.y}
                    return PosDown

            else:
                PosDown = {'x': a.x, 'y': a.y}
                return PosDown
        else:
            return None
    if direction == 3:
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

                else:
                    PosLeft = {'x': c.x, 'y': c.y}
                    return PosLeft

            else:
                PosLeft = {'x': a.x, 'y': a.y}
                return PosLeft
        else:
            return None

    if direction == 4:
        if x < map_width - 1 and not mapfeature[x + 1][y].wall:
            a = mapfeature[x + 1][y]
            # print('敌人是存在上邻居')
            if a.wormhole:
                PosRight = {'x': a.x, 'y': a.y}
                return PosRight
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None

                else:
                    PosRight = {'x': c.x, 'y': c.y}
                    return PosRight

            else:
                PosRight = {'x': a.x, 'y': a.y}
                return PosRight
        else:
            return None


def get_anamynextDirMovePositionV5(x, y, direction):
    global mapfeature
    global map_height
    global map_width

    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    if direction == 1:
        if y > 0 and not mapfeature[x][y - 1].wall and not mapfeature[x][y - 1].myplayer and not mapfeature[x][
            y - 1].attackwall:
            a = mapfeature[x][y - 1]
            # print('敌人是存在上邻居')
            if a.wormhole:
                PosUp = {'x': a.x, 'y': a.y}
                return PosUp
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None

                else:
                    PosUp = {'x': c.x, 'y': c.y}
                    return PosUp

            else:
                PosUp = {'x': a.x, 'y': a.y}
                return PosUp
        else:
            return None
    if direction == 2:
        if y < map_height - 1 and not mapfeature[x][y + 1].wall and not mapfeature[x][y + 1].myplayer and not \
        mapfeature[x][y + 1].attackwall:
            a = mapfeature[x][y + 1]
            # print('敌人是存在下邻居')
            if a.wormhole:
                PosDown = {'x': a.x, 'y': a.y}
                return PosDown
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None

                else:
                    PosDown = {'x': c.x, 'y': c.y}
                    return PosDown

            else:
                PosDown = {'x': a.x, 'y': a.y}
                return PosDown
        else:
            return None
    if direction == 3:
        if x > 0 and not mapfeature[x - 1][y].wall and not mapfeature[x - 1][y].myplayer and not mapfeature[x - 1][
            y].attackwall:
            a = mapfeature[x - 1][y]
            # print('敌人是存在左邻居')
            if a.wormhole:
                PosLeft = {'x': a.x, 'y': a.y}
                return PosLeft
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None

                else:
                    PosLeft = {'x': c.x, 'y': c.y}
                    return PosLeft

            else:
                PosLeft = {'x': a.x, 'y': a.y}
                return PosLeft
        else:
            return None

    if direction == 4:
        if x < map_width - 1 and not mapfeature[x + 1][y].wall and not mapfeature[x + 1][y].myplayer and not \
        mapfeature[x + 1][y].attackwall:
            a = mapfeature[x + 1][y]
            # print('敌人是存在上邻居')
            if a.wormhole:
                PosRight = {'x': a.x, 'y': a.y}
                return PosRight
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None

                else:
                    PosRight = {'x': c.x, 'y': c.y}
                    return PosRight

            else:
                PosRight = {'x': a.x, 'y': a.y}
                return PosRight
        else:
            return None


def get_anamynextDirMovePositionV5lesslimit(x, y, direction):
    global mapfeature
    global map_height
    global map_width

    tar_pos = {'x': x, 'y': y}
    # 找它的上邻居
    NextmovePos = []
    if direction == 1:
        if y > 0 and not mapfeature[x][y - 1].wall and not mapfeature[x][y - 1].truemyplayer and not mapfeature[x][
            y - 1].attackwall:
            a = mapfeature[x][y - 1]
            # print('敌人是存在上邻居')
            if a.wormhole:
                PosUp = {'x': a.x, 'y': a.y}
                return PosUp
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None

                else:
                    PosUp = {'x': c.x, 'y': c.y}
                    return PosUp

            else:
                PosUp = {'x': a.x, 'y': a.y}
                return PosUp
        else:
            return None
    if direction == 2:
        if y < map_height - 1 and not mapfeature[x][y + 1].wall and not mapfeature[x][y + 1].truemyplayer and not \
        mapfeature[x][y + 1].attackwall:
            a = mapfeature[x][y + 1]
            # print('敌人是存在下邻居')
            if a.wormhole:
                PosDown = {'x': a.x, 'y': a.y}
                return PosDown
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None

                else:
                    PosDown = {'x': c.x, 'y': c.y}
                    return PosDown

            else:
                PosDown = {'x': a.x, 'y': a.y}
                return PosDown
        else:
            return None
    if direction == 3:
        if x > 0 and not mapfeature[x - 1][y].wall and not mapfeature[x - 1][y].truemyplayer and not mapfeature[x - 1][
            y].attackwall:
            a = mapfeature[x - 1][y]
            # print('敌人是存在左邻居')
            if a.wormhole:
                PosLeft = {'x': a.x, 'y': a.y}
                return PosLeft
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None

                else:
                    PosLeft = {'x': c.x, 'y': c.y}
                    return PosLeft

            else:
                PosLeft = {'x': a.x, 'y': a.y}
                return PosLeft
        else:
            return None

    if direction == 4:
        if x < map_width - 1 and not mapfeature[x + 1][y].wall and not mapfeature[x + 1][y].truemyplayer and not \
        mapfeature[x + 1][y].attackwall:
            a = mapfeature[x + 1][y]
            # print('敌人是存在上邻居')
            if a.wormhole:
                PosRight = {'x': a.x, 'y': a.y}
                return PosRight
            elif a.tunnel != 'no':
                c = findgoodneighbourV2(a)
                if a.x == c.x and a.x == c.y:
                    return None

                else:
                    PosRight = {'x': c.x, 'y': c.y}
                    return PosRight

            else:
                PosRight = {'x': a.x, 'y': a.y}
                return PosRight
        else:
            return None


def findnearestpowerX(playerX, powersetX):
    powerbest = []

    dis = 10000000000000
    # print('在寻找距离最近的powerout的情况下，我们打印一下powerserout以便更好判断我们得到的是不是最好的')
    # print(powersetout)
    for power in powersetX:

        tempdis = abs(playerX['x'] - power['x']) + abs(playerX['y'] - power['y'])
        if tempdis < dis:
            dis = tempdis

            powerbest = power
    return powerbest


def get_poweractionmap1(playerX, anamyplayers):
    import random
    global powersetin
    global powersetout
    global playerworm
    global playerout
    global playerattackup
    global playerattackdown
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer, flag_get_Attackanamy

    global mapfeature

    global playerwormtarget
    global flag_playerinworm
    global flag_getsolution
    global path

    global Intera  # 惯性概念

    # flag_playerinworm=True
    path = []
    action = []
    if playerX == playerworm:
        # print('我们在actionfind当中，应当首先进行的就是要判断这个player是不是已经进入到了我们的tunnel内部了')
        if flag_playerinworm:  # 如果我们已经在wormhole里面了
            # 这个函数保证的是能够返回距离当前player最近的power
            # print('这个时候我已经能够进入到player进入虫洞内部了')
            if len(powersetin) == 0:

                # 这个时候就去到外面去抓人吗？？还是到外面去吃

                # print('pwoersetin是空的,导致目前的动作是空的')  #这个时候，理论上应该能够
                return random.randint(1, 4)
            else:

                powersettemp = findnearestpoweri(playerX)
                # print(player)
                # print(powersettemp)
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[powersettemp['x']][powersettemp['y']]

                path = getpath(start, end)

                if flag_getsolution:

                    powersetin.remove(powersettemp)
                    # print('flag_getsolution 是ok的')
                    ac = get_actionfrompath()
                    return ac
                else:
                    if Attack:
                        # print('攻击模式下,我们是没有用的,进行额是随机运动,')
                        # 后面要修改为攻击敌人的情况，顺带的攻击敌人
                        ac = random.randint(1, 4)
                        return ac
                    else:
                        # print('我们准备在计划躲避的时候 action的给出None的情况')
                        # w我们要逃跑，所以留给后面的逃跑的情况给出action
                        return None

                    # print('打印一下当前坤的路径')
                    # mapshow(mapfeature)
        else:  # 这个时候我们的player 还没有进入到wormwhole 内部

            # print(player)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[playerwormtarget['x']][playerwormtarget['y']]
            path = getpath(start, end)

            if flag_getsolution:

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
                    return None

    else:  # 这个时候的player实际上,是为playerout 专门吃外面的分数的 #########powersetout 外面的player去找到路径                            #这个敌方我希望如果能够看到敌方的player的情况下; 我们就进行直接的追击
        # 这个函数保证的是能够返回距离当前player最近的power                    #实际上也一样，我们应当对player的action进行交集操作以达到最优的情况
        # print('打印一下当前需要虚招路径的player的信息bcd')
        # print(player)
        if len(powersetout) == 0:  # 如果已经空了 则根据模式，如果是攻击模式，则进行攻击。如果不是攻击模式，则尽量原远离自己的伙伴和墙壁，是否可以采用
            # 还需要再继续再进行修改
            if len(anamyplayers) == 0:
                return random.randint(1, 4)
            else:

                anamytarget = findbestanamytarget(anamyplayers)
                # 定位选择吃哪个player

                # attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal=get_anamynextmoveposition(anamytarget)
                attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(
                    anamytarget)
                attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
                targetnearestplayer = get_nearestanamy_player()

                flag_get_Attackanamy = True
                powersetX = []
                return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)



        else:
            powersettemp = findnearestpowero(playerX)  # 实际上，我们寻找power的方式要是基于power的才行
            # print(player)
            # print(powersettemp)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[powersettemp['x']][powersettemp['y']]

            path = getpath(start, end)
            # print('传回来的flaggetsolution是否有用呢', flag_getsolution)
            if flag_getsolution:
                # print('flag_getsolution 是ok的')
                powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。

                ac = get_actionfrompath()
                return ac
            else:
                if Attack:
                    # print('攻击模式下,我们是没有用的,进行额是随机运动,')
                    # 后面要修改为攻击敌人的情况
                    if len(anamyplayers) == 0:
                        return random.randint(1, 4)
                    else:

                        anamytarget = findbestanamytarget(anamyplayers)
                        # 定位选择吃哪个player

                        # attack_positionA,attack_positionB,attack_positionC,attack_positionD,attack_positionOriginal=get_anamynextmoveposition(anamytarget)
                        attack_positionA, attack_positionB, attack_positionC, attack_positionD = get_attackanamyposition2V2(
                            anamytarget)
                        attack_positionOriginal = {'x': anamytarget['x'], 'y': anamytarget['y']}
                        targetnearestplayer = get_nearestanamy_player()

                        flag_get_Attackanamy = True

                        powersetX = []
                        return get_attackactionmap2Upgrade_partb(playerX, anamyplayers, powersetX)

                    # ac = random.randint(1, 4)
                    # return ac
                else:
                    # print('我们在逃跑模式下,但是返回None')
                    # w我们要逃跑，所以留给后面的逃跑的情况给出action
                    return None


def get_poweractionmap1V2(playerX, anamyplayers, powersetX):
    import random
    global powersetin
    global powersetout
    global playerworm
    global playerout
    global playerattackup
    global playerattackdown
    global attack_positionA, attack_positionB, attack_positionC, attack_positionD, attack_positionOriginal, targetnearestplayer, flag_get_Attackanamy

    global mapfeature

    global playerwormtarget
    global flag_playerinworm
    global flag_getsolution
    global path

    global Intera  # 惯性概念

    # flag_playerinworm=True
    path = []
    action = []
    if playerX == playerworm:
        # print('我们在actionfind当中，应当首先进行的就是要判断这个player是不是已经进入到了我们的tunnel内部了')
        if flag_playerinworm:  # 如果我们已经在wormhole里面了

            # 这个函数保证的是能够返回距离当前player最近的power
            # print('这个时候我已经能够进入到player进入虫洞内部了')
            if len(powersetin) == 0:
                # print('这个时候已经没有powersetin了')
                # 这个时候就去到外面去抓人,这个时候加入进攻的功能，

                # print('pwoersetin是空的,导致目前的动作是空的')  #这个时候，理论上应该能够
                return random.randint(1, 4)
            else:

                powersettemp = findnearestpoweri(playerX)
                # print(player)
                # print(powersettemp)
                start = mapfeature[playerX['x']][playerX['y']]
                end = mapfeature[powersettemp['x']][powersettemp['y']]

                # mapshow(mapfeature)
                path = getpath(start, end)

                # 这个时候我们打印出path的位置
                # for i in range(len(path)):
                #     print('path的实际的位置','  x :',path[i].x,'y  :',path[i].y)
                # print('传回来的flaggetsolution是否有用呢', flag_getsolution)
                if flag_getsolution:

                    powersetin.remove(powersettemp)
                    # print('flag_getsolution 是ok的')
                    ac = get_actionfrompath()
                    return ac
                else:
                    if Attack:
                        # print('攻击模式下,我们是没有用的,进行额是随机运动,')
                        # 后面要修改为攻击敌人的情况，顺带的攻击敌人
                        ac = random.randint(1, 4)
                        return ac
                    else:
                        # print('我们准备在计划躲避的时候 action的给出None的情况')
                        # w我们要逃跑，所以留给后面的逃跑的情况给出action
                        return None

                    # print('打印一下当前坤的路径')
                    # mapshow(mapfeature)
        else:  # 这个时候我们的player 还没有进入到wormwhole 内部
            # print('这个是要进入虫洞的一个player，正在努力进入到虫洞内部的路径')
            # print(player)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[playerwormtarget['x']][playerwormtarget['y']]

            # mapshow(mapfeature)
            path = getpath(start, end)

            if flag_getsolution:
                # for i in range(len(path)):
                #     print('path的实际的位置','  x :',path[i].x,'y  :',path[i].y)
                # print('flag_getsolution 是ok的')
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
                    return random.randint(1, 4)
    else:
        if len(powersetX) == 0:  # 如果已经空了 则根据模式，如果是攻击模式，则进行攻击。如果不是攻击模式，则尽量原远离自己的伙伴和墙壁，是否可以采用

            if Attack:  # 这个可以加入养猪计划
                # return get_attackactionmap2(playerX=playerX,anamyplayers=anamyplayers,powersetX=powersetX)
                if playerX == None:
                    pass
                else:

                    # return get_poweractionmap2UpgradeV2(playerX=playerX, anamyplayers=anamyplayers, powersetX=powersetX)

                    return get_attackactionmap2Upgrade_parta(playerX=playerX, anamyplayers=anamyplayers,
                                                             powersetX=powersetX)

            else:
                # print('我们再防守模式下，powerset中啥都没有')
                # 这个时候，实际上，我们可以返回None --这个时候我也建议返回None
                # print('在防守模式中，powerset为空，应当返回None才对')
                return None
                # return random.randint(0,4)

        else:
            # print('打印一下当前的powersetX',powersetX)
            powersettemp = findnearestpowerX(playerX, powersetX)  # 实际上，我们寻找power的方式要是基于power的才行
            # print(player)
            # print(powersettemp)
            start = mapfeature[playerX['x']][playerX['y']]
            end = mapfeature[powersettemp['x']][powersettemp['y']]

            #
            path = getpath(start, end)
            # print('传回来的flaggetsolution是否有用呢', flag_getsolution)
            if flag_getsolution:

                ac = get_actionfrompath()
                return ac
            else:
                # print('吃豆子的情况下没有找到solution，不应该出现这种情况把')
                if Attack:

                    ac = random.randint(1, 4)
                    return ac
                else:

                    return None


# 这个函数作用是希望能够通过player对powerset进行吃
# 追击敌人的情况下，我们还是需要两个player进行追击，
# 如果我们的player被吃掉了也就不足四个玩家的情况呢？？？（后面再考虑好了）
# get_attackaction 的主要的作用就吃敌人的作用的，这个函数的直接的作用就是对给定的player进行攻击规划
def get_attackaction(player, anamyplayers):
    import random
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
    path = []
    action = []

    if playerattackup == player:
        if len(anamyplayers) == 0:
            return get_poweractionmap1(player, anamyplayers)

        else:
            Uptarget, Downtarget = get_attacktargetposiontV1(anamyplayers)

            start = mapfeature[player['x']][player['y']]
            end = mapfeature[Uptarget['x']][Uptarget['y']]

            path = getpath(start, end)
            if flag_getsolution:
                # print('在攻击的时候playerUp,flag_getsolution 是ok的')
                # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
                for i in range(len(path)):
                    print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')
                return
                ac = random.randint(1, 4)
                return ac

    if playerattackdown == player:
        if len(anamyplayers) == 0:
            return get_poweractionmap1(player, anamyplayers)

        else:
            Uptarget, Downtarget = get_attacktargetposiontV1(anamyplayers)

            start = mapfeature[player['x']][player['y']]
            end = mapfeature[Downtarget['x']][Downtarget['y']]

            path = getpath(start, end)
            if flag_getsolution:
                # print('在攻击的时候playerDown,flag_getsolution 是ok的')
                # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
                for i in range(len(path)):
                    print('path的实际的位置', '  x :', path[i].x, 'y  :', path[i].y)
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                # print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')
                return
                ac = random.randint(1, 4)
                return ac


def additional_attackV1(player, Uptarget, Downtarget):
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

    addtionalup, additionaldown = get_Updownposion(Uptarget)

    start = mapfeature[player['x']][player['y']]
    end = mapfeature[addtionalup['x']][additionaldown['y']]

    path = getpath(start, end)
    if flag_getsolution:

        # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
        # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。

        ac = get_actionfrompath()
        return ac
    else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

        ac = random.randint(1, 4)
        return ac


# 函数：能够优化找到最好攻击的敌人
# 需要考虑：
# 1、# 能够看到的敌人的位置
# 2、跑到距离敌人更加靠近中心的地方。
# 3、判断我方的人数，如果我方包含3个人，则额外出来一个player走wormhole 进行进攻这样的路线。
#  需要选择距离要抓的敌人最近的三个人
# 得到希望攻击的敌人,发返回要追击的敌人,这个是在主函数中进行调用确定. 只要给出目标位置的坐标 两个坐标
global oldUptarget
global oldDowntarget


def get_attacktargetposiontV1(anamyplayers):
    global anamy
    global playerattackup
    global playerattackdown
    global oldUptarget
    global oldDowntarget
    global flag_anamycirclefind
    flag_anamycirclefind = False
    if len(anamyplayers) == 0:
        if not flag_anamycirclefind:  # 防止每次都要循环发现敌人的位置，这个时候我们就只有当我们再次丢了的时候我们才再次进行敌方player的寻找
            Uptargetx, Uptargety, Downtargetx, Downtargety = find_anamy()  # 这个函数作用就是
            Uptarget = {'x': Uptargetx, 'y': Uptargety}
            Downtarget = {'x': Downtargetx, 'y': Downtargety}
            oldUptarget = Uptarget
            oldDowntarget = Downtarget
            flag_anamycirclefind = True
            return Uptarget, Downtarget
        else:

            Uptarget = oldUptarget
            Downtarget = oldDowntarget
            return Uptarget, Downtarget
    else:

        ##找到的情况下
        targetanamy = anamyplayers[0]
        # print('打印一下敌人的情况.    ',targetanamy)
        # print('打印一下我方的情况  playerattackup  '  ,playerattackup)
        # print('打印一下我方的情况  playerattackup  ', playerattackdown)

        distanceUp = stepdistance(playerattackup, targetanamy)
        distanceDown = stepdistance(playerattackdown, targetanamy)
        dismin = distanceUp + distanceDown
        for anamyplayer in anamyplayers:
            distanceUp = stepdistance(playerattackup, anamyplayer)
            distanceDown = stepdistance(playerattackdown, anamyplayer)
            dis = distanceUp + distanceDown
            if dis < dismin:
                dismin = dis
                targetanamy = anamyplayer

        Uptarget, Downtarget = get_Updownposion(targetanamy)

        # 表示我们找到了不需要重新找,如果再次丢了可以再找
        if dismin <= 4:
            flag_anamycirclefind = False

        return Uptarget, Downtarget


# This function 的目标是希望能够找到敌人
# 得到的是下一步的运动的坐标,也即是我们向那边找
def find_anamy():
    global playerattackup
    global playerattackdown
    global map_width
    global map_height

    factor_inside = 2

    x = playerattackup['x']
    y = playerattackup['y']
    if x < map_width / 2 and y < map_height / 2:  # 如果其本身就在左上角
        Uptargetx = map_width - factor_inside  # 将其移动到右下角
        Uptargety = map_height - factor_inside
    elif x > map_width / 2 and y < map_height / 2:  # 如果本身在右上角
        Uptargetx = factor_inside  # 则将其移动到左下
        Uptargety = map_height - factor_inside
    elif x < map_width / 2 and y > map_height / 2:  # 如果本身在左下角
        Uptargetx = map_width - factor_inside  # 则将其移动到右上角
        Uptargety = factor_inside
    else:  # 本身在右下角
        Uptargetx = factor_inside  # 将其移动到左上脚
        Uptargety = factor_inside

    x = playerattackdown['x']
    y = playerattackdown['y']
    if x <= map_width / 2 and y <= map_height / 2:  # 如果其本身就在左上角
        Downtargetx = map_width - factor_inside  # 将其移动到右下角
        Downtargety = map_height - factor_inside
    elif x > map_width / 2 and y < map_height / 2:  # 如果本身在右上角
        Downtargetx = factor_inside  # 则将其移动到左下
        Downtargety = map_height - factor_inside
    elif x < map_width / 2 and y > map_height / 2:  # 如果本身在左下角
        Downtargetx = map_width - factor_inside  # 则将其移动到右上角
        Downtargety = factor_inside
    else:  # 本身在右下角
        Downtargetx = factor_inside  # 将其移动到左上脚
        Downtargety = factor_inside

    return Uptargetx, Uptargety, Downtargetx, Downtargety


# this function 的作用是根据攻击的敌人的目标得到这两个playerUP 和 down 的各自的作用
def get_Updownposion(targetanmay):
    global map_width
    global map_height

    # print('打印一下targetanamay 的情况   ', targetanmay )

    # 判断敌人所在位置范围
    x = targetanmay['x']
    y = targetanmay['y']
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

        Uptargetx = x  # 目标位置设定为 右侧
        Uptargety = y
        Downtargetx = x + 1  # 目标位置设定右下
        Downtargety = y

    if x <= map_width / 2 and y <= map_height / 2 and x >= y:  # 如果其本身就在左上角 ,从右逼到左
        Uptargetx = x  # 目标位置设定为 下侧
        Uptargety = y
        Downtargetx = x  # 目标位置设定左下
        Downtargety = y + 1

    if x >= map_width / 2 and y <= map_height / 2 and x / 2 >= y:  # 如果其本身就在右上角 ,从左逼到右
        Uptargetx = x  # 目标位置设定为 下侧
        Uptargety = y
        Downtargetx = x  # 目标位置设定右下
        Downtargety = y + 1

    if x >= map_width / 2 and y <= map_height / 2 and x / 2 <= y:  # 如果其本身就在右上角 ,从下逼到上
        Uptargetx = x  # 目标位置设定为 左侧
        Uptargety = y
        Downtargetx = x - 1  # 目标位置设定左下
        Downtargety = y

        # 在地图下方的情况
    if x <= map_width / 2 and y >= map_height / 2 and x <= y / 2:  # 如果其本身就在左下角 ,上逼到下
        Uptargetx = x  # 目标位置设定为 左侧
        Uptargety = y
        Downtargetx = x + 1  # 目标位置设定左下
        Downtargety = y
        Uptarget = {'x': Uptargetx, 'y': Uptargety}
        Downtarget = {'x': Downtargetx, 'y': Downtargety}

    if x <= map_width / 2 and y >= map_height / 2 and x >= y / 2:  # 如果其本身就在左下角 ,从右逼到左
        Uptargetx = x  # 目标位置设定为 右侧
        Uptargety = y
        Downtargetx = x  # 目标位置设定y右下
        Downtargety = y - 1

    if x >= map_width / 2 and y >= map_height / 2 and x >= y:  # 如果其本身就在右下角 ,从左逼到右
        Uptargetx = x  # 目标位置设定为 右侧
        Uptargety = y
        Downtargetx = x  # 目标位置设定左下
        Downtargety = y - 1

    if x >= map_width / 2 and y >= map_height / 2 and x <= y:  # 如果其本身就在右下角 ,从上逼到下
        Uptargetx = x  # 目标位置设定为 右侧
        Uptargety = y
        Downtargetx = x - 1  # 目标位置设定右下
        Downtargety = y

    if Downtargetx < 0:
        Downtargetx = 0
    if Downtargety < 0:
        Downtargety = 0
    if Downtargetx >= map_width:
        Downtargetx = map_width - 1
    if Downtargety >= map_height:
        Downtargety = map_width - 1

    Uptarget = {'x': Uptargetx, 'y': Uptargety}
    Downtarget = {'x': Downtargetx, 'y': Downtargety}
    return Uptarget, Downtarget

    # 还要考虑敌人突然不在视野内的情况下
    # 这个时候还要考虑如果前面是虫洞的情况下,我们也要跟过去,这个时候需要利用的player自身的视野
    # 同样,如果我们逃跑,也要走向


# 这个函数的作用是在我们得到了一个某条path的情况下，得出下一条路径path
def get_actionfrompath():
    global path
    global Attack
    global map_height
    global map_width

    currentspot = path[len(path) - 1]

    nextspot = path[len(path) - 2]
    startx = currentspot.x
    starty = currentspot.y
    endx = nextspot.x
    endy = nextspot.y
    # print('执行wormhole前')
    # print('单步走的时候，currentsopt的位置  x',startx,'  y:',starty)
    # print('单步走的时候，nextsopt的位置  x',endx,'  y:',endy)
    if iswormhole(endx, endy):
        # print('下一步是虫洞')
        if distancecalculate(x1=endx, y1=endy, x2=startx, y2=starty) == 1:

            pass
        elif distancecalculate(x1=endx, y1=endy, x2=startx, y2=starty) == 0:
            # 得到当前可以移动的范围内
            # print('当前的距离是00000')
            movaableaction = []
            x = startx
            y = starty
            if y > 0:  # 向上

                if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                    y - 1].tunnel == 'down'):
                    movaableaction.append(1)
            if y < map_height - 1:  # 向下
                if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][y + 1].tunnel == 'up'):
                    movaableaction.append(2)
            if x > 0:  # 向左移动
                if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                    y].tunnel == 'right'):
                    movaableaction.append(3)
            if x < map_width - 1:  # 向右移动
                if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                    y].tunnel == 'left'):
                    movaableaction.append(4)
            if len(movaableaction) == 0:
                pass
            else:
                return movaableaction[random.randint(0, len(movaableaction) - 1)]

        else:
            newend = findwormpair(endx, endy)
            endx = newend['x']
            endy = newend['y']
    # print('执行istunnel 前')
    # print('单步走的时候，currentsopt的位置  x', startx, '  y:', starty)
    # print('单步走的时候，nextsopt的位置  x', endx, '  y:', endy)

    # 这句话用来判断下一步是不是tunnel的终点，如果是的我们就不走这个
    if istunnelneighbour(startx=startx, starty=starty, endx=endx, endy=endy):
        endx, endy = viatunnelnewaction(startx=startx, starty=starty, endx=endx, endy=endy)

    if startx == endx:
        if starty > endy:  # 向上移动

            print('mvoe up')
            return 1
        else:

            print('move down')
            return 2
    else:
        if startx > endx:

            print('mvoe left')
            return 3
        else:

            print('move right')
            return 4


def get_actionfrompathold():
    global path
    global Attack

    currentspot = path[len(path) - 1]

    nextspot = path[len(path) - 2]
    startx = currentspot.x
    starty = currentspot.y
    endx = nextspot.x
    endy = nextspot.y

    if startx == endx:
        if starty > endy:  # 向上移动

            # print('mvoe up')
            return 1
        else:

            # print('move down')
            return 2
    else:
        if startx > endx:

            # print('mvoe left')
            return 3
        else:

            # print('move right')
            return 4


def findnearestpowero(player):
    global powersetout
    global powersetin
    global playerworm

    powerbest = []

    dis = 10000000000000
    # print('在寻找距离最近的powerout的情况下，我们打印一下powerserout以便更好判断我们得到的是不是最好的')
    # print(powersetout)
    for power in (powersetout):

        tempdis = abs(player['x'] - power['x']) + abs(player['y'] - power['y'])
        if tempdis < dis:
            dis = tempdis

            powerbest = power
    return powerbest


def findnearestpoweri(player):
    global powersetout
    global powersetin
    global playerworm
    global flagp_layerinworm

    powerbest = []

    dis = 1000000000
    # 这个player已经进入了wormwhole里面并且进入了tunnel内部
    if flag_playerinworm:
        if player == playerworm:
            for power in (powersetin):
                tempdis = abs(player['x'] - power['x']) + abs(player['y'] - power['y'])
                if tempdis < dis:
                    dis = tempdis
                    powerbest = power
            return powerbest
    else:
        pass


# 我们将给定的player作为start 起点
# 我们将给定的powet 作为end  终点
# 其中start 和  end 都是grid 类型的对象
global path
path = []


def getpath(start, end):
    global mapfeature
    global flag
    global flag_getsolution
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    flag_getsolution = False
    openSet = []
    closedSet = []
    openSet.append(start)

    # print('进入时候的openset')
    # print(openSet)

    # 进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous = []

    while True:
        if len(openSet) > 0:
            winner = 0
            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            # current 是最小的节点
            current = openSet[winner]

            # 判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag = 1
                # 确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou = 100
                while temp.previous:
                    cou = cou - 1
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

            # 理论上直接就右neighbours
            neighbours = current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            # 循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):

                neighbour = neighbours[i]

                #   print(type(neighbour))

                # 当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or (neighbour.context == '*') or (neighbour.anamy) or (
                        neighbour.tunnel != 'no'):  # (neighbour.tunnel != 'no') 这句话的作用就是为了保证敌人不会向墙上撞
                    #    print('就在这里')
                    pass
                else:
                    # 当前的邻居不在closedset中

                    tempG = current.g + 1
                    # 当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        # 其在open set
                        if tempG < neighbour.g:
                            neighbour.g = tempG
                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)

                    # if neighbour.wormhole:
                    #     dis = stepdistance({'x': neighbour.x, 'y': neighbour.y}, {'x': end.x, 'y': end.y})
                    #     neighbour.h = dis
                    # else:

                    neighbour.h = heuristic(neighbour, end)

                    # if h==0:
                    #     neighbour.previous = current
                    #
                    #     break
                    neighbour.f = neighbour.g + neighbour.h
                    # came from
                    neighbour.previous = current


        else:
            flag_getsolution = False
            print('no solution')
            break


# 这个函数是为了判断当前地图所处在的类型。
# 我们应当判断出地图中是否存在死区的这种情况
def getpathmapdecide(start, end):
    global mapfeature
    global flag
    global openSet
    global closedSet
    global flag_getsolution
    global path
    global map_width
    global map_height
    openSet = []
    closedSet = []
    openSet.append(start)

    # 进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous = []

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
            # current 是最小的节点
            current = openSet[winner]

            # 判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag = 1

                # 确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou = 100
                while temp.previous:
                    cou = cou - 1
                    path.append(temp.previous)
                    temp = temp.previous

                #    print(' we  have out of the path')
                #    print(' we  have out of the path')
                # for i in range(len(path)):
                #     #   print('x' + str(path[i].i) + 'y' + str(path[i].j))
                #     path[i].context = '-'
                flag_getsolution = True

                # mapshow(mapfeature)
                return path
                #  gridshow(grid)

                break

                # find the path

            ##将该节点移出openset
            openSet.remove(current)
            ##将该节点移入closedset
            closedSet.append(current)

            # 理论上直接就右neighbours
            neighbours = current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            # 循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):

                neighbour = neighbours[i]

                #   print(type(neighbour))

                # 当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or (neighbour.context == '*') or (
                neighbour.anamy) or neighbour.tunnel != 'no' or neighbour.wormhole:
                    #    print('就在这里')
                    pass
                else:
                    # 当前的邻居不在closedset中

                    tempG = current.g + 1
                    # 当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        # 其在open set
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
                    # came from
                    neighbour.previous = current

            # to show actual situation
            # for i in range(len(openSet)):
            #     grid[path[i].i][path[i].j].context = '*'

            #     print(i.context)

            # 展示一下当前的的grid


        else:
            flag_getsolution = False

            print('no solution')
            break

            pass


def getpathnoanamy(start, end):
    global mapfeature
    global flag
    global flag_getsolution
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    flag_getsolution = False
    openSet = []
    closedSet = []
    openSet.append(start)

    # print('进入时候的openset')
    # print(openSet)

    # 进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous = []

    while True:
        if len(openSet) > 0:
            winner = 0
            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            # current 是最小的节点
            current = openSet[winner]

            # 判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag = 1
                # 确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou = 100
                while temp.previous:
                    cou = cou - 1
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

            # 理论上直接就右neighbours
            neighbours = current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            # 循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):

                neighbour = neighbours[i]

                #   print(type(neighbour))

                # 当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or (neighbour.context == '*') or (
                        neighbour.tunnel != 'no'):
                    #    print('就在这里')
                    pass
                else:
                    # 当前的邻居不在closedset中

                    tempG = current.g + 1
                    # 当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        # 其在open set
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
                    # came from
                    neighbour.previous = current


        else:
            flag_getsolution = False
            print('no solution')
            break


def getpathnotruemyplayer(start, end):
    global mapfeature
    global flag
    global flag_getsolution
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    flag_getsolution = False
    openSet = []
    closedSet = []
    openSet.append(start)

    # print('进入时候的openset')
    # print(openSet)

    # 进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous = []

    while True:
        if len(openSet) > 0:
            winner = 0
            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            # current 是最小的节点
            current = openSet[winner]

            # 判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag = 1
                # 确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou = 100
                while temp.previous:
                    cou = cou - 1
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

            # 理论上直接就右neighbours
            neighbours = current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            # 循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):

                neighbour = neighbours[i]

                #   print(type(neighbour))

                # 当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or (neighbour.context == '*') or (
                neighbour.truemyplayer) or (neighbour.tunnel != 'no'):
                    #    print('就在这里')
                    pass
                else:
                    # 当前的邻居不在closedset中

                    tempG = current.g + 1
                    # 当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        # 其在open set
                        if tempG < neighbour.g:
                            neighbour.g = tempG
                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)

                    # if neighbour.wormhole:
                    #     dis = stepdistance({'x': neighbour.x, 'y': neighbour.y}, {'x': end.x, 'y': end.y})
                    #     neighbour.h = dis
                    # else:

                    neighbour.h = heuristic(neighbour, end)

                    # if h==0:
                    #     neighbour.previous = current
                    #
                    #     break
                    neighbour.f = neighbour.g + neighbour.h
                    # came from
                    neighbour.previous = current


        else:
            flag_getsolution = False
            print('no solution')
            break


def getpathnoattackwall(start, end):
    global mapfeature
    global flag
    global flag_getsolution
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    flag_getsolution = False
    openSet = []
    closedSet = []
    openSet.append(start)

    # print('进入时候的openset')
    # print(openSet)

    # 进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous = []

    while True:
        if len(openSet) > 0:
            winner = 0
            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            # current 是最小的节点
            current = openSet[winner]

            # 判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag = 1
                # 确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou = 100
                while temp.previous:
                    cou = cou - 1
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

            # 理论上直接就右neighbours
            neighbours = current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            # 循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):

                neighbour = neighbours[i]

                #   print(type(neighbour))

                # 当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or (neighbour.context == '*') or (
                neighbour.attackwall) or (neighbour.tunnel != 'no'):
                    #    print('就在这里')
                    pass
                else:
                    # 当前的邻居不在closedset中

                    tempG = current.g + 1
                    # 当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        # 其在open set
                        if tempG < neighbour.g:
                            neighbour.g = tempG
                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)

                    # if neighbour.wormhole:
                    #     dis = stepdistance({'x': neighbour.x, 'y': neighbour.y}, {'x': end.x, 'y': end.y})
                    #     neighbour.h = dis
                    # else:

                    neighbour.h = heuristic(neighbour, end)

                    # if h==0:
                    #     neighbour.previous = current
                    #
                    #     break
                    neighbour.f = neighbour.g + neighbour.h
                    # came from
                    neighbour.previous = current


        else:
            flag_getsolution = False
            print('no solution')
            break


def getpathnotrueanamyplayer(start, end):
    global mapfeature
    global flag
    global flag_getsolution
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    flag_getsolution = False
    openSet = []
    closedSet = []
    openSet.append(start)

    # print('进入时候的openset')
    # print(openSet)

    # 进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous = []

    while True:
        if len(openSet) > 0:
            winner = 0
            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            # current 是最小的节点
            current = openSet[winner]

            # 判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag = 1
                # 确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou = 100
                while temp.previous:
                    cou = cou - 1
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

            # 理论上直接就右neighbours
            neighbours = current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            # 循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):

                neighbour = neighbours[i]

                #   print(type(neighbour))

                # 当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or (neighbour.context == '*') or (
                neighbour.trueanamyplayer) or (neighbour.tunnel != 'no'):
                    #    print('就在这里')
                    pass
                else:
                    # 当前的邻居不在closedset中

                    tempG = current.g + 1
                    # 当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        # 其在open set
                        if tempG < neighbour.g:
                            neighbour.g = tempG
                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)

                    # if neighbour.wormhole:
                    #     dis = stepdistance({'x': neighbour.x, 'y': neighbour.y}, {'x': end.x, 'y': end.y})
                    #     neighbour.h = dis
                    # else:

                    neighbour.h = heuristic(neighbour, end)

                    # if h==0:
                    #     neighbour.previous = current
                    #
                    #     break
                    neighbour.f = neighbour.g + neighbour.h
                    # came from
                    neighbour.previous = current


        else:
            flag_getsolution = False
            print('no solution')
            break


def getpathnoattackwallnotruemyplayer(start, end):
    global mapfeature
    global flag
    global flag_getsolution
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    flag_getsolution = False
    openSet = []
    closedSet = []
    openSet.append(start)

    # print('进入时候的openset')
    # print(openSet)

    # 进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous = []

    while True:
        if len(openSet) > 0:
            winner = 0
            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            # current 是最小的节点
            current = openSet[winner]

            # 判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag = 1
                # 确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou = 100
                while temp.previous:
                    cou = cou - 1
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

            # 理论上直接就右neighbours
            neighbours = current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            # 循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):

                neighbour = neighbours[i]

                #   print(type(neighbour))

                # 当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or (neighbour.context == '*') or (
                neighbour.truemyplayer) or (neighbour.tunnel != 'no') or (neighbour.attackwall):
                    #    print('就在这里')
                    pass
                else:
                    # 当前的邻居不在closedset中

                    tempG = current.g + 1
                    # 当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        # 其在open set
                        if tempG < neighbour.g:
                            neighbour.g = tempG
                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)

                    # if neighbour.wormhole:
                    #     dis = stepdistance({'x': neighbour.x, 'y': neighbour.y}, {'x': end.x, 'y': end.y})
                    #     neighbour.h = dis
                    # else:

                    neighbour.h = heuristic(neighbour, end)

                    # if h==0:
                    #     neighbour.previous = current
                    #
                    #     break
                    neighbour.f = neighbour.g + neighbour.h
                    # came from
                    neighbour.previous = current


        else:
            flag_getsolution = False
            print('no solution')
            break


def getpathnoattackwallnoanamyplayer(start, end):
    global mapfeature
    global flag
    global flag_getsolution
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    flag_getsolution = False
    openSet = []
    closedSet = []
    openSet.append(start)

    # print('进入时候的openset')
    # print(openSet)

    # 进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous = []

    while True:
        if len(openSet) > 0:
            winner = 0
            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            # current 是最小的节点
            current = openSet[winner]

            # 判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag = 1
                # 确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou = 100
                while temp.previous:
                    cou = cou - 1
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

            # 理论上直接就右neighbours
            neighbours = current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            # 循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):

                neighbour = neighbours[i]

                #   print(type(neighbour))

                # 当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or (neighbour.context == '*') or (
                neighbour.attackwall) or (neighbour.tunnel != 'no') or (neighbour.trueanamyplayer):
                    #    print('就在这里')
                    pass
                else:
                    # 当前的邻居不在closedset中

                    tempG = current.g + 1
                    # 当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        # 其在open set
                        if tempG < neighbour.g:
                            neighbour.g = tempG
                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)

                    # if neighbour.wormhole:
                    #     dis = stepdistance({'x': neighbour.x, 'y': neighbour.y}, {'x': end.x, 'y': end.y})
                    #     neighbour.h = dis
                    # else:

                    neighbour.h = heuristic(neighbour, end)

                    # if h==0:
                    #     neighbour.previous = current
                    #
                    #     break
                    neighbour.f = neighbour.g + neighbour.h
                    # came from
                    neighbour.previous = current


        else:
            flag_getsolution = False
            print('no solution')
            break


def getpathnoattackwallnotruemyplayernoanamyplayer(start, end):
    global mapfeature
    global flag
    global flag_getsolution
    global openSet
    global closedSet
    global path
    global map_width
    global map_height
    flag_getsolution = False
    openSet = []
    closedSet = []
    openSet.append(start)

    # print('进入时候的openset')
    # print(openSet)

    # 进入程序之前我们应该把所有的previous都要清空掉
    for x in range(map_width):
        for y in range(map_height):
            mapfeature[x][y].previous = []

    while True:
        if len(openSet) > 0:
            winner = 0
            # 找到最小的节点
            for i in range(len(openSet)):
                if openSet[i].f < openSet[winner].f:
                    winner = i
            # current 是最小的节点
            current = openSet[winner]

            # 判断当前节点是不是最终的节点
            if (current.x == end.x) & (current.y == end.y):
                # print("we have DONE this test")
                flag = 1
                # 确定是最佳的节点
                path = []
                temp = current
                path.append(temp)

                cou = 100
                while temp.previous:
                    cou = cou - 1
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

            # 理论上直接就右neighbours
            neighbours = current.neighbours
            # print('打印当前的current的位置')
            # print(current.j)
            # print(current.i)
            # print('打印它的邻居')
            # print(neighbours)

            # 循环当前节点的所有的相邻的节点

            for i in range(len(neighbours)):

                neighbour = neighbours[i]

                #   print(type(neighbour))

                # 当前节点是否在closedset节点里面
                if (neighbour in closedSet) or neighbour.wall or (neighbour.context == '*') or (
                neighbour.truemyplayer) or (neighbour.tunnel != 'no') or (neighbour.attackwall):
                    #    print('就在这里')
                    pass
                else:
                    # 当前的邻居不在closedset中

                    tempG = current.g + 1
                    # 当前的节点是否在openset 即将被估计的数值当中
                    if neighbour in openSet:
                        # 其在open set
                        if tempG < neighbour.g:
                            neighbour.g = tempG
                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)

                    # if neighbour.wormhole:
                    #     dis = stepdistance({'x': neighbour.x, 'y': neighbour.y}, {'x': end.x, 'y': end.y})
                    #     neighbour.h = dis
                    # else:

                    neighbour.h = heuristic(neighbour, end)

                    # if h==0:
                    #     neighbour.previous = current
                    #
                    #     break
                    neighbour.f = neighbour.g + neighbour.h
                    # came from
                    neighbour.previous = current


        else:
            flag_getsolution = False
            print('no solution')
            break


def heuristic(a, b):
    # d=math.sqrt((a.i-b.i)*(a.i-b.i)+(a.j-b.j)*(a.j-b.j))
    d = abs(a.x - b.x) + abs((a.y - b.y))
    #  print(d)
    return d


def stepdistance(A, B):
    global path
    global mapfeature

    start = mapfeature[A['x']][A['y']]
    end = mapfeature[B['x']][B['y']]

    if start.x == end.x and start.y == end.y:
        dis = 0
    path = getpath(start, end)
    if flag_getsolution:
        dis = len(path) - 1
        return dis
    else:
        return 20


def stepdistanceabsolute(A, B):
    d = abs(A['x'] - B['x']) * abs(A['x'] - B['x']) + abs(A['y'] - B['y']) * abs(A['y'] - B['y'])
    return d


def distancecalculate(x1, y1, x2, y2):
    d = abs(x1 - x2) + abs(y1 - y2)
    return d


# 这个函数，采用从少的移动方向到多的移动情况进行退化，这样就可以能够比较完美的使用deadmove了。
def player_avoidactionNew5(player, anamyplayers, actionpower, myplayers):
    global visionrange
    global mapfeature
    global map_width
    global map_height
    global playerworm
    global visionrange
    global anamys_motionpatterns
    x = player['x']
    y = player['y']
    # print('实际坐标x：' + str(x) + '    y' + str(y))
    movaableactiona = []
    # print('筛选动作前，看一下敌人的位置')
    # print('敌人的情况',anamyplayers)
    # mapshow(mapfeature)
    # 实际情况下，这个地方并不应该要是整体视野内的敌人的情况，而是某一个自身的playerx的情况，这个时候，我们是否要重复计算每一个player啊
    seeanamys = []

    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= player['x'] + visionrange and anamyplayer['x'] >= player['x'] - visionrange and \
                anamyplayer['y'] <= player['y'] + visionrange and anamyplayer['y'] >= player['y'] - visionrange:
            seeanamys.append(anamyplayer)

    if len(seeanamys) < 2:
        # 毕竟没有三个人来追我，我就尽量浪费敌人的步骤，所以不用采用更严苛的逃跑的步骤
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1]) or wormholeanamylimit(
                mapfeature[x][y - 1])):
                movaableactiona.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1]) or wormholeanamylimit(
                mapfeature[x][y + 1])):
                movaableactiona.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y]) or wormholeanamylimit(
                mapfeature[x - 1][y])):
                movaableactiona.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y]) or wormholeanamylimit(
                mapfeature[x + 1][y])):
                movaableactiona.append(4)
        movaableaction = movaableactiona
    else:
        # 视野内有二个敌人了这个时候，这个时候，需要尽快使用严格的套件赶紧跑路
        updateanamypositionUpgradehardV1a(anamyplayers, myplayers)
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1]) or wormholeanamylimit(
                mapfeature[x][y - 1])):
                movaableactiona.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1]) or wormholeanamylimit(
                mapfeature[x][y + 1])):
                movaableactiona.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y]) or wormholeanamylimit(
                mapfeature[x - 1][y])):
                movaableactiona.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y]) or wormholeanamylimit(
                mapfeature[x + 1][y])):
                movaableactiona.append(4)
        movaableaction = movaableactiona
        if len(movaableaction) == 0:
            movaableactiona = []
            updateanamypositionUpgrade(anamyplayers)
            if y > 0:  # 向上
                if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                    y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1]) or wormholeanamylimit(
                    mapfeature[x][y - 1])):
                    movaableactiona.append(1)
            if y < map_height - 1:  # 向下
                if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                    y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1]) or wormholeanamylimit(
                    mapfeature[x][y + 1])):
                    movaableactiona.append(2)
            if x > 0:  # 向左移动
                if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                    y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y]) or wormholeanamylimit(
                    mapfeature[x - 1][y])):
                    movaableactiona.append(3)
            if x < map_width - 1:  # 向右移动
                if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                    y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y]) or wormholeanamylimit(
                    mapfeature[x + 1][y])):
                    movaableactiona.append(4)
            movaableaction = movaableactiona

    if len(seeanamys) == 0:
        if actionpower in movaableaction:  # 在上面的严苛的条件下，至少是安全的但是似乎没有考虑到field limit的情况
            return actionpower
        else:  # 这个时候我们应当尽量分散逃跑咯
            # 这个时候表示的是上面返回的是None,这个时候我们尽量对逃跑准则进行一定的规划 分散规划 对于不同的player朝着不同的方向进行跑去吗？？在前面power的规划的过程中，我们就已经进行了一定目标位置的规划的情况
            # 对于聚类的分析，我们是否有更好的分类的方式。是到底要分成几类也是很有关系的

            if len(movaableaction) > 1:
                movaableaction2 = fieldlimit(player, movaableaction)
                # print('经过tunnel筛选的动作：'+str(movaableaction2))
                if len(movaableaction2) == 0:
                    pass
                else:
                    movaableaction = movaableaction2

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
            movaableaction = deadmoveNew5(player, anamyplayers)
            if movaableaction is None:
                return None
            elif len(movaableaction) == 1:
                return movaableaction[0]

        # 如果等于1 表示我们的鲲只有一个方向可以走，这个时候要记录好，视野内的地方的鲲运动的方向
        # 并且给一定概率进行一个反向运动的情况
        # 还需要考虑到敌人是从外面把我们赶到墙上的i情况，这个时候如何更加优雅的判断呢？
        #
        # if len(movaableaction) == 1 and (
        #         player['x'] == 0 or player['x'] == map_width - 1 or player['y'] == 0 or player[
        #     'y'] == map_height - 1):
        #     mindis = 1000
        #     tempdis = 10
        #     flag_anamyindiagonal = False
        #     for anamyplayer in anamyplayers:
        #         x_dis = abs(player['x'] - anamyplayer['x'])
        #         y_dis = abs(player['y'] - anamyplayer['y'])
        #         tempdis = x_dis + y_dis
        #         if tempdis <= mindis:
        #             xmindis = x_dis
        #             ymindis = y_dis
        #             mindis = tempdis
        #             minanamy = anamyplayer
        #             if mindis == 2 and xmindis == 1 and ymindis == 1:
        #                 ndiagonalanamy = anamyplayer
        #                 flag_anamyindiagonal = True
        #                 print('我们还应当判断出来敌人的下一步不会吃到我们')
        #
        #     # print('mindis是多少', mindis)
        #     # print('我是x', x, 'y', y)
        #     # print('敌人是x', minanamy['x'], 'y', minanamy['y'])
        #     if mindis == 2 and flag_anamyindiagonal:
        #         for anamys_motionpattern in anamys_motionpatterns:
        #             if anamys_motionpattern['id'] == minanamy['id']:
        #                 if anamys_motionpattern['lastmove'] == anamys_motionpattern['lastlastmove'] and \
        #                         anamys_motionpattern['updatelast'] and anamys_motionpattern['updatelastlast']:
        #                     if (player['x'] == 0 or player['x'] == map_width - 1) and (
        #                             anamys_motionpattern['lastmove'] == 1 or anamys_motionpattern['lastmove'] == 2):
        #                         print('反向运动启动')
        #                         if movaableaction[0] == 1:
        #                             return 2
        #                         elif movaableaction[0] == 2:
        #                             return 1
        #                     if (player['y'] == 0 or player['y'] == map_height - 1) and (
        #                             anamys_motionpattern['lastmove'] == 3 or anamys_motionpattern['lastmove'] == 4):
        #                         print('反向运动启动')
        #                         if movaableaction[0] == 3:
        #                             return 4
        #                         elif movaableaction[0] == 4:
        #                             return 3
        #
        #
        #

        # 尽量不要贴边走否则容易被吃
        #  但是由于playerworm这个东西是特别的
        if player == playerworm:
            # mapshow(mapfeature)
            # print('这个时候打印一下当前可移动的i情况 和本身的位置',player)
            # print(movaableaction)
            # print('anaamyplayes 的情况', anamyplayers)
            # print('action power 是多少：'+str(actionpower))
            # print('本身是playerworm的情况')
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
            # 这个是为了防止敌人在很远的tunnel的敌方堵我
            if len(movaableaction) > 1:
                # print('我们使用tunnellimitV4')
                movaableaction2 = tunnellimitNew4(player, movaableaction, anamyplayers)
                # print('经过tunnellimit4筛选的结果', movaableaction2)
                if actionpower in movaableaction2:
                    # print('准备吃豆子的action', actionpower)
                    return actionpower

                if len(movaableaction2) == 1:
                    return movaableaction2[0]
                elif len(movaableaction2) > 1:
                    movaableaction = movaableaction2
                else:
                    a = random.randint(0, len(movaableaction) - 1)
                    # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                    # print('打印一下，我们将要选择执行经过tunnel筛选哪些动作，' + str(movaableaction[a]))
                    return movaableaction[a]
            elif len(movaableaction) == 1:
                return movaableaction[0]

            ##这个是为了防止太接近墙边
            if len(movaableaction) > 1:
                # print('我们准备使用fieldlimit')
                movaableaction3 = fieldlimit(player, movaableaction)
                # print('经过field筛选的动作：' + str(movaableaction3))
                if len(movaableaction3) == 1:
                    return movaableaction3[0]
                elif len(movaableaction3) > 1:
                    movaableaction = movaableaction3
                else:
                    a = random.randint(0, len(movaableaction) - 1)
                    # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                    # print('打印一下，我们将要选择执行经过tunnel筛选哪些动作，' + str(movaableaction[a]))
                    return movaableaction[a]
            elif len(movaableaction) == 1:
                return movaableaction[0]

            # 这个 是为了能够远离敌人的情况
            # if len(movaableaction) > 1:
            #     print('我们使用awayfromanamy')
            #     movaableaction4 = awayfrromanamy(player, movaableaction, seeanamys)  # 实际上，这个也在一定程度上防止了他还回到虫洞去
            #     print('经过gawayfromanamy筛选的动作 ' + str(movaableaction4))
            #     if len(movaableaction4) == 1:
            #         # print('')
            #         return movaableaction4[0]
            #     elif len(movaableaction4) > 1:
            #         movaableaction = movaableaction4
            #     else:
            #         a = random.randint(0, len(movaableaction) - 1)
            #         # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
            #         print('打印一下，我们将要选择执行经过tawayfrom筛选哪些动作，' + str(movaableaction[a]))
            #         return movaableaction[a]
            # elif len(movaableaction) == 1:
            #     return movaableaction[0]
            # 这个准备经过重力检测得到的结果
            if len(movaableaction) > 1:
                # print('我们使用centrogtravity')
                movaableaction5 = center_gravity(player, movaableaction)  # 实际上，这个也在一定程度上防止了他还回到虫洞去
                # print('经过gravity筛选的动作 ' + str(movaableaction5))
                if len(movaableaction5) == 1:

                    return movaableaction5[0]
                elif len(movaableaction5) > 1:
                    movaableaction = movaableaction5
                else:
                    a = random.randint(0, len(movaableaction) - 1)
                    # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                    # print('打印一下，我们将要选择执行经过tawayfrom筛选哪些动作，' + str(movaableaction[a]))
                    return movaableaction[a]
            elif len(movaableaction) == 1:
                return movaableaction[0]

            a = random.randint(0, len(movaableaction) - 1)
            # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
            # print('打印一下，我们将要选择执行经过tawayfrom筛选哪些动作，' + str(movaableaction[a]))
            return movaableaction[a]


# 这个函数，采用从少的移动方向到多的移动情况进行退化，这样就可以能够比较完美的使用deadmove了。
def player_avoidactionNew4(player, anamyplayers, actionpower, myplayers):
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
    # 实际情况下，这个地方并不应该要是整体视野内的敌人的情况，而是某一个自身的playerx的情况，这个时候，我们是否要重复计算每一个player啊
    seeanamys = []

    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= player['x'] + visionrange and anamyplayer['x'] >= player['x'] - visionrange and \
                anamyplayer['y'] <= player['y'] + visionrange and anamyplayer['y'] >= player['y'] - visionrange:
            seeanamys.append(anamyplayer)
    x = player['x']
    y = player['y']
    mindis = 1000
    tempdis = 10
    for anamyplayer in anamyplayers:
        x_dis = abs(player['x'] - anamyplayer['x'])
        y_dis = abs(player['y'] - anamyplayer['y'])
        tempdis = x_dis + y_dis
        if tempdis < mindis:
            mindis = tempdis
            minanamy = anamyplayer
    if mindis == 3:
        updateanamypositionUpgradehardV1a(anamyplayers, myplayers)
        '''第一轮筛选：使用更加严格的条件，然后采用deadmove'''
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1]) or wormholeanamylimit(
                mapfeature[x][y - 1])):
                movaableactiona.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1]) or wormholeanamylimit(
                mapfeature[x][y + 1])):
                movaableactiona.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y]) or wormholeanamylimit(
                mapfeature[x - 1][y])):
                movaableactiona.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y]) or wormholeanamylimit(
                mapfeature[x + 1][y])):
                movaableactiona.append(4)
        movaableaction = movaableactiona
    elif mindis == 2 or mindis == 1:
        # 这个时候我们可以让其恢复New3 的逃跑方案
        # updateanamypositionUpgrade(anamyplayers)
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1]) or wormholeanamylimit(
                mapfeature[x][y - 1])):
                movaableactiona.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1]) or wormholeanamylimit(
                mapfeature[x][y + 1])):
                movaableactiona.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y]) or wormholeanamylimit(
                mapfeature[x - 1][y])):
                movaableactiona.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y]) or wormholeanamylimit(
                mapfeature[x + 1][y])):
                movaableactiona.append(4)
        movaableaction = movaableactiona
    else:
        # updateanamypositionUpgrade(anamyplayers)
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1]) or wormholeanamylimit(
                mapfeature[x][y - 1])):
                movaableactiona.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1]) or wormholeanamylimit(
                mapfeature[x][y + 1])):
                movaableactiona.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y]) or wormholeanamylimit(
                mapfeature[x - 1][y])):
                movaableactiona.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y]) or wormholeanamylimit(
                mapfeature[x + 1][y])):
                movaableactiona.append(4)
        movaableaction = movaableactiona

    if len(seeanamys) == 0:
        if actionpower in movaableaction:  # 在上面的严苛的条件下，至少是安全的但是似乎没有考虑到field limit的情况
            return actionpower
        else:  # 这个时候我们应当尽量分散逃跑咯
            # 这个时候表示的是上面返回的是None,这个时候我们尽量对逃跑准则进行一定的规划 分散规划 对于不同的player朝着不同的方向进行跑去吗？？在前面power的规划的过程中，我们就已经进行了一定目标位置的规划的情况
            # 对于聚类的分析，我们是否有更好的分类的方式。是到底要分成几类也是很有关系的

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

            movaableaction = deadmoveNew4(player, anamyplayers)
            if movaableaction is None:
                return None
        # 还需要考虑到敌人是从外面把我们赶到墙上的i情况，这个时候如何更加优雅的判断呢？
        # if len(movaableaction) == 1 and (player['x'] == 0 or player['x'] == map_width-1 or player['y'] == 0 or player['y'] == map_height-1 ):
        #     mindis = 1000
        #     tempdis = 10
        #     flag_anamyindiagonal=False
        #     for anamyplayer in anamyplayers:
        #         x_dis = abs(player['x'] - anamyplayer['x'])
        #         y_dis = abs(player['y'] - anamyplayer['y'])
        #         tempdis = x_dis + y_dis
        #         if tempdis <= mindis:
        #             xmindis = x_dis
        #             ymindis = y_dis
        #             mindis = tempdis
        #             minanamy = anamyplayer
        #             if mindis == 2 and xmindis == 1 and ymindis == 1:
        #                 ndiagonalanamy=anamyplayer
        #                 flag_anamyindiagonal = True
        #                 # print('我们还应当判断出来敌人的下一步不会吃到我们')
        #
        #     # print('mindis是多少', mindis)
        #     # print('我是x', x, 'y', y)
        #     # print('敌人是x', minanamy['x'], 'y', minanamy['y'])
        #     if mindis == 2 and flag_anamyindiagonal:
        #         for anamys_motionpattern in anamys_motionpatterns:
        #             if anamys_motionpattern['id'] == minanamy['id']:
        #                 if anamys_motionpattern['lastmove'] == anamys_motionpattern['lastlastmove'] and anamys_motionpattern['updatelast'] and anamys_motionpattern['updatelastlast']:
        #                     if (player['x']==0 or player['x']==map_width-1)and (anamys_motionpattern['lastmove']==1 or anamys_motionpattern['lastmove']==2):
        #                         if movaableaction[0] == 1:
        #
        #                             if not (mapfeature[x][y+1].trueanamy or mapfeature[x][y+2].trueanamy):
        #                                 print('反向运动启动')
        #
        #                                 anamys_motionpattern['lastmove'] = 0
        #                                 anamys_motionpattern['lastlastmove'] = 0
        #                                 anamys_motionpattern['updatelast']=False
        #                                 anamys_motionpattern['updatelastlast']=False
        #
        #                                 return 2
        #                             else:
        #                                 pass
        #                         elif movaableaction[0] == 2:
        #                             if not (mapfeature[x][y-1].trueanamy or mapfeature[x][y-2].trueanamy):
        #                                 print('反向运动启动')
        #
        #                                 anamys_motionpattern['lastmove'] = 0
        #                                 anamys_motionpattern['lastlastmove'] = 0
        #                                 anamys_motionpattern['updatelast'] = False
        #                                 anamys_motionpattern['updatelastlast'] = False
        #                                 return 1
        #                             else:
        #                                 pass
        #                     if (player['y'] == 0 or player['y'] == map_height - 1) and (anamys_motionpattern['lastmove'] == 3 or anamys_motionpattern['lastmove'] == 4):
        #                         if movaableaction[0] == 3:
        #                             print('反向运动启动')
        #
        #                             if not (mapfeature[x+1][y].trueanamy or mapfeature[x+2][y].trueanamy):
        #                                 anamys_motionpattern['lastmove'] = 0
        #                                 anamys_motionpattern['lastlastmove'] = 0
        #                                 anamys_motionpattern['updatelast'] = False
        #                                 anamys_motionpattern['updatelastlast'] = False
        #                                 return 4
        #                             else:
        #                                 pass
        #                         elif movaableaction[0] == 4:
        #                             if not (mapfeature[x-1][y].trueanamy or mapfeature[x-2][y].trueanamy):
        #                                 print('反向运动启动')
        #                                 anamys_motionpattern['lastmove'] = 0
        #                                 anamys_motionpattern['lastlastmove'] = 0
        #                                 anamys_motionpattern['updatelast'] = False
        #                                 anamys_motionpattern['updatelastlast'] = False
        #
        #                                 return 3
        #                             else:
        #                                 pass

        # 我们可以在中途的情况就加入这样的操作、
        if len(movaableaction) == 1:
            mindis = 1000
            tempdis = 10
            flag_anamyindiagonal = False
            for anamyplayer in anamyplayers:
                x_dis = abs(player['x'] - anamyplayer['x'])
                y_dis = abs(player['y'] - anamyplayer['y'])
                tempdis = x_dis + y_dis
                if tempdis <= mindis:
                    xmindis = x_dis
                    ymindis = y_dis
                    mindis = tempdis
                    minanamy = anamyplayer
                    if mindis == 2 and xmindis == 1 and ymindis == 1:
                        ndiagonalanamy = anamyplayer
                        flag_anamyindiagonal = True
                        # print('我们还应当判断出来敌人的下一步不会吃到我们')

            # print('mindis是多少', mindis)
            # print('我是x', x, 'y', y)
            # print('敌人是x', minanamy['x'], 'y', minanamy['y'])
            if mindis == 2 and flag_anamyindiagonal:
                for anamys_motionpattern in anamys_motionpatterns:
                    if anamys_motionpattern['id'] == minanamy['id']:
                        if anamys_motionpattern['lastmove'] == anamys_motionpattern['lastlastmove'] and \
                                anamys_motionpattern['updatelast'] and anamys_motionpattern['updatelastlast']:
                            if (player['x'] == 0 or player['x'] == map_width - 1) and (
                                    anamys_motionpattern['lastmove'] == 1 or anamys_motionpattern['lastmove'] == 2):
                                if movaableaction[0] == 1:

                                    if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 2].trueanamy or
                                            mapfeature[x][y + 1].wall or mapfeature[x][y + 1].tunnel != 'no' or
                                            mapfeature[x][y + 2].wall or mapfeature[x][y + 2].tunnel != 'no'):
                                        print('反向运动启动')

                                        anamys_motionpattern['lastmove'] = 0
                                        anamys_motionpattern['lastlastmove'] = 0
                                        anamys_motionpattern['updatelast'] = False
                                        anamys_motionpattern['updatelastlast'] = False

                                        return 2
                                    else:
                                        pass
                                elif movaableaction[0] == 2:
                                    if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 2].trueanamy or
                                            mapfeature[x][y - 1].wall or mapfeature[x][y - 1].tunnel != 'no' or
                                            mapfeature[x][y - 2].wall or mapfeature[x][y - 2].tunnel != 'no'):

                                        print('反向运动启动')

                                        anamys_motionpattern['lastmove'] = 0
                                        anamys_motionpattern['lastlastmove'] = 0
                                        anamys_motionpattern['updatelast'] = False
                                        anamys_motionpattern['updatelastlast'] = False
                                        return 1
                                    else:
                                        pass
                            if (player['y'] == 0 or player['y'] == map_height - 1) and (
                                    anamys_motionpattern['lastmove'] == 3 or anamys_motionpattern['lastmove'] == 4):
                                if movaableaction[0] == 3:
                                    print('反向运动启动')

                                    if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 2][y].trueanamy or
                                            mapfeature[x + 1][y].wall or mapfeature[x + 1][y].tunnel != 'no' or
                                            mapfeature[x + 2][y].wall or mapfeature[x + 1][y].tunnel != 'no'):

                                        anamys_motionpattern['lastmove'] = 0
                                        anamys_motionpattern['lastlastmove'] = 0
                                        anamys_motionpattern['updatelast'] = False
                                        anamys_motionpattern['updatelastlast'] = False
                                        return 4
                                    else:
                                        pass
                                elif movaableaction[0] == 4:

                                    if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 2][y].trueanamy or
                                            mapfeature[x - 1][y].wall or mapfeature[x - 1][y].tunnel != 'no' or
                                            mapfeature[x - 2][y].wall or mapfeature[x - 1][y].tunnel != 'no'):
                                        print('反向运动启动')
                                        anamys_motionpattern['lastmove'] = 0
                                        anamys_motionpattern['lastlastmove'] = 0
                                        anamys_motionpattern['updatelast'] = False
                                        anamys_motionpattern['updatelastlast'] = False

                                        return 3
                                    else:
                                        pass

        global fieldlimitfactor
        if len(movaableaction) == 1 and ((x < fieldlimitfactor and y < fieldlimitfactor) or (
                x < fieldlimitfactor and y > map_height - fieldlimitfactor) or (
                                                 x > map_height - fieldlimitfactor and y < fieldlimitfactor) or (
                                                 x > map_width - fieldlimitfactor and y > map_height - fieldlimitfactor)):
            # print('corner situation')
            deadmoveNew4forcorner(player, anamyplayers)

        # 尽量不要贴边走否则容易被吃
        #  但是由于playerworm这个东西是特别的
        if player == playerworm:

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
            # 这个是为了防止敌人在很远的tunnel的敌方堵我
            if len(movaableaction) > 1:
                # print('我们使用tunnellimitV4')
                movaableaction2 = tunnellimitNew4(player, movaableaction, anamyplayers)
                # print('经过tunnellimit4筛选的结果', movaableaction2)
                if actionpower in movaableaction2:
                    # print('准备吃豆子的action', actionpower)
                    return actionpower

                if len(movaableaction2) == 1:
                    return movaableaction2[0]
                elif len(movaableaction2) > 1:
                    movaableaction = movaableaction2
                else:
                    a = random.randint(0, len(movaableaction) - 1)
                    # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                    # print('打印一下，我们将要选择执行经过tunnel筛选哪些动作，' + str(movaableaction[a]))
                    return movaableaction[a]
            elif len(movaableaction) == 1:
                return movaableaction[0]

            ##这个是为了防止太接近墙边
            if len(movaableaction) > 1:
                # print('我们准备使用fieldlimit')
                movaableaction3 = fieldlimit(player, movaableaction)
                # print('经过field筛选的动作：' + str(movaableaction3))
                if len(movaableaction3) == 1:
                    return movaableaction3[0]
                elif len(movaableaction3) > 1:
                    movaableaction = movaableaction3
                else:
                    a = random.randint(0, len(movaableaction) - 1)
                    # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                    # print('打印一下，我们将要选择执行经过tunnel筛选哪些动作，' + str(movaableaction[a]))
                    return movaableaction[a]
            elif len(movaableaction) == 1:
                return movaableaction[0]

            # 这个 是为了能够远离敌人的情况
            # if len(movaableaction) > 1:
            #     print('我们使用awayfromanamy')
            #     movaableaction4 = awayfrromanamy(player, movaableaction, seeanamys)  # 实际上，这个也在一定程度上防止了他还回到虫洞去
            #     print('经过gawayfromanamy筛选的动作 ' + str(movaableaction4))
            #     if len(movaableaction4) == 1:
            #         # print('')
            #         return movaableaction4[0]
            #     elif len(movaableaction4) > 1:
            #         movaableaction = movaableaction4
            #     else:
            #         a = random.randint(0, len(movaableaction) - 1)
            #         # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
            #         print('打印一下，我们将要选择执行经过tawayfrom筛选哪些动作，' + str(movaableaction[a]))
            #         return movaableaction[a]
            # elif len(movaableaction) == 1:
            #     return movaableaction[0]
            # 这个准备经过重力检测得到的结果
            if len(movaableaction) > 1:
                # print('我们使用centrogtravity')
                movaableaction5 = center_gravity(player, movaableaction)  # 实际上，这个也在一定程度上防止了他还回到虫洞去
                # print('经过gravity筛选的动作 ' + str(movaableaction5))
                if len(movaableaction5) == 1:

                    return movaableaction5[0]
                elif len(movaableaction5) > 1:
                    movaableaction = movaableaction5
                else:
                    a = random.randint(0, len(movaableaction) - 1)
                    # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
                    # print('打印一下，我们将要选择执行经过tawayfrom筛选哪些动作，' + str(movaableaction[a]))
                    return movaableaction[a]
            elif len(movaableaction) == 1:
                return movaableaction[0]

            a = random.randint(0, len(movaableaction) - 1)
            # print('打印一下，我们将要选择执行哪些动作，'+str(movaableaction[0]))
            # print('打印一下，我们将要选择执行经过tawayfrom筛选哪些动作，' + str(movaableaction[a]))
            return movaableaction[a]


# 这个函数，采用从少的移动方向到多的移动情况进行退化，这样就可以能够比较完美的使用deadmove了。
def player_avoidactionNew3(player, anamyplayers, actionpower):
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
        if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
            y - 1].tunnel == 'down' or tunnelanamylimit(mapfeature[x][y - 1]) or wormholeanamylimit(
                mapfeature[x][y - 1])):
            movaableactiona.append(1)
    if y < map_height - 1:  # 向下
        if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
            y + 1].tunnel == 'up' or tunnelanamylimit(mapfeature[x][y + 1]) or wormholeanamylimit(
                mapfeature[x][y + 1])):
            movaableactiona.append(2)
    if x > 0:  # 向左移动
        if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
            y].tunnel == 'right' or tunnelanamylimit(mapfeature[x - 1][y]) or wormholeanamylimit(mapfeature[x - 1][y])):
            movaableactiona.append(3)
    if x < map_width - 1:  # 向右移动
        if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
            y].tunnel == 'left' or tunnelanamylimit(mapfeature[x + 1][y]) or wormholeanamylimit(mapfeature[x + 1][y])):
            movaableactiona.append(4)
    movaableaction = movaableactiona
    # print('第一轮筛选后的内容',movaableaction)
    # mapshow(mapfeature)

    # 实际情况下，这个地方并不应该要是整体视野内的敌人的情况，而是某一个自身的playerx的情况，这个时候，我们是否要重复计算每一个player啊
    seeanamys = []

    for anamyplayer in anamyplayers:
        if anamyplayer['x'] <= player['x'] + visionrange and anamyplayer['x'] >= player['x'] - visionrange and \
                anamyplayer['y'] <= player['y'] + visionrange and anamyplayer['y'] >= player['y'] - visionrange:
            seeanamys.append(anamyplayer)

    if len(seeanamys) == 0:
        if actionpower in movaableaction:  # 在上面的严苛的条件下，至少是安全的但是似乎没有考虑到field limit的情况
            return actionpower
        else:  # 这个时候我们应当尽量分散逃跑咯
            # 这个时候表示的是上面返回的是None,这个时候我们尽量对逃跑准则进行一定的规划 分散规划 对于不同的player朝着不同的方向进行跑去吗？？在前面power的规划的过程中，我们就已经进行了一定目标位置的规划的情况
            # 对于聚类的分析，我们是否有更好的分类的方式。是到底要分成几类也是很有关系的

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
            return ac

        else:
            # 尽量不要贴边走否则容易被吃
            #  但是由于playerworm这个东西是特别的
            if player == playerworm:
                # mapshow(mapfeature)
                # print('这个时候打印一下当前可移动的i情况 和本身的位置',player)
                # print(movaableaction)
                # print('anaamyplayes 的情况', anamyplayers)
                # print('action power 是多少：'+str(actionpower))
                # print('本身是playerworm的情况')
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
                    # print('我们准备使用fieldlimit')
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
                        # print('我们使用centrogtravity')
                        movaableaction3 = center_gravity(player, movaableaction)  # 实际上，这个也在一定程度上防止了他还回到虫洞去
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


# 更新了敌人的位置的i情况，从多的的移动的方向到移动多的情况 不能使用deadmove了
def player_avoidactionNew2(player, anamyplayers, actionpower):
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
            y].tunnel == 'right'):
            movaableactiona.append(3)
    if x < map_width - 1:  # 向右移动
        if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
            y].tunnel == 'left'):
            movaableactiona.append(4)
    movaableaction = movaableactiona
    print('第一轮筛选后的内容', movaableaction)
    updateanamyposition(anamyplayers)  # 这个刷新了敌人的位置不包含，走了tunnel之后的终点
    '''第二轮筛选：放宽敌人位置的限制，敌人的位置经过tunnel之后的扩大一圈'''
    # print('筛选动作前，看一下敌人的位置')
    # mapshow(mapfeature)
    if len(movaableaction) >= 2:
        movaableactionb = []
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
        if len(movaableactionb) > 0:

            movaableaction = movaableactionb
            print('第二轮筛选后的内容', movaableactionb)

        else:

            print('第二轮筛选后的内容', movaableactionb)

    '''第三轮筛选：放宽敌人位置的限制，敌人的位置所有的都扩大一圈'''
    updateanamypositionUpgrade(anamyplayers)  # 这个是最真实的，都有可能不能走箭头了
    # print('筛选动作前，看一下敌人的位置')
    # mapshow(mapfeature)
    if len(movaableaction) >= 2:
        movaableactionc = []
        # 得到当前可以移动的范围内
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down'):
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
                y].tunnel == 'left'):
                movaableactionc.append(4)
        if len(movaableactionc) > 0:

            movaableaction = movaableactionc
            print('第二轮筛选后的内容', movaableactionc)

        else:

            print('第二轮筛选后的内容', movaableactionc)

    if len(anamyplayers) == 0:
        if actionpower in movaableaction:
            return actionpower
        else:  # 这个时候我们应当尽量分散逃跑咯
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
                        movaableaction3 = center_gravity(player, movaableaction)  # 实际上，这个也在一定程度上防止了他还回到虫洞去
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


# 下面是未将敌人的邻居进行更新到帧是邻居的情况，进行从多个移动方向到少的移动方向的选择
def player_avoidactionNew1(player, anamyplayers, actionpower):
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
    if len(movaableaction) >= 2:
        movaableaction = []
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

    if len(movaableaction) >= 2:
        movaableaction = []
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
        else:  # 这个时候我们应当尽量分散逃跑咯
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
                    movaableaction0 = anamynexttunnelmovelimit(player, movaableaction)
                    if len(movaableaction0) == 0:
                        pass
                    else:
                        movaableaction = movaableaction0
                        if len(movaableaction) > 1:

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
                        movaableaction3 = center_gravity(player, movaableaction)  # 实际上，这个也在一定程度上防止了他还回到虫洞去
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


def anamynexttunnelmovelimit(player, movaableaction, anamplayers):
    global tunnelsneighbours
    global mapfeature
    x = player['x']
    y = player['y']

    '''针对只走一步是tunnel终点的情况，防止敌人直接走tunnel吃我，但是又不能杜绝不走这个'''
    newmovableactiion = []
    for moveaction in movaableaction:
        if moveaction == 1 and mapfeature[x][y - 1] not in tunnelsneighbours:
            newmovableactiion.append(moveaction)
        if moveaction == 2 and mapfeature[x][y + 1] not in tunnelsneighbours:
            newmovableactiion.append(moveaction)
        if moveaction == 3 and mapfeature[x - 1][y] not in tunnelsneighbours:
            newmovableactiion.append(moveaction)
        if moveaction == 4 and mapfeature[x + 1][y] not in tunnelsneighbours:
            newmovableactiion.append(moveaction)
    return newmovableactiion

    pass


# 这个函数的目的就希望能够根据地方的player的位置躲着
def player_avoidaction(player, anamyplayers, actionpower):
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

    if len(anamyplayers) == 0:
        # 分程两种，一种是在内部的豆子，一种是不在内部的豆子
        # 如果敌人都不在哦我们的视野内的时候，我们也要吃豆子啊
        # 吃豆子成俗
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
            return actionpower
        else:
            # 这个时候表示的是上面返回的是None,这个时候我们尽量对逃跑准则进行一定的规划 分散规划

            a = random.randint(0, len(movaableaction) - 1)
            # print('打印一下，我们将要选择执行哪些动作，没有敌人的情况下----'+str(movaableaction[a]))
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
            # print('打印一下，我们将要选择执行哪些动作，死亡移动----'+str(ac))
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

                    movaableaction1 = fieldlimit(player, movaableaction)
                    # print('未经过筛选的动作：'+str(movaableaction))
                    # print('经过field筛选的动作：'+str(movaableaction1))
                    if len(movaableaction1) == 0:
                        pass
                    else:
                        movaableaction = movaableaction1

                        if len(movaableaction) > 1:
                            movaableaction2 = tunnellimit(player, movaableaction)
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
                        movaableaction3 = center_gravity(player, movaableaction)
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


# 这个function的作用就是为了实现在可行的路线中寻找最优的路线
def fieldlimit(player, movaableaction):
    global map_width
    global map_height
    global fieldlimitfactor
    x = player['x']
    y = player['y']
    newmovableactiion = []
    for moveaction in movaableaction:
        if moveaction == 1 and y >= fieldlimitfactor:
            newmovableactiion.append(moveaction)
        if moveaction == 2 and y <= map_height - fieldlimitfactor:
            newmovableactiion.append(moveaction)
        if moveaction == 3 and x >= fieldlimitfactor:
            newmovableactiion.append(moveaction)
        if moveaction == 4 and x <= map_width - fieldlimitfactor:
            newmovableactiion.append(moveaction)
    return newmovableactiion
    pass


def tunnellimit(player, movaableaction):
    global mapfeature
    x = player['x']
    y = player['y']

    newmovableactiion = []
    for moveaction in movaableaction:
        if moveaction == 1 and mapfeature[x][y - 1].tunnel == 'no':
            newmovableactiion.append(moveaction)
        if moveaction == 2 and mapfeature[x][y + 1].tunnel == 'no':
            newmovableactiion.append(moveaction)
        if moveaction == 3 and mapfeature[x - 1][y].tunnel == 'no':
            newmovableactiion.append(moveaction)
        if moveaction == 4 and mapfeature[x + 1][y].tunnel == 'no':
            newmovableactiion.append(moveaction)
    return newmovableactiion


def tunnellimitNew4(player, movaableaction, anamyplayers):
    # 我们判断出走tunne之后的位置的范围是未知的情况，我们就尽量不走，否则我们就认为可以走
    global mapfeature
    x = player['x']
    y = player['y']
    # 在前面的时候实际上已经确定了可移动的范围的终点是不是tunnellimit，如果可能是的话，我们就已经排除了那个方向了
    a = len(anamyplayers)
    if a == 3 or a == 4:
        return movaableaction

    newmovableactiion = []
    for moveaction in movaableaction:
        if moveaction == 1:
            if mapfeature[x][y - 1].tunnel != 'no':
                # 找到走过后的真实的邻居，判断走过后的真实的邻居是不是敌人
                a = findgoodneighbourV2(mapfeature[x][y - 1])
                # print('走tunnel邻居之后的位置x ',a.x, 'y',a.y)
                if abs(a.x - x) > 3 or abs(a.y - y) > 3:
                    pass
                    # print('下一步经过tunnel后的位置较远，我们排除这个动作')
                else:
                    newmovableactiion.append(moveaction)
            else:
                newmovableactiion.append(moveaction)

        if moveaction == 2:
            if mapfeature[x][y + 1].tunnel != 'no':
                a = findgoodneighbourV2(mapfeature[x][y + 1])
                # print('走tunnel邻居之后的位置x ',a.x, 'y',a.y)

                if abs(a.x - x) > 3 or abs(a.y - y) > 3:
                    pass
                    # print('下一步经过tunnel后的位置较远，我们排除这个动作')
                else:
                    newmovableactiion.append(moveaction)

            else:
                newmovableactiion.append(moveaction)
        if moveaction == 3:
            if mapfeature[x - 1][y].tunnel != 'no':
                a = findgoodneighbourV2(mapfeature[x - 1][y])
                # print('走tunnel邻居之后的位置x ',a.x, 'y',a.y)
                if abs(a.x - x) > 3 or abs(a.y - y) > 3:
                    pass
                    # print('下一步经过tunnel后的位置较远，我们排除这个动作')

                else:
                    newmovableactiion.append(moveaction)
            else:
                newmovableactiion.append(moveaction)

        if moveaction == 4:
            if mapfeature[x + 1][y].tunnel != 'no':

                a = findgoodneighbourV2(mapfeature[x + 1][y])
                # print('走tunnel邻居之后的位置x ',a.x, 'y',a.y)

                if abs(a.x - x) > 3 or abs(a.y - y) > 3:
                    pass
                    # print('下一步经过tunnel后的位置较远，我们排除这个动作')
                else:
                    newmovableactiion.append(moveaction)


            else:
                newmovableactiion.append(moveaction)

    return newmovableactiion


def center_gravity(player, moveableaction):
    global map_width
    global map_height
    gravity_factor = 4
    x = player['x']
    y = player['y']
    # print('打印出 实际的位置 x，y',x,'    ',y)
    y_away = abs(y - map_height / 2) / map_height
    x_away = abs(x - map_width / 2) / map_width
    newmovableactiion = []
    for moveaction in moveableaction:
        if moveaction == 1 and y >= map_height / 2:
            newmovableactiion.append(moveaction)
        if moveaction == 2 and y < map_height / 2:
            newmovableactiion.append(moveaction)
        if moveaction == 3 and x >= map_width / 2:
            newmovableactiion.append(moveaction)
        if moveaction == 4 and x < map_width / 2:
            newmovableactiion.append(moveaction)
    # 这一段是用来选择走左还是走右的
    if len(newmovableactiion) == 2:
        newmovableactiion1 = []
        for moveaction in moveableaction:
            if moveaction == 1 and y_away >= x_away:
                newmovableactiion1.append(moveaction)
            if moveaction == 2 and y_away >= x_away:
                newmovableactiion1.append(moveaction)
            if moveaction == 3 and x_away >= y_away:
                newmovableactiion1.append(moveaction)
            if moveaction == 4 and x_away >= y_away:
                newmovableactiion1.append(moveaction)
        return newmovableactiion1
    else:
        return newmovableactiion


# 这个函数作用是为了防止走完tunnel之后，终点就是敌人的情况
# 我们需要得到移动的方向，然后终点是哪里
def tunnelanamylimit(neighbour):
    global mapfeature
    if neighbour.tunnel == 'no':
        # print('我们的邻居是nonononono，也就不是tunnel了')
        return False  # 表示不是敌人
        pass
    else:
        c = findgoodneighbour(neighbour)  # 给定mapfeature的一个对象，然后返回对应实际的neighbour。
        # print('这个时候返回走过tunnel之后的情况敌人的位置',c.anamy)
        return c.anamy

    pass


# 这个函数是判断经过tunnel之后的是不是真实的敌人的位置
def tunneltrueanamylimit(neighbour):
    global mapfeature
    if neighbour.tunnel == 'no':
        # print('我们的邻居是nonononono，也就不是tunnel了')
        return False  # 表示不是敌人
        pass
    else:
        c = findgoodneighbour(neighbour)  # 给定mapfeature的一个对象，然后返回对应实际的neighbour。
        # print('这个时候返回走过tunnel之后，trueannamy的i情况',c.trueanamy)
        return c.trueanamy


def wormholeanamylimit(neighbour):
    global mapfeature
    if neighbour.wormhole:
        Anamyworm = findwormpair(neighbour.x, neighbour.y)
        # print('返回的worm对面的是不是敌人',mapfeature[Anamyworm['x']][Anamyworm['y']].anamy)
        return mapfeature[Anamyworm['x']][Anamyworm['y']].anamy
    else:
        return False


def wormholetrueanamylimit(neighbour):
    global mapfeature
    if neighbour.wormhole:
        anamyworm = findwormpair(neighbour.x, neighbour.y)
        # print('返回的worm对面的是不是敌人',mapfeature[anamyworm['x']][anamyworm['y']].anamy)
        return mapfeature[anamyworm['x']][anamyworm['y']].trueanamy
    else:
        return False

    pass

    pass


def awayfrromanamy(playerX, movaableactions, seeanamyplayers):
    x = 0
    y = 0
    for anamyplayer in seeanamyplayers:
        x = x + anamyplayer['x']
        y = y + anamyplayer['y']
    a = len(seeanamyplayers)
    x = x / a;
    y = y / a;
    newmove = []
    for moac in movaableactions:
        if moac == 1 and playerX['y'] <= y:
            newmove.append(moac)
        if moac == 2 and playerX['y'] > +y:
            newmove.append(moac)
        if moac == 3 and playerX['x'] <= x:
            newmove.append(moac)
        if moac == 4 and playerX['x'] >= x:
            newmove.append(moac)

    return newmove


global anamys_pos
anamys_pos = [{'id': 0, 'x': 0, 'y': 0}, {'id': 0, 'x': 0, 'y': 0}, {'id': 0, 'x': 0, 'y': 0},
              {'id': 0, 'x': 0, 'y': 0}]
global oldanamyplayersid
oldanamyplayersid = []

global flag_firstintialoldanamyplayers
flag_firstintialoldanamyplayers = False


def get_trueanamymotionpattern(anamyplayers):
    import copy
    global lastmove
    global lastlastmove
    global mapfeature
    global map_width
    global map_height
    global playerworm
    global visionrange
    global oldanamyplayers
    global flag_firstintialoldanamyplayers
    global get_solution

    global anamys_lastmoves

    # print('实际坐标x：' + str(x) + '    y' + str(y))
    movaableactiona = []
    # print('筛选动作前，看一下敌人的位置')
    # print('敌人的情况',anamyplayers)
    # mapshow(mapfeature)
    # 实际情况下，这个地方并不应该要是整体视野内的敌人的情况，而是某一个自身的playerx的情况，这个时候，我们是否要重复计算每一个player啊
    seeanamys = []

    # for anamyplayer in anamyplayers:
    #     if anamyplayer['x'] <= player['x'] + visionrange and anamyplayer['x'] >= player['x'] - visionrange and \
    #             anamyplayer['y'] <= player['y'] + visionrange and anamyplayer['y'] >= player['y'] - visionrange:
    #         seeanamys.append(anamyplayer)
    if flag_firstintialoldanamyplayers:
        idnew = []
        idold = []
        for anamyplayer in anamyplayers:
            idnew.append(anamyplayer['id'])
        for anamyplayer in oldanamyplayers:
            idold.append(anamyplayer['id'])
        for anamys_motionpattern in anamys_motionpatterns:
            if anamys_motionpattern['id'] in idnew and anamys_motionpattern['id'] in idold:
                if anamys_motionpattern['updatelast']:
                    anamys_motionpattern['updatelastlast'] = True
                    anamys_motionpattern['lastlastmove'] = anamys_motionpattern['lastmove']
                else:
                    pass

                for anamyplayer in anamyplayers:
                    if anamyplayer['id'] == anamys_motionpattern['id']:
                        start = mapfeature[anamys_motionpattern['x']][anamys_motionpattern['y']]
                        end = mapfeature[anamyplayer['x']][anamyplayer['y']]
                        # 敌人的位置的变化
                        path = getpathnoanamy(start, end)
                        if start.x == end.x and start.y == end.y:
                            # 这个时候敌人是不动的,但是我们需要给敌人的上一步运动进行赋值。
                            anamys_motionpattern['lastmove'] = 0
                            anamys_motionpattern['udpate'] = True

                        if len(path) == 2:
                            ac = get_actionfrompath()
                            anamys_motionpattern['lastmove'] = ac
                            anamys_motionpattern['x'] = end.x
                            anamys_motionpattern['y'] = end.y
                            anamys_motionpattern['updatelast'] = True

                        break

            elif anamys_motionpattern['id'] in idnew and anamys_motionpattern['id'] not in idold:
                anamys_motionpattern['updatelastlast'] = False
                anamys_motionpattern['lastlastmove'] = 0
                # 如果这个时候只更新id 就好

                for anamyplayer in anamyplayers:
                    if anamyplayer['id'] == anamys_motionpattern['id']:
                        anamys_motionpattern['lastmove'] = 0
                        anamys_motionpattern['x'] = anamyplayer['x']
                        anamys_motionpattern['y'] = anamyplayer['y']
                        anamys_motionpattern['updatelast'] = False
                        break
            elif anamys_motionpattern['id'] not in idnew and anamys_motionpattern['id'] in idold:

                anamys_motionpattern['updatelastlast'] = False
                anamys_motionpattern['lastlastmove'] = 0
                anamys_motionpattern['lastmove'] = 0
                anamys_motionpattern['updatelast'] = False
                pass
            else:

                anamys_motionpattern['updatelastlast'] = False
                anamys_motionpattern['lastlastmove'] = 0
                anamys_motionpattern['lastmove'] = 0
                anamys_motionpattern['updatelast'] = False

                pass
        oldanamyplayers = anamyplayers
    else:
        oldanamyplayers = anamyplayers

        for oldanamyplayer in oldanamyplayers:
            oldanamyplayersid.append(oldanamyplayer['id'])
        flag_firstintialoldanamyplayers = True

    # print(anamys_motionpatterns)


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
    return myplayers, anamyplayers
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

def deadmoveNew5(player, anamyplayers):
    # 要找到分数最多的敌人。
    # 攻击最近的敌人
    global mapfeature
    mindis = 1000
    x = player['x']
    y = player['y']

    # 敌人在我斜对角的情况
    flag_anamyindiagonal = False
    for anamyplayer in anamyplayers:
        x_dis = abs(player['x'] - anamyplayer['x'])
        y_dis = abs(player['y'] - anamyplayer['y'])
        tempdis = x_dis + y_dis
        if tempdis <= mindis:
            xmindis = x_dis
            ymindis = y_dis
            mindis = tempdis
            minanamy = anamyplayer
            if mindis == 2 and xmindis == 1 and ymindis == 1:
                flag_anamyindiagonal = True
    if mindis == 2 and flag_anamyindiagonal:
        return None
    else:  # 这个时候的情况下也是有路走的啊，因为即使走tunnel也是没有路了啊，这个时候，我们就将敌人当成帧是的敌人，其他的位置是不考虑的哦~
        '''我们派出了敌人在我斜对角的情况，这样的情况下，我希望还能有路可以走，这个时候我就认为敌人不会穿过tunnel来找我'''

        '''这个时候需要一次放松限制'''
        # print('')
        updateanamyposition(anamyplayers)  # 这个是将敌人的位置仅仅更新到不走过tunnel的情况,这个认为是敌人不走tunnel的情况或者不会走tunnnel去围堵我
        move_backplanb = []
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1]) or wormholetrueanamylimit(
                mapfeature[x][y - 1])):
                move_backplanb.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1]) or wormholetrueanamylimit(
                mapfeature[x][y + 1])):
                move_backplanb.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y]) or wormholetrueanamylimit(
                mapfeature[x - 1][y])):
                move_backplanb.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y]) or wormholetrueanamylimit(
                mapfeature[x + 1][y])):
                move_backplanb.append(4)
        # print('第一层放宽敌人限制后可移动的情况', move_backplanb)
        if len(move_backplanb) == 0:
            # 这个时候，我们周围都是敌人的真实的位置，这个时候

            # mapshow(mapfeature)
            move_backplanc = []
            if y > 0:  # 向上
                if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 1].wall or mapfeature[x][
                    y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1]) or wormholetrueanamylimit(
                    mapfeature[x][y - 1])):
                    move_backplanc.append(1)
            if y < map_height - 1:  # 向下
                if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 1].wall or mapfeature[x][
                    y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1]) or wormholetrueanamylimit(
                    mapfeature[x][y + 1])):
                    move_backplanc.append(2)
            if x > 0:  # 向左移动
                if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                    y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y]) or wormholetrueanamylimit(
                    mapfeature[x - 1][y])):
                    move_backplanc.append(3)
            if x < map_width - 1:  # 向右移动
                if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                    y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y]) or wormholetrueanamylimit(
                    mapfeature[x + 1][y])):
                    move_backplanc.append(4)
            # print('第二层放宽敌人限制后可移动的情况', move_backplanc)

            if len(move_backplanc) == 0:
                '''这个时候进行死亡死亡死亡的垂死挣扎'''

                return None
            else:
                return move_backplanc
        else:
            return move_backplanb


def deadmoveNew4(player, anamyplayers):
    # 要找到分数最多的敌人。
    # 攻击最近的敌人
    global mapfeature
    mindis = 1000
    x = player['x']
    y = player['y']

    # 敌人在我斜对角的情况
    flag_anamyindiagonal = False
    for anamyplayer in anamyplayers:
        x_dis = abs(player['x'] - anamyplayer['x'])
        y_dis = abs(player['y'] - anamyplayer['y'])
        tempdis = x_dis + y_dis
        if tempdis <= mindis:
            xmindis = x_dis
            ymindis = y_dis
            mindis = tempdis
            minanamy = anamyplayer
            if mindis == 2 and xmindis == 1 and ymindis == 1:
                flag_anamyindiagonal = True
                # print('我们还应当判断出来敌人的下一步不会吃到我们')

    # print('mindis是多少', mindis)

    if mindis == 2 and flag_anamyindiagonal:
        # print('我们还应当判断出来敌人的下一步不会吃到我们')
        # print('我们看一下我们当前的位置是不是真的敌人下一步就能迟到我们的情况', mapfeature[x][y].anamy)
        return None
    else:  # 这个时候的情况下也是有路走的啊，因为即使走tunnel也是没有路了啊，这个时候，我们就将敌人当成帧是的敌人，其他的位置是不考虑的哦~
        '''我们派出了敌人在我斜对角的情况，这样的情况下，我希望还能有路可以走，这个时候我就认为敌人不会穿过tunnel来找我'''

        '''这个时候需要一次放松限制'''
        # print('')
        updateanamyposition(anamyplayers)  # 这个是将敌人的位置仅仅更新到不走过tunnel的情况
        move_backplanb = []
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1]) or wormholetrueanamylimit(
                mapfeature[x][y - 1])):
                move_backplanb.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1]) or wormholetrueanamylimit(
                mapfeature[x][y + 1])):
                move_backplanb.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y]) or wormholetrueanamylimit(
                mapfeature[x - 1][y])):
                move_backplanb.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y]) or wormholetrueanamylimit(
                mapfeature[x + 1][y])):
                move_backplanb.append(4)
        # print('第一层放宽敌人限制后可移动的情况',move_backplanb)
        if len(move_backplanb) == 0:

            print('进行垂死挣扎1')
            print('我是x', x, 'y', y)
            print('敌人是x', minanamy['x'], 'y', minanamy['y'])

            # mapshow(mapfeature)
            move_backplanc = []
            if y > 0:  # 向上
                if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 1].wall or mapfeature[x][
                    y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1]) or wormholetrueanamylimit(
                    mapfeature[x][y - 1])):
                    move_backplanc.append(1)
            if y < map_height - 1:  # 向下
                if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 1].wall or mapfeature[x][
                    y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1]) or wormholetrueanamylimit(
                    mapfeature[x][y + 1])):
                    move_backplanc.append(2)
            if x > 0:  # 向左移动
                if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                    y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y]) or wormholetrueanamylimit(
                    mapfeature[x - 1][y])):
                    move_backplanc.append(3)
            if x < map_width - 1:  # 向右移动
                if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                    y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y]) or wormholetrueanamylimit(
                    mapfeature[x + 1][y])):
                    move_backplanc.append(4)
            print('第二层放宽敌人限制后可移动的情况', move_backplanc)

            if len(move_backplanc) == 0:
                '''这个时候进行死亡死亡死亡的垂死挣扎'''
                print('进行垂死挣扎2')

                return None
            else:
                return move_backplanc
        else:
            return move_backplanb


def deadmoveNew4forcorner(player, anamyplayers):
    # 要找到分数最多的敌人。
    # 攻击最近的敌人
    global mapfeature
    mindis = 1000
    x = player['x']
    y = player['y']

    # 敌人在我斜对角的情况
    flag_anamyindiagonal = False
    for anamyplayer in anamyplayers:
        x_dis = abs(player['x'] - anamyplayer['x'])
        y_dis = abs(player['y'] - anamyplayer['y'])
        tempdis = x_dis + y_dis
        if tempdis <= mindis:
            xmindis = x_dis
            ymindis = y_dis
            mindis = tempdis
            minanamy = anamyplayer
            if mindis == 2 and xmindis == 1 and ymindis == 1:
                flag_anamyindiagonal = True
                # print('我们还应当判断出来敌人的下一步不会吃到我们')

    # print('mindis是多少', mindis)

    if mindis == 2 and flag_anamyindiagonal:
        # print('我们还应当判断出来敌人的下一步不会吃到我们')
        # print('我们看一下我们当前的位置是不是真的敌人下一步就能迟到我们的情况', mapfeature[x][y].anamy)
        return None
    else:  # 这个时候的情况下也是有路走的啊，因为即使走tunnel也是没有路了啊，这个时候，我们就将敌人当成帧是的敌人，其他的位置是不考虑的哦~
        '''我们派出了敌人在我斜对角的情况，这样的情况下，我希望还能有路可以走，这个时候我就认为敌人不会穿过tunnel来找我'''

        '''这个时候需要一次放松限制'''
        #
        # print('进行垂死挣扎1')
        # print('我是x', x, 'y', y)
        # print('敌人是x', minanamy['x'], 'y', minanamy['y'])

        # mapshow(mapfeature)
        move_backplanc = []
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].trueanamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1]) or wormholetrueanamylimit(
                mapfeature[x][y - 1])):
                move_backplanc.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].trueanamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1]) or wormholetrueanamylimit(
                mapfeature[x][y + 1])):
                move_backplanc.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].trueanamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y]) or wormholetrueanamylimit(
                mapfeature[x - 1][y])):
                move_backplanc.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].trueanamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y]) or wormholetrueanamylimit(
                mapfeature[x + 1][y])):
                move_backplanc.append(4)
        print('第二层放宽敌人限制后可移动的情况', move_backplanc)

        if len(move_backplanc) == 0:
            '''这个时候进行死亡死亡死亡的垂死挣扎'''
            print('进行垂死挣扎2')

            return None
        else:
            return move_backplanc


def deadmoveNew3(player, anamyplayers):
    # 要找到分数最多的敌人。
    # 攻击最近的敌人
    global mapfeature
    mindis = 1000
    x = player['x']
    y = player['y']
    move_backplan = []

    for anamyplayer in anamyplayers:
        x_dis = abs(player['x'] - anamyplayer['x'])
        y_dis = abs(player['y'] - anamyplayer['y'])
        tempdis = x_dis + y_dis
        if tempdis < mindis:
            xmindis = x_dis
            ymindis = y_dis
            mindis = tempdis
            minanamy = anamyplayer

    if mindis == 2 and xmindis == 1 and ymindis == 1:

        return None
    else:  # 这个时候的情况下也是有路走的啊，因为即使走tunnel也是没有路了啊，这个时候，我们就将敌人当成帧是的敌人，其他的位置是不考虑的哦~
        '''我们派出了敌人在我斜对角的情况，这样的情况下，我希望还能有路可以走，这个时候我就认为敌人不会穿过tunnel来找我'''
        updateanamyposition(anamyplayers)  # 这个是将敌人的位置仅仅更新到不走过tunnel的情况
        if y > 0:  # 向上
            if not (mapfeature[x][y - 1].anamy or mapfeature[x][y - 1].wall or mapfeature[x][
                y - 1].tunnel == 'down' or tunneltrueanamylimit(mapfeature[x][y - 1]) or wormholetrueanamylimit(
                mapfeature[x][y - 1])):
                move_backplan.append(1)
        if y < map_height - 1:  # 向下
            if not (mapfeature[x][y + 1].anamy or mapfeature[x][y + 1].wall or mapfeature[x][
                y + 1].tunnel == 'up' or tunneltrueanamylimit(mapfeature[x][y + 1]) or wormholetrueanamylimit(
                mapfeature[x][y + 1])):
                move_backplan.append(2)
        if x > 0:  # 向左移动
            if not (mapfeature[x - 1][y].anamy or mapfeature[x - 1][y].wall or mapfeature[x - 1][
                y].tunnel == 'right' or tunneltrueanamylimit(mapfeature[x - 1][y]) or wormholetrueanamylimit(
                mapfeature[x - 1][y])):
                move_backplan.append(3)
        if x < map_width - 1:  # 向右移动
            if not (mapfeature[x + 1][y].anamy or mapfeature[x + 1][y].wall or mapfeature[x + 1][
                y].tunnel == 'left' or tunneltrueanamylimit(mapfeature[x + 1][y]) or wormholetrueanamylimit(
                mapfeature[x + 1][y])):
                move_backplan.append(4)

        # print('第一层放宽限制后的可运动的范围',move_backplan)
        if len(move_backplan) == 0:
            '''这个时候需要再一次放松限制'''
            # print('第二层放宽敌人限制')
            # print('')

            # mapshow(mapfeature)
            movaableactionb = []
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
            if len(movaableactionb) == 0:
                return random.randint(1, 4)
            else:
                ac = movaableactionb[random.randint(0, len(movaableactionb) - 1)]
                return ac

        else:
            ac = move_backplan[random.randint(0, len(move_backplan) - 1)]
            return ac


# 我们进行整体的规划
# 通过对当前player要进行的action的运动的集合
# 我们对敌人进行追击的策略就是包围策略
#
def deadmove(player, anamyplayers):
    # 要找到分数最多的敌人。
    # 攻击最近的敌人
    global mapfeature
    mindis = 1000
    x = player['x']
    y = player['y']
    move_backplan = []

    for anamyplayer in anamyplayers:
        x_dis = abs(player['x'] - anamyplayer['x'])
        y_dis = abs(player['y'] - anamyplayer['y'])
        tempdis = x_dis + y_dis
        if tempdis < mindis:
            mindis = tempdis
            # minanamy = anamyplayer
    if mindis == 2 and x_dis == 1 and y_dis == 1:
        return None
    elif mindis == 1:  # 这个时候的情况下也是有路走的啊，因为即使走tunnel也是没有路了啊，这个时候，我们就将敌人当成帧是的敌人，其他的位置是不考虑的哦~
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
        if len(move_backplan) == 0:
            return random.randint(1, 4)
        else:
            ac = move_backplan[random.randint(0, len(move_backplan) - 1)]
            return ac


def getmindistance(player, anamyplayers):
    mindis = 10000000000000
    # print('在寻找距离最近的powerout的情况下，我们打印一下powerserout以便更好判断我们得到的是不是最好的')
    # print(powersetout)
    for anamyplayer in anamyplayers:

        tempdis = abs(player['x'] - anamyplayer['x']) + abs(player['y'] - anamyplayer['y'])
        if tempdis < mindis:
            mindis = tempdis

            minanamy = anamyplayer
    return minanamy


def getcentrolpos(posset, myplayers):
    global mapfeature
    global flag_getsolution
    if posset is None:
        return None, None

    x = 0
    y = 0
    dismin = 1000
    for pos in posset:
        x = x + pos['x']
        y = y + pos['y']
    x = x / len(posset)
    y = y / len(posset)

    if len(posset) == 1:
        return posset[0], None
    else:
        # try:
        for j in range(100):
            for pos in posset:
                distemp = abs(x - pos['x']) + abs(y - pos['y'])
                if distemp < dismin:
                    dismin = distemp
                    minpos = pos
            player = myplayers[random.randint(0, len(myplayers) - 1)]
            start = mapfeature[player['x']][player['y']]
            end = mapfeature[minpos['x']][minpos['y']]
            getpathnoanamy(start, end)
            if flag_getsolution:
                return minpos, posset
            else:
                posset.remove(minpos)
    # except:
    #     return None,None


def findnearestplayertomapexplorepos(myplayers, pos):
    dismin = 100

    if pos is None:
        return None
    # print()

    for player in myplayers:
        distemp = stepdistance(player, pos)
        if distemp < dismin:
            dismin = distemp
            minplayer = player

    return minplayer

    # print('当前list的长度',len(bestlist))
    # print('bestlist的情况',bestlist)
    # print('cen的情况',cen[0])


def updatepartABCDpos(myplayers):
    global partApos, partBpos, partCpos, partDpos, partABCDpos
    global visionrange

    for myplayer in myplayers:
        player_x = myplayer['x']
        player_y = myplayer['y']
        for x in range(player_x - visionrange, player_x + visionrange):
            for y in range(player_y - visionrange, player_y + visionrange):
                pos = {'x': x, 'y': y}

                if pos in partABCDpos:
                    partABCDpos.remove(pos)
                if partApos is None:
                    pass
                else:
                    if pos in partApos:
                        partApos.remove(pos)
                    if len(partApos) == 0:
                        partApos = None

                if partBpos is None:
                    pass
                else:
                    if pos in partBpos:
                        partBpos.remove(pos)
                    if len(partBpos) == 0:
                        partBpos = None
                if partCpos is None:
                    pass
                else:
                    if pos in partCpos:
                        partCpos.remove(pos)
                    if len(partCpos) == 0:
                        partCpos = None
                if partDpos is None:
                    pass
                else:
                    if pos in partDpos:
                        partDpos.remove(pos)
                    if len(partDpos) == 0:
                        partDpos = None





#这个函数作用是希望能够通过player对powerset进行吃
#追击敌人的情况下，我们还是需要两个player进行追击，
#如果我们的player被吃掉了也就不足四个玩家的情况呢？？？（后面再考虑好了）
#
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
            return get_poweraction(player)

        else:
            Uptarget, Downtarget = get_attacktargetposiont(anamyplayers)
            # if Uptarget==Downtarget:
            #     start = mapfeature[player['x']][player['y']]
            #     end = mapfeature[Uptarget['x']+random.randint(-1,1)][Uptarget['y']+random.randint(-1,1)]
            # else:
            #     start = mapfeature[player['x']][player['y']]
            #     end = mapfeature[Uptarget['x']][Uptarget['y']]
            start = mapfeature[player['x']][player['y']]
            end = mapfeature[Uptarget['x']][Uptarget['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                print('在攻击的时候playerUp,flag_getsolution 是ok的')
                # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get

                    print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')
                    return
                    ac = random.randint(1, 4)
                    return ac

    if playerattackdown == player:
        if len(anamyplayers)==0:
            return get_poweraction(player)

        else:
            Uptarget, Downtarget = get_attacktargetposiont(anamyplayers)
            # if Uptarget==Downtarget:
            #     start = mapfeature[player['x']][player['y']]
            #     end = mapfeature[Downtarget['x']+random.randint(-1,1)][Downtarget['y']+random.randint(-1,1)]
            # else:
            #     start = mapfeature[player['x']][player['y']]
            #     end = mapfeature[Downtarget['x']][Downtarget['y']]
            start = mapfeature[player['x']][player['y']]
            end = mapfeature[Downtarget['x']][Downtarget['y']]
            print('起始的位置')
            print('x' + str(start.x) + 'y' + str(start.y))
            print('终止的位置')
            print('x' + str(end.x) + 'y' + str(end.y))
            path = getpath(start, end)
            if flag_getsolution:
                print('在攻击的时候playerDown,flag_getsolution 是ok的')
                # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
                ac = get_actionfrompath()
                return ac
            else:  # 如果在attack下没有solution ,我们就朝着那个方向走,也就是get


                    print('攻击模式下,我们是没有找到合适的路线,进行的是随机运动,')
                    return
                    ac = random.randint(1, 4)
                    return ac




# if len(powersetout) == 0:  # 如果已经空了 则根据模式，如果是攻击模式，则进行攻击。如果不是攻击模式，则尽量原远离自己的伙伴和墙壁，是否可以采用
#
#        return random.randint(1, 4)
#    else:
#        powersettemp = findnearestpowero(player)  # 实际上，我们寻找power的方式要是基于power的才行
#        # print(player)
#        # print(powersettemp)
#        start = mapfeature[player['x']][player['y']]
#        end = mapfeature[powersettemp['x']][powersettemp['y']]
#        print('起始的位置')
#        print('x' + str(start.x) + 'y' + str(start.y))
#        print('终止的位置')
#        print('x' + str(end.x) + 'y' + str(end.y))
#        path = getpath(start, end)
#        print('传回来的flaggetsolution是否有用呢', flag_getsolution)
#        if flag_getsolution:
#            print('flag_getsolution 是ok的')
#            # powersetout.remove(powersettemp)  # 移除掉已经被定位的，这个是跟根据player的最近来定，而不是根据power来制定的。
#            ac = get_actionfrompath()
#            return ac
#        else:
#            if Attack:
#                print('攻击模式下,我们是没有用的,进行额是随机运动,')
#                # 后面要修改为攻击敌人的情况

# else:
#     # w我们要逃跑，所以留给后面的逃跑的情况给出action
#     return None
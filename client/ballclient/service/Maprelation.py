
import client.client.ballclient.service.astarpath as astarpath


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
    global  tunnel
    mapfeature = []
    print('ok0')

    print('mapheight:'+str(map_height))
    print('mapheight:' + str(map_width))
    h=map_height
    w=map_width

    # print('ok1')
    for x in range(w):
        mapfeature += [[]]
        for y in range(h):
            mapfeature[x].append(astarpath.Grid(x, y, h, w))
        pass
    # print('ok2')
    for x in range(w):
        for y in range(h):
            astarpath.addneighbours(mapfeature[x][y])


    # print('ok3')
    # print(len(meteor))
    # print('###########menotr######')
    for i in range(len(meteors)):
        mapfeature[meteors[i]['x']][meteors[i]['y']].wall=True
        mapfeature[meteors[i]['x']][meteors[i]['y']].context='*'
   #     print('x'+str(meteor[i]['x'])+'y'+str(meteor[i]['y']))
  #  mapshow(mapfeature)
    for i in range(len(tunnel)):
        mapfeature[tunnel[i]['x']][tunnel[i]['y']].wall = True
        mapfeature[tunnel[i]['x']][tunnel[i]['y']].context = '*'

        mapfeature[tunnel[i]['x']][tunnel[i]['y']].tunnel= tunnel[i]['direction']
        mapfeature[tunnel[i]['x']][tunnel[i]['y']].context =tunnel[i]['direction'][0]


        pass

def mapshow(mapfeature):
    global map_height
    global map_width
    for y in range(map_height):
        b = ''
        for x in range(map_width):
            b += mapfeature[x][y].context + '   '
        print(b)

# coding: utf-8

# # Solving Maze with A-star algorithm, Q-learning and Deep Q-network

# ### Objective of this notebook is to solve self-made maze with A-star algorithm, Q-learning and Deep Q-network.
# ### The maze is in square shape, consists of start point, goal point and tiles in the mid of them.
# ### Each tile has numericals as its point. In other words, if you step on to the tile with -1, you get 1 point subtracted.
# ### The maze has blocks to prevent you from taking the route.

# In[1]:

import numpy as np
import pandas as  x
import random
import copy
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam, RMSprop
from collections import deque
from keras import backend as K


import  service


# In[ ]:

# Maze generator consists of maze class and field class.
# It generates a square shaped maze. The maze has route tiles, wall and block tiles, starting and goal point.
# The route tiles have -1 or 0 on it, which is the point you can get by stepping it.
# Apparently you will get 1 point subtracted if you step on -1 tile. The wall and block tiles, in #, are where you cannot interude.
# You have to bypass #. The starting point, namely S, is where you start the maze and goal point,
# which is shown as 50, is where you head to. You will earn 50 points when you made to the goal.




##Intialize my map class


#openset 装着每一个点 这个对象 openset[1,2,3]
#每一个对象又有很多f g h i j 等这样的特征 以及它本身的内容。
#所以我们应当建立一个数据对象
#for count in xrange(4):
    # x = SimpleClass()
    # x.attr = count
    # simplelist.append(x)

class mapgame:
    def __init__(self, w,h):
        self.w = w
        self.h=h
        self.size=w
        self.mapfeature=[]


    def map_intialization(self,meteors,tunnels,wormholws):
        for x in range(self.w):
            self.mapfeature += [[]]
            for y in range(self.h):
                self.mapfeature[x].append('0')
            pass

        for tunnel in tunnels:
            self.mapfeature[tunnel['x']][tunnel['y']]=tunnel['direction'][0]

        for meteor in meteors :
            self.mapfeature[meteor['x']][meteor['y']]='#'

    def map_update(self,myplayers,anamyplayers,powerlist):
        for myplayer in myplayers:
            self.mapfeature[myplayer['x']][myplayer['y']]='M'
        for anamyplayer in anamyplayers:
            self.mapfeature[anamyplayer['x']][anamyplayer['y']] = 'A'
        for power in powerlist:
            self.mapfeature[power['x']][power['y']] = '*'

    def map_display(self):
        #展示一下当前map的情况
        for y in range(self.h):
            b = ''
            for x in range(self.w):
                b += self.mapfeature[x][y] + '   '
            print(b)






'''


# # Maze Class

# In[2]:
# 建立Maze的图形
class Maze(object):
    def __init__(self, size=10, blocks_rate=0.1):
        self.size = size if size > 3 else 10  # 设定迷宫的大小
        self.blocks = int((size ** 2) * blocks_rate)  # 设定迷宫的阻挡的东西
        self.s_list = []  # 开始的点
        self.maze_list = []
        self.e_list = []

    def create_mid_lines(self, k, startrow, endrow):  # 创造一个
        if k == startrow:
            self.maze_list.append(self.s_list)  # 第零行的创造
        elif k == endrow:
            self.maze_list.append(self.e_list)  # 最后一行的创造
        else:  # 中间行的创造
            tmp_list = []
            for l in range(0, self.size):
                if l == 0:
                    tmp_list.extend("#")
                elif l == self.size - 1:
                    tmp_list.extend("#")  # 这个是将周围的最外圈设定为墙 就是＃
                else:  # 如果不是这样的话，我们就随机为它差生一个0 或者 -1 的数据
                    # a = random.randint(-1, 0)       #如果不是在嘴周围，我们就产生一个0  -1  1 的随机数  这个实际上就是随机的q的数值的了把
                    a = 0  # 这个其实上就是用来被更新q表的初始化的数值。
                    tmp_list.extend([a])  # 并且将此随机数添加到tmplist 当中去
            self.maze_list.append(tmp_list)  # 然后将当前行添加到我们的整个maze list 当中去
            # print('打印mazelist')                          #这个进行一行一行的打印 一行一行的建立maze
            # print(self.maze_list)

    def insert_blocks(self, k, s_r, e_r):  # 加入阻挡
        b_y = random.randint(1, self.size - 2)  # 随机我们的位置
        b_x = random.randint(1, self.size - 2)  # 随机x坐标
        if [b_y, b_x] == [1, s_r] or [b_y, b_x] == [self.size - 2, e_r]:
            k = k - 1
        else:
            self.maze_list[b_y][b_x] = "#"  # mazelist 是用来展示用的






    def generate_maze(self):  # 产生blok
        s_r = random.randint(1, (self.size / 2) - 1)

        for i in range(0, self.size):
            if i == s_r:
                self.s_list.extend("S")
            else:
                self.s_list.extend("#")
        start_point = [0, s_r]  # 开始的点

        e_r = random.randint((self.size / 2) + 1, self.size - 2)

        for j in range(0, self.size):
            if j == e_r:
                self.e_list.extend([50])
            else:
                self.e_list.extend("#")
        goal_point = [self.size - 1, e_r]  # 终止的点在那里

        for k in range(0, self.size):  # 创造中间的线
            self.create_mid_lines(k, startrow=start_point[0], endrow=goal_point[0])

        for k in range(self.blocks):
            self.insert_blocks(k, s_r, e_r)

        return self.maze_list, start_point, goal_point  # 返回的maze的列表  开始的点 和终点


# # Maze functions

# In[3]:

class Field(object):
    def __init__(self, maze, start_point, goal_point):
        self.maze = maze
        self.start_point = start_point
        self.goal_point = goal_point
        self.movable_vec = [[1, 0], [-1, 0], [0, 1], [0, -1]]

    def display(self, point=None):  # 这个函数的作用是为了展现dispaly的作用的。 下面所有的设定都是用来做现视使用的。
        field_data = copy.deepcopy(self.maze)
        if not point is None:  # 如果
            y, x = point  # 构建当前的 point point 会有是坐标是x或者坐标是y
            field_data[y][x] = "@@"  # 如果不是的话，我们就人为当前传过来的是有分数的
        else:
            point = ""  # 如果point是none 啥都没有
        for line in field_data:
            # print('打印line 和fileddata')
            # print(line)
            # print(tuple(line))
            print("\t" + "%3s " * len(line) % tuple(line))
        # 这个时候我们打印一下随机的数据

    def get_actions(self, state):  # 根据当前传入的状态 然后得到我们当前能够进行的动作   这个地方返回的可以的动作就已经保证了，我们的下一步的动作不会撞到墙了，
        movables = []
        if state == self.start_point:  # 如果我们当前的状态是处在七十点的地方，我们就是直接将我们的位置向下变化一格
            y = state[0] + 1
            x = state[1]
            a = [[y, x]]
            return a
        else:
            for v in self.movable_vec:  # 我们在可移动的方向中进行选择  这个是四个可以移动的方向list  这个地方得到的action就已经保证了不会撞到墙了

                y = state[0] + v[0]  #
                x = state[1] + v[1]
                if not (0 < x < len(self.maze) and
                        0 <= y <= len(self.maze) - 1 and
                        maze[y][x] != "#" and
                        maze[y][x] != "S"):
                    continue  # 如果x y 不超过地图的范围，如果下一步不等于#  且不到达目标点
                movables.append([y, x])  # 构建出来可以移动的列表
            if len(movables) != 0:  # 最后，如果我们构建完可以移动的范围之后，如果不是空集，则就返回当前可以移动的列表
                return movables
            else:  # 如果可移动的范围是空集 则说明当前不可移动了 返回none
                return None

    def get_val(self, state):
        y, x = state  # 得到评估值把
        if state == self.start_point:
            return 0, False  # 如果还在起始点，则说明此点为0不得分
        else:
            # for i in range(len(self.maze)):
            #     # print()
            #     print(maze[i])#
            if self.maze[y][x] == 'z':
                print('如果有maze中是＃的情况')
            #  print(self.maze[y][x
            v = float(self.maze[y][x])  # 如果当前的maze的分数

            # print('打印一下参数v')
            #
            # print(v)
            # print('打印一下maze')
            # print(self.maze)

            if state == self.goal_point:  # 如果当前的状态已经到达了终点
                return v, True  # 则返回当前的v 数值，并且返回是否到达了终点
            else:
                return v, False


# # Generate a maze

# In[7]:

size = 20  # 设定当前的地图的大小
barriar_rate = 0.1  # 设定障碍率

maze_1 = Maze(size, barriar_rate)  # 我们首先初始化迷宫  构建迷宫类
maze, start_point, goal_point = maze_1.generate_maze()  # 调用mmaze generate 函数   构建地图  起始点  和终点
# print('打印当前的maze')
# print(maze)
print('startpoint:' + str(start_point))
print('goal_point' + str(goal_point))
maze_field = Field(maze, start_point, goal_point)  # 根据我们当前的maze 起始点  和 终点  构建 mazefield
# print('打印当前的mazefiled')
maze_field.display()


# In[ ]:


# # Solving the maze with A-star algorithm
# ### https://en.wikipedia.org/wiki/A*_search_algorithm

# In[8]:

class Node(object):
    def __init__(self, state, start_point, goal_point):
        self.state = state
        self.start_point = start_point
        self.goal_point = goal_point
        self.hs = (self.state[0] - self.goal_point[0]) ** 2 + (self.state[1] - self.goal_point[1]) ** 2
        self.fs = 0
        self.parent_node = None

    def confirm_goal(self):
        if self.goal_point == self.state:
            return True
        else:
            return False


# In[9]:

class NodeList(list):
    def find_nodelist(self, state):
        node_list = [t for t in self if t.state == state]
        return node_list[0] if node_list != [] else None

    def remove_from_nodelist(self, node):
        del self[self.index(node)]


# In[48]:

class Aster_Solver(object):
    def __init__(self, maze, start_point, goal_point, display=False):
        self.Field = maze
        self.start_point = start_point
        self.goal_point = goal_point
        self.open_list = NodeList()
        self.close_list = NodeList()
        self.steps = 0
        self.score = 0
        self.display = display

    def set_initial_node(self):
        node = Node(self.start_point, self.start_point, self.goal_point)
        node.start_point = self.start_point
        node.goal_point = self.goal_point
        return node

    def go_next(self, next_actions, node):
        node_gs = node.fs - node.hs
        for action in next_actions:
            open_list = self.open_list.find_nodelist(action)
            dist = (node.state[0] - action[0]) ** 2 + (node.state[1] - action[1]) ** 2
            if open_list:
                if open_list.fs > node_gs + open_list.hs + dist:
                    open_list.fs = node_gs + open_list.hs + dist
                    open_list.parent_node = node
            else:
                open_list = self.close_list.find_nodelist(action)
                if open_list:
                    if open_list.fs > node_gs + open_list.hs + dist:
                        open_list.fs = node_gs + open_list.hs + dist
                        open_list.parent_node = node
                        self.open_list.append(open_list)
                        self.close_list.remove_from_nodelist(open_list)
                else:
                    open_list = Node(action, self.start_point, self.goal_point)
                    open_list.fs = node_gs + open_list.hs + dist
                    open_list.parent_node = node
                    self.open_list.append(open_list)

    def solve_maze(self):
        node = self.set_initial_node()
        node.fs = node.hs
        self.open_list.append(node)

        while True:
            node = min(self.open_list, key=lambda node: node.fs)
            print("current state:  {0}".format(node.state))

            if self.display:
                self.Field.display(node.state)

            reward, tf = self.Field.get_val(node.state)
            self.score = self.score + reward
            print("current step: {0} \t score: {1} \n".format(self.steps, self.score))
            self.steps += 1
            if tf == True:
                print("Goal!")
                break

            self.open_list.remove_from_nodelist(node)
            self.close_list.append(node)

            next_actions = self.Field.get_actions(node.state)
            self.go_next(next_actions, node)


# In[49]:
#
# astar_Solver = Aster_Solver(maze_field, start_point, goal_point, display=True)
# astar_Solver.solve_maze()


# In[ ]:


# # Solving the maze in Q-learning
# ### https://en.wikipedia.org/wiki/Q-learning

# In[50]:

class QLearning_Solver(object):
    def __init__(self, maze, display=False):
        self.Qvalue = {}
        self.Field = maze
        self.alpha = 0.2
        self.gamma = 0.9
        self.epsilon = 0.2
        self.steps = 0
        self.score = 0
        self.display = display

    def qlearn(self, greedy_flg=False):
        state = self.Field.start_point
        while True:
            if greedy_flg:  # 是否采用贪心随机，如果采用greedyflag  我们就正常的在q表中选择最好优化的上一步的策略
                self.steps += 1
                action = self.choose_action_greedy(state)
                print("current state: {0} -> action: {1} ".format(state, action))
                if self.display:
                    self.Field.display(action)
                reward, tf = self.Field.get_val(action)  # 我们很仔细的选择下一步
                self.score = self.score + reward  # 得到当前的主要的全部的分数
                print("current step: {0} \t score: {1}\n".format(self.steps, self.score))
                if tf == True:  # tf的作用是判断我们是否已经到达终点了
                    print("Goal!")
                    break

            else:  # 在采用贪心策略的另一个的对立面 是随机选择
                action = self.choose_action(state)  # 我们随机选择下一步
            if self.update_Qvalue(state, action):  # 如果更新Q值返回的true
                break
            else:  # 如果返回的false 我们就可以继续将当前的工作己行下去
                state = action

    def update_Qvalue(self, state, action):  # 根据当前的状态和当前的action 进行Q值更新
        Q_s_a = self.get_Qvalue(state, action)  # 根据当前的状态，和action 得到Q现实

        # print('我们打印一下state到底是什么样'+str(state))
        # print('我们打印一下当前的action 是什么样：'+str(action))
        mQ_s_a = max([self.get_Qvalue(action, n_action) for n_action in self.Field.get_actions(action)])  #
        # 这一步希望的是查找我们的状态中的表，在我们执行了下一步的状态之后，我们能够看到的最大的Q值是多少，也就是我们后面潜在的奖励是多少
        # 这个地方为什么是action了 我懂了，是因为action是代表了下一个state
        r_s_a, finish_flg = self.Field.get_val(action)  # 根据选择的这个action 得到最大的reward  和 是否完成
        # 根据这个动作得到当前这个动作的奖赏（实际的奖赏是多少）
        # field get value
        # 有两个作用：  作用1：返回当前的数值    作用2：返回当前是否到达了终点

        q_value = Q_s_a + self.alpha * (r_s_a + self.gamma * mQ_s_a - Q_s_a)
        # 计算新的Q的数值
        self.set_Qvalue(state, action, q_value)
        # 将新的数值q 更新的表中去
        return finish_flg

    def get_Qvalue(self, state, action):
        state = (state[0], state[1])
        action = (action[0], action[1])
        try:
            return self.Qvalue[state][action]  # 根据当前的state 和action 得到当前列表中的对应的Q值

        except KeyError:
            return 0.0

    def set_Qvalue(self, state, action, q_value):
        state = (state[0], state[1])
        action = (action[0], action[1])
        self.Qvalue.setdefault(state, {})
        self.Qvalue[state][action] = q_value  # 将此qvalue设定到标中去

    def choose_action(self, state):
        if self.epsilon < random.random():  # 如果这个随机大于设定的值
            return random.choice(self.Field.get_actions(state))  # 我们就返回当前的能够移动的范围内随机选择一个进行移动就好了
        else:
            return self.choose_action_greedy(state)  # 如果让我们依靠我们的表格进行选择的情况下，进行选择最好的q的数值

    def choose_action_greedy(self, state):  # 根据当前的状态选择最好的qvalue的数值
        best_actions = []
        max_q_value = -100
        for a in self.Field.get_actions(state):  # 当状态可以执行的action中，选择可以执行的最大的action
            q_value = self.get_Qvalue(state, a)
            if q_value > max_q_value:
                best_actions = [a, ]
                max_q_value = q_value
            elif q_value == max_q_value:
                best_actions.append(a)
        return random.choice(best_actions)

    def dump_Qvalue(self):
        print("##### Dump Qvalue #####")
        for i, s in enumerate(self.Qvalue.keys()):  # 将这些东西list中的内容搞成枚举的形式  并且对应起来的新的索引
            for a in self.Qvalue[s].keys():
                print("\t\tQ(s, a): Q(%s, %s): %s" % (str(s), str(a), str(self.Qvalue[s][a])))
            if i != len(self.Qvalue.keys()) - 1:
                print('\t----- next state -----')


# In[53]:

learning_count = 1000  # 我们总共学习多少步   这个我们学习总共就一个地图的情况，实际上，我们应当在多个地图下进行训练哦
QL_solver = QLearning_Solver(maze_field, display=True)  # 我们来调用QL solver 我们来调用的
for i in range(learning_count):
    print('We are in which count :' + str(i))
    QL_solver.qlearn()

QL_solver.dump_Qvalue()

# In[54]:
print('we will use greedy flag')
QL_solver.qlearn(greedy_flg=True)


########上面采用的Q-learning 的方式
# In[ ]:


# In[ ]:


# # Solving the maze in Deep Q-learning
# ### https://deepmind.com/research/dqn/

# In[55]:

class DQN_Solver:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=100000)
        self.gamma = 0.9
        self.epsilon = 1.0
        self.e_decay = 0.9999
        self.e_min = 0.01
        self.learning_rate = 0.0001
        self.model = self.build_model()

    def build_model(self):
        model = Sequential()
        model.add(Dense(128, input_shape=(2, 2), activation='tanh'))
        model.add(Flatten())
        model.add(Dense(128, activation='tanh'))
        model.add(Dense(128, activation='tanh'))
        model.add(Dense(1, activation='linear'))
        model.compile(loss="mse", optimizer=RMSprop(lr=self.learning_rate))
        return model

    def remember_memory(self, state, action, reward, next_state, next_movables, done):
        self.memory.append((state, action, reward, next_state, next_movables, done))

    def choose_action(self, state, movables):
        if self.epsilon >= random.random():
            return random.choice(movables)
        else:
            return self.choose_best_action(state, movables)

    def choose_best_action(self, state, movables):
        best_actions = []
        max_act_value = -100
        for a in movables:
            np_action = np.array([[state, a]])
            act_value = self.model.predict(np_action)
            if act_value > max_act_value:
                best_actions = [a, ]
                max_act_value = act_value
            elif act_value == max_act_value:
                best_actions.append(a)
        return random.choice(best_actions)

    def replay_experience(self, batch_size):
        batch_size = min(batch_size, len(self.memory))
        minibatch = random.sample(self.memory, batch_size)
        X = []
        Y = []
        for i in range(batch_size):
            state, action, reward, next_state, next_movables, done = minibatch[i]
            input_action = [state, action]
            if done:
                target_f = reward
            else:
                next_rewards = []
                for i in next_movables:
                    np_next_s_a = np.array([[next_state, i]])
                    next_rewards.append(self.model.predict(np_next_s_a))
                np_n_r_max = np.amax(np.array(next_rewards))
                target_f = reward + self.gamma * np_n_r_max
            X.append(input_action)
            Y.append(target_f)
        np_X = np.array(X)
        np_Y = np.array([Y]).T
        self.model.fit(np_X, np_Y, epochs=1, verbose=0)
        if self.epsilon > self.e_min:
            self.epsilon *= self.e_decay


# In[56]:

state_size = 2
action_size = 2
dql_solver = DQN_Solver(state_size, action_size)

episodes = 20000
times = 1000

for e in range(episodes):
    state = start_point
    score = 0
    for time in range(times):
        movables = maze_field.get_actions(state)
        action = dql_solver.choose_action(state, movables)
        reward, done = maze_field.get_val(action)
        score = score + reward
        next_state = action
        next_movables = maze_field.get_actions(next_state)
        dql_solver.remember_memory(state, action, reward, next_state, next_movables, done)
        if done or time == (times - 1):
            if e % 500 == 0:  # 每隔500次 打印下当前的分数 和 当前episod  当前循环了多少次才找到终点。
                print("episode: {}/{}, score: {}, e: {:.2} \t @ {}"
                      .format(e, episodes, score, dql_solver.epsilon, time))
            break
        state = next_state
    dql_solver.replay_experience(32)  # 根据所存储的state and action 我们的 我们随机选择一些数据进行神经网络的训练，这样的作用就是为了解决数据相关性的问题。

# In[58]:

state = start_point
score = 0
steps = 0
while True:
    steps += 1
    movables = maze_field.get_actions(state)
    action = dql_solver.choose_best_action(state, movables)
    print("current state: {0} -> action: {1} ".format(state, action))
    reward, done = maze_field.get_val(action)
    maze_field.display(state)
    score = score + reward
    state = action
    print("current step: {0} \t score: {1}\n".format(steps, score))
    if done:
        maze_field.display(action)
        print("goal!")
        break

# In[ ]:


# In[ ]:



'''
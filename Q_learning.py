
import numpy as np
import gym
import random
import matplotlib.pyplot as plt
from random import choice
from tqdm.notebook import tqdm
from kaggle_environments import evaluate, make
class ConnectX(gym.Env):#配置环境
    def __init__(self, switch_prob=0.5):
        self.env = make('connectx', debug=True)
        self.pair = [None, 'negamax']
        self.trainer = self.env.train(self.pair)
        self.switch_prob = switch_prob
        config = self.env.configuration
        self.action_space = gym.spaces.Discrete(config.columns)
        self.observation_space = gym.spaces.Discrete(config.columns * config.rows)

    def switch_trainer(self):#训练时互换先手
        self.pair = self.pair[::-1]
        self.trainer = self.env.train(self.pair)

    def step(self, action):#下棋
        return self.trainer.step(action)
    
    def reset(self):#重新开局
        if random.uniform(0, 1) < self.switch_prob:
            self.switch_trainer()
        return self.trainer.reset()
    
    def render(self, **kwargs):#显示环境
        return self.env.render(**kwargs)


class QTable:
    def __init__(self, action_space):
        self.table = dict()#由于状态太多用字典存
        self.action_space = action_space
        
    def add_item(self, state_key):#字典扩展
        self.table[state_key] = list(np.zeros(self.action_space.n))
        
    def __call__(self, state):#得到状态对应的table
        board = state['board'][:]
        board.append(state.mark)
        state_key = np.array(board).astype(str)
        state_key = hex(int(''.join(state_key), 3))[2:]
        if state_key not in self.table.keys():
            self.add_item(state_key)
        return self.table[state_key]
env = ConnectX()#环境
alpha = 0.1#Q-learnning的table表更新的参数
gamma = 0.6
epsilon = 0.99#随机数小于这个就随机跑
min_epsilon = 0.1#最小epsilon

episodes = 10000#迭代次数

alpha_decay_step = 1000#动态更新alpha，也是公式参数
alpha_decay_rate = 0.9
epsilon_decay_rate = 0.9999#每次减少epsilon
q_table = QTable(env.action_space)

all_epochs = []#存储状态
all_total_rewards = []
all_avg_rewards = []
all_qtable_rows = []
all_epsilons = []

for i in tqdm(range(episodes)):
    state = env.reset()
    epsilon = max(min_epsilon, epsilon * epsilon_decay_rate)
    epochs, total_rewards = 0, 0
    done = False
    
    while not done:
        if random.uniform(0, 1) < epsilon:#随机选择合法列
            action = choice([c for c in range(env.action_space.n) if state['board'][c] == 0])
        else:#按照table进行选择
            row = q_table(state)[:]
            selected_items = []
            for j in range(env.action_space.n):
                if state['board'][j] == 0:
                    selected_items.append(row[j])
                else:
                    selected_items.append(-1e7)
            action = int(np.argmax(selected_items))

        #通过gym的step获得执行aciton后的状态，结果，是否结束
        next_state, reward, done, info = env.step(action)

        # 如果结束获得奖励
        if done:
            if reward == 1:
                reward = 20
            elif reward == 0:
                reward = -20
            else:
                reward = 10
        #本来需要减去0.05，后来发现结果太差了，我们应该要期望我们的机器人能够坚持久一点
        #else:
           #reward = -0.05  
        #得到更新Q表值的参数
        old_value = q_table(state)[action]
        next_max = np.max(q_table(next_state))
        
        # 更新Q表
        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table(state)[action] = new_value
        
        #记录答案
        state = next_state
        epochs += 1
        total_rewards += reward


    all_epochs.append(epochs)
    all_total_rewards.append(total_rewards)
    avg_rewards = np.mean(all_total_rewards[max(0, i-100):(i+1)])
    all_avg_rewards.append(avg_rewards)
    all_qtable_rows.append(len(q_table.table))
    all_epsilons.append(epsilon)

    if (i+1) % alpha_decay_step == 0:
        alpha *= alpha_decay_rate
tmp_dict_q_table = q_table.table.copy()
dict_q_table = dict()

for k in tmp_dict_q_table:
    if np.count_nonzero(tmp_dict_q_table[k]) > 0:
        dict_q_table[k] = int(np.argmax(tmp_dict_q_table[k]))
Q_learning_agent = '''def my_agent(observation, configuration):
    from random import choice

    q_table = ''' \
    + str(dict_q_table).replace(' ', '') \
    + '''

    board = observation.board[:]
    board.append(observation.mark)
    state_key = list(map(str, board))
    state_key = hex(int(''.join(state_key), 3))[2:]

    if state_key not in q_table.keys():
        return choice([c for c in range(configuration.columns) if observation.board[c] == 0])

    action = q_table[state_key]

    if observation.board[action] != 0:
        return choice([c for c in range(configuration.columns) if observation.board[c] == 0])

    return action
    '''

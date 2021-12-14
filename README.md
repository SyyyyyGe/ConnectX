
# ConnectX by 20190441030 孙瑶








## 1. 配置环境

```
!pip install 'kaggle-environments>=0.1.6'
```

## 2. 复制我的def的机器人代码就可以

## 3. 定义比赛并可以查看结果

```python
def mean_reward(rewards):
    return "{0} episodes: won {1}, lost {2}, draw {3}".format(
                                                           len(rewards),
                                                           sum(1 if r[0] > 0 else 0 for r in rewards),
                                                           sum(1 if r[1] > 0 else 0 for r in rewards),
                                                           sum(r[0] == r[1] for r in rewards)
                                                       )
#和官方内置机器人比赛
#print("Q-learning vs random:", mean_reward(evaluate("connectx", [Q_learning_agent, "random"], num_episodes=20)))
#print("Q-learning vs negamax:", mean_reward(evaluate("connectx", [Q_learning_agent, "negamax"], num_episodes=20)))
#先后手区别，每两个都对战20次，10次先手，10次后手
print("Q-learning vs Minimax:", mean_reward(evaluate("connectx", [Q_learning_agent, Minimax_agent], num_episodes=10)))
print("Minimax vs Q-learning:", mean_reward(evaluate("connectx", [Minimax_agent, Q_learning_agent], num_episodes=10)))
print("Q-learning vs MCTSt:", mean_reward(evaluate("connectx", [Q_learning_agent, MCTS_agent], num_episodes=10)))
print("MCTS vs Q-learning:", mean_reward(evaluate("connectx", [MCTS_agent, Q_learning_agent], num_episodes=10)))
print("Minimax vs MCTS:", mean_reward(evaluate("connectx", [Minimax_agent, MCTS_agent], num_episodes=10)))
print("MCTS vs Minimax:", mean_reward(evaluate("connectx", [MCTS_agent, Minimax_agent], num_episodes=10)))
```

## 4. 提交文件

除了Q_learning需要训练很久之后，才可以提交，其他都可以直接提交，提交那个agent的函数定义就行。


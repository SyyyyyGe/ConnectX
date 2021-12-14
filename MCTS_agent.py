
def MCTS_agent(observation, configuration):
    from kaggle_environments import evaluate, make, utils
    import random
    import math
    import time
    env = make("connectx", debug=True)
    configuration = env.configuration
    global current_node
    T_max = configuration.timeout - 0.34  #通过这个来限制每次模拟多少回
    Cp_default = 1 #uct参数
    #得到当前点的uct值
    def uct_score(node_total_score, node_total_visits, parent_total_visits, Cp=Cp_default):
        if node_total_visits == 0:
            return math.inf
        return node_total_score / node_total_visits + Cp * math.sqrt(2 * math.log(parent_total_visits) / node_total_visits)
    def play(board, col, mark, config):#下棋
        cols = config.columns
        rows = config.rows
        row = max([r for r in range(rows) if board[col + (r * cols)] == 0])
        board[col + row * cols] = mark
    #查看是否获胜
    def iswinner(board, col, mark, config):
        cols = config.columns
        rows = config.rows
        inarow = config.inarow - 1
        row = min([r for r in range(rows) if board[col + (r * cols)] == mark])
        def checkwinner(drow, dcol):
            for i in range(1, inarow + 1):#查看与这个棋子的连续几个棋子
                r = row + drow * i
                c = col + dcol * i
                if (
                    r < 0 
                    or r >= rows 
                    or c < 0 
                    or c >= cols 
                    or board[c + r * cols] != mark
                ):return i - 1
            return inarow
        return (checkwinner(1, 0) >= inarow #水平
                or (checkwinner(0, 1)+ checkwinner(0, -1)) >= inarow #竖直
                or (checkwinner(-1,-1) + checkwinner(1,1)) >= inarow #斜线
                or (checkwinner(-1, 1) + checkwinner(1,-1)) >= inarow) #斜线
    #查看是否平局
    def isdraw(board):
    #     cols = config.columns
    #     for col in range(cols):
    #         if board[col] != 0:return False
    #     return True
        return not(any(mark==0 for mark in board))
    def check_play_result(board, col, mark, config):
        #输出下棋结果
        if iswinner(board, col, mark, config): return (True, 1)
        if isdraw(board): return (True, 0.5)
        else: return (False,None)
    def random_action(board, config):
        #随机下棋
        return random.choice([c for c in range(config.columns) if board[c] == 0])
    #对手棋子
    def opp_mark(mark):return 3 - mark
    #对手得分
    def opp_score(score):return 1 - score

    #随机下棋直到下到结果
    def random_policy_simulation(board, mark, config):
        #记录当前属性，后续有用
        ori_mark = mark
        board = board.copy()
        col = random_action(board, config)
        play(board, col, mark, config)#落子
        is_end, score = check_play_result(board, col, mark, config)#检查结果
        while not is_end:#如果没有结束就不断这么做
            mark = opp_mark(mark)
            col = random_action(board, config)
            play(board, col, mark, config)
            is_end, score = check_play_result(board, col, mark, config)
        if(mark == ori_mark):return score#结束后查看获胜玩家和目前玩家是不是一样的，一样目前玩家的分数就是score，不一样就反过来
        else: return opp_score(score)
    def find_action_taken_by_opp(new_board, old_board, config):#找到对手下的那一步棋
        for i, piece in enumerate(now_board):
            if(piece != old_board[i]):return i % config.columns
        return -1
    class Node():
        def __init__(self, board, mark, config, parent = None, is_end = False,end_score = None,action_taken = None):
            self.board = board.copy() #记录对局状况
            self.mark = mark #记录是哪个棋子
            self.config = config #记录游戏配置
            self.parent = parent #记录父节点
            self.children =[] #记录孩子
            self.node_total_score = 0 #记录自己的总分
            self.node_total_visits = 0 #记录自己被遍历次数
            self.available_moves = [c for c in range(config.columns) if board[c] == 0] #记录可以下的位置
            self.expandable_moves = self.available_moves.copy() #记录可以扩展的位置
            self.is_end = is_end #查看该结点是否是终止结点
            self.end_score = end_score #如果是终止结点会有分数
            self.action_taken = action_taken #父节点到该节点经过那一步棋

        def is_expandable(self):
            #判断叶子结点是否可以扩展
            return (not self.is_end) and (len(self.expandable_moves)>0)

        def expand_and_simulate_child(self):#生成孩子节点并且模拟结果更新孩子结点直到游戏结束
            col = random.choice(self.expandable_moves)
            child_board = self.board.copy()
            play(child_board, col, self.mark, self.config)#落子
            is_end,end_score = check_play_result(child_board, col, self.mark, self.config)#下完棋后查看结果
            self.children.append(Node(#扩展叶子结点
                child_board, opp_mark(self.mark), 
                self.config, self,
                is_end = is_end,
                end_score = end_score,
                action_taken = col))
            simulation_score = self.children[-1].simulate()#往下递归不断模拟得到这个选择最终的模拟分数
            self.children[-1].backpropagate(simulation_score)#更新当前score和visits，并且对于父节点进行反馈
            self.expandable_moves.remove(col)

        def simulate(self):#递归模拟返回这次模拟的得分
            if(self.is_end):return self.end_score
            return opp_score(random_policy_simulation(self.board,self.mark,self.config))

        def backpropagate(self, simulation_score):#模拟结束进行反馈
            self.node_total_score += simulation_score #更新当前得分
            self.node_total_visits += 1#更新访问次数
            if self.parent is not None:
                self.parent.backpropagate(opp_score(simulation_score))  #每次更新都是选手互换

        def choose_child_by_action(self,action):
            #得到模拟后的一个状态
            for child in self.children:
                if child.action_taken == action:
                    return child
            return None

        def choose_best_child(self,Cp):
            #模拟过程中，首先获得所有孩子的uct分数
            children_scores = [uct_score(child.node_total_score,
                                         child.node_total_visits,
                                         self.node_total_visits,
                                         Cp)for child in self.children]
            max_score = max(children_scores)
            best_child_index = children_scores.index(max_score)
            #获取最高uct的孩子，模拟
            return self.children[best_child_index]

        def tree_single_run(self):#可以理解为自动模拟
            if self.is_end:#叶子结点返回反馈
                self.backpropagate(self.end_score)
                return
            if self.is_expandable():#未统计的结点进行更新
                self.expand_and_simulate_child()
                return
            self.choose_best_child(Cp_default).tree_single_run()#选择最高uct
        def choose_play_child(self):
            #选择分数最高的孩子结点
            children_scores = [child.node_total_score for child in self.children]
            max_score = max(children_scores)
            best_child_index = children_scores.index(max_score)
            return self.children[best_child_index]
    init_time = time.time()
    board = observation.board
    mark = observation.mark
    #如果这个局面之前模拟过，直接利用，不然就更新棋盘
    try:  
        current_node = current_node.choose_child_via_action(find_action_taken_by_opponent(board, current_node.board, configuration))
        current_node.parent = None  # 传统做法
        
    except: 
        current_node = Node(board, mark,configuration, parent=None, is_end=False, end_score=None, action_taken=None)
   
    #不断模拟
    while time.time() - init_time <= T_max:
        #print(time.time() - init_time)
        current_node.tree_single_run()
    current_node = current_node.choose_play_child()
    return current_node.action_taken

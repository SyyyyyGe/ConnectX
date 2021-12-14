def Minimax_agent(observation, configuration):
    import random
    import copy
    #设置中心柱和底层优先
    scoremp=[
    [0,0,25,100,25,0,0],#最高层
    [0,25,50,500,50,25,0],
    [25,50,100,700,100,50,25],
    [50,100,200,1000,200,100,50],
    [75,150,400,2000,400,150,75],
    [100,200,600,6000,600,200,100]#最底层，权值为6000的那一列就是中心柱
    ]
    #落子
    def drop_piece(mp,c,player):
        mp = copy.deepcopy(mp)
        for r in range(5,-1,-1):
            if mp[r][c]==0:
                break
        mp[r][c]=player
        return mp
    #判断胜负
    def getwinner(mp):
        for r in range(0,6,1):
            for c in range(0, 3, 1):
                if mp[r][c] != 0 and mp[r][c] == mp[r][c+1] == mp[r][c+2] == mp[r][c+3]:return mp[r][c]
        for c in range(0,7,1):
            for r in range(0,3,1):
                if mp[r][c] != 0 and mp[r+1][c]==mp[r+2][c]==mp[r + 3][c]==mp[r][c]:return mp[r][c]
        for r in range(3):
            for c in range(4):
                if mp[r][c] != 0 and mp[r+1][c+1]==mp[r+2][c+2]==mp[r][c]==mp[r+3][c+3]:return mp[r][c]
        for r in range(3):
            for c in range(3, 7, 1):
                if mp[r][c] != 0 and mp[r][c]==mp[r+1][c-1]==mp[r+2][c-2]==mp[r+3][c-3]:return mp[r][c]
        num = 0
        for c in range(7):
            num+=(mp[0][c]==0)
        if num == 0: return -1;
        return 0;
    #将board转为二维，方便计算奖励
    def getMp(arrMp):
        line1 = arrMp[0:7]
        line2 = arrMp[7:14]
        line3 = arrMp[14:21]
        line4 = arrMp[21:28]
        line5 = arrMp[28:35]
        line6 = arrMp[35:42]
        mp = [line1, line2 , line3, line4, line5, line6] 
        return mp
    def colr(tmp, tmplow, player, r):
        score = 0;
        #获胜就加100000；三子一空加700，形成危险翻倍；二子二空加300，形成近似危险加100；一子三空加100；
        #最后一个循环是奇偶策略，符合奇偶策略加100
        if tmp.count(player)==4:score += 100000
        if tmp.count(player)==3 and tmp.count(0)==1:
            for c in range(4):
                if(tmp[c]==0):
                    if ((6-r)-tmplow[c])%2==player%2:#符合奇偶危险
                        score+=700
            score += 700
        if tmp.count(player)==2 and tmp.count(0)==2:
            for c in range(4):
                if(tmp[c]==0):
                    if ((6-r)-tmplow[c])%2==player%2:#符合近似危险
                        score+=100
            score += 300
        if tmp.count(player)==1 and tmp.count(0)==3:
            score += 100
        for c in range(4):#对于枚举的4个棋子，如果存在空位，并且填到这需要的棋子数符合奇偶策略，就加100
            if tmp[c]==0:#tmp[i]=0表示空位
                if ((6-r)-tmplow[c])%2==player%2:#符合奇偶策略
                    score+=100
        return score;
    def colc(tmp,player):
        score = 0;
        if tmp.count(player)==4:score += 100000
        if tmp.count(player)==3 and tmp.count(0)==1:
            score += 700
        if tmp.count(player)==2 and tmp.count(0)==2:
            score += 300
        if tmp.count(player)==1 and tmp.count(0)==3:
            score += 100
        return score//2#因为是列，所以要缩小列权值，因为列最容易被堵住
    def colx1(tmp,tmplow,player,r):
        #斜线同行一样
        score = 0;
        if tmp.count(player)==4:score += 100000
        if tmp.count(player)==3 and tmp.count(0)==1:
            for c in range(4):
                if(tmp[c]==0):
                    if ((6-r-c)-tmplow[c])%2==player%2:
                        score+=700
            score += 700
        if tmp.count(player)==2 and tmp.count(0)==2:
            for c in range(4):
                if(tmp[c]==0):
                    if ((6-r-c)-tmplow[c])%2==player%2:
                        score+=100
            score += 300
        if tmp.count(player)==1 and tmp.count(0)==3:
            score += 100
        for c in range(4):
            if tmp[c]==0:
                if ((6-r-c)-tmplow[c])%2==player%2:
                    score+=100
        return score;
    def colx2(tmp, tmplow,player,r):
        score = 0;
        if tmp.count(player)==4:score += 100000
        if tmp.count(player)==3 and tmp.count(0)==1:
            for c in range(4):
                if(tmp[c]==0):
                    if ((6-r+c)-tmplow[c])%2==player%2:
                        score+=700
            score += 700
        if tmp.count(player)==2 and tmp.count(0)==2:
            for c in range(4):
                if(tmp[c]==0):
                    if ((6-r+c)-tmplow[c])%2==player%2:
                        score+=100
            score += 300
        if tmp.count(player)==1 and tmp.count(0)==3:
            score += 100
        for c in range(4):#对于枚举的4个棋子，如果存在空位，并且填到这需要的棋子数符合奇偶策略，就加100
            if tmp[c]==0:#tmp[i]=0表示空位
                if ((6-r+c)-tmplow[c])%2==player%2:#
                    score+=100

        return score;
    #
    def getscore(mp,player):
        score=0
        for r in range(6):
            for c in range(7):
                if mp[r][c] == player:score+=scoremp[r][c];
        lowc=[0,0,0,0,0,0,0]
        for c in range(7):
            for r in range(5,-1,-1):
                if mp[r][c]!=0:lowc[c]=lowc[c]+1
        for r in range(6):
            row_arr = mp[r]
            for c in range(4):
                tmp=[row_arr[i+c] for i in range(4)]
                tmplow=[lowc[i+c] for i in range(4)]
                score += colr(tmp,lowc, player,r)

        for c in range(7):
            col_arr = [mp[i][c] for i in range(6)]
            for r in range(3):
                tmp = [col_arr[i+r] for i in range(4)]
                score += colc(tmp, player)
        for r in range(3):
            for c in range(4):
                tmp = [mp[r+i][c+i] for i in range(4)]
                tmplow=[lowc[i+c] for i in range(4)]
                score += colx1(tmp, tmplow, player,r)
        for r in range(3):
            for c in range(4):
                tmp = [mp[r+3-i][c+i] for i in range(4)]
                score += colx2(tmp, tmplow, player, r)
        return score
    def getScore(mp,opp_player,ai_player):#注重防御，又不会忽视进攻
        return getscore(mp,ai_player)-2*getscore(mp,opp_player)
    def getVaildActions(mp):
        return [c for c in range(7) if mp[0][c] == 0]
    def alphabeta(mp, depth, alpha, beta, max_player, opp_player, ai_player):#下棋中的Minimax模板，具体流程都一样
        winner = getwinner(mp)
        #判断是否获胜，获胜或者失败直接赋值大数，使得所有策略没用
        if(winner != 0):
            if winner == ai_player:return None,9999999999
            elif winner == opp_player:return None,-9999999999
            else: return None,100
        #深度为0，即搜索结束后，还没分出胜负，就通过启发式策略计算得分
        if(depth == 0):return None,getScore(mp,opp_player,ai_player)
        if(max_player):
            #当前为AI就要得到最大得分
            best_score=-9999999999999
            best_action=3
            for action in getVaildActions(mp):
                newMp = drop_piece(mp, action, ai_player)
                newScore = alphabeta(newMp,depth-1,alpha,beta,False,opp_player,ai_player)[1]
                if(newScore>best_score):#不断更新最大得分和策略
                    best_score=newScore
                    best_action=action
                alpha=max(alpha,newScore)#alphabeta剪枝
                if(alpha>=beta):break
            return best_action,best_score
        else:
            #当前为对手就要得到最小得分
            worst_score=9999999999999
            worst_action=3
            for action in getVaildActions(mp):
                newMp = drop_piece(mp, action, opp_player)
                newScore = alphabeta(newMp,depth-1,alpha,beta,True,opp_player,ai_player)[1]
                if(newScore<worst_score):#不断更新最小得分
                    worst_score=newScore
                    worst_action=action
                beta=min(beta,newScore)#alphabeta剪枝
                if(alpha>=beta):break
            return worst_action,worst_score
    mp = getMp(observation["board"])
    player = observation["mark"]
    opp_player = ((player-1)^1)+1
    action,score=alphabeta(mp,5,-999999999999999,999999999999999,True,opp_player,player)
    print(score)
    return action

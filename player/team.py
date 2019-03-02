"""
The team.py file is where you should write all your code!

Write the __init__ and the step functions. Further explanations
about these functions are detailed in the wiki.

List your Andrew ID's up here!
antianw
jiejiao
"""
from awap2019 import Tile, Direction, State
import random
class Team(object):
    def __init__(self, initial_board, team_size, company_info):
        """
        The initializer is for you to precompute anything from the
        initial board and the company information! Feel free to create any
        new instance variables to help you out.

        Specific information about initial_board and company_info are
        on the wiki. team_size, although passed to you as a parameter, will
        always be 4.
        """
        self.board = initial_board
        self.team_size = team_size
        self.company_info = company_info

        self.team_name = "ah269ciao"
        self.visited = set()

    def perm(self, a, b, w, h):
        result = []

        if (w == 0 and h == 0):
            return [[]]

        if (w != 0):
            res = self.perm(a, b, w - 1, h)
            for i in range(len(res)):
                result.append([a] + res[i])
        if (h != 0):
            res = self.perm(a, b, w, h - 1)
            for i in range(len(res)):
                result.append([b] + res[i])
        return result

    def path(self, tx, ty, bx, by):
        if (tx > bx):
            a = Direction.DOWN
        else:
            a = Direction.UP
        if (ty > by):
            b = Direction.RIGHT
        else:
            b = Direction.LEFT

        h = abs(ty - by)
        w = abs(tx - bx)
        #print("w: ", w, "h: ", h)
        return self.perm(a, b, w, h)

    def evaluate(self, board, tx, ty, bx, by):
        perm = self.path(tx, ty, bx, by)
        if (tx == bx and ty == by):
            return (0, Direction.ENTER)
        minCost = 999999
        minPath = None
        for p in perm:
            cost = 0
            x = bx
            y = by
            for move in p:
                if (move == Direction.RIGHT):
                    cost += board[x][y+1].get_threshold()
                    y += 1
                elif (move == Direction.LEFT):
                    cost += board[x][y-1].get_threshold()
                    y -= 1
                elif (move == Direction.UP):
                    cost += board[x-1][y].get_threshold()
                    x -= 1
                elif (move == Direction.DOWN):
                    cost += board[x+1][y].get_threshold()
                    x += 1
            if (minPath == None or minCost > cost):
                minPath = p
                minCost = cost
        return (minCost, minPath[0])

    def getXY(self, board, name):
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j].get_booth() == name:
                    return i, j

    def line_end(self, board, name):
        for i in range(len(board)):
            for j in range(len(board[0])):
                tile = board[i][j]
                if tile.is_end_of_line() and tile.get_line == name:
                    return i, j

    def valid_index(self, board, x, y):
        return (x >= 0 and  y >= 0 and x < len(board) and y < len(board[0]))
    def step(self, visible_board, states, score):
        """
        The step function should return a list of four Directions.

        For more information on what visible_board, states, and score
        are, please look on the wiki.
        """

        new_dir = [Direction.NONE for x in range(4)]
        for i in range(4):
            x = states[i].x
            y = states[i].y

            if states[i].line_pos == 1 and i != 0 and states[0].x == states[i].x and states[0].y == states[i].y:
                new_dir[0] = Direction.REPLACE
                new_dir[i] = Direction.REPLACE
            
            if states[i].line_pos == 0:
                tmp =  visible_board[x][y].get_line()
                if tmp not in self.visited:
                    self.visited.add(tmp)


            if states[i].line_pos != -1:
                continue
            bestDir = None
            leastPop = 99999

            for j in [-2,-1,0,1,2]:
                for k in [-2,-1,0,1,2]:
                    if(not self.valid_index(visible_board, x+j, y+k)):
                        continue
                    tile = visible_board[x+j][y+k]
                    if tile.is_end_of_line():
                        companyName = tile.get_line()
                        if companyName not in self.visited:
                            states[i].x = x+j
                            states[i].y = y+k
                            oriDir = states[i].dir
                            states[i].dir = Direction.ENTER
                            curr_pos = states[i].line_pos
                            states[i].x -= j
                            states[i].y -= k
                            states[i].dir = oriDir
                            (additional_steps, path) = self.evaluate(visible_board, x+j, y+k, x, y)
                            if curr_pos + additional_steps - self.company_info[companyName] < leastPop:
                                bestDir = path
                                if bestDir == Direction.ENTER:
                                    self.visited.add(companyName)
                                leastPop = curr_pos + additional_steps - self.company_info[companyName]
                                #print("bestDir: ", bestDir, "leastPop: ", leastPop)


            if states[i].line_pos != -1 and i != 0 and bestDir != None:
                memberDis = states[i].line_pos
                companyName = visible_board[states[i].x][states[i].y].get_line()
                companyX, companyY = self.getXY(self.board, companyName)
                leaderDis, leaderPath = self.evaluate(self.board, companyX, companyY, x, y)
                if leaderDis <= memberDis:
                    new_dir[0] = leaderPath

            if bestDir == Direction.ENTER:
                self.visited.add(visible_board[x][y].get_line())
            if i != 0:
                for z in {0,1,2,3} - {i}:
                    if self.board[states[z].x][states[z].y].get_line() == self.board[states[i].x][states[i].y].get_line():
                        new_dir[i] = random.choice([Direction.DOWN, Direction.LEFT, Direction.RIGHT, Direction.UP])

            if bestDir == None:
                bestDir = random.choice([Direction.DOWN, Direction.LEFT, Direction.RIGHT, Direction.UP])

            new_dir[i] = bestDir

        return new_dir

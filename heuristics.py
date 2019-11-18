
from collections import Counter

import math


class heuristics:
    def __init__(self,depth):

        self.depth=depth

    def h1(self,game,state,last_move,player):
        """

        :param state: current game state/board
        :param last_move: last move was played
        :param player: current player
        :return: score for this state
        """

        score = 0
        score += self.evaluate_small_box(game,game.box_won, player) * 200
        for b in range(9):
            idxs = game.indices_of_box(b)
            box_str = state[idxs[0]: idxs[-1] + 1]
            score += self.evaluate_small_box(game,box_str, player)
        return score

    def evaluate_small_box(self, game,box_str, player):
        """
        :param box_str: box to evaluate
        :param player: current player
        :return: score for this small box
        """
        score = 0
        three = Counter(player * 3)
        two = Counter(player * 2 + ".")
        one = Counter(player * 1 + "." * 2)
        three_opponent = Counter(game.opponent(player) * 3)
        two_opponent = Counter(game.opponent(player) * 2 + ".")
        one_opponent = Counter(game.opponent(player) * 1 + "." * 2)

        for idxs in game.possible_goals:
            (x, y, z) = idxs
            current = Counter([box_str[x], box_str[y], box_str[z]])

            if current == three:
                score += 100
            elif current == two:
                score += 10
            elif current == one:
                score += 1
            elif current == three_opponent:
                score -= 100
                return score
            elif current == two_opponent:
                score -= 10
            elif current == one_opponent:
                score -= 1

        return score

    def evaluate2(self, game,state, last_move, player):
        """

        :param state: current game state/board
        :param last_move: last move was played
        :param player: current player
        :return: score for this state
        """

        score = 0
        score += self.evaluate_small_matrix(game,game.box_won, player) * 200
        for b in range(9):
            idxs = game.indices_of_box(b)
            box_str = state[idxs[0]: idxs[-1] + 1]
            score += self.evaluate_small_matrix(game,box_str, player)
        return score

    def evaluate_small_matrix(self,game, box_str, player):
        """

        :param game: game object
        :param box_str: box to evaluate
        :param player: current player
        :return: score for this box
        """
        score = 0
        center_index = 4
        corner_indecies = [0, 2, 6, 8]
        side_indecies = [1, 3, 5, 7]

        for idx in box_str:
            if idx == center_index:
                if box_str[idx] == player:
                    score += (76 ** 2)
                elif box_str[idx] == game.opponent(player):
                    score -= (76 ** 2)
            elif idx in corner_indecies:
                if box_str[idx] == player:
                    score += 76
                elif box_str[idx] == game.opponent(player):
                    score -= 76
            elif idx in side_indecies:
                if box_str[idx] == player:
                    score += 1
                elif box_str[idx] == game.opponent(player):
                    score -= 1
        return score

    def evaluateBlocking(self, game, state, lastMove, player):
        """

        :param game: Game object
        :param state: State we are currently checking
        :param lastMove: The move that we last did
        :param player: Current player
        :return: The score for the current state using blocking methods, checking the current state and the next state
        """

        if player == 'O':
            opponent = 'X'
        else:
            opponent = 'O'
        possibleMoves = game.possible_moves(state, lastMove)
        if(possibleMoves == []):
            temp = game.update_box_won(state)
            game_won = game.check_small_box(temp)
            if(game_won == player):
                return 100000
            elif(game_won == opponent):
                return -100000
            else:
                return 0
        box1 = int(lastMove / 9)
        box2 = int(possibleMoves[0] / 9)
        check1 = self.evaluateByCurrentStateBox(box1, game, player, opponent, state)
        check3 = self.evaluateByNextStateBox(box2, game, player, opponent, state, check1)
        return check3

    def evaluateByCurrentStateBox(self, box, game, player, opponent, state):
        """

        :param box: The current states box number(outer)
        :param game: Game object
        :param player: Current player
        :param opponent: Opponent
        :param state: Current state
        :return: Score of current state regardless of the next move
        """
        currentPossibleGoals = self.possibleGoalsBox(box)
        moves = game.indices_of_box(box)
        boxEdges = [moves[0], moves[2], moves[6], moves[8]]
        boxCenter = moves[4]
        boxSides = [moves[1], moves[3], moves[5], moves[7]]
        max = 0
        condition = 0
        for options in currentPossibleGoals:
            index1, index2, index3 = options
            countOpponent = 0
            countPlayer = 0
            for index in options:
                if (state[index] == opponent):
                    countOpponent += 1
                if (state[index] == player):
                    countPlayer += 1
            if (countOpponent == 1 and countPlayer == 1):
                condition = 1
            if (countOpponent == 3):
                condition = -50000
            if (countOpponent == 2 and countPlayer == 0):
                condition = -10000
            if (countPlayer == 2 and countOpponent == 1):
                condition = 2500
            if (countOpponent == 0 and countPlayer == 2):
                condition = 5000
            if (countPlayer == 1 and countOpponent == 2):
                condition = 7500
            if (countPlayer == 3):
                condition = 10000
            max += condition
        return max

    def evaluateByNextStateBox(self, box, game, player, opponent, state, scoreCurrentBox):
        """

        :param box: The current states box number(outer)
        :param game: Game object
        :param player: Current player
        :param opponent: Opponent
        :param state: Current state
        :param scoreCurrentBox: The score of the state which was last done
        :return: the score of the state with consideration of the score of the last state
        """
        currentPossibleGoals = self.possibleGoalsBox(box)
        moves = game.indices_of_box(box)
        boxEdges = [moves[0], moves[2], moves[6], moves[8]]
        boxCenter = moves[4]
        boxSides = [moves[1], moves[3], moves[5], moves[7]]
        max = 0
        condition = 0
        for options in currentPossibleGoals:
            index1, index2, index3 = options
            countOpponent = 0
            countPlayer = 0
            for index in options:
                if (state[index] == opponent):
                    countOpponent += 1
                if (state[index] == player):
                    countPlayer += 1
            if (countOpponent == 1 and countPlayer == 1):
                condition = 1
            if (countOpponent == 3):
                condition = -50000
            if (countOpponent == 2 and countPlayer == 0):
                condition = -10000
            if (countPlayer == 2 and countOpponent == 1):
                condition = 2500
            if (countOpponent == 0 and countPlayer == 2):
                condition = 5000
            if (countPlayer == 1 and countOpponent == 2):
                condition = 7500
            if (countPlayer == 3):
                condition = 10000
            max += condition
        if (scoreCurrentBox >= 2500):
            return max + scoreCurrentBox
        if (scoreCurrentBox < 2500):
            return scoreCurrentBox

    def possibleGoalsBox(self, box):
        """

        :param box: The current states box number(outer)
        :return: Possible goal moves in this box
        """
        place = 9 * box
        tempPossibleGoals = [(0 + place, 4 + place, 8 + place), (2 + place, 4 + place, 6 + place)]
        tempPossibleGoals += [(i + place, i + place + 3, i + place + 6) for i in range(3)]
        tempPossibleGoals += [(3 * i + place, 3 * i + 1 + place, 3 * i + 2 + place) for i in range(3)]
        return tempPossibleGoals


    def get_heur(self,h):
        """

        :param h: The heuristic's number
        :return: The heuristic according to h
        """
        if h=="1":
            return self.h1
        if h == "2":
            return self.evaluate2
        if h == "3":
            return self.evaluateBlocking
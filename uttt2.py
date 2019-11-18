import random
from contextlib import contextmanager
import sys, os

# =============================================================================
# State is stored as a string where index is at place shown in the board below
#
#  --------------------------------
# |  0  1  2 | 9  10 11 | 18 19 20 |
# |  3  4  5 | 12 13 14 | 21 22 23 |
# |  6  7  8 | 15 16 17 | 24 25 26 |
#  --------------------------------
# | 27 28 29 | 36 37 38 | 45 46 47 |
# | 30 31 32 | 39 40 41 | 48 49 50 |
# | 33 34 35 | 42 43 44 | 51 52 53 |
#  --------------------------------
# | 54 55 56 | 63 64 65 | 72 73 74 |
# | 57 58 59 | 66 67 68 | 75 76 77 |
# | 60 61 62 | 69 70 71 | 78 79 80 |
#  --------------------------------
#
# =============================================================================
from copy import deepcopy

from math import inf
from collections import Counter
from time import time

from heuristics import heuristics
from monte import MCTS
def index(x, y):
    """

    :param x: place in board
    :param y: place in board
    :return: the number on the board 0-80
    """
    x -= 1
    y -= 1
    return ((x // 3) * 27) + ((x % 3) * 3) + ((y // 3) * 9) + (y % 3)


def box(x, y):
    """

    :param x: place on board
    :param y: place on board
    :return: the box number of this position
    """
    return index(x, y) // 9


def next_box(i):
    """

    :param i: box number
    :return: next box
    """
    return i % 9





def print_board(state):
    """

    :param state: current state to print
    :return: nothing
    """
    for row in range(1, 10):
        row_str = ["|"]
        for col in range(1, 10):
            row_str += [state[index(row, col)]]
            if (col) % 3 == 0:
                row_str += ["|"]
        if (row - 1) % 3 == 0:
            print("-" * (len(row_str) * 2 - 1))
        print(" ".join(row_str))
    print("-" * (len(row_str) * 2 - 1))


class ultiTic:
    def __init__(self, first_eval, second_eval, init_state):
        """

        :param first_eval: evaluation function for X
        :param second_eval: evaluation function for O
        :param init_state: state to play from
        """
        self.possible_goals = [(0, 4, 8), (2, 4, 6)]
        self.possible_goals += [(i, i + 3, i + 6) for i in range(3)]
        self.possible_goals += [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(3)]
        self.first_eval = first_eval
        self.second_eval = second_eval

        self.state = init_state
        self.box_won = "." * 9
        self.state = "." * 81

    def add_piece(self, state, move, player):
        """

        :param state: current state
        :param move: move to be aded
        :param player: current player
        :return: new board after adding the piece
        """

        if not isinstance(move, int):
            move = index(move[0], move[1])
        if move < 0:
            return state
        return state[: move] + player + state[move + 1:]

    def indices_of_box(self,b):
        """

        :param b: box number
        :return: the box state
        """
        return list(range(b * 9, b * 9 + 9))
    def update_box_won(self, state):
        """

        :param state: current state
        :return: current game win/lose status
        """
        temp_box_win = ["."] * 9
        for b in range(9):
            idxs_box = self.indices_of_box(b)
            box_str = state[idxs_box[0]: idxs_box[-1] + 1]
            temp_box_win[b] = self.check_small_box(box_str)
        return temp_box_win

    def check_small_box(self, box_str):
        """

        :param box_str: small game box
        :return: the winner if there is one or D if draw or . if nothing yet
        """

        for idxs in self.possible_goals:
            (x, y, z) = idxs
            if (box_str[x] == box_str[y] == box_str[z]) and box_str[x] != "." and box_str[x] != "D":
                return box_str[x]
        if "." not in box_str:
            return "D"
        return "."

    def possible_moves(self, state, last_move):
        """

        :param state: current state
        :param last_move: last move was played by opponent
        :return: list of legal moves for current player
        """
        cur_state=["."]
        if (last_move != -1):
            cur_state = [state[i] for i in self.indices_of_box(last_move % 9)]
        if not isinstance(last_move, int):
            last_move = index(last_move[0], last_move[1])
        if (last_move == -1 or self.box_won[(last_move % 9)] != ".") or "." not in cur_state:
            return [i for i in range(81) if (state[i] == "." and self.box_won[(i // 9)] == ".")]
        return [i for i in self.indices_of_box(last_move % 9) if state[i] == "."]



    def opponent(self, p):
        """

        :param p: current player
        :return: the opponent of the player
        """
        return "O" if p == "X" else "X"

    def expectimax(self, state, last_move, player, depth, eval):
        """

        :param state: current state
        :param last_move: last move played
        :param player: cureent player
        :param depth: minimax depth
        :param eval: evaluation function
        :return: best move to be played by the player
        """
        succ = self.possible_moves(state, last_move)
        best_move = (-inf, None)
        for s in succ:
            new_state = self.add_piece(state, s, player)
            val = self.expecti_min_turn(new_state, s, self.opponent(player), depth - 1,
                                        -inf, inf, eval)
            if val > best_move[0]:
                best_move = (val, s)
        return best_move[1]

    def expecti_min_turn(self, state, last_move, player, depth, alpha, beta, eval):
        """

        :param state: current state
        :param last_move: last move played
        :param player: cureent player
        :param depth: minimax depth
        :param alpha: param for the algorithm
        :param beta: param for the algorithm
        :param eval: evaluation function
        :return: best move to be played by the player
        """

        if depth <= 0 or self.check_small_box(self.box_won) != ".":  # or time() - s_time >= 10:
            return eval(self,state, last_move, self.opponent(player))
        succ = self.possible_moves(state, last_move)
        expicti_val = 0
        for s in succ:
            new_state = self.add_piece(state, s, player)
            val = self.max_turn(new_state, s, self.opponent(player), depth - 1,
                                alpha, beta, eval)
            expicti_val += val / len(succ)
        return expicti_val
    def minimax(self, state, last_move, player, depth, eval):
        """

        :param state: current state
        :param last_move: last move played
        :param player: cureent player
        :param depth: minimax depth
        :param eval: evaluation function
        :return: best move to be played by the player
        """
        succ = self.possible_moves(state, last_move)
        best_move = (-inf, None)
        for s in succ:
            new_state = self.add_piece(state, s, player)
            val = self.min_turn(new_state, s, self.opponent(player), depth - 1,
                                -inf, inf, eval)
            if val > best_move[0]:
                best_move = (val, s)
        return best_move[1]

    def min_turn(self, state, last_move, player, depth, alpha, beta, eval):
        """

        :param state: current state
        :param last_move: last move played
        :param player: cureent player
        :param depth: minimax depth
        :param alpha: alpha param
        :param beta: beta param
        :param eval: evaluation function used to evaluate
        :return: score for the state
        """
        if depth <= 0 or self.check_small_box(self.box_won) != ".":  # or time() - s_time >= 10:
            return eval(self,state, last_move, self.opponent(player))
        succ = self.possible_moves(state, last_move)
        for s in succ:
            new_state = self.add_piece(state, s, player)
            val = self.max_turn(new_state, s, self.opponent(player), depth - 1,
                                alpha, beta, eval)
            if val < beta:
                beta = val
            if alpha >= beta:
                break
        return beta

    def max_turn(self, state, last_move, player, depth, alpha, beta, eval):
        """

        :param state: current state
        :param last_move: last move played
        :param player: cureent player
        :param depth: minimax depth
        :param alpha: alpha param
        :param beta: beta param
        :param eval: evaluation function used to evaluate
        :return: score for the state
        """

        if depth <= 0 or self.check_small_box(self.box_won) != ".":  # or time() - s_time >= 20:
            return eval(self,state, last_move, player)
        succ = self.possible_moves(state, last_move)
        for s in succ:
            new_state = self.add_piece(state, s, player)
            val = self.min_turn(new_state, s, self.opponent(player), depth - 1,
                                alpha, beta, eval)
            if alpha < val:
                alpha = val
            if alpha >= beta:
                break
        return alpha

    def valid_input(self, state, move):
        """

        :param state: current state
        :param move: current move
        :return: true if move is valid , false other wise
        """
        if not (0 < move[0] < 10 and 0 < move[1] < 10):
            return False
        if self.box_won[box(move[0], move[1])] != ".":
            return False
        if state[index(move[0], move[1])] != ".":
            return False
        return True

    def take_input(self, state, oppopent_move):
        """

        :param state: current state
        :param oppopent_move: last move played to determine place to play
        :return:
        """
        (x, y) = self.inputs(state, oppopent_move)
        while index(x, y) not in self.possible_moves(state, oppopent_move) or not self.valid_input(state, (x, y)):
            print("pls input correct number")
            (x, y) = self.inputs(state, oppopent_move)
        return index(x, y)

    def inputs(self, state, oppopent_move):
        """

        :param state: current state
        :param oppopent_move: last move played by opponent
        :return: legal move taken by user
        """
        if not isinstance(oppopent_move, int):
            oppopent_move = index(oppopent_move[0], oppopent_move[1])
        print("#" * 40)
        all_open_flag = False
        if oppopent_move == -1 or len(self.possible_moves(state, oppopent_move)) > 9:
            all_open_flag = True
        if all_open_flag:
            print("Play anywhere you want!")
        else:
            box_dict = {0: "Upper Left", 1: "Upper Center", 2: "Upper Right",
                        3: "Center Left", 4: "Center", 5: "Center Right",
                        6: "Bottom Left", 7: "Bottom Center", 8: "Bottom Right"}
            print("Where would you like to place 'X' in ~"
                  + box_dict[next_box(oppopent_move)] + "~ box?")
        try:
            x = int(input("Row = "))
            if x == -1:
                sys.exit(12)
            y = int(input("Col = "))
        except:
            return (1000,1000)
        print("")
        return (x, y)

    def game(self,pre_p1,pre_p2 ,simulate=False):
        """

        :param pre_p1: function for player 1 decision
        :param pre_p2: function for player 2 decision
        :param simulate: true if you running simulation ( test purpose) false if normal game
        :return: the winner if one exists
        """


        self.box_won = self.update_box_won(self.state)
        game_won = self.check_small_box(self.box_won)
        if game_won == "X":
            if not simulate:
                print("$$$$$ Congratulations p1 X WIN! $$$$$")
            return "X"
        elif game_won == "O":
            if not simulate:
                print("$$$$$ Congratulations p2 O WIN! $$$$$")
            return "O"
        elif game_won == ".":
            pass
        else:
            if not simulate:
                print("Its a draw :(")
        if not simulate:
            print_board(self.state)
        p2_move = -1

        while True:
            if (self.possible_moves(self.state, p2_move) == []):
                game_won = "Z"
                break
            if not simulate:
                print("Please wait, p1 is thinking...")



            p1_move = pre_p1(self.state, p2_move)


            self.state = self.add_piece(self.state, p1_move, "X")
            if not simulate:
                print("#" * 40)
                print("p1 placed X on", p1_move, "\n")
                print_board(self.state)
            self.box_won = self.update_box_won(self.state)

            game_won = self.check_small_box(self.box_won)
            if game_won != ".":
                self.state = self.state
                break
            if (self.possible_moves(self.state, p2_move) == []):
                game_won = "Z"
                break
            if not simulate:
                print("Please wait, p2 is thinking...")

            p2_move = pre_p2(self.state, p1_move)
            if not simulate:
                print("#" * 40)
                print("p2 placed O on", p2_move, "\n")

            self.state = self.add_piece(self.state, p2_move, "O")
            if not simulate:
                print_board(self.state)
            self.box_won = self.update_box_won(self.state)
            game_won = self.check_small_box(self.box_won)
            if game_won != ".":
                break
        print_board(self.state)
        if game_won == "X":
            if not simulate:
                print("$$$$$ Congratulations p1 X WIN! $$$$$")
            return "X"
        elif game_won == "O":
            if not simulate:
                print("$$$$$ Congratulations p2 O WIN! $$$$$")
            return "O"
        else:
            if not simulate:
                print("Its a draw :(")
            return "Z"



    def prepare_minimax(self, state, last_move):
        """

        :param state: current state
        :param last_move: last move played by opponent
        :return: best move to be played by minimax algorithm
        """


        if state[last_move] == "O" or last_move<0:
            eval_func = self.first_eval[0]
            depth=self.first_eval[1]
        else:
            eval_func = self.second_eval[0]
            depth = self.second_eval[1]
        return self.minimax(state,last_move, "X" if state[last_move] == "O" or last_move < 0 else "O", depth, eval_func)
    def prepare_expectimax(self, state, last_move):
        """

                :param state: current state
                :param last_move: last move played by opponent
                :return: best move to be played by expectimax algorithm
                """


        if state[last_move] == "O" or last_move<0:
            eval_func = self.first_eval[0]
            depth=self.first_eval[1]
        else:
            eval_func = self.second_eval[0]
            depth = self.second_eval[1]
        return self.expectimax(state,last_move, "X" if state[last_move] == "O" or last_move < 0 else "O", depth, eval_func)




    def random_move(self, state, last_move):
        """

        :param state: current state
        :param last_move: last move played by opponent
        :return: random legal move
        """
        return random.choice(self.possible_moves(state, last_move))

    def pre_monte(self, state, move):
        """

        :param state: current state
        :param move: last move played by opponent
        :return: best move according to monte carlo algorithm
        """
        if self.state[move] == "O" or move < 0:
            player = "X"
            iteration=self.first_eval[0]
            ew = self.first_eval[1]
        else:
            player = "O"
            iteration = self.second_eval[0]
            ew = self.second_eval[1]
        mont = MCTS(deepcopy(state), self, move, player,iteration,ew)
        score, to_play = mont.solve()
        return to_play


def user_choose(val,player):
    """

    :param val: value user choosed
    :param player: which player choosed what to play
    :return: the type of algo user chose
    """
    if val=="2" or val=="1":
        return None
    if val=="3":
        h=input("player "+player+" please choose your heuristic:\n1 = h1\n2 = h2\n3 = h3\nyour choice: ")
        depth=input("player "+player+" please choose your depth:")
        while not str.isdigit(h) or not str.isdigit(depth):
            print("one of the choices is not a number\n")
            h = input("player " + player + " please choose your heuristic:\n1 = h1\n2 = h2\n3 = h3\nyour choice: ")
            depth = input("player " + player + " please choose your depth:")
        heur=heuristics(int(depth))
        return (heur.get_heur(h),int(depth))
    if val=="4":
        h=input("player "+player+" please choose your heuristic:\n1 = h1\n2 = h2\n3 = h3\nyour choice: ")
        depth=input("player "+player+" please choose your depth:")
        while not str.isdigit(h) or not str.isdigit(depth):
            print("one of the choices is not a number\n")
            h = input("player " + player + " please choose your heuristic:\n1 = h1\n2 = h2\n3 = h3\nyour choice: ")
            depth = input("player " + player + " please choose your depth:")
        heur=heuristics(int(depth))
        return (heur.get_heur(h),int(depth))
    if val=="5":
        iterations=input("\nchoose the number of iterations for the monte carlo learning: ")
        ew=input("\nchoose your exploration weight for the score of the monte carlo: ")
        while not str.isdigit(iterations) or not isfloat(ew):
            print("one of the choices is not a number\n")
            iterations = input("\nchoose the number of iterations for the monte carlo learning: ")
            ew = input("\nchoose your exploration weight for the score of the monte carlo: ")
        return ((int)(iterations),(float)(ew))


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False
def choose_pre(val,game):
    """

    :param val: value of the algorithm the user want to play with
    :param game: game object
    :return: pre_function for the algorithm user chose
    """
    if val=="1":
        return game.take_input
    if val=="2":
        return game.random_move
    if val=="3":
        return game.prepare_minimax
    if val=="4":
        return game.prepare_expectimax
    if val=="5":
        return game.pre_monte


if __name__ == "__main__":
    """
    main function to play the game
    """
    val = input("Player 1 please choose \
    \n1 = User Input\n2 = Random Player\n3 = Minimax\n4 = Expectimax\n5 = Monte Carlo\nYour Choice:  ")
    p1=user_choose(val,"1")

    val2 = input("Player 2 please choose \
        \n1 = User Input\n2 = Random Player\n3 = Minimax\n4 = Expectimax\n5 = Monte Carlo\nYour Choice:  ")
    p2 = user_choose(val2, "2")
    ut = ultiTic(p1, p2, "." * 81)
    p1_pre = choose_pre(val, ut)
    p2_pre = choose_pre(val2, ut)


    ut.state="."*81
    final_state = ut.game(p1_pre,p2_pre,False)

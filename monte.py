from copy import deepcopy
import math


class MCTS:
    def __init__(self, board, game, last_move, player, iterations=250, exploration_weight=0.2, parent=None):
        """

        :param board: current game state
        :param game: UTTT object
        :param last_move: last move by the opponent
        :param player: current player
        :param parent: usually None
        :param iterations: number of iteration and nodes expanded
        :param exploration_weight: number used in calculating the node score
        """
        self.children = dict()  # children of each self.node
        self.node = Node(board, parent, last_move, game, exploration_weight)
        self.node.update_children()
        self.children[self.node] = self.node.get_children()
        self.exploration_weight = exploration_weight
        self.global_path = []
        self.board = board
        self.iterations = iterations
        self.player = player
        self.last_move = last_move
        self.game = game

    def solve(self):
        """
        this function connect everything it select then expand then simulate then back propagation and return best move
        :return: the best move to play
        """
        new_state = self.node
        if new_state.board=="."*81:
            return 1,40

        for i in range(self.iterations):
            succ = new_state
            # selection: select the best node
            while succ.children != []:
                succ.update_visits()
                succ = succ.get_succesor()
            succ.update_visits()
            # expansion : expand a new random move,state
            succ = self.expand_node(succ)

            # simulate a game: play a game to check the results
            score = self.simulate(succ)

            # backpropagation : update the nodes visits and wins to the root
            self.update_the_way(succ, score)

        succ = sorted(new_state.children, key=lambda c: c.wins / c.visists)
        return (succ[-1].score, succ[-1].move)

    def simulate(self, node):
        """
        simulate a full game with random moves
        :param node: current game state node
        :return: which player won
        """
        to_sim = deepcopy(node)
        box_won = to_sim.game.update_box_won(to_sim.board)
        game_won = to_sim.game.check_small_box(box_won)
        player = "X" if to_sim.board[to_sim.move] == "O" else "O"
        while game_won == ".":
            action = to_sim.game.random_move(to_sim.board, to_sim.move)
            to_sim.board = to_sim.game.add_piece(to_sim.board, action, player)
            player = to_sim.game.opponent(player)
            box_won = to_sim.game.update_box_won(to_sim.board)
            game_won = to_sim.game.check_small_box(box_won)
        return game_won

    def update_the_way(self, ran, score_to_update):
        """
        this function updates the win/loses of every node
        :param ran: leaf node
        :param score_to_update: parameter to determine how to update
        :return: nothing
        """
        if self.player == score_to_update:
            game_result = 1
        elif score_to_update == "D":
            game_result = 0
        else:
            game_result = -1
        while ran.get_parent() is not None:
            ran.update_wins(game_result)
            ran.update_visits()
            ran = ran.get_parent()

    def expand_node(self, succ):
        """

        :param succ: node to be expanded
        :return: and expanded node which is the next state of current state
        """
        player = "X" if succ.board[succ.move] == "O" else "O"
        if not succ.game.possible_moves(succ.board, succ.move):
            return succ
        else:
            move = succ.game.random_move(succ.board, succ.move)
            new_node = succ.game.add_piece(succ.board, move, player)
            node = Node(new_node, succ, move, succ.game, self.exploration_weight)
            node.update_visits()
            return node


class Node:
    def __init__(self, board, parent, move, game, exploration_weight=0.2):
        """

        :param board: current state of the game
        :param parent: the parent of the node
        :param move: the move used to get to this state
        :param game: game object
        :param exploration_weight: param for calculating the score
        """
        self.board = board
        self.parent = parent
        self.move = move
        self.wins = 0
        self.visists = 1
        self.game = game
        self.children = []
        self.score = 0
        self.exploration_weight = exploration_weight

    def update_visits(self, vists=1):
        """

        :param vists: update how many times this nodes was visited
        :return: nothing
        """

        self.visists += vists

    def update_wins(self, wins):
        """

        :param wins: wins score
        :return: nothing
        """
        self.wins += wins

    def get_parent(self):
        """

        :return: parent of this node
        """
        return self.parent

    def update_children(self):
        """

        :return: generate all the children of the current state
        """

        for child in self.game.possible_moves(self.board, self.move):
            node = Node(self.game.add_piece(deepcopy(self.board), child, self.game.opponent(self.board[self.move])),
                        self, child, self.game, self.exploration_weight)
            self.update_child(node)

    def get_children(self):
        """

        :return: return all the expanded children
        """
        return self.children

    def update_child(self, node):
        """

        :param node: child to update
        :return: True if child was aded None if its already a child
        """
        for i in self.children:
            if node.board == i.board:
                return None
        self.children.append(node)
        return True

    def get_randon_child(self):
        """

        :return: unexpanded random child of the current state
        """
        move = self.game.random_move(self.board, self.move)
        node = Node(self.game.add_piece(deepcopy(self.board), move, self.game.opponent(self.board[self.move]))
                    , self, move, self.game, self.exploration_weight)
        while True:
            if self.update_child(node) == True:
                break
            move = self.game.random_move(self.board, self.move)
            node = Node(self.game.add_piece(deepcopy(self.board), move, self.game.opponent(self.board[self.move]))
                        , self, move, self.game, self.exploration_weight)

        return node
    def get_succesor(self):
        """

        :return: score of the node for next select
        """
        s = sorted(self.children, key=lambda c: c.wins / c.visists +self.exploration_weight*
                                                 math.sqrt(2*math.log(self.visists) / c.visists))
        return s[-1]

# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood().asList()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"

        # it appears that the weakly types thingy of python comes in handy here
        if successorGameState.isLose():
            return float ('-inf')
        
        if successorGameState.isWin():
            return float ('+inf')
        
        score = successorGameState.getScore()

        closestGhostDistance = manhattanDistance(newPos, newGhostStates[0].getPosition())
        for ghostState in newGhostStates:
            closestGhostDistance = min(closestGhostDistance, manhattanDistance(newPos, ghostState.getPosition())) / (1 + ghostState.scaredTimer * 0.1)

        closestFoodDistance = 0
        if len(newFood) > 0:
            closestFoodDistance = manhattanDistance(newPos, newFood[0])
        for food in newFood:
            closestFoodDistance = min (closestFoodDistance, manhattanDistance(newPos, food))

        fear    = 1
        desire  = 20

        score -= 10 / max (1, closestGhostDistance * desire)

        score += 10 / max (1, closestFoodDistance  * fear)

        score += (len(currentGameState.getFood().asList()) - len(newFood)) * 20
        
        if action == 'Stop': score -= 50

        return score

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """
    

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"

        def maximum(gs : GameState, depth : int) -> float:
            # Pacman's turn, single generation of successor

            # evaluate if win, loss or depth reached
            if gs.isWin() or gs.isLose() or depth == self.depth: 
                return self.evaluationFunction(gs)
            
            # find the best move using minimax on all possible actions
            highestFound = float('-inf')

            actions = gs.getLegalActions()
            if 'Stop' in actions: actions.remove('Stop')

            for action in actions:
                highestFound = max(highestFound, minimum(1, gs.generateSuccessor(0, action), depth))

            return highestFound



        def minimum(id : int, gs : GameState, depth : int) -> float:
            # Ghost's turn, multiple successor generations / runs of minimum

            # evaluate if win or lose
            if gs.isWin() or gs.isLose(): 
                return self.evaluationFunction(gs)
            
            # find the best move for the ghost
            lowestFound = float('+inf')

            actions = gs.getLegalActions(id)
            if 'Stop' in actions: actions.remove('Stop')

            # if the next turn is Pacman's, use the maximum
            if id + 1 == gs.getNumAgents():
                for action in actions:
                    lowestFound = min(lowestFound, maximum(gs.generateSuccessor(id, action), depth + 1))
            # else, continue with the next ghost's move
            else:    
                for action in actions:
                    lowestFound = min(lowestFound, minimum(id + 1, gs.generateSuccessor(id, action), depth))

            return lowestFound

    
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [minimum(1, gameState.generateSuccessor(0, action), 0) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)

        return legalMoves[chosenIndex]



class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """
    
    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
            
        def maximum(gs : GameState, depth : int, a, b) -> float:
            # Pacman's turn, single generation of successor

            # evaluate if win, loss or depth reached
            if gs.isWin() or gs.isLose() or depth == self.depth: 
                return self.evaluationFunction(gs)
            
            # find the best move using minimax on all possible actions
            v = float('-inf')

            actions = gs.getLegalActions()
            if 'Stop' in actions: actions.remove('Stop')

            for action in actions:
                v = max(v, minimum(1, gs.generateSuccessor(0, action), depth, a, b))
                a = max(a, v)
                if v > b: return v
            return v



        def minimum(id : int, gs : GameState, depth : int, a, b) -> float:
            # Ghost's turn, multiple successor generations / runs of minimum

            # evaluate if win or lose
            if gs.isWin() or gs.isLose(): 
                return self.evaluationFunction(gs)
            
            # find the best move for the ghost
            v = float('+inf')

            actions = gs.getLegalActions(id)
            if 'Stop' in actions: actions.remove('Stop')

            # if the next turn is Pacman's, use the maximum
            if id + 1 == gs.getNumAgents():
                for action in actions:
                    v = min(v, maximum(gs.generateSuccessor(id, action), depth + 1, a, b))
                    b = min (b, v)
                    if v < a: return v
            # else, continue with the next ghost's move
            else:    
                for action in actions:
                    v = min(v, minimum(id + 1, gs.generateSuccessor(id, action), depth, a, b))
                    b = min (b, v)
                    if v < a: return v
            return v

        
        v = float('-inf')
        alpha = float('-inf')

        actions = gameState.getLegalActions()
        if 'Stop' in actions: actions.remove('Stop')

        # the first moves must also update the alpha and beta values
        for action in actions:
            sucv = minimum(1, gameState.generateSuccessor(0, action), 0, alpha, float('+inf'))
            if sucv > v:
                v = sucv
                ba = action
            alpha = max(alpha, v)

        return ba
    
class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

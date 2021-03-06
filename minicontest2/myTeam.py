# myTeam.py
# ---------
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'AvocadoAgent', second = 'AvocadoAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.start = gameState.getAgentPosition(self.index)

    
    ####################################################
    #  adapted from baselineTeam.py ReflexCaptureAgent #
    ####################################################
  def chooseAction(self, gameState):

    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    print ('eval time for agent %d: %.4f' % (self.index, time.time() - start))

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}

  def getNearGhost(self, gameState):
    myPos = gameState.getAgentState(self.index).getPosition()
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    ghosts = [a for a in enemies if (a.isPacman == False) and a.getPosition() != None]
    if len(ghosts) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
      return min(dists)
    else:
      return None

       ####################
       # FROM baseline.py #
       ####################
     

class OffensiveCleverAgent(DummyAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)   # self.getScore(successor)

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance 

    # Compute the distance to the nearest ghost enemy

    if len(foodList) > 0: 
      minDistGhost = self.getNearGhost(successor)
      if minDistGhost != None:
        features['nearestGhostCost'] = 1/(minDistGhost+0.5)
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1,'nearestGhostCost': -60}

class DefensiveReflexAgent(DummyAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}

########################################################## 分割线 ##########################################################
########################################################## 分割线 ##########################################################
########################################################## 分割线 ##########################################################
########################################################## 分割线 ##########################################################
########################################################## 分割线 ##########################################################
########################################################## 分割线 ##########################################################


class AvocadoAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)

    self.agentState = 0
    self.start = gameState.getAgentPosition(self.index)

    self.initialFood = len(self.getFood(gameState).asList())

    self.corner = {}

    


  def chooseAction(self, gameState):

    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    print ('eval time for agent %d: %.4f' % (self.index, time.time() - start))

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start,pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights


  def getNearGhost(self, gameState):
    myPos = gameState.getAgentState(self.index).getPosition()
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    ghosts = [a for a in enemies if (a.isPacman == False) and a.getPosition() != None]
    if len(ghosts) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in ghosts]
      return min(dists)
    else:
      return None

       ####################
       # FROM baseline.py #
       ####################


  # Features: 'successsorScore' 'distanceToFood' 'nearestGhostCost'
  #           'numInvaders' 'onDefense' 'invaderDistance' 'stop' 'reverse'
  # Weight for Offensive Agent: 'successorScore': 100, 'distanceToFood': -1,'nearestGhostCost': -60
  # Weight for Defensive Agent: 'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2


  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()    
    features['successorScore'] = -len(foodList)   # self.getScore(successor)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)

    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Compute distance to the nearest food

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance


    # Compute the distance to the nearest ghost enemy

    if len(foodList) > 0: 
      minDistGhost = self.getNearGhost(successor)
      if minDistGhost != None:
        features['nearestGhostCost'] = 1/(minDistGhost+0.5)

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1


    # Compute risk, let the agent return when get enough food.
    if not myState.isPacman:
      self.initialFood = len(foodList)
    eatenFood = self.initialFood - len(foodList)
    if self.red:
      mid = gameState.data.layout.width/2
    else:
      mid = gameState.data.layout.width/2 + 1
    midLine = [(mid, y) for y in range(gameState.data.layout.height)]
    diss = []
    for p in midLine:
      if not gameState.hasWall(int(p[0]), int(p[1])):
        diss.append(self.getMazeDistance(myPos, p))
    if len(diss) != 0:
      #if eatenFood > 0 and min(diss) == 2:
      #  print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
      #  features['risk'] = -eatenFood
      #else:
      features['risk'] = eatenFood*min(diss)
     


    # Compute distance to Capsules
    Capsules = self.getCapsules(gameState)
    if len(Capsules) > 0:
      features['distanceToCapsules'] = min([self.getMazeDistance(myPos, capsule) for capsule in Capsules])
    else:
      features['distanceToCapsules'] = 0

    # Store last 2 positions:
    #if myPos in self.last2Position:
    #  features['wonder'] = 1
    #else:
    #  features['wonder'] = 0

    # Do not go into walls !!!
    if minDistGhost < 3:
      nextPoints = [(myPos[0], myPos[1]-1), (myPos[0], myPos[1]+1), (myPos[0]-1, myPos[1]), (myPos[0]+1, myPos[1])]
      if p not in self.corner:
        count = 0
        for p in nextPoints:
          if gameState.hasWall(int(p[0]), int(p[1])):
            count += 1
        self.corner[myPos] = count
      if self.corner[myPos] == 3:
        features['wall'] = -1000
      else:
        features['wall'] = 0
    else:
      features['wall'] = 0

    return features



  def getWeights(self, gameState, action):
    successor = self.getSuccessor(gameState, action)
    myState = successor.getAgentState(self.index)
    if myState.isPacman:
      return {'successorScore': 100, 'distanceToFood': -1, 'distanceToCapsules': -3, 'nearestGhostCost': -30, 'numInvaders': 0, 'onDefense': 0, 'invaderDistance': 0, 'stop': -10, 'reverse': 0, 'risk': -5, 'wall': 1}
    else:
      team = self.getTeam(gameState)
      for partnerIndex in team:
        if partnerIndex != self.index:
          partnerState = gameState.getAgentState(partnerIndex)
          break
      if partnerState.isPacman:
        return {'successorScore': 0, 'distanceToFood': 0, 'distanceToCapsules': 0 ,'nearestGhostCost': 0, 'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -20, 'risk': 0, 'wall': 0}
      else:
        return {'successorScore': 100, 'distanceToFood': -1, 'distanceToCapsules': -3, 'nearestGhostCost': -30, 'numInvaders': -500, 'onDefense': 0, 'invaderDistance': -10, 'stop': 0, 'reverse': 0, 'risk': 0, 'wall': 0}
        
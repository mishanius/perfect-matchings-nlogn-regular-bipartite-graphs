import random
import numpy as np

class RealGraph:

	def __init__(self, n, d):
		if n == 0 or d == 0:
			raise Exception("Graph with 0 vertices or 0 neighbors isn't supported")
		if d > n-1:
			raise Exception("d's value cannot be bigger than n-1")
		self.groupP, self.groupQ, self.loop = self.createGraph(n, d)

	#groupFlag=1 represents group Q, groupFlag=0 represents group P
	def generateGroup(self, n, groupFlag):
		if groupFlag:
			return {str(k)+"Q":[] for k in range(0,n)}
		else:
			return {str(k)+"P":[] for k in range(0, n)}

	def generateCountedGroup(self, n, d):
		return {str(k)+"Q":d for k in range(0,n)}

	def generateNeighbores(self, n, d, loopCounter):
		if loopCounter>900:
			raise Exception("Almost reaching the max depth of recursion")
		firstGroup = self.generateGroup(n, 0)
		secondGroup = self.generateGroup(n, 1)
		optionalNeighbores = self.generateCountedGroup(n,d)
		for x in firstGroup.keys():
			uniteratedOptionalNeighbors = list(optionalNeighbores.keys())
			while(1):
				if len(firstGroup[x]) == d:             #vertex x has d neighbors, we can move to next vertex
					if x[:len(x)-1] == str(n-1):               #if its the last vertex, we're done with the procedure
						#print("Looped: ", loopCounter)
						return firstGroup, secondGroup, loopCounter
					break                               #vertex x has d neighbors, we can move to next vertex
				a = uniteratedOptionalNeighbors.pop(random.randrange(len(uniteratedOptionalNeighbors))) #pick random ind that wasnt picked before for this vertex
				if len(firstGroup[str(n-1)+"P"]) < d-1 and len(uniteratedOptionalNeighbors) == 0:
					return self.generateNeighbores(n, d, loopCounter+1)
				if not(a in firstGroup[x]):           #check that choosen vertex isnt already a neighbor
					firstGroup[x].append(a)             #if isnt, add to x's neighbor list
					secondGroup[a].append(x)
					optionalNeighbores[a] = optionalNeighbores[a]-1 #mark that choosen vertex a has room for 1 less neighbor
					if optionalNeighbores[a] == 0:
						del optionalNeighbores[a]

	def getGroupP(self):
		return list(self.groupP.keys())

	def getGroupQ(self):
		return list(self.groupQ.keys())

	def getNeighborsOfP(self):
		return list(map(self.groupP.get, self.groupP.keys()))

	def getNeighborsOfQ(self):
		return list(map(self.groupQ.get, self.groupQ.keys()))

	#this func is made to monitor amount of loops needed
	def getLoop(self):
		return self.loop

	def setLoop(self, counter):
		self.loop = counter

	#returns a specific's vertex' neighbores list
	#groupFlag=1 represents group Q, groupFlag=0 represents group P
	def getNeighbors(self, key, groupFlag):
		if groupFlag:
			return self.groupQ[key]
		else:
			return self.groupP[key]

	def createGraph(self, n, d):
		counter=0
		while(1):
			counter+=1
			try:
				firstGroup, secondGroup, loopCounter =  self.generateNeighbores(n, d, 0)
				#print("counter before multiplying with loops is : ",counter)
				return firstGroup, secondGroup, loopCounter*counter
			except:
				continue	#catch the exception, and keep trying .

	def find_match(self):
		matches=set()
		superNodes={}
		j=0
		pVertices = self.getGroupP()
		unmatchedPVertices=pVertices.copy()  #Deep copies, so we can remove from this variable
		n=len(pVertices)
		while len(matches)<n:
			b=2*(2+n/(n-j))
			path={}
			chosen=unmatchedPVertices.pop(random.randrange(len(unmatchedPVertices)))
			fail_count=0
			while not self.truncated_walk(chosen, b-1, path, superNodes):
				path={}
				fail_count+=1
				if (fail_count>1000):
					print("failed retry b:{0} superNodes:{1}".format(b,superNodes))
			if fail_count>2:
				print("fail count:{0}".format(fail_count))
			x=len(matches)
			matches=matches.symmetric_difference(self.path_to_matching(path))
			y=len(matches)
			if x+1<y:
				print("not a match!!!!!!")
				exit()
			superNodes=self.superize(matches)
			j=j+1
			if j==n and len(matches)<n:
				raise Exception("J REACHED ITS LIMIT")
		return self.matchesToSortedPairs(matches)

	def matchesToSortedPairs(self, matches):
		matcheslist=[]
		fixedmatcheslist=[]
		for x in matches:
			matcheslist.append(list(x))
		for y in matcheslist:
			if 'P' in y[0]:
				y=[y[1],y[0]]
			fixedmatcheslist.append(y)
		fixedmatcheslist.sort(key=self.get_label)
		# ----- THE FOLLOWING 3 LINES ARE TO FIX SORTING BY P! ALSO, CHANGE *if 'p' in y[0]* TO 'Q'
		#temp = fixedmatcheslist[0]
		#fixedmatcheslist.remove(temp)
		#fixedmatcheslist.append(temp)
		return fixedmatcheslist

	def get_label(self, list):
		return list[0]

	def superize(self, matchings):
		supers={}
		for (x,y) in matchings:
			z=x.__str__()
			w=y.__str__()
			supers[z]=w
			supers[w]=z
		return supers

	def path_to_matching(self, path):
		moves=set()
		for k in path:
			moves.add(frozenset({k,path[k]}))
		return moves

	def truncated_walk(self, choosenVertic, b, path, superNodes):
		if b<1:
			return False
		if choosenVertic in self.getGroupP():  #checks if the vertice is from group P
			randomFromQ=np.random.choice(self.getNeighbors(choosenVertic, 0))  #generates a neighbore of choosenVertic, choosenVertice belongs to P.
			path[choosenVertic]=randomFromQ #attach the pair (choosenVertice,next)
			return self.truncated_walk(randomFromQ, b-1, path, superNodes)
		else:  #this scenerio stands for when choosenVertic is actually from Q
			superNodesKeys=superNodes.keys()
			if not choosenVertic in superNodesKeys:  #and this verifies this ver doesnt participate yet in the matching
				return True
			else:									#choosenVertic is already in the match, so we want to update
				other = superNodes[choosenVertic]  #the value, which is a P vertex
				del superNodes[choosenVertic]
				del superNodes[other]
				path[choosenVertic] = other
				neighbors = graph.getNeighbors(other, 0)
				listedSuperNodesKeys = list(superNodesKeys)
				listedSuperNodesKeys.append(choosenVertic)
				neighbors = [x for x in neighbors if x not in listedSuperNodesKeys]
				next = np.random.choice(neighbors)  #choose a new vertex from Q so we can continue the procedure
				path[other]=next
				return self.truncated_walk(next, b-1, path, superNodes)


print("-------Testing with n=?, d=?")
#graph = RealGraph(10, 2)
#print("after multiplying : ",graph.getLoop())
#print(graph.getGroupP())
#print(graph.getNeighborsOfP())
counter=0
for i in range(0,10):
	n=10
	graph=RealGraph(10000,5)
	try:
		res = graph.find_match()
		counter+=1
		print("result is: ",res)
	except Exception as msg:
		print(msg)
		continue



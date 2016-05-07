import sys
class Game:
	def __init__(self,inputFile):
		with open(inputFile) as f:
			self.initGame(f)
		if self.task!=4:
			self.nextState(self.firstPlayer,self.task,self.cutOff)
			self.printState(self.nextStateOuput)
			self.nextStateOuput.truncate(self.nextStateOuput.tell()-1)
		else:
			self.play()
			self.traceOuput.truncate(self.traceOuput.tell()-1)
	def initGame(self,file):
		self.gameEnd=False
		self.task=int(file.readline())
		self.firstPlayerValue,self.secondPlayerValue=0,0
		if self.task!=4:
			self.firstPlayer=file.readline().strip()
			self.secondPlayer="X" if self.firstPlayer=="O" else "O"
			self.cutOff=int(file.readline().strip())
			self.nextStateOuput=open("next_state.txt","w")
			if self.task!=1:
				self.traverseOut=open("traverse_log.txt","w")
				self.traverseOut.write("Node,Depth,Value")
				if self.task==3: self.traverseOut.write(",Alpha,Beta")
		else:
			self.firstPlayer=file.readline().strip()
			self.firstAlg=int(file.readline().strip())
			self.firstCutOff=int(file.readline().strip())
			self.secondPlayer=file.readline().strip()
			self.secondAlg=int(file.readline().strip())
			self.secondCutOff=int(file.readline().strip())
			self.traceOuput=open("trace_state.txt","w")
		self.boardValue=[] ##int
		for line in range(5):
			self.boardValue.append([])
			for v in file.readline().split():
				self.boardValue[line].append(int(v))
		self.boardState=[] ##char
		for index,line in enumerate(file.readlines()):
			self.boardState.append(list(line.strip()))
			for i,v in enumerate(line.strip()):
				if v==self.firstPlayer:
					self.firstPlayerValue+=self.boardValue[index][i]
				elif v==self.secondPlayer:
					self.secondPlayerValue+=self.boardValue[index][i]
	def play(self):
		##bug if end between tw0 lines  and no exit check algorithm alpha and minmax
		while self.gameEnd==False:
			self.nextState(self.firstPlayer,self.firstAlg,self.firstCutOff)
			if self.gameEnd==True: return 
			self.printState(self.traceOuput)
			self.nextState(self.secondPlayer,self.secondAlg,self.secondCutOff)
			if self.gameEnd==True: return 
			self.printState(self.traceOuput)
	def  nextState(self,player,task,cutoff):
		methodDict={1:self.greedyBFS,2:self.minMax,3:self.alphaPruning}
		methodDict[task](player,cutoff)
	def move(self,player,i,j,res):
		if player==self.firstPlayer:
			self.firstPlayerValue=res[1]
			self.secondPlayerValue=res[2]
		else:
			self.secondPlayerValue=res[1]
			self.firstPlayerValue=res[2]
		self.boardState[i][j]=player
		direction=[(0,1),(1,0),(-1,0),(0,-1)]

		for d in res[3]:
			self.boardState[i+direction[d][0]][j+direction[d][1]]=player

	def evaluation(self,player,pos_i,pos_j):
		myplayer=0;opplayer=0
		if player==self.firstPlayer:
			myplayer=self.firstPlayerValue
			opplayer=self.secondPlayerValue
		else:
			myplayer=self.secondPlayerValue
			opplayer=self.firstPlayerValue
		myplayer+=self.boardValue[pos_i][pos_j]
		direction=[(0,1),(1,0),(-1,0),(0,-1)]
		raid=[]
		if self.canraid(player,pos_i,pos_j):
			for i in range(4):
				print i
				if self.opponent(player,pos_i+direction[i][0],pos_j+direction[i][1]):
					myplayer+=self.boardValue[pos_i+direction[i][0]][pos_j+direction[i][1]]
					opplayer-=self.boardValue[pos_i+direction[i][0]][pos_j+direction[i][1]]
					raid.append(i)
		eva=myplayer-opplayer
		print raid,eva,pos_i,pos_j
		return (eva,myplayer,opplayer,raid)

	def canraid(self,player,i,j):
		if i-1>=0 and self.boardState[i-1][j]==player: return True
		if i+1<5 and self.boardState[i+1][j]==player: return True
		if j-1>=0 and self.boardState[i][j-1]==player: return True
		if j+1<5 and self.boardState[i][j+1]==player: return True
		return False

	def opponent(self,player,i,j):
		if i>=0 and i<5 and j>=0 and j<5 and self.boardState[i][j]!="*" and self.boardState[i][j]!=player:
			return True
		return False

	def greedyBFS(self,player,cutoff):
		maxEva=float('-inf')
		i=-1;j=-1;
		result=()
		evaResult=()
		for row in range(5):
			for col in range(5):
				
				if self.boardState[row][col]=='*':
					evaResult= self.evaluation(player,row,col)
					if evaResult[0]>maxEva:
						maxEva=evaResult[0];i=row;j=col;result=evaResult;
		print evaResult
		if i==-1 and j==-1:
			self.gameEnd=True
		else:
			self.move(player,i,j,result)

	def minMax(self,player,cutoff):
		result=self.max_value(player,cutoff,0,'root',False,float('-inf'),float('inf'))
		if result[1]==-1 and result[2]==-1:
			self.gameEnd=True
		else: self.move(player,result[1],result[2],self.evaluation(player,result[1],result[2]))

	def max_value(self,player,cutoff,depth,curpos,prune,a,b):
		if depth==cutoff: 
			return self.max_helper(player,cutoff,depth,curpos,prune,a,b)
		i,j,v=-1,-1,float('-inf')
		for row in range(5):
			for col in range(5):
				 if self.boardState[row][col]=='*':
					temp_state=[r[:] for r in self.boardState]
					temp_first,temp_second=self.firstPlayerValue,self.secondPlayerValue
					self.printTraverse(curpos,depth,v,a,b)
					self.move(player,row,col,self.evaluation(player,row,col))
					cur=self.min_value(self.opponent_player(player),cutoff,depth+1,self.pos(row,col),prune,a,b)
					if cur[0]>v:
						v=cur[0];i=row;j=col; 
					self.boardState,self.firstPlayerValue,self.secondPlayerValue=temp_state,temp_first,temp_second
					if prune: 
						if v>=b:
							self.printTraverse(curpos,depth,v,a,b)
							return (v,i,j)
						a=max(a,v)
		if i==-1 and j==-1: return self.max_helper(player,cutoff,depth,curpos,prune,a,b)
		self.printTraverse(curpos,depth,v,a,b)
		return (v,i,j)
	def max_helper(self,player,cutoff,depth,curpos,prune,a,b):
		if player==self.firstPlayer:
			self.printTraverse(curpos,depth,self.firstPlayerValue-self.secondPlayerValue,a,b)
			return (self.firstPlayerValue-self.secondPlayerValue,-1,-1)
		else:
			self.printTraverse(curpos,depth,-self.firstPlayerValue+self.secondPlayerValue,a,b)
			return (self.secondPlayerValue-self.firstPlayerValue,-1,-1)
	def min_value(self,player,cutoff,depth,curpos,prune,a,b):
		if depth==cutoff:
			return self.min_helper(player,cutoff,depth,curpos,prune,a,b)
		v=float('inf')
		i,j=-1,-1
		for row in range(5):
			for col in range(5):
				 if self.boardState[row][col]=='*':
					temp_state=[r[:] for r in self.boardState]
					temp_first=self.firstPlayerValue
					temp_second=self.secondPlayerValue
					self.printTraverse(curpos,depth,v,a,b)
					self.move(player,row,col,self.evaluation(player,row,col))
					cur=self.max_value(self.opponent_player(player),cutoff,depth+1,self.pos(row,col),prune,a,b)
					if cur[0]<v:
						v=cur[0];i=row;j=col;
					self.boardState,self.firstPlayerValue,self.secondPlayerValue=temp_state,temp_first,temp_second
					if prune: 
						if v<=a :
							self.printTraverse(curpos,depth,v,a,b)
							return (v,i,j)
						b=min(b,v)
		if i==-1 and j==-1: return self.min_helper(player,cutoff,depth,curpos,prune,a,b)
		self.printTraverse(curpos,depth,v,a,b)
		return (v,i,j)

	def min_helper(self,player,cutoff,depth,curpos,prune,a,b):
			if player==self.secondPlayer:
				self.printTraverse(curpos,depth,self.firstPlayerValue-self.secondPlayerValue,a,b)	
				return (self.firstPlayerValue-self.secondPlayerValue,-1,-1)
			else:
				self.printTraverse(curpos,depth,-self.firstPlayerValue+self.secondPlayerValue,a,b)
				return (self.secondPlayerValue-self.firstPlayerValue,-1,-1)		
	def opponent_player(self,player):
		if player==self.firstPlayer: return self.secondPlayer
		else: return self.firstPlayer    
	def alphaPruning(self,player,cutoff):
		result=self.max_value(player,cutoff,0,'root',True,float('-inf'),float('inf'))
		if result[1]==-1 and result[2]==-1:
			self.gameEnd=True
		else: self.move(player,result[1],result[2],self.evaluation(player,result[1],result[2]))
	def printState(self,output):
		output.write( "\n".join(["".join(line) for line in self.boardState]))
		output.write("\n")
	def pos(self,i,j):
		return chr(ord('A')+j)+str(i+1)
	def printTraverse(self,curpos,depth,v,a,b):
		def printInf(s):
			if 	s=="inf" :return "Infinity"
			elif s=="-inf":return "-Infinity"
			return s
		if self.task in [2,3]:
			self.traverseOut.write("\n"+str(curpos)+","+str(depth)+","+printInf(str(v)))
		if self.task==3: self.traverseOut.write(","+printInf(str(a))+","+printInf(str(b)))
if __name__=='__main__':
	if len(sys.argv)!=3 or sys.argv[1]!="-i":
		print "input formate error"
		sys.exit()
	game=Game(sys.argv[2])
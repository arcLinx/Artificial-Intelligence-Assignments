import sys
import copy
class Fol:
	def __init__(self,inputFile):
		# init knowledge baes and query
		with open(inputFile) as f:
			self.initKb(f)
		# query and infer uding backforward-chaining alg
		self.var=0
		self.usedVar=set()

		with open("output.txt","w") as self.output:
			self.ask(self.kb,self.query)

	def initKb(self,file):
		self.kb=[] 
		self.query=self.generate_query(file.readline().strip())
		kb_num=int(file.readline().strip())
		for i in range(kb_num):
			self.kb.append(self.generate_clause(file.readline().strip()))
	
	def generate_query(self, query):
		querys=[]
		for q in query.split(" && "):
			querys.append(self.generate_predicate(q))
		return querys
	def generate_clause(self,clause):
		
		# implication   term1 && term2 && term3 =>term1(lhs => rhs) term(args(list), ops(str))
		kbEntry={"lhs":[],'rhs':{}}
		index=clause.find(" => ")
		if not index==-1:
			for term in clause[:index].split(" && "):
				kbEntry["lhs"].append(self.generate_predicate(term))
			index+=3;

		index+=1 # make it  point to start of rhs
		kbEntry["rhs"]=self.generate_predicate(clause[index:])
		return kbEntry
	def generate_predicate(self,term):
		predicate={}
		predicate["ops"]=term[:term.find("(")]
		predicate["args"]=term[term.find("(")+1:-1].split(", ")
		return predicate
	
	def ask(self,kb,query):
		if not len(query)==0:
			try:
				self.fol_bc_or(kb,query[0],{}).next()
				self.ask(kb,query[1:])
			except Exception:
				self.output.write("False")
		else: self.output.write("True")		
	def fol_bc_or(self,kb,goal,theta):
		self.output.write("Ask: "+self.myprint(goal,theta)+"\n")
		self.usedVar.update(goal["args"])
		find=False
		truenum=0
		for (lhs,rhs) in self.fetch_rules_for_goals(kb,goal):
			
			(lhs,rhs)= self.standardize_variables((lhs,rhs)) ##can not change value here
			u=self.unify(goal,rhs,copy.deepcopy(theta))
			if u : 
				truenum+=1
				if truenum>1:self.output.write("Ask: "+self.myprint(goal,theta)+"\n")
			for x in self.fol_bc_and(kb,lhs,u):
				self.output.write("True: "+self.myprint(self.subst(x,goal),theta)+"\n")
				find=True
				yield x
		# # handle negation operator
		# if find==False and goal["ops"][0]=='~': #questions here ask Ta!!!
		# 	for x in self.fol_bc_or(kb,self.negate(goal),theta,level):
		# 		print "False",self.myprint(self.subst(x,goal),theta)
		# 		return 
			
		# 	print "True",self.myprint(goal,theta)
		# 	yield theta

		if find==False: self.output.write("False: "+self.myprint(goal,theta)+"\n")	
	
	def standardize_variables(self,t):		
		lhs,rhs=t
		change={}
		tempvar=set()
		
		temp=[rhs]+lhs
		for x in temp:
			for i in range(len(x["args"])):
				if x["args"][i] in self.usedVar and x["args"][i][0].islower():
					if x["args"][i] not in change: change[x["args"][i]]=self.nextVar()
					x["args"][i] =change[x["args"][i]]
				else :tempvar.add(x["args"][i])


		# for i in range(len(rhs["args"])):
		# 	if rhs["args"][i] in self.usedVar and rhs["args"][i][0].islower() :
		# 		if rhs["args"][i] not in change : change[rhs["args"][i]]=self.nextVar()
		# 		rhs["args"][i]=change[rhs["args"][i]]
		# 	else: tempvar.add(rhs["args"][i] )

		# for x in lhs:
		# 	for i in range(len(x["args"])):
		# 		if x["args"][i]  in change:
		# 			x["args"][i]=change[x["args"][i]]
		# 		elif x["args"][i] not in tempvar and x["args"][i] in self.usedVar and x["args"][i][0].islower():
		# 			change[x["args"][i]]=self.nextVar()
		# 			x["args"][i]=change[x["args"][i]]
				
		self.usedVar.update(tempvar)
		return(lhs,rhs) 
	def nextVar(self):
		self.var+=1
		self.usedVar.add("x"+str(self.var))
		return "x"+str(self.var)			
	def fol_bc_and(self,kb,goal,theta):
	 	if theta==None: return 
	 	elif len(goal)==0: yield theta
	 	else: 
	 		first,rest=goal[0],goal[1:]
	 		for  x in self.fol_bc_or(kb,self.subst(theta,first),copy.deepcopy(theta)):
	 			for y in self.fol_bc_and(kb,copy.deepcopy(rest),copy.deepcopy(x)):	
	 				yield y

	def subst(self,theta,first):
		first=copy.deepcopy(first)
		for f in first:
			for i in range(len(first["args"])):
				while first["args"][i] in theta:
					first["args"][i]=theta[first["args"][i]]
		return first 
	def fetch_rules_for_goals(self,kb,goal):
		a=[ (copy.deepcopy(k["lhs"]),copy.deepcopy(k["rhs"])) for k in kb if k["rhs"]["ops"]==goal["ops"] ]
		return a
	def unify(self,x,y,theta): # theta is dictionary key is variable,value is constant to substiteu
		if theta is None : return None ## None means failure
		elif x==y: return theta
		elif type(x) is str and x[0].islower() : return self.unify_var(x,y,theta)
		elif type(y) is str and y[0].islower():  return self.unify_var(y,x,theta)
		elif type(x) is dict and type(y) is dict: return self.unify(x["args"],y["args"],self.unify(x["ops"],y["ops"],theta))
		elif type(x) is list  and type(y) is list: return self.unify(x[1:],y[1:],self.unify(x[0],y[0],theta))
		else: return None

	def unify_var(self,var,x,theta):
		if  var in theta: return self.unify(theta[var],x,theta)
		elif x in theta: return self.unify(var,theta[x],theta)
		# elif occur_check(var,x):return failure
		else : theta[var]=x;return theta

	def myprint(self,term,theta):
		def change(c):
			if c[0].islower() and c not in theta: return "_"
			return c
		return term["ops"]+"("+", ".join(map(change,term["args"]))+")"
if __name__=='__main__':
	if len(sys.argv)!=3 or sys.argv[1]!='-i':
		print "input error"
		sys.exit()
	fol=Fol(sys.argv[2])
import sys
import  copy
from decimal import Decimal
class HW3:
	def __init__(self,input_file):
		"""
			1.construct query
			2.construct bn
			3.execute query based on query type
		"""
		with open(input_file) as f:
			self.construct_query(f)
			self.construct_bn(f)
		with open("output.txt","w") as output:
			self.execute(output)
	def construct_query(self,file):
		self.queries=[]
		"""
			query={"type":"P/Eu/Meu", "query":{"var":boolean }/[vars] if meu , eveidence:"null"/{"var""boolean} }
		"""
		def parse(s):
			r=s.split(" = ")
			r[1]=0 if r[1]=='-' else 1
			return r
		for line in iter(file.readline,"*"*6+'\n'):
			line=line.strip()
			index=line.find("(")
			query={}
			query["type"]=line[:index]
			line=line[index+1:-1]
			temp=line.split(' | ')
			if not query["type"]=="MEU":
				query["query"]={var:value for (var,value) in map(parse,temp[0].split(", "))}
			else : query["query"]=[var for var in temp[0].split(", ")]
			query["evidence"]={var:value for (var,value) in map(parse,temp[1].split(", "))} if len(temp)==2 else dict()
			self.queries.append(query)
	def construct_bn(self,file):
		def get_index(l):
			return sum([ (1<<(len(l)-i-1))*(1 if l[i]=='+' else 0) for i in range(len(l))])
		self.bn=Bayesian_Network() 
		while True:
			line=file.readline().strip()
			t=line.split(" | ") 
			if len(t)==1:
				self.bn.parents[t[0]]=[] #None
			else: self.bn.parents[t[0]]=t[1].split(' ')
			if not t[0]=="utility": self.bn.vars.append(t[0])
			size=pow(2,len(t[1].split(' ')) if len(t)==2 else 0)
			self.bn.cpt[t[0]]=[ 1 for i in range(size)]
			for i in range(size):
				l=file.readline().strip().split(" ")
				index=get_index(l[1:])
				if l[0]=="decision": self.bn.decision.append(t[0]);break;
				self.bn.cpt[t[0]][index]=float(l[0])
			if not file.readline():break

	def execute(self,output):
		# start = timeit.default_timer()
		alg={"P":self.enumeration,"EU":self.eu,"MEU":self.meu}
		for query in self.queries:
			 result=alg[query["type"]](query)
			 if query["type"]=="P":
			 	if not query["evidence"]:
			 		print result[0]
			 		output.write(str(Decimal(str(result[0]+1e-8)).quantize(Decimal(".01")))) 		
			 	else:
			 		l=query["query"].keys()
			 		print result[sum([ (1<<(len(l)-i-1))*query["query"][l[i]] for i in range(len(l))])]
			 		output.write( str(Decimal(str(result[sum([ (1<<(len(l)-i-1))*query["query"][l[i]] for i in range(len(l))])] +1e-8)).quantize(Decimal(".01"))))
			 elif query["type"]=="EU" :
			 	print result
			 	output.write(str(int(round(result))))
			 else:
			 	print result
			 	output.write(str(result))
			 if query!=self.queries[-1]:output.write("\n")
		# end = timeit.default_timer()
		# print end-start
	def enumeration(self,query):
		"""
			suppose when given  evidence there is only one  
		"""
		def normalize(result):
			total=sum(result)
			return [i/total for i in result]
		result = []
		if query["evidence"]:
			var = query["query"].keys()
			for q in self.enumerate_helper(var):
				result.append(self.enumerate_all(self.bn.vars,dict(query["evidence"].items()+q)))
			result=normalize(result)
		else:
			result.append(self.enumerate_all(self.bn.vars,dict(query["query"].items())))
		return result
	def enumerate_all(self,var,e):
		if not var: return 1
		y=var[0]
		if y in e:
			parent=self.bn.parents[y]
			return self.p_of_y_given_parent(y,e)*self.enumerate_all(var[1:],e)
		else:
			e[y]=0
			r=self.p_of_y_given_parent(y,e)*self.enumerate_all(var[1:],copy.deepcopy(e))
			e[y]=1
			t=r+self.p_of_y_given_parent(y,e)*self.enumerate_all(var[1:],copy.deepcopy(e))
			return t		
	def p_of_y_given_parent(self,y,e):
		index=0
		parent=self.bn.parents[y]
		if not parent:
			return self.bn.cpt[y][0] if e[y]==1 or y in self.bn.decision else 1-self.bn.cpt[y][0]
		for i,p in enumerate(parent):
			index=(index<<1)+e[p]
		return self.bn.cpt[y][index] if e[y]==1 or y in self.bn.decision else 1-self.bn.cpt[y][index]
	def eu(self,query):
		p=list(set(self.bn.parents["utility"])-set(query["evidence"].keys()+query["query"].keys()))
		result=0.0
		new_query={}
		new_query["query"]={ var:0 for var in p}
		new_query["evidence"]=dict(query["evidence"].items()+query["query"].items())
		# print query , new_query
		for i,q in enumerate(self.enumeration(new_query)): #variable_elimination enumeration
			# print i;
			index=0
			for parent in self.bn.parents["utility"]:
				print index
				if parent in new_query["query"]:
					index=(index<<1)+(1&(i>>(len(p)-p.index(parent)-1)))
				else:
					index=(index<<1)+new_query["evidence"][parent]
			# print q,index,self.bn.cpt["utility"]
			result+=q*self.bn.cpt["utility"][index]
		return result
	def meu(self,query):
		def formate(s):
			if s==1 or s==0:return  "+ " if s&1==1 else "- "
			return formate(s>>1)+ ("+ " if s&1==1 else "- ")
		cmax=-100000000
		for index,q in enumerate(self.enumerate_helper(query["query"])):
			print query["query"] , index, formate(index)
			query["query"]=dict(q)
			cur=self.eu(query)
			if cur>cmax:
				cmax=cur;choice=formate(index)
		return choice+str(int(round(cmax)))
	def enumerate_helper(self,var):
		size = 1<<len(var)
		result=[]
		for i in range(size):
			item=[]
			for j in range(len(var)):
				item.append((var[j],1&(i>>(len(var)-j-1))))
			result.append(item)
		return result

	def variable_elimination(self,query):
		def normalize(result):
			if len(result)==1:return result
			total=sum(result)
			return [i/total for i in result]
		factors=self.generate_factors(query)
		for var in self.eliminatevars(query):
			factors=self.sumout(var,factors)
		return normalize(reduce(self.pointwise_product,factors).p)
	def sumout(self,var,factors):
		'''
			input var to be eliminated and factors list
			reuturn new list after sumout factors var


			step:
				1.find all factors related to var 
				2.poinstwiase them to one new factors
				3.sum out new factors based on var 
		'''
		factor_list=[f for f in factors if var in f.var]
		factor=reduce(self.pointwise_product,factor_list)
		new_factor=Factor()
		new_factor.var=[v for v in factor.var if not v==var]
		index=factor.var.index(var)
		new_factor.p=pow(2,len(new_factor.var))*[0]
		# print new_factor.p,new_factor.var,index
		for i,p in enumerate(factor.p):
			n=0
			for j in range(len(factor.var)):
				if j!=index:
					n=(n<<1)+(1&(i>>(len(factor.var)-1-j)))	
			new_factor.p[n]+=p
		return [f for f in factors if var not in f.var ]+[new_factor]	
	def pointwise_product(self,*factors):
		'''
			input: a list contain two factors
			output : new factor

		'''
		def index(a,b,i):
			result=0
			d={ var: 1&(i>>(len(a)-1-j)) for j,var in enumerate(a)}
			for var in b:
				result=(result<<1)+d[var]
			return result
		a,b=factors
		var=list(set(a.var+b.var))
		new_factor=Factor()
		new_factor.var=var
		for i in range(pow(2,len(var))):
			new_factor.p.append(a.p[index(var,a.var,i)]*b.p[index(var,b.var,i)])
		return new_factor
	def generate_factors(self,query):

		factors=[]
		for var in self.bn.vars:
			f=Factor()
			if query["evidence"]:
				f.var=[v for v in self.bn.parents[var]+[var] if v not in query["evidence"].keys()]
			else: f.var=[v for v in self.bn.parents[var]+[var] if v not in query["query"].keys()]
			if not f.var and var in query["evidence"].keys() : continue

			# print f.var
			for i in range(pow(2,len(f.var))):
				index=0
				parents=self.bn.parents[var]
				for p in parents:
					if p not in f.var:
						x=query["evidence"][p] if p in query["evidence"] else query["query"][p] 
					else:
						x=1 if 1&(i>>(len(f.var)-1-f.var.index(p))) else 0
					index=(index<<1)+x
				if not var in f.var:
					if var in query["query"]:
				 		f.p.append(self.bn.cpt[var][index] if query["query"][var] else 1-self.bn.cpt[var][index])
				 	else: f.p.append(self.bn.cpt[var][index] if query["evidence"][var] else 1-self.bn.cpt[var][index])
				else:
					f.p.append(self.bn.cpt[var][index] if 1&(i>>(len(f.var)-1-f.var.index(var)))  else 1-self.bn.cpt[var][index])
			factors.append(f)
		return factors	
	def eliminatevars(self,query):
		'''
		 bn.vars-query.vars(query+evidence)
		'''
		return [v for v in self.bn.vars if v not in query["evidence"].keys()+ query["query"].keys()]
class Bayesian_Network:
	def __init__(self):
		self.cpt={}
		self.parents={}
		self.vars=[]
		self.decision=[]
class Factor:
	def __init__(self):
		self.var=[]
		self.p=[]		
if __name__=="__main__":
	if len(sys.argv)!=3 or sys.argv[1]!="-i":
		sys.exit()
	bn= HW3(sys.argv[2])
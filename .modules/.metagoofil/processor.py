#Christian Martorella 2011
'''
This class will sort the results and create unique list of software, users and paths
'''

class processor():
		def __init__(self,list):
			self.list = list
			self.unique_users = []
			self.unique_soft = []
			self.stat_soft = []
			self.unique_paths = []

		def print_all(self):
			for x in self.list:
 				print x[0]
 				if x[1] != []:
					print x[1]
 				if x[2] != []:
					print x[2]
  
		def sort_users(self):
			for x in self.list:
 				if x[1]!=[]: 
 					for y in x[1]:
 						if self.unique_users.count(y) != 0:
							pass
						else:
							try:
								self.unique_users.append(y.lstrip())
							except:
								pass
				else:
					pass 
			return self.unique_users

 		def sort_software(self):
			for x in self.list:
				if x[3]!=[]:
 					for y in x[3]:
						if self.unique_soft.count(y) != 0:
							pass
						else:
							try:
								self.unique_soft.append(y.lstrip())
							except Exception, e:
								pass
				else:
					pass
			return self.unique_soft

		def sort_paths(self):
			for x in self.list:
				if x[2]!=[]:
 					for y in x[2]:
						if self.unique_paths.count(y) != 0:
							pass
						else:
							self.unique_paths.append(y)
			return self.unique_paths

class Annotation:
	def traverseTree(self, root):
		if not root:
			return
		
		self.generateAnnotation(root)

		if root.children:
			for child in root.children:
				self.traverseTree(child)

	def comparison(self, node):
		if len(node.alternate_plans) != 0:
			for altScan in node.alternate_plans:
				annotation = f"\nCompared to {node.attributes['Node Type']}, {altScan} is {node.alternate_plans.get(altScan):.2f} " \
								f"times as expensive.\n"
				node.annotations += annotation
		else:
			annotation = f"{node.attributes['Node Type']} is used across all AQPs.\n"
			node.annotations += annotation

	def getKeys(self, node):
		group_key = []
		if "Group Key" in node.attributes:
			group_key = node.attributes['Group Key']

		list_of_keys = []
		for key in group_key:
			list_of_keys.append(key)
		stringOfKeys = ', '.join(list_of_keys)
		if len(stringOfKeys) > 1:
			stringOfKeys = ', '.join(list_of_keys)
		else:
			stringOfKeys = list_of_keys[0]
		return stringOfKeys

	def getTables(self, cond):
		cond = cond.replace(" ", "")
		cond = cond.lstrip("(").rstrip(")")
		condsplit = cond.split('.')
		table1 = condsplit[0]
		condsplit2 = condsplit[1].split('=')
		table2 = condsplit2[1]
		return table1, table2

	def formatCondition(self, cond):
		cond = cond.replace(" ", "")
		cond = cond.replace(")AND(", ", ")
		cond = cond.replace(")OR(", ", ")
		cond = cond.replace("(", "")
		cond = cond.replace(")", "")
		return cond

	def generateAnnotation(self, node):
		nodeType = node.attributes['Node Type']
		annotation = ""

		# For scans
		if nodeType == "Seq Scan":
			table = node.attributes['Relation Name']
			node.annotations += "Sequential scan is used to read the {} table, because there is either no index available, " \
				"or the result is about the same size as the tree, which would cause an Index Scan to take longer".format(table)
			node.annotations += ".\n"
			self.comparison(node)

		if nodeType == "Index Scan":
			table = node.attributes['Relation Name']
			node.annotations += "Index scan is used to read the {} table, because there is an index available " \
				"and it would be faster compared to Sequential Scan".format(table)
			if "Index Cond" in node.attributes:
				cond = node.attributes['Index Cond']
				cond = self.formatCondition(cond)
				node.annotations += " with conditions {}".format(cond)
			node.annotations += ".\n"
			self.comparison(node)

		if nodeType == "Index Only Scan":
			table = node.attributes['Relation Name']
			node.annotations += "Index only scan is used to read the {} table ".format(table)
			if "Index Cond" in node.attributes:
				cond = self.formatCondition(cond)
				node.annotations += " with conditions {}".format(cond)
			node.annotations += ".\n"
			self.comparison(node)

		# For joins
		if nodeType == "Hash Join":
			cond = node.attributes['Hash Cond']
			try:
				cond = self.formatCondition(cond)

				condsplit = cond.split('.')
				table1 = condsplit[0]
				condsplit2 = condsplit[1].split('=')
				table2 = condsplit2[1]
				annotation = "Hash join is performed on tables {} and {}, with the conditions {}.\n".format(table1, table2, cond)
			except:
				annotation = "Hash join is performed with the conditions {}.\n".format(cond)
			node.annotations += annotation
			self.comparison(node)

		if nodeType == "Merge Join":
			cond = node.attributes['Merge Cond']
			try:
				cond = self.formatCondition(cond)

				condsplit = cond.split('.')
				table1 = condsplit[0]
				condsplit2 = condsplit[1].split('=')
				table2 = condsplit2[1]
				annotation = "Merge join is performed on tables {} and {}, with the conditions {}.\n".format(table1, table2, cond)
			except:
				annotation = "Merge join is performed with the conditions {}.\n".format(cond)
			node.annotations += annotation
			self.comparison(node)

		if nodeType == "Nested Loop":
			node.annotations += "Nested Loop join is performed.\n"
			self.comparison(node)

		# All other operators
		if nodeType == "Hash":
			if "Output" in node.attributes:
				output = node.attributes['Output']
				temp = output[0].split('.')
				temp1 = temp[0]
				annotation = "Perform hashing on table {}.\n".format(temp1)
			else:	
				annotation = "Perform hashing on table.\n"
			node.annotations += annotation

		if nodeType == "Aggregate":
			strategy = node.attributes['Strategy']
			if strategy == "Sorted":
				if "Group Key" in node.attributes:
					stringOfKeys = self.getKeys(node)
					annotation = "The Sort Aggregate operation will perform grouping on keys: {}.\n".format(stringOfKeys)
				else:
					annotation = "The Sort Aggregate operation will be performed.\n"
			elif strategy == "Hashed":
				if "Group Key" in node.attributes:
					stringOfKeys = self.getKeys(node)
					annotation = "The Hash Aggregate operation will perform grouping on {}.\n".format(stringOfKeys)
				else:
					annotation = "The Hash Aggregate operation will be performed.\n"
			else:
				if "Group Key" in node.attributes:
					stringOfKeys = self.getKeys(node)
					annotation = "The Aggregate operation will perform grouping on {}.\n".format(stringOfKeys)
				else:
					annotation = "The Aggregate operation will be performed.\n"
			node.annotations += annotation

		if nodeType == "Sort":
			annotation = "Sort the table on keys "
			desc = False
			for key in node.attributes['Sort Key']:
				if "DESC" in key:
					desc = True
				else:
					annotation += f"{key}, "
			annotation = annotation[:-2]
			if desc:
				annotation += ' in a decremental manner.'
			else:
				annotation += ' in an incremental manner.'
			annotation += '\n\n'
			node.annotations += annotation

		if nodeType == "Unique":
			annotation = "Duplicates are removed from the table.\n"
			node.annotations += annotation

		if nodeType == "Gather":
			annotation = "Gather operation is performed on the table.\n"
			node.annotations += annotation

		if nodeType == "Gather Merge":
			annotation = "Gather Merge operation is performed, combining the output of child nodes.\n"
			node.annotations += annotation

		if nodeType == "Append":
			annotation = "Append Tables.\n"
			node.annotations += annotation

		if nodeType == "Bitmap Index Scan":
			annotation = "Bitmap index scan is used as multiple indices are constructed for this table.\n"
			node.annotations += annotation
			self.comparison(node)

		if nodeType == "Bitmap Heap Scan":
			annotation = "Bitmap heap scan is used as multiple indices as constructed. A heap is used to " \
							"sort the indices and quickly cut down the number of tuples scanned.\n "
			node.annotations += annotation
			self.comparison(node)

		if nodeType == "CTE Scan":
			annotation = "CTE Scan is performed on table {}.\n".format(node.attributes['CTE Name'])
			node.annotations += annotation

		if nodeType == "Foreign Scan":
			annotation = "Foreign Scan is performed on table {}.\n".format(node.attributes['Relation Name'])
			node.annotations += annotation

		if nodeType == "Limit":
			numRows = node.attributes['Plan Rows']
			annotation = "The Limit operation limits the scanning of the table, with a limitation of {} rows\n".format(numRows)
			node.annotations += annotation

		if nodeType == "Materialize":
			annotation = "The Materialize operation is performed, storing the result of the child operation in memory.\n"
			node.annotations += annotation

		if nodeType == "GroupAggregate":
			if "Group Key" in node.attributes:
				stringOfKeys = self.getKeys(node)
				annotation = "The Group Aggregate operation will perform grouping on keys: {}.\n".format(stringOfKeys)
			else:
				annotation = "The Group Aggregate operation will be performed.\n"
			node.annotations += annotation
			self.comparison(node)

		if nodeType == "HashAggregate":
			if "Group Key" in node.attributes:
				stringOfKeys = self.getKeys(node)
				annotation = "The Hash Aggregate operation will perform grouping on keys: {}.\n".format(stringOfKeys)
			else:
				annotation = "The Hash Aggregate operation will be performed.\n"
			node.annotations += annotation
			self.comparison(node)

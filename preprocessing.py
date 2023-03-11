# Imports

# Need to run the following installations
# pip install psycopg2
# pip install python-decouple
from cgi import test
from cgitb import text
import psycopg2
# from decouple import config
import json

class PlanNode():

    # Construct a node
    def __init__(self) -> None:
        self.parent = None
        self.children = []
        self.attributes = {}
        self.annotations = ""
        self.alternate_plans = {} # Key: alternative plan used, Value: ratio, how much more costly (alternate plan cost / optimal cost)
    
    def print_tree(self):
        queue = []
        queue.append(self)
        while len(queue) != 0:
            childlength = len(queue)
            # Add appropriate children ndoes
            for i in range(childlength):
                node = queue.pop(0)
                if node != None:
                    print(node.attributes['Node Type'] + "->cost: ", node.attributes['Total Cost'], "->Alternate Plans: ", node.alternate_plans , end='\n')
                for child in node.children:
                    queue.append(child)

    # def check_for_join(self):
    #     queue = []
    #     queue.append(self)
    #     joins_used = {}
    #     while len(queue)!=0:
    #         childlength = len(queue)
    #         for i in range(childlength):
    #             node = queue.pop(0)
    #             if "Join" in node.attributes['Node Type'] or "Loop" in node.attributes['Node Type']:
    #                 joins_used[node.attributes['Node Type']] = int(node.attributes['Total Cost'])
    #             for child in node.children:
    #                 queue.append(child)
    #     return joins_used


class SetUp():
    # Attributes
    off_config = {
        # Joins
        "Hash Join" : "set enable_hashjoin=off",
        "Merge Join" : "set enable_mergejoin=off",
        "Nested Loop" : "set enable_nestloop=off",
        # Scans
        "Seq Scan" : "set enable_seqscan=off",
        "Index Scan" : "set enable_indexscan=off",
        "Bitmap Scan": "set enable_bitmapscan=off",
        "Index Only Scan": "set enable_indexonlyscan=off",
        "Tid Scan": "set enable_tidscan=off",
        # Sort
        "Sort" : "set enable_sort=off",
        #Others
        "Hash Agg": "set enable_hashagg=off",
        "Material": "set enable_material=off",
    }

    on_config = {
        # Joins
        "Hash Join" : "set enable_hashjoin=on",
        "Merge Join" : "set enable_mergejoin=on",
        "Nested Loop" : "set enable_nestloop=on",
        # Scans
        "Seq Scan" : "set enable_seqscan=on",
        "Index Scan" : "set enable_indexscan=on",
        "Bitmap Scan": "set enable_bitmapscan=on",
        "Index Only Scan": "set enable_indexonlyscan=on",
        "Tid Scan": "set enable_tidscan=on",
        # Sort
        "Sort" : "set enable_sort=on",
        #Others
        "Hash Agg": "set enable_hashagg=on",
        "Material": "set enable_material=on",
    }

    query_plans = {
        "chosen_plan": "", # Will be replaced by a tuple of (plan_type, root_node, cost)
        "alternative_plans": [] # List of tuples (plan_type, root_node, cost)
    }



    # , host, port_num, database_name, username, password
    def __init__(self, host, port_num, database_name, username, password):
        # Setting up connection
        self.connection = None
        try:
            self.connection = psycopg2.connect(host = host, port = port_num,database= database_name, user= username, password= password)
            #self.connection = psycopg2.connect(host = config("HOST"), port = config("PORT") ,database= config("DATABASE"), user= config("USER"), password= config("PASSWORD"))
            self.verify = True
            if(self.verify):
                #print("Connected")
                self.cursor = self.connection.cursor()
        except (Exception, psycopg2.DatabaseError):
            self.verify = False

    def executeQuery(self, query, off=[]):
        optimalQEP = "EXPLAIN (VERBOSE, COSTS, FORMAT JSON)" + query.strip('\n')

        try:
            # set cursor variable
            cursor = self.cursor
            #Setting off for alternate query plans
            # Default turn off variables not used
            cursor.execute(self.off_config["Tid Scan"])
            cursor.execute(self.off_config["Index Only Scan"])
            for condition in off:
                cursor.execute(self.off_config[condition])
            
            cursor.execute(optimalQEP)
            
            explain_query = cursor.fetchall()

            # Setting config back on to set up for next alternate query plan
            for condition in off:
                #print(self.on_config[condition])
                cursor.execute(self.on_config[condition])
            # write explain details into json file
            # with open('chosenQueryPlan.json', 'w') as output_file:
            #     chosenQueryPlan = (json.dump(explain_query, output_file, ensure_ascii = False, indent = 4))
            self.queryError = False

            return explain_query[0][0][0]['Plan']
        except(Exception, psycopg2.DatabaseError) as error:
                
                # Check how to seperate errors
                print("Your error is: ", error)
                # print("Your query is: ", query)
                message = "Please check your sql statement: \n" + query
                print(message)
                self.queryError = True
                self.connection.rollback()
                return "error"
       

    def add_attributes(self, plan, node):
        """
        Get current plan and insert the corresponding attributes into the current node 
        """
        for key,val in plan.items():
            if key != "Plans":
                node.attributes[key] = val

    def add_node(self, plan,node):
        """
        Recursive create nodes based on the number of "Plans" of current node (Each "Plans" corresponds to an additional child node)
        """
        # Break condition when no further nodes need to be created
        if "Plans" not in plan:
            return
        for plan in plan["Plans"]:
            # Create PlanNode
            child = PlanNode()
            child.parent = node
            self.add_attributes(plan,child)
            self.add_node(plan,child)
            node.children.append(child)

    def build_tree(self, plan):
        """
        Build the query plan tree
        """
        if (plan == "error"):
            print("Please check your sql statements")
            return
        root = PlanNode()
        self.add_attributes(plan, root)
        self.add_node(plan,root)
        return root

    def compareTree(self, chosen_plan_root, alternate_plan_root):
        queue1 = []
        queue2 = []
        queue1.append(chosen_plan_root)
        queue2.append(alternate_plan_root)
        while len(queue1) != 0:
            childlength = len(queue1)
            # Add appropriate children ndoes
            for i in range(childlength):
                node1 = queue1.pop(0)
                node2 = queue2.pop(0)
                if node1.attributes['Node Type'] != node2.attributes['Node Type']:
                    return 0
                for child in node1.children:
                    queue1.append(child)
                for child in node2.children:
                    queue2.append(child)
        return 1

    def computeTotalCost(self, plan_root):
        queue = []
        queue.append(plan_root)
        totalCost = 0
        while len(queue) != 0:
            childlength = len(queue)
            # Add appropriate children ndoes
            for i in range(childlength):
                node = queue.pop(0)
                if node != None:
                    totalCost += node.attributes['Total Cost']
                for child in node.children:
                    queue.append(child)
        return totalCost

    def addToAlternatePlans(self, plan, plan_type):
        if(plan == "error"):
            print(plan_type + " not added")
            return
        alternate_root = self.build_tree(plan)
        # If both trees are the same dont add to alternate plan
        if(self.compareTree(self.query_plans['chosen_plan'][1], alternate_root) == 1):
            print(plan_type + " not added")
            return
        cost = self.computeTotalCost(alternate_root)
        self.query_plans["alternative_plans"].append((plan_type,alternate_root, cost))

    def preAnnotation(self, optimalTreeRoot):
        queue = []
        queue.append(optimalTreeRoot)
        while len(queue) != 0:
            childlength = len(queue)
            # Add appropriate children ndoes
            for i in range(childlength):
                node = queue.pop(0)
                if "Join" in node.attributes['Node Type'] or "Loop" in node.attributes['Node Type']:
                    for alternate_nodes in self.query_plans["alternative_plans"]:
                        if ("Join" in alternate_nodes[0] or "Loop" in alternate_nodes[0]) and (alternate_nodes[0] != node.attributes['Node Type']):
                            if (alternate_nodes[2] > self.query_plans["chosen_plan"][2]):
                                # total alternate plan cost / total optimal plan cost
                                node.alternate_plans[alternate_nodes[0]] = alternate_nodes[2]/self.query_plans["chosen_plan"][2]
                elif "Scan" in node.attributes['Node Type']:
                    for alternate_nodes in self.query_plans["alternative_plans"]:
                        if "Scan" in alternate_nodes[0] and (alternate_nodes[0] != node.attributes['Node Type']):
                            if (alternate_nodes[2] > self.query_plans["chosen_plan"][2]):
                                # total alternate plan cost / total optimal plan cost
                                node.alternate_plans[alternate_nodes[0]] = alternate_nodes[2]/self.query_plans["chosen_plan"][2]
                for child in node.children:
                    queue.append(child)

   
    def getAllQueryPlans(self, query):

        #Original plan
        plan = self.executeQuery(query)
        if(plan == "error"):
            print("Please check your sql statements")
            return
        root = self.build_tree(plan)
        cost = self.computeTotalCost(root)
        self.query_plans["chosen_plan"]= ("Optimal Plan", root, cost)


        #Alternate plans (Max: 6)
        #Checking for AEP for Joins 
        #Full Merge Join
        plan = self.executeQuery(query, ["Nested Loop", "Hash Join"])
        plan_type = "Merge Join"
        self.addToAlternatePlans(plan, plan_type)

        #Full hash join
        plan = self.executeQuery(query, ['Nested Loop', "Merge Join"])
        plan_type = "Hash Join"
        self.addToAlternatePlans(plan, plan_type)

        #Full nested loop join
        plan = self.executeQuery(query, ['Merge Join', "Hash Join"])
        plan_type = "Nested Loop"
        self.addToAlternatePlans(plan, plan_type)

        #Checking for AEP for Scans
        #Seq scan 
        plan = self.executeQuery(query, ["Index Scan", "Bitmap Scan"])
        plan_type = "Seq Scan"
        self.addToAlternatePlans(plan, plan_type)

        # Index Scan
        plan = self.executeQuery(query, ["Seq Scan", "Bitmap Scan"])
        plan_type = "Index Scan"
        self.addToAlternatePlans(plan, plan_type)

        # Bitmap Scan
        plan = self.executeQuery(query, ["Seq Scan", "Index Scan"])
        plan_type = "Bitmap Scan"
        self.addToAlternatePlans(plan, plan_type)

        # Final print
        #print("length: ", len(self.query_plans['alternative_plans']))
        self.preAnnotation(self.query_plans["chosen_plan"][1])









    # # Connect to Postgre database
    # def validateConnect(username, password, database_name):
    #     connection = None
    #     try:
    #         connection = psycopg2.connect(database=database_name, user=username, password=password)
    #         verify = True

    #         # Write login information into json file
    #         loginInfo = {
    #             "username" : username,
    #             "password" : password,
    #             "database" : database_name
    #         }
    #         json_object = json.dumps(loginInfo, indent=4)
    #         with open("loginInfo.json", "w") as outputfile:
    #             outputfile.write(json_object)
    #     except (Exception, psycopg2.DatabaseError):
    #         verify = False
        
    #     return verify

    # def connect():
    #     """Connect using credentials"""
    #     connection = None
    #     loginInfo = json.load(open('loginInfo.json', "r"))
    #     username = loginInfo['username']
    #     password = loginInfo['password']
    #     database_name = loginInfo['database']
    #     try:
    #         connection = psycopg2.connect(database=database_name, user=username, password = password)
    #         # Create a cursor
    #         cursor = connection.cursor()
    #     except(Exception, psycopg2.DatabaseError) as error:
    #         print(error)
    #     finally:
    #         return cursor
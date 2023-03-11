from preprocessing import *
from Interface import *



if __name__ == "__main__":
    app = projectWindow()
    app.mainloop()
    # username = "postgres"
    # password = ""
    # database_name = "TPC-H"


    # print("Welcome to CZ4003 database")

    # # Setting up connection and queries
    # connect = SetUp()
    # with open('query3.txt', 'r') as file:
    #     data = file.read().replace('\n', ' ')
    # query = data
    # #query = "SELECT * FROM customer"
    # #query = "select * from customer C, orders O where C.c_custkey = O.o_custkey"
     

    # #Executing queries
    # connect.getAllQueryPlans(query)

    # #Checking of tree
    # # connect.query_plans['chosen_plan'].print_tree()
    # # connect.query_plans['alternative_plans'][0].print_tree()

    # #Printing best plan tree
    # print("-------------------Best plan operator tree--------------")
    # print(connect.query_plans['chosen_plan'][1].print_tree())

    # #Printing AEP plan tree
    # print("-----------------Alternative plan operator tree----------------")
    # for plan in connect.query_plans['alternative_plans']:
    #     print(plan[1].print_tree())
    #     print("--------------------------------------------")
    

    # # close cursor
    # connect.cursor.close()
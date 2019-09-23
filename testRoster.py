from roster import Roster



rost = Roster("password.json", "EAST")
q = Roster.getOutOfQueue()
print(q)

'''rost.setEmployees()
rost.getCategories()
rost.setOutOfQueue()'''

'''def printQ():
    for t in q:
        print(t)
        print("\n")

def testTrainingIds():
    
    idset = set()
    
    
    if not q:
        return idset

    for t in q:
        print(t)
        if 'user_id' in t and t['user_id']:
            idset.add(t['user_id'])
            print(idset)

    #print(f"idset: {idset}")

printQ()
#testTrainingIds()'''
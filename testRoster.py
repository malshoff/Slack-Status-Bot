from roster import Roster



rost = Roster("password.json", "EAST")
q = rost.getOutOfQueue()

#migrating users collection to employees
def addAccessTokens(self):
    users = db.users

    all = users.find()
    for a in all:
        employees.update({'first_name':a['first_name'], 'last_name':a['last_name']},
        
                        {'$set': {
                            "user_id": a['user_id'], 'access_token': a['access_token']
                        }
        },
            upsert=False,
            )
            
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
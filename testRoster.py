from roster import Roster

rost = Roster("password.json", "EAST")

rost.setEmployees()
rost.setOutOfQueue()

q = rost.getOutOfQueue()

print(q)
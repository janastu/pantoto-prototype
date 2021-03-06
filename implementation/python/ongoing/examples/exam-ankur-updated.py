from engine import *

# initial conditions
system = System()

# pagelets
exam = Pagelet("exam")
system.addPagelet(exam)

# fields
system.addField(Field("Q"))                  #Question
system.addField(Field("A"))                  #Answer
system.addField(Field("G"))                  #Grade

# users
system.addUser("S")
system.addUser("T")

# setting initial state
state = State({"S":"ready", "T":"ready"})
system.setInitialState(state)

# s-t: ready-ready
system.addFieldToView("T","exam","Q","rw")

#defining 1st transition
newstate = State({"S":"writing", "T":"waiting"})

perm = {}
perm["S"]={}
perm["T"]={}
perm["S"]["exam"]={}
perm["T"]["exam"]={}
perm["S"]["exam"]["Q"]="r-"
perm["S"]["exam"]["A"]="rw"
perm["T"]["exam"]["Q"]="r-"

t = Transition(state, newstate, perm)
system.addTransition(t,"sendpaper")

#defining 2nd transition

state = newstate

newstated={}
newstated["S"]="waiting"
newstated["T"]="grading"
newstate = State(newstated)

perm = {}
perm["S"]={}
perm["T"]={}
perm["S"]["exam"]={}
perm["T"]["exam"]={}
perm["S"]["exam"]["A"]="r-"
perm["T"]["exam"]["Q"]="r-"
perm["T"]["exam"]["A"]="r-"
perm["T"]["exam"]["G"]="rw"

t = Transition(state, newstate, perm)
system.addTransition(t,"sendanswer")

#defining 3rd transition

state = newstate

newstated={}
newstated["S"]="done"
newstated["T"]="done"
newstate = State(newstated)

perm = {}
perm["S"]={}
perm["T"]={}
perm["S"]["exam"]={}
perm["T"]["exam"]={}
perm["S"]["exam"]["G"]="r-"
perm["T"]["exam"]["G"]="r-"

t = Transition(state, newstate, perm)
system.addTransition(t,"sendgrade")

#executing actions

#init state
print system.setFieldByUser("S","exam","Q","abc")    #prints false as student doesnt have permission to set Q
print system.setFieldByUser("T","exam","Q","abc")    #prints true as teacher has rw permission on Q and sets Q to "abc"
print system.getFieldByUser("S","exam","Q")          #prints None as student doesnt have permission on Q
print system.getFieldByUser("T","exam","Q")          #prints Q as teacher has rw permission on Q
print system.setFieldByUser("S","exam","A","abc")    #prints false as student doesnt have permission to set A

# paper has not been delivered yet
print system.executeAction("sendanswer")      #prints false as it doesnt matches the transition rules
# paper sent
print system.executeAction("sendpaper")       #prints true as it matches the transition rules

# state t: waiting, s:writing
#s cannot change the question
print system.setFieldByUser("S","exam","Q","abc")    #prints false as student has r- permission on Q
#s can read the question
print system.getFieldByUser("S","exam","Q")          #prints Q as student has r- permission on Q
#t cannot change the question
print system.setFieldByUser("T","exam","Q","abc")    #prints false as teacher has r- permission on Q
#s can answer
print system.setFieldByUser("S","exam","A","abc")    #prints true as student has rw permission on A
print system.executeAction("sendanswer")      #prints true as it matches the transition rules
#state t:grading, s: waiting
print system.executeAction("sendgrade")       #prints true as it matches the transition rules


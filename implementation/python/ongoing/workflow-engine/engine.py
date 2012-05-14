class hashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class State:
    """ State Class
    """
    def __init__(self, userstates):                #userstates is a dict off the states of all the users. (user->state)
        self.statemap = hashableDict(userstates)

    def getState(self):
        """returns Statemap from user->state
        """
        return self.statemap


class Transition:

    def __init__(self, state, new_state, permissions):    #permissions is the dict (user->(pagelet->(field->perm))) of the changed permissions cause of the transition. state new_state are of type State.
        self.initialState = state
        self.newState = new_state
        self.perm = permissions


class Transitions:

    def __init__(self):
        self.transitions={}

    def addTransition(self,trans,action):            #trans is of type Transition, action is a string in this case.
        if not self.transitions.has_key(action):
            self.transitions[action]={}
        self.transitions[action][trans.initialState.getState()] = [trans.newState.getState(), trans.perm]

    def executeAction(self, action, state):
        if not self.transitions.has_key(action):
            return None
        if not self.transitions[action].has_key(state.getState()):
            return None
        return self.transitions[action][state.getState()]


        

class Field:
    
    def __init__(self, label, value=None):
        self.label = label
        self.value = value
    
    def setValue(self, value):
        self.value = value
    
    def getValue(self):
        return self.value
    
    def getLabel(self):
        return self.label



class Fields:

    def __init__(self):
        self.fields={}

    def addField(self, field):            #field is of type Field
        self.fields[field.getLabel()]=field

    def getFields(self):
        return self.fields

    def getValueByField(self, fieldlabel):
        if not self.fields.has_key(fieldlabel):
            return None
        return self.fields[fieldlabel].getValue()

    def setValueByField(self, fieldlabel, val):
        if not self.fields.has_key(fieldlabel):
            return False
        self.fields[fieldlabel].setValue(val)
        return True




class Users:

    def __init__(self):
        self.users=[]

    def addUser(self, user):            #user is a string
        self.users.append(user)

    def getUsers(self):
        return self.users



class Pagelet:

    def __init__(self,label):
        self.label = label
    
    def getLabel(self):                #label is a string
        return self.label
    

class Pagelets:

    def __init__(self):
        self.pagelets={}

    def addPagelet(self, pageletlabel):
        temp = Pagelet(pageletlabel)
        self.pagelets[pageletlabel]= temp
        return temp
         
    def getPagelet(self, pageletlabel):
        return self.pagelets[pageletlabel]

    def getAllPagelets(self):        # returns a dictionary with label->pagelet
        return self.pagelets



class System:

    def __init__(self):
        self.view = {}                #view is a dictionary - user -> pageletlabel -> fieldlabel -> perm
        self.transitions = Transitions()
        self.currentState = None
        self.fields = Fields()
        self.users = Users()
        self.pagelets = Pagelets()

    def addField(self, field):            #field is of type Field
        self.fields.addField(field)

    def addPagelet(self, pagelet):
        self.pagelets.addPagelet(pagelet)

    def addUser(self, user):
        self.users.addUser(user)
        self.view[user]={}

    def setInitialState(self, state):        #state is of type State
        self.currentState = state

    def getCurrentState(self):
        return self.currentState

    def setCurrentState(self, state):
        self.currentState = state

    def addFieldToView(self,user, pageletlabel, fieldlabel,perm):    #perm IN ['--', 'r-', 'rw', '-w']
        if not self.view.has_key(user):
            return False
        if not self.view[user].has_key(pageletlabel):
            self.view[user][pageletlabel] = {}
        self.view[user][pageletlabel][fieldlabel]=perm

    def updateFieldView(self,user,pageletlabel,fieldlabel,perm):    #perm IN ['--', 'r-', 'rw', '-w']
        if not self.view.has_key(user):
            return false
        if not self.view[user].has_key(pageletlabel):
            self.view[user][pageletlabel] = {}
        self.view[user][pageletlabel][fieldlabel]=perm

    def getPermissions(self,user,pageletlabel,fieldlabel):
        if not self.view.has_key(user):
            return None
        if not self.view[user].has_key(pageletlabel):
            return None
        if not self.view[user][pageletlabel].has_key(fieldlabel):
            return None
        return self.view[user][pageletlabel][fieldlabel]

    def executeAction(self,action):
        temp = self.transitions.executeAction( action, self.getCurrentState())
        if temp==None:
            return False
        self.setCurrentState(State(temp[0]))
        for user in temp[1]:
            for pageletlabel in temp[1][user]:
                for fieldlabel in temp[1][user][pageletlabel]:
                    perm = temp[1][user][pageletlabel][fieldlabel]
                    self.updateFieldView(user,pageletlabel,fieldlabel,perm)
        return True

    def getFieldByUser(self,user,pageletlabel,fieldlabel):            #get value of field if the user has permission to read it. Returns None if cant be read.
        if self.getPermissions(user,pageletlabel,fieldlabel) in ["rw","r-"]:
            return self.fields.getValueByField(fieldlabel)
        else:
            return None


    def setFieldByUser(self,user,pageletlabel,fieldlabel,val):            #set value of field if the user has permission to write on it. Returns True if set, False if not.
        if self.getPermissions(user, pageletlabel, fieldlabel) in ["rw","-w"]:
            return self.fields.setValueByField(fieldlabel, val)
        else:
            return False

    def getUserContent(self,user):
        if not self.view.has_key(user):
            return None
        return self.view[user]
    
    def addTransition(self,trans,action):            #trans is of type Transition, action is a string in this case.
        self.transitions.addTransition(trans,action)


    





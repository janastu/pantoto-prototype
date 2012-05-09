#!/usr/bin/python
# Filename: TestContext
from pagelet import Pagelet
from utilities import *
from viewcategory import ViewCategory
from field import Field
import cPickle


# Instantiating users
u1 = User("Student","1")
u2 = User("Student","2")
u3 = User("Teacher","1")
u4 = User("Teacher","2")
cPickle.dump(u1, open(u1.getid()+".obj",'wb'))
cPickle.dump(u2, open(u2.getid()+".obj",'wb'))
cPickle.dump(u3, open(u3.getid()+".obj",'wb'))
cPickle.dump(u4, open(u4.getid()+".obj",'wb'))

# Instantiating a work flow with all users
workflow = Role("AugustPaper","AugustPaper Role")
workflow.adduser(u1.getid())
workflow.adduser(u2.getid())
workflow.adduser(u3.getid())
workflow.adduser(u4.getid())
cPickle.dump(workflow, open(workflow.getid()+".obj",'wb'))

# Instantiating groups with users
stud_grp = Group("Students")
stud_grp.adduser(u1.getid())
stud_grp.adduser(u2.getid())
cPickle.dump(stud_grp, open(stud_grp.getid()+".obj",'wb'))

teach_grp = Group ("Teachers")
teach_grp.adduser(u3.getid())
teach_grp.adduser(u4.getid())
cPickle.dump(teach_grp, open(teach_grp.getid()+".obj", 'wb'))

#****************************************************************************************
# Session user is the teacher now
#****************************************************************************************
sessionuser = u3
print "\nNow you are the teacher 1"
# Instantiating fields
q1 = Field(sessionuser.getid(),{"format":"textbox"},"Sin(30)=")
cPickle.dump(q1, open(q1.getid()+".obj", 'wb'))

q2 = Field(sessionuser.getid(),{"format":"textbox"},"Cos(30)=")
cPickle.dump(q2, open(q2.getid()+".obj", 'wb'))

g = Field(sessionuser.getid(),{"format":"textbox"},"Grade=")
cPickle.dump(g, open(g.getid()+".obj", 'wb'))

# Instantiating Views
qp_perm = Permissions({stud_grp.getid():{q1.getlabel():"-w",q2.getlabel():"-w",g.getlabel():"--"},\
                      teach_grp.getid():{q1.getlabel():"r-",q2.getlabel():"r-",g.getlabel():"--"}})

qpaper = ViewCategory(sessionuser.getid(),"qpaper",qp_perm,workflow)

gp_perm = Permissions({stud_grp.getid():{q1.getlabel():"rn",q2.getlabel():"rn",g.getlabel():"r-"},\
                      teach_grp.getid():{q1.getlabel():"r-",q2.getlabel():"r-",g.getlabel():"rw"}})

gpaper = ViewCategory(sessionuser.getid(),"gpaper",gp_perm,workflow)

p = Pagelet(sessionuser.getid(),[qpaper],[q1,q2,g])
print "\nQpaper view attached:"  
#****************************************************************************************
# Session user is the student 1 now
#****************************************************************************************
sessionuser = u2
print "\nNow you are Student 2"
u1_p = p.postsimilar(sessionuser.getid())
editf= u1_p.edit(sessionuser.getid())
for eachf in editf.keys():
    f =cPickle.load(open(eachf + ".obj",'rb'))
    var = raw_input(f.getlabel())
    f.setvalue(var)
    cPickle.dump(f,open(eachf + ".obj",'wb'))
u1_p.view(sessionuser.getid())
# session user will be globally available to get id from in the actual app.
#****************************************************************************************
# Session user is the student 2 now
#****************************************************************************************
sessionuser = u1
print "\nNow you are Student 1"
u2_p = p.postsimilar(sessionuser.getid())
editf= u2_p.edit(sessionuser.getid())
for eachf in editf.keys():
    f =cPickle.load(open(eachf + ".obj",'rb'))
    var = raw_input(f.getlabel())
    f.setvalue(var)
    cPickle.dump(f,open(eachf + ".obj",'wb'))
u2_p.view(sessionuser.getid())

print "\nBefore grading you'll view your pagelet list as student 2"
pgtlist = [p,u1_p,u2_p]
p.listpagelets(u2.getid(),pgtlist)
#****************************************************************************************
# Session user is the teacher again 
#****************************************************************************************
sessionuser = u3
print"\nNow you are Teacher 1 again"
p.attachcategory(gpaper)
print "\nGradePaper view attached:" 
editf = u1_p.edit(sessionuser.getid())
for eachf in editf.keys():
    f =cPickle.load(open(eachf + ".obj",'rb'))
    var = raw_input(f.getlabel())
    f.setvalue(var)
    cPickle.dump(f,open(eachf + ".obj",'wb'))
print u1_p.view(sessionuser.getid())


editf = u2_p.edit(sessionuser.getid())
for eachf in editf.keys():
    f =cPickle.load(open(eachf + ".obj",'rb'))
    var = raw_input(f.getlabel())
    f.setvalue(var)
    cPickle.dump(f,open(eachf + ".obj",'wb'))
print u2_p.view(sessionuser.getid())

print "\nAfter grading you'll view your pagelet list as student 2"
p.listpagelets(u2.getid(),pgtlist)

# states
ready_ready = State("ready-ready")
ready_waiting = State("ready-waiting")
writing_waiting = State("writing-waiting")
waiting_waiting = State("waiting-waiting")
waiting_grading = State("waiting-grading")
waiting_done = State("waiting-done")
done_done = State("done-done")

states = [ready_ready, writing_waiting, waiting_waiting, waiting_grading, waiting_done, done_done]

# events
send_paper = Event("send-paper")
send_answer = Event("send-answer")
send_grade = Event("send-grade")
get_paper = Event("get-paper")
get_answer = Event("get-answer")
get_grade = Event("get-grade")

events = [send_paper, send_answer, send_grade, get_paper, get_answer, get_grade]

# transitions Transition(from state --event--> new state) + followed by a hook

rr_rwa = Transition(ready_ready, send_paper, ready_waiting)
update_field_view(teacher, paper, question, "ro")

rwa_wrwa = Transition(ready_waiting, get_paper, writing_waiting)
answer = Field("answer")
add_field(answer) # add answer field to field set
update_field_view(student, paper, question ,"ro")
update_field_view(student, paper, answer ,"rw")

wrwa_wawa = Transition(writing_waiting, send_answer, waiting_waiting)
update_field_view(student, paper, answer, "ro")

wawa_wag = Transition(waiting_waiting, get_answer, waiting_grading)
grade = Field("grade")
add_field(grade)
update_field_view(teacher, paper, answer, "ro")
update_field_view(teacher, paper, grade, "rw")

wagr_wad = Transition(waiting_grading, send_grade, waiting_done)
update_field_view(teacher, paper, grade, "ro")

wad_dd = Transition(waiting_done, get_grade, done_done)
update_field_view(student, paper, grade, "ro")

# initial conditions

# users
student = User("student")
teacher = User("teacher")

# pagelets
paper = Pagelet("paper")

# fields
question= Field("2+2=")
answer= Field("")
grade= Field("")

# init workflow
start_workflow(ready_ready) # init state, initilize workflow
add_user(student)
add_user(teacher)
add_pagelet(paper)
add_field(question)
update_field_view(teacher, paper, question, "rw")

# move(event_name) will move state
# users, pagelets, fields, events, states, current_state are global variables




#lang scheme

(require "../../workflow-engine/main.ss")

(provide

  ;; users
  ;; -----
  student
  teacher

  ;; pagelets and fields
  ;; -------------------
  paper
  question
  answer
  grade

  ;; actions
  ;; -------
  send-paper
  send-answer
  send-grade
  get-paper
  get-answer
  get-grade

  ;; user control is limited to 
  set-content! ;; change the content of field to a given value
  next-state   ;; proceed to the next state by invoking an action

  ;; note that the user may not directly update the view of
  ;; any field.  That happens only indirectly as a result of
  ;; an action.


  ;; workflow information
  ;; --------------------
  user-names
  pagelet-names
  field-names
  state-names
  action-names

  ;; view information
  ;; ----------------
  list-pagelets-for-user
  list-all

)
  

;; Exam Workflow
;; =============

;; users
;; -----
(define student (new-user 'student))
(define teacher (new-user 'teacher))


;; states
;; -------
;; student : (ready   writing waiting done)
;; teacher:  (setting waiting grading done)

;; workflow-states:
;; ----------------

(define ready-setting   (new-state 'ready-setting))
(define ready-waiting   (new-state 'ready-waiting))
(define writing-waiting (new-state 'writing-waiting))
(define waiting-waiting (new-state 'waiting-waiting))
(define waiting-grading (new-state 'waiting-grading))
(define waiting-done    (new-state 'waiting-done))
(define done-done       (new-state 'done-done))

(define *states*
  (list
    ready-setting
    ready-waiting
    writing-waiting
    waiting-waiting
    waiting-grading
    waiting-done
    done-done))


;; Actions
;; -------

;; student-actions: (get-paper send-answer get-grade)
;; teacher-actions: (send-paper get-answer send-grade)

(define send-paper  (new-action 'send-paper))
(define send-answer (new-action 'send-answer))
(define send-grade  (new-action 'send-grade))

(define get-paper   (new-action 'get-paper))
(define get-answer  (new-action 'get-answer))
(define get-grade   (new-action 'get-grade))

(define *actions*
  (list
    send-paper
    send-answer
    send-grade

    get-paper
    get-answer
    get-grade))




;; initial state
;; ------------

;; ready-setting

;; Moves
;; -----

; (move ready-setting   send-paper)     => ready-waiting
; (move ready-waiting   get-paper)      => writing-waiting
; (move writing-waiting send-answer)    => waiting-waiting
; (move waiting-waiting get-answer)     => waiting-grading
; (move waiting-grading send-grade)     => waiting-done
; (move waiting-done    get-grade)      => done-done


(define-move
  ready-setting  send-paper ;; =>
  ready-waiting
  (lambda ()
    (update-field-view! teacher paper question ro)))

(define-move
  ready-waiting get-paper ;; =>
  writing-waiting
  (lambda ()
    (add-field! answer)
    (update-field-view! student paper question ro)
    (update-field-view! student paper answer rw)))

(define-move
  writing-waiting send-answer ;; =>
  waiting-waiting  
  (lambda ()
    (update-field-view! student paper answer ro)))

(define-move
  waiting-waiting get-answer  ;; =>
  waiting-grading
  (lambda ()
    (add-field! grade)
    (update-field-view! teacher paper answer ro)
    (update-field-view! teacher paper grade rw)))

(define-move
  waiting-grading send-grade ;; =>
  waiting-done  
  (lambda ()
    (update-field-view! teacher paper grade ro)))


(define-move
  waiting-done get-grade  ;; =>
  done-done
  (lambda ()
    (update-field-view! student paper grade ro)))

;; Intial conditions
;; =================

;; pagelets
;; --------
(define paper  (new-pagelet 'paper))

;; fields
;; -------
(define question (new-field 'question "Mauritius capital?"))
(define answer  (new-field  'answer   "blank"))
(define grade   (new-field  'grade    "blank"))

;; initialize the workflow
;; -----------------------
(start-workflow!
  ready-setting          ;; start state
  (lambda ()
    (add-user! student)
    (add-user! teacher)
    (add-pagelet! paper)
    (add-field! question)
    (update-field-view! teacher paper question rw)))









          
        
      



    

    

    
    


  












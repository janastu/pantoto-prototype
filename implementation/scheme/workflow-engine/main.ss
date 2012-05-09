#lang scheme

(provide

  ;; workflow specification
  ;; ----------------------
  new-state 
  new-action
  define-move
  state-names
  action-names
  

  ;; view specification
  ;; ------------------
  new-user
  new-field
  new-pagelet
  oo ro ow rw

  user-names
  field-names
  pagelet-names
  
  add-user!
  add-field!
  add-pagelet!
  update-field-view!

  
  start-workflow!
  next-state
  set-content!


  get-content
  list-pagelets-for-user
  list-pagelets-for-all-users
  list-all
  
  )  ;; provide


;; Workflow: states and actions
;; ============================

;; workflow state
;; --------------
(define-struct state (name transitions))
(define new-state
  (lambda (name)
    (make-state name (make-hash))))


;; workflow action
;; ---------------
(define-struct action (name))
(define new-action make-action)


;; move
;; ----
;; define-move adds one rule in the workflow automaton
;;

(define define-move
  (lambda (state action new-state hook)
    (hash-set!
      (state-transitions state)
      action
      (lambda ()
        (set! *current-state* new-state)
        (hook)))))

(define next-state
  (lambda (action)
    (let* ([transitions (state-transitions *current-state*)]
           [hook (hash-ref  transitions action
                   (lambda ()
                     (error 'next-state
                       "no transition from  state ~a on action ~a"
                       (state-name *current-state*)
                       (action-name action))))])
      (hook))))
          

;; Users, Fields and Pagelets
;; ===========================

;; A user has a name and a pagelet-view, which is initially
;; empty.


;; A pagelet-view maps pagelets to field-views
;; TYPE pagelet-view? : (hashof pagelet? field-view?)

;; A field-view maps fields to permissions
;; TYPE field-view?   : (hashof field?  perm?)

(define-struct user
   (name            ;; : symbol?
    view))          ;; : pagelet-view?

(define new-user
  (lambda (name)
    (make-user name (make-hash))))

(define-struct pagelet
   (name)) ;;          : symbol?

(define new-pagelet make-pagelet)

(define-struct field
  (  name                ;; : symbol?
    [content #:mutable]) ;; : string?
  )

(define new-field make-field)

;; Permissions
;; ===========
(define oo "--")
(define ro "r-")
(define ow "-w")
(define rw "rw")

(define perm?
  (lambda (s)
    (member s (list oo ro ow rw))))

(define perm-writable?
  (lambda (perm)
    (memq perm (list ow rw))))

(define perm-readable?
  (lambda (perm)
    (memq perm (list ro rw))))

(define list-field/perm
  (lambda (f perm)
    (list 'name: (field-name f) 'perm: perm 'content: (field-content f))))


;; Global State Variables
;; ======================

(define *states* '())
(define *actions* '())
(define *current-state* #f)

(define *users*         '())
(define *fields*        '())
(define *pagelets*      '())


(define reset-system!
  (lambda ()
    (set! *states* '())
    (set! *actions* '())
    (set! *current-state* #f)
    (set! *users*         '())
    (set! *fields*        '())
    (set! *pagelets*      '())))


(define start-workflow!
  (lambda (init-state hook)
    (set! *current-state* init-state)
    (hook)))


;; Add functions
;; ==============

;; add-user! : user? -> void
(define add-user!
  (lambda (u)
    (set! *users* (cons u *users*))))

;; add-field! : field? -> void
(define add-field!
  (lambda (f)
    (set! *fields* (cons f *fields*))))

;; add-pagelet! : pagelet? -> void
(define add-pagelet!
  (lambda (p)
    (set! *pagelets* (cons p *pagelets*))))


;; View functions
;; ==============


;; TYPES
;; user-view             : user? -> pagelet-view?
;; pagelet-view?         : (hashof pagelet?  field-view?)
;; field-view?           : (hashof field?    perm?)

;; field-view-ref: [field-view? field?] -> perm?
(define field-view-ref
  (lambda (field-view f)
    (hash-ref field-view f
      (lambda () #f))))

;; pagelet-view-ref : [pagelet-view? pagelet?] -> field-view?
(define pagelet-view-ref
  (lambda (pv p)
    (hash-ref pv p
      (lambda () #f))))

;; get-field-view-of-pagelet-for-user : [user? pagelet?] -> field-view?
(define get-field-view-of-pagelet-for-user
  (lambda (u p)
    (or (pagelet-view-ref (user-view u) p)
      (error 'get-field-view-of-pagelet-for-user
        "user ~a can not see pagelet ~a"
        (user-name u) (pagelet-name p)))))


;; updates the user's view of a field in a given pagelet
;; with the given perm.

(define update-field-view!
  (lambda (u p f perm)
    (hash-update! (user-view u) p
      (lambda (field-view)
        (hash-update! field-view f
          (lambda (old-perm) perm)
          perm)
        field-view) 
      (make-hash))))


(define get-perm
  (lambda (u p f)
    (let ([fv (get-field-view-of-pagelet-for-user u p)])
      (or (field-view-ref fv f)
        (error 'get-perm
          "field ~a of pagelet ~a is nonexistent/inaccessible to user ~a"
          (field-name f)  (pagelet-name p) (user-name u))))))


(define get-content
  (lambda (u p f)
    (if (perm-readable? (get-perm u p f))
      (field-content f)
      (error 'get-content
        "field ~a of pagelet ~a is visible to user ~a but is not readable"
        (field-name f) (pagelet-name p) (user-name u)))))

(define set-content!
  (lambda (u p f c)
    (if (perm-writable? (get-perm u p f))
      (set-field-content! f c)
      (error 'set-content!
        "field ~a of pagelet ~a is visible to user ~a but is not writable"
        (field-name f) (pagelet-name p) (user-name u)))))


;; listing functions for pretty-printing
;; =====================================

;; list-field-view: field-view? -> (listof (symbol? content? perm?))
(define list-field-view
  (lambda (fv)
    (hash-map
      fv
      list-field/perm)))

(define list-pagelet-view
  (lambda (pv)
    (hash-map
      pv
      (lambda (p field-view)
        (list
          'pagelet: (pagelet-name p)
          'fields:
          (list-field-view field-view))))))




;; User listing functions
;; =======================

(define user-names
  (lambda ()
    (map  user-name *users*)))

(define field-names
  (lambda ()
    (map  field-name *fields*)))

(define pagelet-names
  (lambda ()
    (map  pagelet-name *pagelets*)))

(define state-names
  (lambda ()
    (map  state-name *states*)))

(define action-names
  (lambda ()
    (map  action-name *actions*)))




;; list-pagelets-for-user: user? ->
;;                   (listof  (paglet-name: symbol?
;;                             fields: (listof (symbol? content? perm?)))

(define list-pagelets-for-user
  (lambda (u)
    (list-pagelet-view (user-view u))))

(define list-pagelets-for-all-users
  (lambda ()
    (map (lambda (u)
           (list
             'user: (user-name u)
             'pagelets: (list-pagelets-for-user u)))
      *users*)))

(define list-all list-pagelets-for-all-users)








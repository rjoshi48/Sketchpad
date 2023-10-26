import tkinter as tk
import copy
import os
import pickle
from tkinter import *
from tkinter import ttk

color = 'black'                 #default color for the shapes
figure = 'sketch'               #default shape (freehand)
method = 'draw'                 #default method 
previous_x, previous_y = 0,0
prev_shape = -1   
poly_coordinates = []  
prev_poly = -1 
selected_option = 'move'
selected_objectid =-1
object_tags = {'sketch':0,'polygon':0, 'group':0} #tag the objects for selection operations
copy_object_info = []
advance_option = 'group'
group_objects = []
canvas_history = []
canvas_history_index = -1
undoredo_option ='undo'
undo_stack =[]
redostack = []



root = tk.Tk()
root.title("Sketchpad")
#root.geometry("366x346")
root.state('zoomed')
#root.resizable(0, 0)
root.config(bg="#333333")
root.rowconfigure(0,weight=1)
root.columnconfigure(0,weight=1)

#canvas.create
canvas = tk.Canvas(root)
canvas.grid(row=0, column=0,sticky='nsew')

## Track user selections and mouse clicks and movements on canvas

def left_click(event):   #local x and y coordinates also set varaibls based on user selections 
    global previous_x, previous_y, prev_shape, poly_coordinates, selected_objectid, object_tags, selected_option, advance_option
    if method == 'draw':
        previous_x, previous_y = event.x, event.y
        prev_shape = -1
        if figure != 'polygon':
            poly_coordinates = [] 

        if figure=="sketch":
            object_tags["sketch"] = object_tags["sketch"] + 1 
    
    elif method == 'select':
        #selected_objectid = canvas.find_closest(event.x, event.y)[0]
        selected_objectid = find_selected_object(event)
        if (selected_objectid!=-1):			#check if not button
            #print('moveeeeeeeeeeeee', selected_objectid)
            selected_Options(event)
        if selected_option == 'paste':
            paste_currentobj(event)
    elif method == 'advanced':
         selected_advanced_options(event)

def mouse_move(event):
    global previous_x, previous_y, prev_shape, poly_coordinates,prev_poly, selected_option
    if method == 'draw':
        if figure == 'sketch':
            addLine(event)
        elif figure == 'line':
            addStraightLine(event)
        elif figure == 'rectangle':
            draw_rectangle(event)
        elif figure == 'ellipse':
            draw_ellipse(event)
        elif figure == 'circle':
            draw_circle(event)
        elif figure == 'square':
            draw_square(event)
        # elif figure == 'open polygon':
        #     draw_openpolygon(event)
        elif figure == 'polygon':
            draw_closedpolygon(event)
    elif method == 'select':
        if selected_option == 'move':
            move_elements(event)


#Save old coordinates of the polygon which will be the start point for the next line of the polygon
def button_release(event):
    global figure, poly_coordinates
    if figure == 'polygon':
        poly_coordinates.append((event.x,event.y))
        #print(poly_coordinates[-1][0], poly_coordinates[-1][1])
    if method == 'draw' or selected_option == 'move' or selected_option=='paste':
         undo_stack.append((event.x,event.y))

# added right cick binding for grouping objects
def right_click(event):
    #global method
    if method == 'advanced':
         advanced_group_shapes(event) 

#Bind mouse clicks with functions 
canvas.bind("<Button-1>", left_click)
canvas.bind("<B1-Motion>", mouse_move)
canvas.bind("<ButtonRelease-1>", button_release)
canvas.bind("<Button-3>", right_click)

#Methods to set properties
def clear_obj(shape):
    if shape != -1:
        canvas.delete(shape)

def set_shape(shape):
    global figure, method
    figure = shape
    if figure == 'polygon':
         object_tags['polygon'] = object_tags['polygon'] + 1
    method = 'draw'

def set_options(option):
    global method, selected_option, selected_objectid 
    method = 'select'
    selected_option = option

    selected_objectid =-1

def set_advance_options(adv_option):
     global method, advance_option, selected_objectid, group_objects
     method= 'advanced'
     advance_option = adv_option
     selected_objectid = -1 
     group_objects = []

def set_undo_redo(option):
     global method, undoredo_option
     method = 'very advanced'
     undoredo_option = option
     set_advanced_undoredo()
     

def find_selected_object(event):
	object_id = canvas.find_closest(event.x, event.y)[0] #get object id (works for square, circle, straight line)
	object_tags = canvas.gettags(object_id) # for sketch and polygon
	for tag in object_tags:									
		if tag.find("button") != -1: #identify buttons 							
			return -1											
	for tag in object_tags:									
		if tag.find("group") != -1:								
			return tag											
	for tag in object_tags:									
		if (tag.find("sketch")!=-1) or (tag.find("poly")!=-1):	# get tags for sketch
			return tag											
	return object_id	

## Methods to draw shapes on canvas 

# Sketech /Freehand
def addLine(event): # Add tags for move and select operations to consider freehand line as one https://tkdocs.com/tutorial/canvas.html (Tags section)
    global previous_x, previous_y, object_tags
    canvas.create_line((previous_x, previous_y, event.x, event.y), fill=color, width=2, tag= ('sketch_'+str(object_tags["sketch"])))  
    previous_x, previous_y = event.x, event.y

# Straight Line
def addStraightLine(event):
    global previous_x, previous_y, prev_shape
    clear_obj(prev_shape) # delete multiple lines created from anchor https://stackoverflow.com/questions/73453180/problems-while-drawing-straight-line-and-dragging-in-tkinter-canvas
    prev_shape = canvas.create_line((previous_x, previous_y, event.x, event.y), fill=color, width=2)

# Rectangle 
def draw_rectangle(event):
    global previous_x, previous_y, prev_shape
    clear_obj(prev_shape) # delete multiple lines created from anchor https://stackoverflow.com/questions/73453180/problems-while-drawing-straight-line-and-dragging-in-tkinter-canvas
    prev_shape = canvas.create_rectangle((previous_x, previous_y, event.x, event.y), fill=color, width=2)

# Ellipse
def draw_ellipse(event):
    global previous_x, previous_y, prev_shape
    clear_obj(prev_shape) # delete multiple lines created from anchor https://stackoverflow.com/questions/73453180/problems-while-drawing-straight-line-and-dragging-in-tkinter-canvas
    prev_shape = canvas.create_oval((previous_x, previous_y, event.x, event.y), fill=color, width=2)

# Circle
def draw_circle(event):
    global previous_x, previous_y, prev_shape
    clear_obj(prev_shape) # delete multiple lines created from anchor https://stackoverflow.com/questions/73453180/problems-while-drawing-straight-line-and-dragging-in-tkinter-canvas
    
    #Special case of a circle. Keep the horizontal and vertical length same. Find radius which is equal to all sides of boundry
    # https://stackoverflow.com/questions/63314409/how-to-draw-a-perfect-square-using-tkinter-canvas
    radius = min(abs(event.x-previous_x), abs(event.y-previous_y))	#find max size in current selection
    signx = 1 if (event.x-previous_x) >=0 else -1
    signy = 1 if (event.x-previous_x) >=0 else -1
    x = previous_x + (radius * signx)
    y = previous_y + (radius * signy)

    prev_shape = canvas.create_oval((previous_x, previous_y, x, y), fill=color, width=2)

# Square
def draw_square(event):
    global previous_x, previous_y, prev_shape
    clear_obj(prev_shape) # delete multiple lines created from anchor https://stackoverflow.com/questions/73453180/problems-while-drawing-straight-line-and-dragging-in-tkinter-canvas

    # https://stackoverflow.com/questions/63314409/how-to-draw-a-perfect-square-using-tkinter-canvas
    sides = min(abs(event.x-previous_x), abs(event.y-previous_y))	#find max size in current selection
    signx = 1 if (event.x-previous_x) >=0 else -1
    signy = 1 if (event.x-previous_x) >=0 else -1
    x = previous_x + (sides * signx)
    y = previous_y + (sides * signy)

    prev_shape = canvas.create_rectangle((previous_x, previous_y, x, y), fill=color, width=2)

#Polygon
def draw_closedpolygon(event):
    global previous_x, previous_y, prev_shape, poly_coordinates
    clear_obj(prev_shape)
    if not poly_coordinates:
        prev_shape = canvas.create_line((previous_x, previous_y, event.x, event.y), fill=color, width=3,tag= ('polygon_'+str(object_tags['polygon'])))
    
    else:
        prev_shape = canvas.create_line((poly_coordinates[-1][0], poly_coordinates[-1][1], event.x, event.y),fill=color, width=3,tag= ('polygon_'+str(object_tags['polygon'])))
   
def draw_openpolygon(event):
    global previous_x, previous_y, prev_shape
    clear_obj(prev_shape) # delete multiple lines created from anchor https://stackoverflow.com/questions/73453180/problems-while-drawing-straight-line-and-dragging-in-tkinter-canvas
    prev_shape = canvas.create_line((previous_x, previous_y, event.x, event.y), fill=color, width=3)

# Selection methods (move, copy, cut, paste)
def selected_Options(event):
    global selected_option, selected_objectid, previous_x, previous_y
    if selected_option == 'move':
        previous_x, previous_y = event.x, event.y
    elif selected_option == 'copy':
         save_currentobj(event)
    elif selected_option == 'cut':
         save_currentobj(event)
         canvas.delete(selected_objectid)
         
# Move
def move_elements(event):
    global previous_x, previous_y, selected_objectid
    if selected_objectid !=-1:
        x = event.x - previous_x
        y = event.y - previous_y
        canvas.move(selected_objectid, x, y)
        previous_x, previous_y = event.x, event.y
    #print(canvas.type(selected_objectid),canvas.itemcget(selected_objectid,"tags"))

#Copy, Cut
def save_currentobj(event):
    global selected_objectid, copy_object_info
    print('copied object',selected_objectid)
    copy_object_info=[]										
    for object_id in canvas.find_withtag(selected_objectid):	# extracting width, color, coordinates and tags of selected shape https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_line.html
            obj_details={}
            obj_details["options"]={}
            obj_details["options"]["width"]=canvas.itemcget(object_id, "width") # itemcget returns the value of the given configuration option in the selected object https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/canvas-methods.html
            obj_details["options"]["fill"]=canvas.itemcget(object_id, "fill")
            obj_details["options"]["tags"]=canvas.itemcget(object_id, "tags")
            obj_details["coords"]=canvas.coords(object_id)
            obj_details["type"]=canvas.type(object_id)
            copy_object_info.append(obj_details)			#store the config details of selected object 
    #print(copy_object_info)
		
def paste_currentobj(event):
    global copy_object_info
    draw_functions={ 
        "line":getattr(canvas,"create_line"),
        "rectangle":getattr(canvas,"create_rectangle"),
        "oval":getattr(canvas,"create_oval"),
        "sketch":drawcustom,
        "polygon":drawcustom
    }
    tags={}
    copied_obj=copy.deepcopy(copy_object_info)
    #print('copied object',copied_obj)
    if not copied_obj:													
        return
    # print(copied_obj["options"]["tags"])														
    x=event.x-copied_obj[0]["coords"][0]
    y=event.y-copied_obj[0]["coords"][1]
    for objectid in copied_obj:
        print('printting',objectid)
        objectid["coords"][0]=objectid["coords"][0]+x                
        objectid["coords"][2]=objectid["coords"][2]+x
        objectid["coords"][1]=objectid["coords"][1]+y
        objectid["coords"][3]=objectid["coords"][3]+y
        if objectid["options"]["tags"]!='':									
            old_tags = objectid["options"]["tags"].split(" ")				
            new_tags=[]
            for curr_tag in old_tags:
                if curr_tag not in ("{}","current"):						
                    if curr_tag not in tags:							
                        tags[curr_tag]=create_new_tag(curr_tag)				
                    new_tags.append(tags[curr_tag])					
            objectid["options"]["tags"] = new_tags
            #print('tags for objects',objectid["options"]["tags"])
        draw_functions[objectid["type"]](objectid["coords"], objectid["options"])
                
def drawcustom(data, options): #this function will draw scrible line and polygon which has custom shapes 
     global object_tags
     object_tags["polygon"] = object_tags["polygon"]+1
     for i in data:
        id = canvas.create_line(i)
        canvas.itemconfigure(id, options)
        canvas.dtag(id)
     canvas.itemconfig(id, tags=('polygon_'+str(object_tags["polygon"])))
     return 'polygon_'+str(object_tags["polygon"])

def create_new_tag(tag):
    global object_tags
    tagno,s=tag.split('_')
    object_tags[tagno]=object_tags[tagno]+1
    newTag=tagno+"_"+str(object_tags[tagno])
    return newTag

# Advanced menthds (group, ungroup)

#left click to group and right click to create a new group (on the canvas left click all the objects to form group and end with right click)

def selected_advanced_options(event):
     global advance_option, group_objects, selected_objectid
     if advance_option == 'group':
          selected_objectid = find_selected_object(event)
          if selected_objectid != -1:
               group_objects.append(selected_objectid)
     
     elif advance_option == 'ungroup':
          selected_objectid = find_selected_object(event)
          advanced_ungroup_shaped(event)
     #print('Grouped elements',group_objects)


def advanced_group_shapes(event): 
     # group elements by adding same tags to all the objects https://stackoverflow.com/questions/67924299/how-to-move-multiple-objects-together-in-tkinter-canvas, https://web.archive.org/web/20201108093851id_/http://effbot.org/tkinterbook/canvas.htm#item-specifiers
     global group_objects, object_tags
     object_tags['group'] = object_tags['group'] + 1
     for obj in group_objects:
          canvas.itemconfig(obj, tags=('group_'+str(object_tags["group"]),canvas.gettags(i)))
          #print('Current Tags', canvas.itemcget(i, "tags"))

def advanced_ungroup_shaped(event):
    global group_objects, object_tags, selected_objectid
    if selected_objectid.find('group') != -1:
         for obj in canvas.find_withtag(selected_objectid):
              canvas.itemconfig(obj,tags=remove_group_tag(obj)) #ungroup by removing the group tag and retaining/restoring the indivisual tag

     
def remove_group_tag(object):
	tags = canvas.gettags(object)
	oldtags=[]
	for j in tags:
		if j.find("group")==-1:									
			oldtags.append(j)							
	return oldtags

## Advanced UNDO and REDO

def set_advanced_undoredo():
     global undoredo_option, undo_stack, redostack
     if undoredo_option == 'undo':
          object_id = canvas.find_closest(undo_stack[-1][0], undo_stack[-1][1])
          object_id= canvas.find_withtag(object_id)
          object_tags = canvas.gettags(object_id)
          #redostack.append(object_id)
          
          if object_tags:
            for tags in object_tags:
                if (tags.find("sketch")!=-1) or (tags.find("poly")!=-1):
                    undo_save_data(tags)
                    canvas.delete(tags)
          else:
                undo_save_data(object_id)
                canvas.delete(object_id)
          #undo_stack.pop()
          #print(object_id, canvas.type(object_id))

     elif undoredo_option == 'redo':
          redo_create_shape()

def undo_save_data(object_id):
    global redostack, undo_stack

    for object_id in canvas.find_withtag(object_id):
        obj_details={}
        objinfo = []
        obj_details["options"]={}
        obj_details["options"]["width"]=canvas.itemcget(object_id, "width")
        obj_details["options"]["fill"]=canvas.itemcget(object_id, "fill")
        obj_details["options"]["tags"]=canvas.itemcget(object_id, "tags")
        obj_details["coords"]=canvas.coords(object_id)
        obj_details["type"]=canvas.type(object_id)
        redostack.append(obj_details)
    #redostack.append(objinfo)
    #print(redostack)

def redo_create_shape():
    global redostack
    draw_functions={ 
        "line":getattr(canvas,"create_line"),
        "rectangle":getattr(canvas,"create_rectangle"),
        "oval":getattr(canvas,"create_oval"),
        "sketch":drawcustom_redo,
        "polygon":drawcustom_redo
    }
    #stack = redostack[-1]
    #print(objectid["options"]["tags"])
    tags={}
    for objectid in redostack: 
        if objectid["options"]["tags"]!='':									
            old_tags = objectid["options"]["tags"].split(" ")				
            new_tags=[]
            for curr_tag in old_tags:
                if curr_tag not in ("{}","current"):						
                    if curr_tag not in tags:							
                        tags[curr_tag]=get_tag(curr_tag)				
                    new_tags.append(tags[curr_tag])					
            objectid["options"]["tags"] = new_tags

        draw_functions[objectid["type"]](objectid["coords"], objectid["options"])
    redostack.pop()

def drawcustom_redo(data, options):
     for i in data:
        id = canvas.create_line(data)
        canvas.itemconfigure(id, options)

def get_tag(tag):
    global object_tags
    tagno,s=tag.split('_')
    object_tags[tagno]=object_tags[tagno]
    newTag=tagno+"_"+str(object_tags[tagno])
    return newTag

### Save and Load file on disk ###
def save_load_file(option):
     shapes = canvas.find_all()
     #print("Shapes in print", shapes)
     if option == 'save':
          save_file(shapes)
     elif option == 'load':
          #print('Loadddddddddddd', file_name.get())
          load_file()

def save_file(shapes):
    global file_name 											
    save_data={}
    save_data["object_tags"]=object_tags
    save_data["shapes"]=[]

    for obj in shapes:
        tags=canvas.itemcget(obj, "tags").split(" ")
        check=False
        for t in tags:						
            if t.find("buttons")!=-1:
                check=True
        if not check and str(canvas.type(obj)) != 'window':	
            #print('inside check', canvas.type(obj))								
            shape_details={}								
            shape_details["options"]={}
            shape_details["type"]=canvas.type(obj)
            shape_details["options"]["width"]=canvas.itemcget(obj, "width")
            shape_details["options"]["fill"]=canvas.itemcget(obj, "fill")
            shape_details["options"]["tags"]=tags
            shape_details["coords"]=canvas.coords(obj)
            save_data["shapes"].append(shape_details)
            #print('Type is',canvas.type(obj))		
    file=file_name.get()
    if file=='':
        print("No filename")
        return
    with open(file, 'wb') as file:
        pickle.dump(save_data, file)


def load_file():
     global  object_tags, file_name
     #file_name = file_name
     file = file_name.get()
     if os.path.isfile(file):
          with open(file, 'rb') as source:
               source_obj = pickle.load(source)
     delete_existing_data()
     object_tags=source_obj["object_tags"]
     load_data(source_obj)

def delete_existing_data():
    current_shapes = canvas.find_all()
    #print(current_shapes)
    for shape in current_shapes:
        tags_list=canvas.itemcget(shape, "tags").split(" ")
        flag=False
        for obj in tags_list:
            #print(canvas.type(obj))						
            if obj.find("buttons")!=-1:
                flag=True
        if not flag and str(canvas.type(shape)) != 'window':									
            canvas.delete(shape)

def load_data(source_obj):						
    function_list={
        "freehand":drawcustom_redo, 
        "line":getattr(canvas,"create_line"),
        "rectangle":getattr(canvas,"create_rectangle"),
        "oval":getattr(canvas,"create_oval"),
        "polygon":drawcustom_redo
    }
    for obj in source_obj["shapes"]:
        function_list[obj["type"]](obj["coords"], obj["options"])
                

### Add BUTTONS ####

## Colors ##
colors = ["black","grey", "white","blue", "cyan3", "skyblue1","salmon","purple1","brown", "red", "green", "springgreen2", "yellow", "peachpuff3"]
place = 20
#created a new method due to issue with tag bind in loop https://stackoverflow.com/questions/37583274/python-tkinter-tag-bind-not-working-inside-loop
def lambda_setcolor(selected_color): 
    return lambda x:set_color(selected_color)
for i in colors:
    selected_color = canvas.create_rectangle(10, place, 30, place+20,fill=i, tags=('buttons'))
    canvas.tag_bind(selected_color, '<Button-1>', lambda_setcolor(i))
    place+=30

def set_color(selected_color):
    global color
    color = selected_color
    #print(color)

## Shapes ##
shapes = ['sketch', 'line', 'rectangle', 'ellipse', 'square', 'circle', 'polygon']
button_width = 90
button_height = 30
place = 40

for shape in shapes:
    shape_button = tk.Button(root, text=shape.capitalize(), command=lambda s=shape: set_shape(s))
    canvas.create_window(place, 10, anchor='nw', window=shape_button, width=button_width, height=button_height)
    place += button_width + 10


## Selection buttons (move, copy, cut, paste) ##
options = ['move', 'copy', 'cut','paste']
for o in options:
    option_button = tk.Button(root, text=o.capitalize(), command=lambda s=o: set_options(s),bg='grey2',fg='white')
    canvas.create_window(place, 10, anchor='nw', window=option_button, width=button_width, height=button_height)
    place += button_width + 10

## Advanced buttons Group, Ungroup ##
adv_options= ['group', 'ungroup']
for a in adv_options:
    option_button = tk.Button(root, text=a.capitalize(), command=lambda s=a: set_advance_options(s),bg='steelblue',fg='white')
    canvas.create_window(place, 10, anchor='nw', window=option_button, width=button_width, height=button_height)
    place += button_width + 10

### Very Advanced buttons ###

# Undo, Redo #
undoredo_options= ['undo', 'redo']
for a in undoredo_options:
    option_button = tk.Button(root, text=a.capitalize(), command=lambda s=a: set_undo_redo(s),bg='mediumpurple4',fg='white')
    canvas.create_window(place, 10, anchor='nw', window=option_button, width=button_width, height=button_height)
    place += button_width + 10

# Save, Load #

#Text box for user input
file_name = Entry(root)
place = 50
canvas.create_window(place, 50, window=file_name, anchor=NW, width=200, height=button_height, tags=('buttons'))
outline_coords = (place, 50, place + 200, 50 + button_height)  # Coordinates for the outline rectangle
canvas.create_rectangle(outline_coords, outline="black", width=3, tags=('buttons'))  # Create the outline rectangle
place = place + 210

save_options = ['save','load']
for so in save_options:
    save_button = tk.Button(root, text=so.capitalize(), command=lambda a=so: save_load_file(a),bg='brown3',fg='white')
    canvas.create_window(place, 50, anchor='nw', window=save_button, width=button_width, height=button_height)
    place += button_width + 10

shapes = canvas.find_all()

clear_canvas = ['clear Canvas']
clear_button = tk.Button(root, text=clear_canvas[0].capitalize(), command=lambda a=clear_canvas[0]: delete_existing_data(), bg='forest green', fg='white')
canvas.create_window(place, 50, anchor='nw', window=clear_button, width=button_width, height=button_height)

root.mainloop()

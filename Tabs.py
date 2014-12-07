# Allows for tabbed editing within the pythonista editor
import ui
import editor
import sqlite3 as sql
import console
import os
from math import pi
import webbrowser
from editmenu import editmenuclass
import inspect
base=os.path.dirname(inspect.getframeinfo(inspect.currentframe())[0])
tabdb=os.path.join(base,'tabs.db')
available_width = 500
open_tabs = {}
num_of_tabs = 0
tab_height = 45
tab_y = 5
count = 0
tab_width = 150

def edit_menu(sender):
    editmenuclass.load_and_show()

@ui.in_background    
def check_tab():
    open_path = os.path.split(editor.get_path())[1]
    for t in range(len(sv.subviews)):
        if sv.subviews[t].name != open_path and sv.subviews[t].background_color != 'white':
            sv.subviews[t].background_color = 'white'
        if sv.subviews[t].name == open_path:
            sv.subviews[t].background_color = 'orange'

def add_new_button(name, new = False):
    b = ui.Button(title = str(name))
    b.height = tab_height
    b.width = tab_width
    b.border_width = 0.5
    b.corner_radius = 10
    if new == True:
        for r in range(len(sv.subviews)):
            sv.subviews[r].background_color = 'white'
        b.background_color = 'orange'
    else:
        b.background_color = 'white'
    b.border_color = 'grey'
    b.image = ui.Image.named('_blank')
    b.tint_color = 'black'
    b.action = open_url
    b.transform = ui.Transform.rotation(pi/2)
    global count
    b.y = tab_width*count*1.05 + 120
    b.x = -10
    b.name = str(name)
    close_title = name + '_close'
    c = ui.Button()
    c.width = 15
    c.height = 15
    c.x = 3
    c.y = 3
    #c.corner_radius = c.height/2
    #c.border_width = 1
    c.image = ui.Image.named('ionicons-close-24')
    c.action = close_button
    b.add_subview(c)
    sv.add_subview(b)
    count += 1
    
def close_button(sender):
    marker = sender.superview.y
    tab = sender.superview
    tab_name = sender.superview.title
    sv.remove_subview(tab)
    def move():
        for i in range(len(sv.subviews)):
            if sv.subviews[i].y > marker:
                sv.subviews[i].y -= tab_width*1.05
    ui.animate(move, duration = 0.3)
    global count
    count -=1
    conn = sql.connect(tabdb)
    conn.text_factory = str
    c = conn.cursor()
    c.execute('DELETE FROM files WHERE name = ?', (tab_name,))
    conn.commit()

# Create tab for current file
@ui.in_background
def add_file(sender):
    current_path = str(editor.get_path())
    conn = sql.connect(tabdb)
    c = conn.cursor()
    name = os.path.split(current_path)[1]
    c.execute('''select url from files where name = ?''', (name,))
    is_open = c.fetchall()
    if is_open:
        console.hud_alert('There is already a tab for this file', duration = 1)
        return None
    c.execute('''INSERT INTO files VALUES (?, ?)''', (name, current_path))
    conn.commit()
    conn.close()
    open_tabs.append(name)
    add_new_button(name, new = True)

# Open file when tab is pressed
def open_url(sender):
    current_path = editor.get_path()
    conn = sql.connect(tabdb)
    conn.text_factory = str
    c = conn.cursor()
    button_title = sender.title
    c.execute('''select name from files where url = ?''', (current_path,))
    current_tab = c.fetchall()
    if current_tab:
        current_tab = current_tab[0][0]
        sv[current_tab].background_color = 'white'
    c.execute('''SELECT url FROM files WHERE name = ?''', (button_title,))
    path = c.fetchone()
    path = path[0]
    if not os.path.isfile(path):
        console.hud_alert('The file for this tab has been moved, renamed, or deleted. the tab will now be removed.', icon = 'error', duration = 3)
        marker = sender.y
        view.remove_subview(sender)
        c.execute('''delete from files where name = ?''', (button_title,))
        global count
        count -= 1
        def move():
            for i in range(len(sv.subviews)):
                if sv.subviews[i].y > marker:
                    sv.subviews[i].y -= tab_width*1.05
        ui.animate(move, duration = 0.3)
        conn.commit()
        check_tab()
    else:
        editor.open_file(path)
        sender.background_color = 'orange'
    conn.close()




view = ui.load_view('Tabs')
sv=view['scrollview1']
add_button = sv['add_button']
remove = sv['remove']
edit = sv['edit']

# Create database and table on first run and make tabs for all files in database on start
first_time = False
current_path = editor.get_path()
if not os.path.isfile(tabdb):
    first_time = True
conn = sql.connect(tabdb)
conn.text_factory = str
c = conn.cursor()
if first_time == True:
    c.execute('''CREATE TABLE files (name text, url text)''')
q = c.execute('''SELECT name FROM files''')
open_tabs = q.fetchall()
conn.close()

for i in range(len(open_tabs)):
    add_new_button(open_tabs[i][0])

view.present('sidebar', hide_title_bar = True)
check_tab()

import clipboard
clipboard.set(editor.get_path())
	
def tabs():
    view.present('sidebar',hide_title_bar = True)

import curses
import sys
from curses.textpad import rectangle, Textbox
import os
from time import sleep
import random
from textwrap import wrap
import json

def cursestransition(stdscr,func_to_call,args=(),type=0):
    block = "█"
    mx,my = os.get_terminal_size()
    if type == 0:
        
        for y in range(my-1):
            stdscr.addstr(y,0,block*(mx-1))
            stdscr.refresh()
            sleep(0.01)
        for y in range(my-1):
            stdscr.addstr(y,0," "*(mx-1))
            stdscr.refresh()
            sleep(0.01)
    elif type == 1:
        _grid = [(x,y) for y in range(my-1) for x in range(mx-1)]
        while _grid:
            for i in range(round(((my*mx)/(24*80))*20)):# Fixing slow transitions on HD screens
                try:
                    pk = random.choice(_grid)
                    _grid.pop(_grid.index(pk))
                    stdscr.addstr(pk[1],pk[0],block)
                    stdscr.refresh()
                except:
                    break
            sleep(0.01)
        _grid = [(x,y) for y in range(my-1) for x in range(mx-1)]
        while _grid:
            for i in range(round(((my*mx)/(24*80))*20)):
                try:
                    pk = random.choice(_grid)
                    _grid.pop(_grid.index(pk))
                    stdscr.addstr(pk[1],pk[0]," ")
                    stdscr.refresh()
                except:
                    break
            sleep(0.01)
    func_to_call(*args)

def donothing():
    pass

def displaymsg(stdscr,message: list):
    stdscr.clear()
    x,y = os.get_terminal_size()
    message = [m[0:x-5] for m in message]#Limiting characters
    maxs = max([len(s) for s in message])
    rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+2, x//2+(maxs//2+1)+1)
    stdscr.addstr(0,0,"Message: ")
    mi = -(len(message)/2)
    
    for msgl in message:
        mi += 1
        stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl)
    stdscr.addstr(y-2,0,"Press any key to dismiss this message")
    stdscr.refresh()
    stdscr.getch()
    stdscr.erase()

def cursesinput(stdscr,prompt: str):
    x,y = os.get_terminal_size()
    stdscr.erase()
    stdscr.addstr(0, 0, f"{prompt} (hit Enter to send)")

    editwin = curses.newwin(1,x-2, 2,1)
    rectangle(stdscr, 1,0, 3, x-1)
    stdscr.refresh()

    box = Textbox(editwin)

    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    message = box.gather()
    return message

def updateappdata():
    global LIBRARY
    global APPDATA
    global APPDATADIR
    APPDATA["library"] = LIBRARY
    with open(APPDATADIR,"w+") as f:
        f.write(json.dumps(APPDATA))

def add2library(name):
    global LIBRARY
    LIBRARY.append(name)
    updateappdata()

def read_book(stdscr,filename: str):
    global LIBRARY
    try:
        with open(filename) as f:
            data = f.read()
    except (PermissionError, OSError, FileNotFoundError) as e:
        displaymsg(stdscr,["Failed to open book",filename,str(e)])
        return 1
    try:
        data = "\n".join([ln for ln in data.split("\n") if ln.replace(" ","") != ""])#Removing empty lines
        config = data.split("\n%startdata\n")[0]
        book = data.split("\n%startdata\n")[1]
        config = {st.split("=")[0].strip():st.split("=")[1].strip() for st in config.split("\n")}
        stdscr.clear()
        while True:
            x,y = os.get_terminal_size()
            message = [config["title"],f"By {config['publisher']}",f"Published {config['date']}"]
            maxs = max([len(s) for s in message])
            rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+2, x//2+(maxs//2+1)+1)
            mi = -(len(message)/2)
            message = [m[0:x-4] for m in message]#Limiting characters
            for msgl in message:
                mi += 1
                stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl)
            stdscr.addstr(y-2,0,"Press enter to begin reading.")
            stdscr.refresh()
            __c = stdscr.getch()
            
            if __c == curses.KEY_ENTER or __c == 10 or __c == 13:
                break
            stdscr.erase()
    except Exception as e:
        displaymsg(stdscr,["Book Init Error",filename,str(e)])
        return 1
    if filename not in LIBRARY:
        stdscr.erase()
        if askyesno(stdscr,"You have not read this book before. Do you want to add it to your library?"):
            add2library(filename)
    cursestransition(stdscr,donothing,type=1)
    stdscr.erase()
    stdscr.addstr(0,0,f"Loading {config['title']}")
    stdscr.refresh()
    x,y = os.get_terminal_size()
    book = [d for d in book.splitlines() if d[0] != "#" and d.replace(" ","") != ""]#Removing comments and empty lines
    
    linc = 0
    chapregister = {}
    validchars = ["#","$","%","+","-","@"]
    recoverdoc = None
    #Validating syntax
    for bline in book:
        linc += 1
        if bline[0] not in validchars:
            if recoverdoc is None:
                displaymsg(stdscr,["Syntax error in",filename,f"Invalid character on line {linc}","\""+bline+"\"","Press any key to see options"])
                _rec = displayops(stdscr,["Yes (once)","No","Yes to all","No to all"],"Would you like to recover this document?")
                if _rec == 0:
                    str(list(bline).insert(0,"+"))
                elif _rec == 2:
                    recoverdoc = True
                elif _rec == 3:
                    recoverdoc = False
            elif recoverdoc:
                str(list(bline).insert(0,"+"))
        if len(bline) > 9 and bline[0:8] == "$register":
            chapregister[" ".join(bline.split(" ")[1:])] = linc
    linc = 0
    textlist = []
    chapregister = []
    activefg = 8
    for bline in book:
        if bline[0] == "+":
            if bline[1:] == "":

                textlist.append({"data":bline[1:],"cen":False,"cl":activefg,"appendr":False})
            else:
                _brline = wrap(bline[1:],x-3)
                for _br in _brline:
                    textlist.append({"data":_br,"cen":False,"cl":activefg,"appendr":False})
        elif bline[0:2] == "--":
            textlist.append({"data":bline[2:],"cen":True,"cl":activefg,"appendr":False})
        elif bline.strip() == "%pagebreak":
            textlist.append({"data":"","special":"break"})
        elif bline[0] == "$":
            if bline[1:3].upper() == "FG":
                newfg = bline[4:]
                if newfg.lower() == "reset":
                    activefg = 8
                    continue
                try:
                    activefg = int(newfg)
                except:
                    displaymsg(stdscr,["Syntax Error: Invalid colour"])
            elif bline[1:9] == "register":
                textlist.append({"data":bline[10:],"special":"putchapter"})#Telling interpreter to register a new chapter
            linc -= 1
        elif bline[0] == "@":
            textlist.append({"data":bline[1:],"cen":False,"cl":activefg,"appendr":True})#New entry for text but telling interpreter to remove formatting
        linc += 1
    linc = 0
    stdscr.erase()
    brokenpage = False
    #Calculating pagelist
    pagelist = []
    #print(textlist)
    page = 0
    lpage = 0
    x,y = os.get_terminal_size()
    validrlines = y - 6
    activeopage = []
    for instruction in textlist:
        
        if "special" in instruction.keys():
            if instruction["special"] == "break":
                pagelist.append(activeopage)#Early break of page
                page += 1
                lpage = 0
                activeopage = []
            elif instruction["special"] == "putchapter":
                chapregister.append((page,instruction["data"]))#Tuple in structure of (page,name)
                continue#DO NOT increment local page
        else:
            activeopage.append(instruction)
        lpage += 1
        if lpage == validrlines:
            lpage = 0
            page += 1
            pagelist.append(activeopage)
            activeopage = []
    del lpage
    del textlist#Freeing up memory
    page = 0
   
    #print(pagelist)
    #print(chapregister)
    #input()
    while True:
        x,y = os.get_terminal_size()
        validrlines = y - 6
        llinc = 0
        
        #Iterate through textlist
        for t in pagelist[page]:
            if t == "":
                continue
            else:
                if not t["cen"]:
                    if t["appendr"]:
                        stdscr.addstr(llinc+2-1,len(pagelist[page][llinc-1+linc]["data"]),t["data"],curses.color_pair(t["cl"]))
                        llinc += 1
                    else:
                        _brdata = wrap(t["data"],x-3)
                        if len(_brdata) == 0:
                            llinc += 1
                        for br in _brdata:
                            stdscr.addstr(llinc+2,1,br,curses.color_pair(t["cl"]))
                            llinc += 1
                elif t["cen"]:
                    _brdata = wrap(t["data"],x-3)
                    if len(_brdata) == 0:
                            llinc += 1
                    for br in _brdata:
                        stdscr.addstr(llinc+2,x//2-(len(br)//2),br,curses.color_pair(t["cl"]))
                        llinc += 1
            if llinc > validrlines:
                break
            #llinc += 1
        stdscr.addstr(0,0,f"Reading {config['title']} by {config['publisher']}")
        rectangle(stdscr,1,0,y-2,x-1)
        stdscr.addstr(y-1,0,f"Page: {page+1}/{len(pagelist)} ({round((page+1)/len(pagelist)*100,2)}%)")#+1 for user friendliness
        stdscr.refresh()
        ch = stdscr.getch()
        if ch == curses.KEY_LEFT and page> 0:
            page -= 1
        elif ch == curses.KEY_RIGHT and page < len(pagelist)-1:
            page += 1
        elif ch == curses.KEY_BACKSPACE:
            stdscr.erase()
            return
        elif ch == 103:#g
            if len(chapregister) > 0:
                stdscr.erase()
                gtc = displayops(stdscr,[f"{c[1]} (Page {c[0]+1})" for c in chapregister],"Please choose a chapter")
                page = gtc
            else:
                displaymsg(stdscr,["this book has no chapters."])
        stdscr.erase()

def displayops(stdscr,options: list,title="Please choose an option") -> int:
    mx, my = os.get_terminal_size()
    selected = 0
    options = [l[0:mx-3] for l in options][0:my-5]
    maxlen = max([len(l) for l in options])
    stdscr.addstr(0,0,title[0:mx-1])
    while True:
        stdscr.addstr(0,0,title[0:mx-1])
        mx, my = os.get_terminal_size()
        options = [l[0:mx-3] for l in options][0:my-5]
        maxlen = max([len(l) for l in options])
        rectangle(stdscr,1,0,2+len(options),maxlen+2)
        oi = -1
        for o in options:
            oi += 1
            if oi == selected:
                stdscr.addstr(oi+2,1,o,curses.color_pair(14))
            else:
                stdscr.addstr(oi+2,1,o)
        stdscr.addstr(len(options)+4,0,"Please choose an option with the arrow keys then press enter."[0:mx-1])
        stdscr.refresh()
        _ch = stdscr.getch()
        if _ch == curses.KEY_ENTER or _ch == 10 or _ch == 13:
            return selected
        elif _ch == curses.KEY_UP and selected > 0:
            selected -= 1
        elif _ch == curses.KEY_DOWN and selected < len(options)-1:
            selected += 1
        stdscr.erase()

def askyesno(stdscr,title: str) -> int:
    result = displayops(stdscr,["Yes","No"],title)
    if result == 0:
        return True
    else:
        return False

def loadlibrary(stdscr,library):
    if len(library) == 0:
        displaymsg(stdscr,["You have no books in your library"])

def main(stdscr):
    global LIBRARY
    global APPDATA
    global APPDATADIR
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)
    APPDATADIR = os.path.expanduser("~/.local/share/teleread.json")
    if not os.path.isfile(APPDATADIR):
        with open(APPDATADIR,"w+") as f:
            f.write(json.dumps({"library":[]}))
            APPDATA = {}
            LIBRARY = []
    else:
        with open(APPDATADIR) as f:
            APPDATA = json.load(f)
            LIBRARY = APPDATA["library"]
    while True:
        op = displayops(stdscr,["Read Book","View Library","Add book to library","Quit"],"Teleread 0.2")
        if op == 3:
            cursestransition(stdscr,sys.exit,type=0)
        elif op == 0:
            #cursestransition(stdscr,read_book,(stdscr,cursesinput(stdscr,"What is the file path of the book you want to read?").strip()),1)
            read_book(stdscr,cursesinput(stdscr,"What is the file path of the book you want to read?").strip())
        elif op == 2:
            stdscr.erase()
            e = cursesinput(stdscr,"What book do you want to add to your library")
            if os.path.isfile(e):
                add2library(e)
            else:
                displaymsg(stdscr,["Not a book",e])
        elif op ==1:
            stdscr.erase()
            opl = []
            binc = 0
            for book in LIBRARY:
                if os.path.isfile(book):
                    try:
                        with open(book) as g:
                            _data = g.read()
                            data = "\n".join([ln for ln in _data.split("\n") if ln.replace(" ","") != ""])#Removing empty lines
                            config = data.split("\n%startdata\n")[0]
                            config = {st.split("=")[0].strip():st.split("=")[1].strip() for st in config.split("\n")}
                            opl.append(f"{config['title']} by {config['publisher']}")
                    except Exception as e:
                        opl.append(book+" (ERROR!)"+str(e))
                else:
                    opl.append(book+" (MISSING!)")
                binc += 1
            while True:
                stdscr.erase()
                rop = displayops(stdscr,opl,"Please choose a book")
                read_book(stdscr,LIBRARY[rop])

curses.wrapper(main)
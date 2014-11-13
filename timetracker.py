import tkinter as tk
from tkinter import ttk, messagebox
from multiprocessing import Queue, Process
import time, os, glob

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)#, bg="gray90")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(self.canvas)
        interior_id = self.canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)

        return

class multiprocessor():
    def __init__(self, maxQueueSize):
        self.queue=Queue(maxQueueSize)
        self.processes=[]
    
    def createProcess(self, target, args=(),  daemon=1):
        self.processes.append(Process(target=target, args=args))
        self.processes[-1].daemon=daemon
    
    def checkQueue(self):
        try:
            content=self.queue.get(0)
            return content
        except Exception:
            pass

class app:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Time Tracker")
        self.root.wm_resizable(0, 0)
        
        self.initVariables()
        
        self.createGUI()
        #self.clockProcess=Process(name="clock",target=self.clockTick, args=(q,))
        #self.clockProcess.daemon=True
        self.root.after(100,self.iterateClock)

    def initVariables(self):
        self.selectedRow=-1
        
        self.taskEntryWindow = tk.Toplevel()
        self.taskEntryWindow.destroy()
        
        self.path=os.path.expanduser('~')+"/Documents/timetracking"
        self.tasks_path=self.path+"/tasks"
        
        self.table_options = {"count": 4,
           "names" : ("#", "Task Name", "Time Started", "Time Elapsed"),
           "width" : (3,30,25,20),
           }
        
        self.color_table={
        "regular" : "gray90",
        "off_regular" : "gray99",
        "running" : "DarkOliveGreen2",
        "off_running" : "DarkOliveGreen1",
        "paused" : "LightSkyBlue1",
        "off_paused" : "SkyBlue1",
        "selected" : "DarkSlateGray2",
        "off_selected" : "DarkSlateGray1"
        }
    
    def loadFile(self):
        pass
    
    def saveFile(self):
        pass
    
    def createTableTemplateGUI(self, master):
        ttk.Separator(master,orient=tk.VERTICAL).grid(column=0,row=1,sticky="N S")
        column_count=1
        for i in range(self.table_options["count"]):
            tk.Label(master, text=self.table_options["names"][i], width=self.table_options["width"][i]).grid(column=column_count,row=1)
            ttk.Separator(master,orient=tk.VERTICAL).grid(column=column_count+1,row=1,sticky="N S")
            column_count+=2
        else:
            ttk.Separator(master,orient=tk.HORIZONTAL).grid(column=0,row=0,columnspan=column_count,sticky="E W")
            ttk.Separator(master,orient=tk.HORIZONTAL).grid(column=0,row=2,columnspan=column_count,sticky="E W")
        
    def createGUI(self):
        self.rows=[]
        
        masterFrame=tk.Frame(self.root, padx=4, pady=4)
        masterFrame.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)
        
        controlsFrame = tk.LabelFrame(masterFrame, text="Controls", padx=2, pady=2)
        controlsFrame.pack(side=tk.LEFT,fill=tk.BOTH)
        
        tk.Button(controlsFrame,text="New Task", command=lambda: self.createTaskEntryWindow()).pack(side=tk.TOP, fill=tk.BOTH)
        tk.Button(controlsFrame,text="Start Task", command=lambda: self.startTask(self.selectedRow)).pack(side=tk.TOP, fill=tk.BOTH)
        tk.Button(controlsFrame,text="End Task").pack(side=tk.TOP, fill=tk.BOTH)
        tk.Button(controlsFrame,text="Pause Task").pack(side=tk.TOP, fill=tk.BOTH)
        tk.Button(controlsFrame,text="Delete Task",command=lambda: self.deleteTask(self.selectedRow)).pack(side=tk.TOP, fill=tk.BOTH)
        
        viewFrame = tk.LabelFrame(masterFrame, text="Tasks", padx=2, pady=2)
        viewFrame.pack(side=tk.LEFT, fill=tk.BOTH)
        
        self.tableFrame=VerticalScrolledFrame(viewFrame)
        self.tableFrame.pack(side=tk.LEFT,fill=tk.BOTH)        
        
        self.createTableTemplateGUI(self.tableFrame.interior)
        
    def iterateClock(self):
            self.timeStepAllTasks()
            self.root.after(1000,self.iterateClock)
        
    def addTask(self, master, name, running=False, fromfile=False):
        rowNum=len(self.rows)+1
        num=tk.IntVar()#.set(rowNum)
        taskName=tk.StringVar()#.set(name)
        startTime=tk.StringVar()#.set(getTimeLong())
        timeElapsed=tk.StringVar()
        task_running=tk.IntVar()
        task_running.set(running)
        
        if (rowNum % 2) == 0:
            if running==False:
                bg = self.color_table["regular"]
            else:
                bg = self.color_table["running"]
        else:
            if running==False:
                bg = self.color_table["off_regular"]
            else:
                bg = self.color_table["off_running"]
        
        a=tk.Entry(master,width=self.table_options["width"][0]-1, textvariable=num, state=tk.DISABLED,
                   disabledforeground="black", disabledbackground=bg, font=(None, 12))
        a.grid(column=1,row=rowNum+2)
        a.bind("<Button-1>",lambda x: self.selectRow(num.get()-1))
        b=tk.Entry(master,width=self.table_options["width"][1]-1, textvariable=taskName, state=tk.DISABLED,
                   disabledforeground="black", disabledbackground=bg, font=(None, 12))
        b.grid(column=3,row=rowNum+2)
        b.bind("<Button-1>",lambda x: self.selectRow(num.get()-1))
        c=tk.Entry(master,width=self.table_options["width"][2]-1, textvariable=startTime, state=tk.DISABLED,
                   disabledforeground="black", disabledbackground=bg, font=(None, 12))
        c.grid(column=5,row=rowNum+2)
        c.bind("<Button-1>",lambda x: self.selectRow(num.get()-1))
        d=tk.Entry(master,width=self.table_options["width"][3]-1, textvariable=timeElapsed, state=tk.DISABLED,
                   disabledforeground="black", disabledbackground=bg, font=(None, 12))
        d.grid(column=7,row=rowNum+2)
        d.bind("<Button-1>",lambda x: self.selectRow(num.get()-1))
        
        num.set(rowNum)
        taskName.set(name)
        if running==True:
            startTime.set(getTimeLong())
        else:
            startTime.set("Not yet started")
        
        self.rows.append(((num, taskName, startTime, timeElapsed),(a,b,c,d),task_running))
        
        if fromfile==False:
            if not os.path.exists(self.tasks_path):
                os.makedirs(self.tasks_path)
            file = open(self.tasks_path+"/"+str(rowNum)+".txt", 'w')
            file.write("TaskName:"+name+"\n")
            if running==True:
                file.write("StartTime:"+str(round(time.time()))+"\n")
            else:
                file.write("StartTime:NONE\n")
            
        print("Row added, ID " + str(len(self.rows)))
    
    def deleteTask(self, index):
        if self.selectedRow!=-1:
            try:
                for i in self.rows[index][1]:
                    i.destroy()
                
                if os.path.isfile(self.tasks_path+"/"+str(self.rows[index][0][0].get())+".txt"):
                    os.remove(self.tasks_path+"/"+str(self.rows[index][0][0].get())+".txt")
                
                del(self.rows[index])
                
                self.selectedRow=-1
                print("Row deleted, ID " + str(index))
                try:
                    for i in self.rows[index:]:
                        file=self.tasks_path+"/"+str(i[0][0].get())+".txt"
                        if os.path.isfile(file):
                            os.rename(file, self.tasks_path+"/"+str((i[0][0].get()-1))+".txt")
                        
                        i[0][0].set(i[0][0].get()-1)
                        for j in i[1]:
                            j.grid(row=2+i[0][0].get())
                            #0 = regular, 1=off
                            if i[0][0].get()%2==0:
                                offset = ""
                            else:
                                offset = "off_"
                        
                            if i[0][2].get()==0:
                                j["disabledbackground"]=self.color_table[offset+"regular"]
                            elif i[0][2].get()==1:
                                j["disabledbackground"]=self.color_table[offset+"running"]
                            elif i[0][2].get()==2:
                                j["disabledbackground"]=self.color_table[offset+"paused"]
                            
                except IndexError:
                    print("Deleted final element")
            except IndexError:
                print("Theres nothing in the array to delete")
        else:
            print("No rows selected")
    
    def startTask(self, index):
        if self.selectedRow!=-1:
            if self.rows[index][2].get()!=1:
                if self.rows[index][2].get()==0:
                    self.rows[index][0][2].set(getTimeLong())
                    self.rows[index][2].set(1)
                    self.selectedRow=-1
                    for i in self.rows[index][1]:
                        if self.rows[index][0][0].get()%2==0:
                            i["disabledbackground"]=self.color_table["running"]
                        else:
                            i["disabledbackground"]=self.color_table["off_running"]
        else:
            print("No rows selected")
    
    def selectRow(self, index):
        if self.selectedRow!=-1:
            if self.rows[self.selectedRow][0][0].get()%2 == 0:
                offset=""
            else:
                offset="off_"
            for i in self.rows[self.selectedRow][1]:
                if self.rows[self.selectedRow][2].get()==0:
                    i["disabledbackground"]=self.color_table[offset+"regular"]
                elif self.rows[self.selectedRow][2].get()==1:
                    i["disabledbackground"]=self.color_table[offset+"running"]
                elif self.rows[self.selectedRow][2].get()==2:
                    i["disabledbackground"]=self.color_table[offset+"paused"]
        
        self.selectedRow=index
        if self.selectedRow!=-1:
            if self.rows[self.selectedRow][0][0].get()%2 == 0:
                offset=""
            else:
                offset="off_"
            for i in self.rows[self.selectedRow][1]:
                i["disabledbackground"]=self.color_table[offset+"selected"]
    
    def createTaskEntryWindow(self):
        if self.taskEntryWindow.winfo_exists()==True:
            self.taskEntryWindow.destroy()
        self.taskEntryWindow=tk.Toplevel()
        self.taskEntryWindow.title("Enter New Task Name")
        
        frame = tk.Frame(self.taskEntryWindow,padx=3, pady=3,relief=tk.RIDGE)
        frame.pack(side=tk.LEFT,expand=1,fill=tk.BOTH)
        
        entryVar=tk.StringVar()
        e = tk.Entry(frame,textvariable=entryVar)
        e.grid(column=0,row=0,columnspan=3)
        e.focus()
        e.bind("<Return>",lambda x: self.destroyTaskEntryWindow(entryVar.get(), 0))
        
        tk.Button(frame, text="Create",command=lambda: self.destroyTaskEntryWindow(entryVar.get(), 0)).grid(column=0,row=1)
        tk.Button(frame, text="Create and Start",command=lambda: self.destroyTaskEntryWindow(entryVar.get(), 1)).grid(column=1,row=1)
        tk.Button(frame, text="Cancel", command=lambda: self.taskEntryWindow.destroy()).grid(column=2,row=1)
    
    def destroyTaskEntryWindow(self, name, running):
        self.addTask(self.tableFrame.interior, name, running)
        self.taskEntryWindow.destroy()
    
    def clockTick(self, event):
        while(1):
            self.timeStepAllTasks()
            print("tick")
            time.sleep(1)

    def timeStepAllTasks(self):
        if os.path.isdir(self.tasks_path)==True:
            tasks=glob.glob(self.tasks_path+"/*.txt")
            if len(self.rows)>0:
                for i in tasks:
                    file=open(i,"r")
                    taskNum=-1+int(i.split("/")[-1].split(".")[0])
                    pauseTime=0
                    for i in file:
                        try:
                            key=i.split(":")[0]
                            val=i.split(":")[1][:-1]
                            print(key + " _ " + val)
                        except IndexError:
                            pass
                    
                    if key=="StartTime":
                        if val!="NONE":
                            startTime=int(val)
                        else:
                            startTime=-1
                    
                    if key=="Pause":
                        pause1=val.split("-")[0]
                        pause2=val.split("-")[1]
                        if pause2!="PAUSE":
                            pauseTime+=(int(pause2)-int(pause1))
                else:
                    if startTime!=-1:
                        print("Updating time value for index %s" % (taskNum))
                        try:
                            timeDiff=time.ctime(time.time()-(pauseTime+startTime))
                            self.rows[taskNum][0][3].set(timeDiff)
                        except Exception as error:
                            print(error)
            else:
                print("No tasks found")
        else:
            print("No taskdir found")
                    
def getTimeLong():
    return time.strftime("%a, %b %d %Y %H:%M%p ", time.localtime())

def monitorServer(event):
    #fpath = os.path.expanduser('~')+"/Documents/rsc_init.txt"
    oemdb_location = "/Users/cgi-28/Desktop/dev/oemdb_main"
    while (1):
        if os.path.isdir(oemdb_location):
            users_dir=oemdb_location+"/oemdb_users"
            if os.path.isdir(users_dir):
                u=glob.glob(users_dir+"/*")
                if (len(u)>0):
                    users=[]
                    for i in u:
                        if os.path.isdir(i):
                            users.append(str(i).split("/")[-1])
                    print(users)
        else:
            print("File check failed at " + getTimeLong())
        
        time.sleep(10)

            
if __name__=="__main__":
    #q=Queue()
    #q.cancel_join_thread()
    application=app()
    #application.clockProcess.start()
    application.root.mainloop()

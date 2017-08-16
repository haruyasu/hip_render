''' 
HIP Render v1.0
'''
import os, ttk, platform, time
from Tkinter import *
from tkFileDialog import askopenfilename
from threading import Thread

errorMessages = {0: "No Error", 1: "Invalid start frame", 2: "Invalid end frame", 6: "No HIP file selected",
                 7: "Invalid Step number"}
errorNumber = 0
startFrame = 0
endFrame = 0
hipFile = ""
options = ["-"]
options_res = ["1920 x 1080", "1280 x 720", "854 x 480", "640 x 360", "426 x 240"]
currentStartFrame = 0
currentEndFrame = 0
currentSteps = 0
currentMantra = ""
currentResolution = ""
osName = platform.system()

if osName == "Windows":
    command_hscript = "hscript "
    defaultDir = "C:/"
else:
    command_hscript = "/opt/hfs16.0.633/bin/hscript "
    defaultDir = "/home"


def App():
    def onUnexpectedClosing():
        root.destroy()

    def fileWindowDialog():
        global defaultDir, startFrame, endFrame, hipFile, options
        options = []
        hipFile = askopenfilename(initialdir=defaultDir, title="Select an HIP file to render", multiple=False,
                                  filetypes=[("hiplc", ".hiplc"), ("hipnc", ".hipnc"), ("hip", ".hip")])

        print str(hipFile)

        if hipFile != "":
            filePathEntry.delete(0, END)
            filePathEntry.insert(0, hipFile)
            defaultDir = hipFile.rpartition("/")[0]

            with open("render.cmd", "w") as file:
                file.write("mread " + hipFile + "\n")
                file.write("opls /out\n")
                file.write("quit")

            os.system(command_hscript + "render.cmd > output.txt")

            with open("output.txt") as file:
                my_list = file.readlines()
                my_list = [x.strip() for x in my_list]

            for rows in my_list:
                if rows != "hbatch Version 16.0.633 (Compiled on Jun  8 2017)":
                    options.append(rows)

            startFrame = 1
            endFrame = 3
            updateInterface(startFrame, endFrame)
            updateOptionMenu()

            os.remove("output.txt")
            os.remove("render.cmd")

    def updateInterface(start, end):
        startFrameEntry.delete(0, END)
        startFrameEntry.insert(0, str(start))
        endFrameEntry.delete(0, END)
        endFrameEntry.insert(0, str(end))

    def updateOptionMenu():
        menu = mantraEntry["menu"]
        menu.delete(0, "end")
        for string in options:
            menu.add_command(label=string, command=lambda value=string: mantraName.set(value))
        mantraName.set(options[0])

    def optionSelect(*args):
        print mantraName.get()

    def optionResSelect(*args):
        print resolutionName.get()

    def getResolution():
        res = resolutionName.get()
        if res == "1920 x 1080":
            current_res = "1920 1080"
        elif res == "1280 x 720":
            current_res = "1280 720"
        elif res == "854 x 480":
            current_res = "854 480"
        elif res == "640 x 360":
            current_res = "640 360"
        elif res == "426 x 240":
            current_res = "426 240"
        return current_res

    def checkFrame():
        global errorNumber, currentStartFrame, currentEndFrame, currentSteps, currentMantra, currentResolution
        errorNumber = 0

        currentStartFrame = startFrameEntry.get()
        currentEndFrame = endFrameEntry.get()
        currentSteps = stepsEntry.get()
        currentMantra = mantraName.get()
        currentResolution = getResolution()

        ### File path
        if filePathEntry.get() == "":
            errorNumber = 6
        else:
            try:
                #### Start Frame
                currentStartFrame = startFrameEntry.get()
                current_start = int(currentStartFrame)
                #### End Frame
                currentEndFrame = endFrameEntry.get()
                current_end = int(currentEndFrame)

                try:
                    if current_end < current_start:
                        errorNumber = 2
                    else:
                        #### Steps
                        currentSteps = stepsEntry.get()
                        try:
                            current_steps = int(currentSteps)
                            if current_steps < 0 or current_steps > current_end:
                                errorNumber = 7
                        except:
                            errorNumber = 7
                #### End Frame Except
                except:
                    errorNumber = 2
            #### Start Frame Except
            except:
                errorNumber = 1

    def renderFile():
        with open("render.cmd", "w") as file:
            file.write("mread " + hipFile + "\n")
            file.write("render -V -R " + str(currentResolution) + " -f " + str(currentStartFrame) + " " + str(
                currentEndFrame) + " -i " + str(currentSteps) + " " + currentMantra + "\n")
            file.write("quit")

        # time.sleep(5)
        os.system(command_hscript + "render.cmd")

        totalProgressSteps = 100
        progressCount = 0
        progressCount += totalProgressSteps
        progressVar.set(progressCount)
        Tk.update(root)

        print "Render finished"
        finish_time()
        os.remove("render.cmd")

    def submit_time():
        ##### Time #####
        currentTime = str(time.strftime("%Y/%m/%d")) + " at " + str(time.strftime("%H:%M:%S"))
        submitTime = "Submit time: {0}".format(currentTime)
        submitTimeLabel = Label(root, text=submitTime, bg=bgColor, fg=textColor)
        submitTimeLabel.place(x=300, y=55)

        ##### Render in Progress #####
        renderMessage = "Render in progress!"
        renderInProgress = Label(root, text=renderMessage, bg=bgColor, fg=textColor, font=("Arial", 20, "bold"))
        renderInProgress.place(x=270, y=140)

    def finish_time():
        ##### Time #####
        currentTime = str(time.strftime("%Y/%m/%d")) + " at " + str(time.strftime("%H:%M:%S"))
        finishTime = "  Finish time: {0}".format(currentTime)
        finishTimeLabel = Label(root, text=finishTime, bg=bgColor, fg=textColor)
        finishTimeLabel.place(x=300, y=85)

    def render():
        print "clicked render"
        checkFrame()
        if errorNumber == 0:
            submit_time()
            p = Thread(name='render', target=renderFile)
            p.start()
            progressVar.set(0)
            Tk.update(root)
        else:
            print errorMessages[errorNumber]

    def cancel():
        print "clicked cancel"
        os.system("taskkill /F /IM mantra.exe")

    ##### Colors #####

    bgColor = "#333333"
    filePathColor = "#181818"
    textColor = "#c6c6c6"
    bordersColor = "#242424"
    selectedBordersColor = "#222222"
    buttonsColor = "#222222"
    selectedButtonColor = "#383838"

    ##### Main Window #####
    root = Tk()
    root.config(bg=bgColor)
    root.title("v1.0 HIP Render")
    root.resizable(width=False, height=False)

    sizeX = 580
    sizeY = 340
    screenW = (root.winfo_screenwidth() / 2) - (sizeX / 2)
    screenH = (root.winfo_screenheight() / 2) - (sizeY / 2)
    root.geometry("{0}x{1}+{2}+{3}".format(sizeX, sizeY, screenW, screenH))

    yPos = 15
    yOffset = 30

    if osName == "Windows":
        filePathEntryWidth = 58
        renderButtonX = 95
    else:
        filePathEntryWidth = 45
        renderButtonX = 112

    ##### Load File #####
    filePathLabel = Label(root, text="HIP File", bg=bgColor, fg=textColor)
    filePathLabel.place(x=36, y=yPos)

    filePathEntry = Entry(root, width=filePathEntryWidth, bg=filePathColor, fg=textColor,
                          highlightbackground=bordersColor, highlightcolor=selectedBordersColor, highlightthickness=2)
    filePathEntry.place(x=95, y=yPos)

    filePathButton = Button(text="Browse", bg=buttonsColor, fg=textColor, activebackground=selectedButtonColor,
                            activeforeground=textColor, width=7, highlightbackground=bordersColor,
                            highlightcolor=selectedBordersColor, highlightthickness=1, relief="solid",
                            command=fileWindowDialog)  # flat, groove, raised, ridge, solid, or sunken
    filePathButton.place(x=480, y=yPos)

    yPos += yOffset

    ##### Start Frame #####
    startFrameLabel = Label(root, text="Start Frame", bg=bgColor, fg=textColor)
    startFrameLabel.place(x=8, y=yPos)

    startFrameEntry = Entry(root, width=5, bg=filePathColor, fg=textColor, disabledforeground=textColor,
                            disabledbackground=filePathColor, highlightbackground=bordersColor,
                            highlightcolor=selectedBordersColor, highlightthickness=2, justify="center")
    startFrameEntry.place(x=95, y=yPos)

    yPos += yOffset

    ##### End Frame #####
    endFrameLabel = Label(root, text="End Frame", bg=bgColor, fg=textColor)
    endFrameLabel.place(x=14, y=yPos)

    endFrameEntry = Entry(root, width=5, bg=filePathColor, fg=textColor, disabledforeground=textColor,
                          disabledbackground=filePathColor, highlightbackground=bordersColor,
                          highlightcolor=selectedBordersColor, highlightthickness=2, justify="center")
    endFrameEntry.place(x=95, y=yPos)

    yPos += yOffset

    ##### Steps #####
    stepsFrameLabel = Label(root, text="Steps", bg=bgColor, fg=textColor)
    stepsFrameLabel.place(x=47, y=yPos)

    stepsEntry = Entry(root, width=5, bg=filePathColor, fg=textColor, disabledforeground=textColor,
                       disabledbackground=filePathColor, highlightbackground=bordersColor,
                       highlightcolor=selectedBordersColor, highlightthickness=2, justify="center")
    stepsEntry.place(x=95, y=yPos)
    stepsEntry.insert(0, "1")

    yPos += yOffset

    ##### Mantra #####
    mantraLabel = Label(root, text="Rop", bg=bgColor, fg=textColor)
    mantraLabel.place(x=50, y=yPos)

    mantraName = StringVar(root)
    mantraName.set(options[0])
    mantraName.trace('w', optionSelect)
    mantraEntry = OptionMenu(root, mantraName, *options)
    mantraEntry.config(width=10, bg=filePathColor, fg=textColor, activebackground=filePathColor,
                       activeforeground=textColor, disabledforeground=textColor, highlightbackground=bordersColor,
                       highlightcolor=selectedBordersColor, highlightthickness=2, justify="center")
    mantraEntry.place(x=95, y=yPos)

    yPos += yOffset + 10

    ##### Resolution #####
    resolutionLabel = Label(root, text="Resolution", bg=bgColor, fg=textColor)
    resolutionLabel.place(x=20, y=yPos)

    resolutionName = StringVar(root)
    resolutionName.set(options_res[0])
    resolutionName.trace('w', optionResSelect)
    resolutionEntry = OptionMenu(root, resolutionName, *options_res)
    resolutionEntry.config(width=10, bg=filePathColor, fg=textColor, activebackground=filePathColor,
                           activeforeground=textColor, disabledforeground=textColor, highlightbackground=bordersColor,
                           highlightcolor=selectedBordersColor, highlightthickness=2, justify="center")
    resolutionEntry.place(x=95, y=yPos)

    yPos += yOffset + 20

    ##### Progress Bar ####
    progressVar = DoubleVar()
    progressBarWidget = ttk.Progressbar(root, variable=progressVar, orient="horizontal", mode="determinate", length=460)
    progressBarWidget.place(x=60, y=yPos)

    yPos += yOffset + 20

    ##### Render #####
    renderButton = Button(text="Render", bg=buttonsColor, fg=textColor, activebackground=selectedButtonColor,
                          activeforeground=textColor, height=2, width=25, highlightbackground=bordersColor,
                          highlightcolor=selectedBordersColor, highlightthickness=1, relief="solid", command=render)
    renderButton.place(x=renderButtonX, y=yPos)

    ##### Cancel #####
    renderButton = Button(text="Cancel", bg=buttonsColor, fg=textColor, activebackground=selectedButtonColor,
                          activeforeground=textColor, height=2, width=25, highlightbackground=bordersColor,
                          highlightcolor=selectedBordersColor, highlightthickness=1, relief="solid", command=cancel)
    renderButton.place(x=renderButtonX + 200, y=yPos)

    root.protocol("WM_DELETE_WINDOW", onUnexpectedClosing)
    root.mainloop()


if __name__ == "__main__":
    App()

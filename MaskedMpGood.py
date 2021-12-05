#   Todo -
#       main menu, Choose langages : this can control masking color, translation language target and easyocr language reader
#       implement boxSelectChatbox Location to the main menu when user doesnt want to use default location
# https://python-mss.readthedocs.io/examples.html
# https://www.codegrepper.com/code-examples/python/mss+grab+part+of+screen
from easyocr import Reader
import numpy as np
import cv2 as cv2
from PIL import ImageGrab
# https://realpython.com/pysimplegui-python/
import PySimpleGUI as sg
import time
import torch.multiprocessing as mp
from deep_translator import GoogleTranslator
import mss
# gui_queue = None
# ocr_queue = None


class GraphicalUserInterface: #rename to gameoverlayinterface
    global gui_queue
    global ocr_queue
    def __init__(self,gQueue,oQueue):
        self.gui_queue = gQueue
        self.ocr_queue = oQueue
        # global gui_queue
        # global ocr_queue
        sg.theme('DarkBlack') # give our window a spiffy set of colors

        layout = [
                [sg.Output(size=(50, 10), font=('Helvetica', '8','bold'), text_color = 'White', key = '_OUTPUT_',background_color= 'grey')],
                [sg.Button('Exit')]]#sg.Button('Start'),

        self.window = sg.Window('Chat window', layout, font=('Helvetica', ' 13','bold'),background_color='grey', default_button_element_size=(1,1), use_default_focus=False,
                    transparent_color='grey',alpha_channel=1,titlebar_background_color='black', no_titlebar=True,grab_anywhere=True,keep_on_top=True,enable_close_attempted_event=True, location=sg.user_settings_get_entry('-location-', (None, None)))

        while True:  # Event Loop
            event, values = self.window.read(timeout=10, timeout_key='timeout')#,timeout_key='timeout'timeout=500
            # self.window.KeepOnTop = True
            self.window.bring_to_front()
            # print(event, values)
            # print("test take over")
            # self.window['_OUTPUT_'].Update('')
            if event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, 'Exit'):
                # gui_queue.put('Stop')
                sg.user_settings_set_entry('-location-', self.window.current_location())  # The line of code to save the position before exiting
                break
            # if event == 'Start':
            #     # Update the "output" text element to be the value of "input" element
            #     self.window['_OUTPUT_'].update("started")
            #     begin(gui_queue, ocr_queue)
            self.printOutput()

            # print('realtest')
            # self.window.refresh()
            # self.window.TKroot.after(1000, self.printOutput)
        self.window.close()

    def printOutput(self):
        # self.window['_OUTPUT_'].Update('')
        # print(ocr_queue.get())
        outText = []
        try:
            for msg in self.ocr_queue.get(0):
                if msg[0] == r'[':
                    continue
        # https://medium.com/analytics-vidhya/how-to-translate-text-with-python-9d203139dcf5
                # print(msg)
                outText.append(msg+'\n')
            self.window['_OUTPUT_'].Update(''.join(outText))
        except:
            pass
        # self.window.refresh()
        # self.window.TKroot.after(1000, self.printOutput)


def begin(gui_queue, ocr_queue,coords):
    ocrProc = mp.Process(target=startOcr, args=(gui_queue,ocr_queue,coords))
    ocrProc.start()
    return ocrProc

def cleanup_text(text):
    # strip out non-ASCII text so we can draw the text on the image
    # using OpenCV
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()

def startOcr(gui_queue, ocr_queue, ChatCoord):
    # outputText = []
    # langs =["en"]
    # x = 560
    # y = 595
    # x2= 1310
    # y2=
    #default is currently set to dota's chat box at 1080p (560,595,1310,760)
    # workers (int, default = 0) - Number thread used in of dataloader
    # https://www.jaided.ai/easyocr/documentation/
    reader = Reader(['en'], gpu = True)
    x = ChatCoord[0]
    y = ChatCoord[1]
    w= ChatCoord[2]
    h= ChatCoord[3]
    color1 = np.asarray([235])
    color2 = np.asarray([237])
    color3 = np.asarray([255])
    color4 = np.asarray([255])
    i=1
    while True:
        # sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, 'Loading', text_color='black', transparent_color='blue', background_color='blue', time_between_frames=100)
        try:
            message = gui_queue.get_nowait()    # see if something has been posted to Queue
        except Exception as e:                     # get_nowait() will get exception when Queue is empty
            message = None                      # nothing in queue so do nothing
        if message:
            print(f'Got a queue message {message}!!!')
            break
    # while(i == 1):
        # deskimage = ImageGrab.grab()
        # image = np.array(deskimage)
        # crop_img = image[y:y2, x:x2]
        # image = crop_img

        sct = mss.mss()
        # -1 i think gets primary monitor? 0 is all and then increments to the number they identify as. for example my primary is 2
        monitor = {"top": y, "left": x, "width": w, "height": h}
        image = np.asarray(sct.grab(monitor))

        # cv2.imshow('image', image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('grey', image)

        # this one gets pure white text as seen in the spanish dota2 client
        # brightWhiteText = cv2.inRange(image, color3, color4)
        # cv2.imshow('brightWhiteText', brightWhiteText)

        # cv2.imshow('image', image)

        # This mask gets the off white text seen in the rest of dota
        mask = cv2.inRange(image, color1, color2)
        # cv2.imshow('mask', mask)

        #this blends the two
        # mask=cv2.addWeighted(mask, 1, brightWhiteText, 1 - 0.3, 0)



        # cv2.waitKey(30)


        results = reader.readtext(mask,decoder='greedy',width_ths = 1.5)#workers=4,
        # results = reader.readtext(image)
        outputText = []
        # loop over the results
        for (bbox, text, prob) in results:
            text = cleanup_text(text)
            # print(text)
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(text)
            except:
                translated = text
            outputText.append(translated)#+'\n'
        ocr_queue.put(outputText)
        time.sleep(2)
        # print(outputText)
        # i=0
    # return outputText


def main():
    global gui_queue
    global ocr_queue
    ocr_queue = mp.Queue()
    gui_queue = mp.Queue()
    # gui = GraphicalUserInterface()
    startOcr(gui_queue,ocr_queue,(560,595,500,300))
if __name__ == '__main__':
    main()

# # https://github.com/PySimpleGUI/PySimpleGUI/issues/1077
# # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Notification_Window_Multiprocessing.py
# # https://stackoverflow.com/questions/60213167/pysimplegui-how-to-make-transparent-click-through-window
# # https://github.com/PySimpleGUI/PySimpleGUI/issues/2525
# # https://docs.python.org/3/library/multiprocessing.html
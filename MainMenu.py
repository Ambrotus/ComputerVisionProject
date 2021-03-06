#  todo-
#       update and restart reader with it's new settings when ever settings are changed on the main menu via event calls
#       save new game profiles (coords from custom chatbox)
#       save and load profiles
#       save the profile as a key value pair. We can display the key as Aoe4 value :x y x2y2 or something
#       I could use the custom box tool to also have the user select the colour of the text so we can run custom threshholding mask for anything but that colour.
#       option to use custom mask or default mask?

import PySimpleGUI as sg
import MaskedMpGood as mmg
import boxSelectChatbox as bsc
import multiprocessing as mp

# from project.MaskedMpGood import startOcr
gui_queue = None
ocr_queue = None
class MainUserInterface:

    overlayOpen = False
    processorType = 'CPU'
    additionalLangs = ''
    targetLanguage = 'en'
    startedOcr = False
    ocrProcess = None
    gameOverlayProc = None

    def __init__(self):
        global gui_queue
        global ocr_queue
        self.chatLocation = None
        col2 = sg.Column([[sg.Frame('Output:',
        [[sg.Column([[sg.Output(font=('Helvetica', '8','bold'), text_color = 'Black', key = '-OUTPUT-',background_color= 'White',size=(27,21)),]],size=(200,315))]])]],pad=(0,0))

        processor_Rkeys = ['CPU', 'GPU']
        language_Rkeys = ['ch_sim','ru']
        col1 = sg.Column([
            [sg.Frame('Processor:',[ [sg.Radio(text = name, group_id = 'ProcessorRadio',enable_events=True, default = (False,True)[name == 'CPU'],key=name ,size=(10,1)) for name in processor_Rkeys],],)],
            [sg.Frame('Settings:', [[sg.Text(), sg.Column([[sg.Text('Additional Character Set:')],
                                    [sg.Radio(text = name, group_id = 'LanguageRadio',enable_events=True,key=name ,size=(10,1)) for name in language_Rkeys],
                                    # [ sg.Radio('S. Chinese', 'radio1',enable_events=True, default=True, key='-SCHINESE-', size=(10,1)),
                                    # sg.Radio('Russian', 'radio1',enable_events=True, key='-RUSSIAN-',  size=(10,1))],
                                    [sg.Text('Target Language:')],
                                    [sg.Input(key='-LANG-IN-', default_text='en', size=(27,1), disabled=True)],
                                    [sg.Text('Game Profiles:')],
                                    [sg.Multiline(key='-PROFILE-', default_text='Dota 2', size=(25,5),disabled=True)],
                                    [sg.Button('Load',disabled=True), sg.Button('Delete',disabled=True)],
                                    ], size=(220,265), pad=(0,0))]])], ], pad=(0,0))

        col3 = sg.Column([[sg.Frame('Actions:',
                                    [[sg.Column([[sg.Button('Start'), sg.Button('Stop'), sg.Button('Custom Chat Location'),sg.Button('Launch Game Overlay'), ]],
                                                size=(460,45), pad=(0,0))]])]], pad=(0,0))

        # The final layout is a simple one
        self.layout = [sg.vtop([col1, col2]),
                [col3]]

        self.window = sg.Window('In-game Chat Translator', self.layout)

        while True:
            event, values = self.window.read(timeout=10, timeout_key='timeout')
            # print(event, values)
            if event in processor_Rkeys:
                if self.startedOcr == True:
                    # with gui_queue.mutex:
                    #     gui_queue.queue.clear()
                    # gui_queue.put('Stop')
                    # self.processorSelection=[ key for key in processor_Rkeys if values[key]][0]
                    # self.ocrProcess.join()
                    # self.ocrProcess.close()
                    # print('this feature still in progress, process has been stopped. Please restart by hitting start button.')
                    # self.ocrProcess = mmg.begin(gui_queue, ocr_queue,self.chatLocation,self.processorSelection,self.additionalLangs)
                # for key in processor keys, print which every value is true
                    print([ key for key in processor_Rkeys if values[key]][0])

            if event in language_Rkeys:
                 # print([ key for key in language_Rkeys if values[key]][0])
                key = language_Rkeys[0]
                value = values[key]
                value2 = values.get(key)
                print (value,value2)

            if event == sg.WIN_CLOSED:
                gui_queue.put('Stop')
                break
            if event == 'Custom Chat Location':
                newCoords = bsc.getCoords()
                self.chatLocation = newCoords
            if event == 'Start':
                self.window['-OUTPUT-'].update("started")
                 #let mainui start the process, and then we can have a flag to pull the ocr text from it and place it in main or overlay if it's open

                #  testing launching with defaults
                if self.chatLocation == None:
                    self.chatLocation = (570, 610, 800, 150) #(377, 405, 530, 103)
                mmg.begin(gui_queue, ocr_queue,self.chatLocation)
                self.window['Start'].update(disabled=True)
                self.startedOcr = True

            if event == 'Stop':
                gui_queue.put('Stop')
                self.window['Start'].update(disabled=False)
            if event == 'Launch Game Overlay':
                self.window['-OUTPUT-'].update("Switched output to GameOverlay")
                self.overlayOpen = True
                self.window['Launch Game Overlay'].update(disabled=True)
                self.gameOverlayProc = mp.Process(target=mmg.GraphicalUserInterface, args=(gui_queue,ocr_queue))
                self.gameOverlayProc.start()
                # enable after process dead and re enable button

            self.mainPrintOutput()

        self.window.close()

    def mainPrintOutput(self):
        if not self.overlayOpen:
            outText = []
            try:
                for msg in ocr_queue.get(0):
                    if msg[0] == r'[':
                        continue
                    outText.append(msg+'\n')
                self.window['-OUTPUT-'].Update(''.join(outText))
                self.window.Refresh()
            except:
                pass


def main():
    global gui_queue
    global ocr_queue
    ocr_queue = mp.Queue()
    gui_queue = mp.Queue()
    mainGui = MainUserInterface()

if __name__ == '__main__':
    main()

import CYKParse
import Tree
import requests
import json
import tkinter as tk
from PIL import Image, ImageTk
from urllib.request import urlopen

url = "https://poe.ninja/api/data/itemoverview?league=Ritual&type=UniqueWeapon"


requestInfo = {
        'item': '',
        'item1':'',
        'lookingForPrice' : False,
        'exalted':False,
        'lookingForType' : False,
        'lookingForLevel' :False,
        'lookingForIcon' :False,
        'lookingForModifiers':False,
        'description':False,
        'implicit':False,
        'explicit':False,
        'comparison':False,
        'compareWord':'',
        'compareWord1':''
}

# Given the collection of parse trees returned by CYKParse, this function
# returns the one corresponding to the complete sentence.
def getSentenceParse(T):
    sentenceTrees = { k: v for k,v in T.items() if k.startswith('S/0') }
    
    try:
        completeSentenceTree = max(sentenceTrees.keys())
    except ValueError:
        outputLabel.config(text = "Please try another input")
    #print('getSentenceParse', completeSentenceTree)
    return T[completeSentenceTree]

# Processes the leaves of the parse tree to pull out the user's request.
def updateRequestInfo(Tr):
    global requestInfo

    foundFirstAdverb = False
    foundFirstItem = False

    for leaf in Tr.getLeaves():

        if(leaf[1] == 'than' and not requestInfo['comparison']):
            requestInfo['comparison'] = True
            
        if(requestInfo['comparison']):
            for leaf in Tr.getLeaves():
                if(leaf[0] == 'Name'):
                    if (foundFirstItem):
                        requestInfo['item1'] = leaf[1]
                    else:
                        requestInfo['item'] = leaf[1]
                        foundFirstItem = True

                if(leaf[1] == 'more' or  leaf[1] == 'less' or leaf[1] == 'higher' or leaf[1] == 'lower'):
                    requestInfo['compareWord'] = leaf[1]

                if(leaf[1] == 'expensive'):
                    requestInfo['lookingForPrice'] = True
                
                if(leaf[1] == 'level'):
                    requestInfo['lookingForLevel'] = True
                    requestInfo['compareWord1'] = leaf[1]

                if(leaf[1] == 'expensive'):
                    requestInfo['lookingForPrice'] = True
                    requestInfo['compareWord1'] = leaf[1]

        else:
            for leaf in Tr.getLeaves():
                if leaf[0] == 'Noun' and leaf[1] == 'cost' or leaf[1] == 'price' or leaf[1] == 'value':
                    requestInfo['lookingForPrice'] = True

                if leaf[1] == 'exalted':
                    requestInfo['exalted'] = True

                if leaf[0] == 'Noun' and leaf[1] == 'type':
                    requestInfo['lookingForType'] = True

                if leaf[0] == 'Noun' and leaf[1] == 'level' or leaf[1] =='requirement':
                    requestInfo['lookingForLevel'] = True

                if leaf[0] == 'Noun' and leaf[1] == 'appearance' or leaf[1] == 'look':
                    requestInfo['lookingForIcon'] = True

                if leaf[1] == 'description':
                    requestInfo['description'] = True

                if leaf[1] == 'modifiers':
                    requestInfo['lookingForModifiers'] = True

                if leaf[1] == 'implicit':
                    requestInfo['implicit'] = True

                if leaf[1] == 'explicit':
                    requestInfo['explicit'] = True

                if leaf[0] == 'Name':
                    requestInfo['item'] = leaf[1]

                


# These functions contains the data known by our simple chatbot
def getChaos(item):   
    for i in CYKParse.item_list:
        if(item.replace('_',' ') == i['name']):
            return i['chaosValue']
def getExalted(item):
    for i in CYKParse.item_list:
        if(item.replace('_',' ') == i['name']):
            return i['exaltedValue']
def getType(item):
    for i in CYKParse.item_list:
        if(item.replace('_',' ') == i['name']):
            return i['baseType']

def getLevel(item):
    for i in CYKParse.item_list:
        if(item.replace('_',' ') == i['name']):
            return i['levelRequired']

def getIcon(item):
    for i in CYKParse.item_list:
        if(item.replace('_',' ') == i['name']):
            im = Image.open(urlopen(i['icon']))
            return im

def getExplicit(item):
    modifier_list = []
    for i in CYKParse.item_list:
        if(item.replace('_',' ') == i['name']): 
            for j in i['explicitModifiers']:
                modifier_list.append(j['text'])
            return modifier_list

def getImplicit(item):
    modifier_list = []
    for i in CYKParse.item_list:
        if(item.replace('_',' ') == i['name']): 
            for j in i['implicitModifiers']:
                modifier_list.append(j['text'])
            return modifier_list
def getAllModifiers(item):
    modifier_list = []
    for i in CYKParse.item_list:
        if(item.replace('_',' ') == i['name']): 
            for j in i['implicitModifiers']:
                modifier_list.append(j['text'])
            for j in i['explicitModifiers']:
                modifier_list.append(j['text'])
            return modifier_list

def getFlavourText(item):
    for i in CYKParse.item_list:
        if(item.replace('_',' ') == i['name']):
            return i['flavourText']
# Format a reply to the user, based on what the user wrote.
def reply():
    global requestInfo
    itemPrice = 0
    itemPrice1 = 0
    itemType = ''
    itemLevel = 0
    itemLevel1 = 0
    if(requestInfo['lookingForPrice'] == True):
        if(requestInfo['comparison']):
            itemPrice = getChaos(requestInfo['item'])
            itemPrice1 = getChaos(requestInfo['item1'])

            if(requestInfo['compareWord'] == 'more' and requestInfo['compareWord1'] == 'expensive'):
                if(itemPrice > itemPrice1):
                    outputLabel.config(text = " Response: " + requestInfo['item'].replace('_', ' ') + " is more expensive than " + requestInfo['item1'].replace('_', ' '))
                    requestInfo['lookingForPrice'] = False
                    requestInfo['comparison'] = False
                    photoLabel.configure(image = "")
                    return
                else:
                    outputLabel.config(text = " Response: " + requestInfo['item'].replace('_', ' ') + " is not more expensive than " + requestInfo['item1'].replace('_', ' '))
                    requestInfo['lookingForPrice'] = False
                    requestInfo['comparison'] = False
                    photoLabel.configure(image = "")
                    return

            if(requestInfo['compareWord'] == 'less' and requestInfo['compareWord1'] == 'expensive'):
                if(itemPrice < itemPrice1):
                    outputLabel.config(text = " Response: " + requestInfo['item'].replace('_', ' ') + " is less expensive than " + requestInfo['item1'].replace('_', ' '))
                    requestInfo['lookingForPrice'] = False
                    requestInfo['comparison'] = False
                    photoLabel.configure(image = "")
                    return
                else:
                    outputLabel.config(text = " Response: " + requestInfo['item'].replace('_', ' ') + " is not less expensive than " + requestInfo['item1'].replace('_', ' '))
                    requestInfo['lookingForPrice'] = False
                    requestInfo['comparison'] = False
                    photoLabel.configure(image = "")
                    return
        elif(requestInfo['exalted']):
            itemPrice = getExalted(requestInfo['item'])
            outputLabel.config(text = " Response: " + "Price of " + requestInfo['item'].replace('_', ' ') + " is " + str(itemPrice) + " exalted orbs.")

            im = getIcon(requestInfo['item'])
            photo = ImageTk.PhotoImage(im)
            photoLabel.configure(image = photo)
            photoLabel.image = photo

            requestInfo['lookingForIcon'] = False
            requestInfo['lookingForPrice'] = False
            requestInfo['exalted'] = False
            return

        else:
            itemPrice = getChaos(requestInfo['item'])
            outputLabel.config(text = " Response: " + "Price of " + requestInfo['item'].replace('_', ' ') + " is " + str(itemPrice) + " chaos orbs.")

            im = getIcon(requestInfo['item'])
            photo = ImageTk.PhotoImage(im)
            photoLabel.configure(image = photo)
            photoLabel.image = photo

            requestInfo['lookingForIcon'] = False
            requestInfo['lookingForPrice'] = False
            requestInfo['chaos'] = False
            return

    if(requestInfo['lookingForLevel'] == True and requestInfo['comparison']):
        itemLevel = getLevel(requestInfo['item'])
        itemLevel1 = getLevel(requestInfo['item1'])
        if(requestInfo['compareWord'] == 'higher' and requestInfo['compareWord1'] == 'level'):
            if(itemLevel > itemLevel1):
                outputLabel.config(text = " Response: " + requestInfo['item'].replace('_', ' ') + " is higher level than " + requestInfo['item1'].replace('_', ' '))
                requestInfo['lookingForLevel'] = False
                requestInfo['comparison'] = False
                photoLabel.configure(image = "")
                return
            else:
                outputLabel.config(text = " Response: " + requestInfo['item'].replace('_', ' ') + " is not higher level than " + requestInfo['item1'].replace('_', ' '))
                requestInfo['lookingForLevel'] = False
                requestInfo['comparison'] = False
                photoLabel.configure(image = "")
                return

        if(requestInfo['compareWord'] == 'lower' and requestInfo['compareWord1'] == 'level'):
            if(itemLevel < itemLevel1):
                outputLabel.config(text = " Response: " + requestInfo['item'].replace('_', ' ') + " is lower level than " + requestInfo['item1'].replace('_', ' '))
                requestInfo['lookingForLevel'] = False
                requestInfo['comparison'] = False
                photoLabel.configure(image = "")
                return
            else:
                outputLabel.config(text = " Response: " + requestInfo['item'].replace('_', ' ') + " is not lower level than " + requestInfo['item1'].replace('_', ' '))
                requestInfo['lookingForLevel'] = False
                requestInfo['comparison'] = False
                photoLabel.configure(image = "")
                return
        
    if(requestInfo['lookingForType'] == True):
        itemType = getType(requestInfo['item'])
        outputLabel.config(text = " Response: " + requestInfo['item'].replace('_',' ') +  ' is a unique ' + itemType + '.')
        requestInfo['lookingForType'] = False
        im = getIcon(requestInfo['item'])
        photo = ImageTk.PhotoImage(im)
        photoLabel.configure(image = photo)
        photoLabel.image = photo
        return

    if(requestInfo['lookingForLevel'] == True):
        itemLevel = getLevel(requestInfo['item'])
        outputLabel.config(text = " Response: " + requestInfo['item'].replace('_',' ') +  ' is a level ' + str(itemLevel) + ' item.')
        requestInfo['lookingForLevel'] = False
        im = getIcon(requestInfo['item'])
        photo = ImageTk.PhotoImage(im)
        photoLabel.configure(image = photo)
        photoLabel.image = photo
        return

    if(requestInfo['lookingForIcon'] == True):
        im = getIcon(requestInfo['item'])
        photo = ImageTk.PhotoImage(im)
        outputLabel.config(text = requestInfo['item'].replace('_',' ') + ' looks like this: ')
        photoLabel.configure(image = photo)
        photoLabel.image = photo
        requestInfo['lookingForIcon'] = False
        return

    if(requestInfo['lookingForModifiers'] == True):
        modifier_list = []
        modifiers = ''

        if(requestInfo['explicit'] == True):
            modifier_list = getExplicit(requestInfo['item'])
            for s in modifier_list:
                modifiers += s + '\n'
            outputLabel.config(text = requestInfo['item'].replace('_',' ') + '\'s explicit modifiers are: \n ' +modifiers)

        if(requestInfo['implicit'] == True):
            print('in implicit')
            modifier_list = getImplicit(requestInfo['item'])
            for s in modifier_list:
                modifiers += s + '\n'

            if (len(modifiers) == 0):
                outputLabel.config(text = requestInfo['item'].replace('_',' ') + ' has no implicit modifiers.')

            else:
                outputLabel.config(text = requestInfo['item'].replace('_',' ') + '\'s implicit modifiers are: \n ' +modifiers)

        if(requestInfo['explicit'] == False and requestInfo['implicit'] == False):
            modifier_list = getAllModifiers(requestInfo['item'])
            for s in modifier_list:
                modifiers += s + '\n'
            outputLabel.config(text = requestInfo['item'].replace('_',' ') + '\'s modifiers are: \n ' +modifiers)
    
        im = getIcon(requestInfo['item'])
        photo = ImageTk.PhotoImage(im)
        photoLabel.configure(image = photo)
        photoLabel.image = photo
        requestInfo['lookingForIcon'] = False
        requestInfo['implicit'] = False
        requestInfo['explicit'] = False
        requestInfo['lookingForModifiers'] = False

        return

    if(requestInfo['description'] == True):
        
        description = getFlavourText(requestInfo['item'])
        outputLabel.config(text = " Description of " + requestInfo['item'].replace('_',' ') +  ':' + description)
        im = getIcon(requestInfo['item'])
        photo = ImageTk.PhotoImage(im)
        photoLabel.configure(image = photo)
        photoLabel.image = photo
        requestInfo['lookingForIcon'] = False
        return
    outputLabel.config(text = "Please try another input")

def getInput():
    sentence = userEntry.get()
    userEntry.delete(0,'end')
    for key,value in CYKParse.tokenized_names.items():
        index = sentence.find(key)
        if (index > 0):
            sentence = sentence.replace(key,value)

    input_list = sentence.split()
    T, P = CYKParse.CYKParse(input_list, CYKParse.getGrammarItems())
    sentenceTree = getSentenceParse(T)
    updateRequestInfo(sentenceTree)
    reply()
    
    
# A simple hard-coded proof of concept.
def main():
    global requestInfo
    global userEntry
    global outputLabel
    global photoLabel
    sentence = ""
    photoUrl = "https://web.poecdn.com/image/Art/2DItems/Weapons/TwoHandWeapons/TwoHandMaces/Trypanon.png?v=eb43e5e1c1e7b8dd83f456c4d567ece9&w=2&h=4&scale=1"


    root = tk.Tk()
    baseImage = ImageTk.PhotoImage(Image.open(urlopen(photoUrl)))
    root.title("Poe Chat Bot")
    root.geometry("700x500")

    frame = tk.Frame(root)
    frame1 = tk.Frame(root)
    frame2 = tk.Frame(root)


    label = tk.Label(frame,text = "PoE chat bot")
    label.pack()

    userEntry = tk.Entry(frame, width = 40)
    userEntry.pack()

    buttonInput = tk.Button(frame, text = "Enter", command = getInput)
    buttonInput.pack()

    outputLabel = tk.Label(frame1,text = "Response:")
    outputLabel.pack()

    photoLabel = tk.Label(frame2, image = "")
    photoLabel.pack()

    frame.pack(padx = 1, pady = 1)
    frame1.pack(padx = 10, pady = 10)
    frame2.pack(padx = 10, pady = 10)
    root.mainloop()
    
main()

#here is a list of sentences that can be used:
#What is the appearance of Doomfletch
#What is the price/value of Doomfletch 
#What is the exalted price/value of Doomfletch
#What is the requirement of Doomfletch
#What are the implicit modifiers of Doomfletch
#What are the explicit modifiers of Doomfletch
#What are the modifiers of Doomfletch
#Is Doomfletch more/less expensive than Soul Taker

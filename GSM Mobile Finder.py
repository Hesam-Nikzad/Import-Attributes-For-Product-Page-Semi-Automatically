import requests
from bs4 import BeautifulSoup
import json
import re


def dict2json(dict):
    fileName = 'source'
    fileName = fileName + '.json'
    with open(fileName, 'w') as f:
        json.dump(dict, f)

def Find_OS():
    Numbers = [2, 3, 4, 5, 6, 7, 9, 10, '}']
    OSs = ['Android', 'iOS', 'Windows Phone', 'Symbian', 'RIM', 'Bada', 'Firefox', 'KaiOS']
    URL = 'https://www.gsmarena.com/search.php3?sOSes=%2'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    Versions = soup.find_all('script', type="text/javascript")[5].string
    #print(Versions)
    dict = {}
    for i in range(len(Numbers)-1):
        ind1 = Versions.find(str(Numbers[i]) + ':')
        try:
            ind2 = Versions.find(str(Numbers[i+1]) + ':')
        except: 
            ind2 = Versions.find(Numbers[i+1])

        OS_Versions = Versions[ind1+3 : ind2-5]
        OS_Version = re.findall('\[(.*?)\]', OS_Versions)
        List = []
        for Version in OS_Version:
            if Version[0] == '[': Version = Version[1:]
            Version = Version[1:]
            Version = Version[: Version.find('\"')]
            List.append(Version)
        
        dict[OSs[i]] = List

    dict['Feature phones'] = ''
    return dict

def Find_Network():
    dict = {}
    URL = 'https://www.gsmarena.com/search.php3?'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    Networks = soup.find_all('div', class_='l-col l-col-1-4 mr10')
    Networks1 = soup.find_all('div', class_='l-col l-col-1-4 mr0')
    Networks.extend(Networks1)

    for Network in Networks:
        try:
            label = Network.find('label').text[:-1]
            if 'G' not in label: continue
            options = Network.find_all('option')
            List = []
            for option in options:
                List.append(option.text)

            dict[label] = List

        except: pass

    return dict

def Find_Display_Resolution():
    
    URL = 'https://www.gsmarena.com/search.php3?'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    soup = str(soup)
    soup = soup[soup.find('makeSlider(".phonefinder-slider-display", "#skipval-display-min", "#skipval-display-max", [')+90:]
    soup = soup[:soup.find(']);')]
    Res = soup.split('\r\n\t\t\t')
    List = []
    for item in Res:
        item = item[item.find('"')+1 : ]
        item = item[ : item.find('"')]
        List.append(item)
    
    return List

def Find_RAM():
    URL = 'https://www.gsmarena.com/search.php3?'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    Sliders = soup.find_all('div', class_="framed clearfix p10")
        
    for Slider in Sliders:
        label = Slider.find('span', class_="label float-left").text[:-1]
        if label == 'RAM':
            
            Slider = str(Slider)
            Slider = Slider[Slider.find('makeSlider')+10 : Slider.find(';')]
            RAMs = re.findall('\[(.*?)\]', Slider)
            optList=[]
            for RAM in RAMs:
                RAM = RAM[RAM.find('\"') + 1:]
                RAM = RAM[:RAM.find('\"')]
                optList.append(RAM)
    
    return optList
                


URL = 'https://www.gsmarena.com/search.php3?'
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

DICT ={}
temp_dict ={}
List_temp = []
Titles = soup.find_all('div', class_='row')
for Title in Titles:
    dict = {}

    try:
        major_title = Title.find('h3', class_='phonefinder-title').text
        temp_title = major_title
        List = []
    except:
        major_title = temp_title
        dict = temp_dict
        List = List_temp

    try:
        #major_title = Title.find('h3', class_='phonefinder-title').text
        Subtitles = Title.find_all('div', class_='l-col l-col-1-2 mr10')
        Subtitles1 = Title.find_all('div', class_='l-col l-col-1-2')
        Subtitles.extend(Subtitles1)
    
        for Subtitle in Subtitles:
        
            try:
                label = Subtitle.find('label')
                options = Subtitle.find_all('option')
                opts = []
                for option in options:
                    opts.append(option.text)

                dict[label.text[:-1]] = opts
            except:
                pass
        DICT[major_title] = dict

    except: pass

    try:
        #major_title = Title.find('h3', class_='phonefinder-title').text
        Subtitles = Title.find_all('div', class_='l-col l-col-1-4 mr10')
        if major_title == 'General': continue
    
        for Subtitle in Subtitles:
        
            try:
                #print(Subtitle)
                label = Subtitle.find('label')
                options = Subtitle.find_all('option')
                opts = []
                for option in options:
                    opts.append(option.text)

                dict[label.text[:-1]] = opts
            except:
                pass
        DICT[major_title] = dict

    except: pass
        
    try:
        #major_title = Title.find('h3', class_='phonefinder-title').text
        Sliders = Title.find_all('div', class_="framed clearfix p10")
        
        for Slider in Sliders:
        
            try:
                label = Slider.find('span', class_="label float-left").text[:-1]
                Slider = str(Slider)
                Slider = Slider[Slider.find('makeSlider')+10 : Slider.find(';')]
                Elements = Slider.split(',')
                min, max, step = int(Elements[3]), int(Elements[4]), int(Elements[5])
                dict[label] = {'min': min, 'max': max, 'step': step}
                
            except: pass
        DICT[major_title] = dict

    except: pass

    try:
        #major_title = Title.find('h3', class_='phonefinder-title').text
        Sliders = Title.find_all('div', class_="framed clearfix p10")
        
        for Slider in Sliders:
        
            try:
                label = Slider.find('span', class_="label float-left").text[:-1]
                Slider = str(Slider)
                Slider = Slider[Slider.find('makeSlider')+10 : Slider.find(';')]
                Elements = Slider.split('\r\n\t\t\t\t\t')
                if len(Elements) == 1: continue
                Elements = Elements[1:]
                optList=[]
                for Element in Elements:
                    Element = Element[Element.find('\"') + 1:]
                    Element = Element[:Element.find('\"')]
                    optList.append(Element)
                dict[label] = optList
                
            except: pass
        DICT[major_title] = dict

    except: pass

    try:
        #major_title = Title.find('h3', class_='phonefinder-title').text
        Subtitles = Title.find_all('div', class_='framed l-col l-col-1-4')
        Subtitles1 = Title.find_all('div', class_='framed l-col l-col-1-4 mr0')
        Subtitles2 = Title.find_all('div', class_='framed l-col l-col-1-4 mr10')
        Subtitles.extend(Subtitles1)
        Subtitles.extend(Subtitles2)
    
        for Subtitle in Subtitles:
        
            try:
                label = Subtitle.find('label')
                List.append(label.text)

            except:
                pass

        dict['Options'] = List
        DICT[major_title] = dict

    except: pass

    temp_dict = dict
    List_temp = List

OS = Find_OS()
DICT['Platform']['OS Version'] = OS

Nets = Find_Network()
DICT['Network'] = Nets

Res = Find_Display_Resolution()
DICT['Display']['Resolution'] = Res

RAM = Find_RAM()
DICT['Memory']['RAM'] = RAM

dict2json(DICT)
print(DICT)

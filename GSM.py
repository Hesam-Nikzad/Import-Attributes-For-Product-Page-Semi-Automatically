import requests
import json
import glob
import os
from bs4 import BeautifulSoup


class All_Brands_Page:
    def __init__(self, URL=None, path=None):
        if URL != None:
            self.page = requests.get(URL)
            self.soup = BeautifulSoup(self.page.content, "html.parser")
        elif path != None:
            self.page = open(path, "r").read()
            self.soup = BeautifulSoup(self.page, "html.parser")

    def Crawl(self):
        DICT = {}
        Table = self.soup.find('table')
        Rows = Table.find_all('a')

        for Row in Rows:
            URL = Row['href']
            device_numbers = Row.find('span').text
            Brand = Row.text
            Brand = Brand[ : Brand.find(device_numbers)]
            DICT[Brand] = [URL, device_numbers]
        
        self.URLs = DICT
        return DICT

    def Export_Json(self, path):
        fileName = path + 'Brands_URLs.json'
        with open(fileName, 'w') as f:
            json.dump(self.URLs, f)

class Brand_Page:
    def __init__(self, URL):
        URL = URL.split('/')[3][:-4]
        URL_base = 'https://www.gsmarena.com/'
        ind = URL.rfind('-')
        self.URL_base = URL_base + URL[:ind] + '-f' + URL[ind:] + '-0-p'

    def Crawl(self, URL=None, path=None):
        if URL != None:
            self.page = requests.get(URL)
            self.soup = BeautifulSoup(self.page.content, "html.parser")
        elif path != None:
            self.page = open(path, "r").read()
            self.soup = BeautifulSoup(self.page, "html.parser")

        Table = self.soup.find('div', class_='makers')
        Phones = Table.find_all('a')
        DICT = {}
        for Phone in Phones:
            #print(Phone)
            URL = Phone['href']
            Title = Phone.text
            Spec = Phone.find('img')['title'] + ' '
            Spec = Spec.split('. ')
            Specs = [Spec[0], Spec[1]]
            Specs.extend(Spec[2].split(','))
            Specs[2] = Specs[2][9:]                 # To remove 'Features ' word
            Specs.insert(0, URL)
            DICT[Title] = Specs
        
        self.Phones = DICT
        return DICT

    def URL_Maker(self, n):
        
        pageNumbers = n//40 + 1
        List = []
        
        for Number in range(pageNumbers):
            URL = self.URL_base + '%s.php' %(Number+1)
            List.append(URL)
        
        return List

class Mobile_Page:
    def __init__(self, URL=None, path=None, proxy=None):
        self.status = 'OK'

        if URL != None and proxy != None:
            try:
                self.page = requests.get(URL, proxies={"http": proxy, "https": proxy})
                self.soup = BeautifulSoup(self.page.content, "html.parser")
                title = self.soup.find('h1').text
                if title == 'Too Many Requests':
                    self.status = 'Banned'
            except:
                self.status = 'error'

        elif URL != None:
            try:
                self.page = requests.get(URL)
                self.soup = BeautifulSoup(self.page.content, "html.parser")
                title = self.soup.find('h1').text
                if title == 'Too Many Requests':
                    self.status = 'Banned'
            except:
                self.status = 'error'

        elif path != None:
            self.page = open(path, "r").read()
            self.soup = BeautifulSoup(self.page, "html.parser")
        
        
        
    
    def Crawl(self):
        DICT = {}
        Tables = self.soup.find_all('table', cellspacing='0')
        for Table in Tables:
            dict = {}
            Title = Table.find('th', scope='row').text          # Major title
            ttls = Table.find_all('td', class_='ttl')           # Minor title
            nfos = Table.find_all('td', class_='nfo')           # Minor title's info
            
            for i in range(len(ttls)):
                ttl = ttls[i].text
                nfo = nfos[i].text
                dict[ttl] = nfo
            
            DICT[Title] = dict
        
        self.Table = DICT
        return DICT

    def Export_Json(self, path, fileName=None):
        if fileName == None:
            Name = self.soup.find('title').text
            fileName = Name.split(' - ')[0]
        fileName = path + fileName + '.json'
        with open(fileName, 'w') as f:
            json.dump(self.Table, f)

class Proxies:
    def __init__(self, local=False):
        self.i = 0
        self.Proxy = []

        if local == False:
            page = requests.get('https://free-proxy-list.net/')
            soup = BeautifulSoup(page.content, "html.parser")
            Table = soup.find('table', class_='table table-striped table-bordered').find('tbody')
            Rows = Table.find_all('tr')
            
            for Row in Rows:
                Row = Row.find_all('td')
                proxy = 'http://' + Row[0].text + ':' + Row[1].text
                self.Proxy.append(proxy)
            print('%s proxies have been fetched from https://free-proxy-list.net/' %len(self.Proxy))

        elif local == True:
            path = os.getcwd().replace('\\', '/') + '/Proxies.txt'
            f = open(path, 'r')
            contents = f.readlines()
            for line in contents:
                line = line.strip()
                proxy = 'http://' + line
                self.Proxy.append(proxy)
            print('%s proxies have been fetched localy' %len(self.Proxy))

    def Select(self, Next=False):
        if Next == True:
            self.i += 1
            print('The proxy changed to number %s' %self.i)
        
        if self.i >= 299:
            return None
        
        return self.Proxy[self.i]

class DataFlow:
    def __init__(self, path=None):
        self.URL = 'https://www.gsmarena.com/'
        if path == None:
            self.path = os.getcwd().replace('\\', '/') + '/'
        else:
            self.path = path

        self.fileName = 'List of all mobile phone brands - GSMArena.com.html'

    def Brands(self):
        
        # If the all brands page is available offline
        try:
            filePath = self.path + 'Pages/' + self.fileName
            Brands = All_Brands_Page(path=filePath)
        # Request online if the web page is not available offline
        except:
            Brands = All_Brands_Page(URL=self.URL + 'makers.php3')

        Brands.Crawl()
        Brands.Export_Json(self.path)

         # If the Brand folder does not exist, create it
        brandsPath = self.path + 'Brands/'
        if not os.path.exists(brandsPath):
            os.makedirs(brandsPath)

        # If brands' names folders do not exist, create them
        for key in Brands.URLs.keys():
            if key[-1] == '.':
                key = key[:-1]

            brandPath = brandsPath + key + '/'
            if not os.path.exists(brandPath):
                os.makedirs(brandPath)
                print('%s folder has been created' %key)

    def Brand_General_Info(self):
        f = open(self.path + 'Brands_URLs.json')
        Brands = json.load(f)
        for key in Brands.keys():
            Brand = key
            if Brand[-1] == '.':
                Brand = Brand[:-1]

            URL = Brands[key][0]
            Number = Brands[key][1]
            devicesNumber = int(Number[:Number.find(' ')])
            
            brandPath = self.path + 'Brands/%s/%s.json' %(Brand, Brand) 
            # If the file is already done skip
            if os.path.exists(brandPath) and len(json.load(open(brandPath)).keys()) == devicesNumber:
                print('%s Json file is already done' %Brand)
                continue
            
            # Brands page object and the brands url list
            brandPage = Brand_Page(URL)
            URLs = brandPage.URL_Maker(devicesNumber)
            
            DICT = {}
            for URL in URLs:
                DICT.update(brandPage.Crawl(URL))

            with open(brandPath, 'w') as f:
                json.dump(DICT, f)
            
            print('%s Json file has been created' %Brand)
            
    def Crawl_Mobile(self):
        try:
            Proxy = Proxies()
        except:
            Proxy = Proxies(local=True)

        path = self.path + 'Brands/'
        for name in glob.glob(path + '*/' , recursive = True):

            brandName = name[name.find('\\')+1 : name.rfind('\\')]
            brandData = path + '%s/%s.json' %(brandName, brandName)
            f = open(brandData)
            devices = json.load(f)
            for device in devices:
                URL = self.URL + devices[device][0]
                deviceFullName = devices[device][1]
                mobilePath = path + '%s/%s.json' %(brandName, deviceFullName)
                
                if os.path.exists(mobilePath) and len(json.load(open(mobilePath)).keys()) != 0:
                    print('%s Json file is already done' %deviceFullName)
                    continue
                
                print('Crawling %s has been started' %deviceFullName)

                Mobile = Mobile_Page(URL=URL, proxy=Proxy.Select())

                # If the proxy does not work change it
                while Mobile.status == 'Banned' or Mobile.status == 'error':
                    
                    proxy = Proxy.Select(Next=True)          
                    if proxy == None:
                        break
                    
                    try: 
                        Mobile = Mobile_Page(URL=URL, proxy=proxy)
                    except:
                        Mobile.status = 'Banned'
                
                Mobile.Crawl()
                Mobile.Export_Json(path + '%s/' %brandName, fileName=deviceFullName)

            try: 
                if Mobile.status == 'Banned':
                        print('GSM Arena banned crawling')
                        break
            except:
                pass
                

# --------- Main ---------
DF = DataFlow()
DF.Brands()
DF.Brand_General_Info()
DF.Crawl_Mobile()

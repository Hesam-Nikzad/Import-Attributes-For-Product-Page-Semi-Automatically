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
        #self.Path = 'C:/Users/Hessum/OneDrive/Python Projects/bitt/Import-Attributes-For-Product-Page-Semi-Automatically/Pics/'
        self.imageFlag = True

        if URL != None and proxy != None:
            try:
                self.page = requests.get(URL, timeout=20, proxies={"http": proxy, "https": proxy})
                self.soup = BeautifulSoup(self.page.content, "html.parser")
                title = self.soup.find('h1').text
                if title == 'Too Many Requests':
                    self.status = 'Banned'

                image_element = self.soup.find('img', class_='specs-photo-main')
                self.image_url = image_element['src']
                
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

    def Image(self, proxy):
            
        try:
            response = requests.get(self.image_url, timeout=20, proxies={"http": proxy, "https": proxy})
            #print(response.content)
            print(type(response.content))
            self.Picture = response.content
            self.imageFlag = False
        except:
            self.imageFlag = True
        
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
            self.proxyscrape()
            self.Free_Proxy_List()
            #self.geonode()    
        
        elif local == True:
            path = os.getcwd().replace('\\', '/') + '/Proxies.txt'
            f = open(path, 'r')
            contents = f.readlines()
            for line in contents:
                line = line.strip()
                proxy = 'http://' + line
                self.Proxy.append(proxy)
            print('%s proxies have been fetched localy' %len(self.Proxy))

    def Free_Proxy_List(self):
        page = requests.get('https://free-proxy-list.net/')
        soup = BeautifulSoup(page.content, "html.parser")
        Table = soup.find('table', class_='table table-striped table-bordered').find('tbody')
        Rows = Table.find_all('tr')
        n = len(self.Proxy)
        for Row in Rows:
            Row = Row.find_all('td')
            proxy = 'http://' + Row[0].text + ':' + Row[1].text
            self.Proxy.append(proxy)
        print('%s proxies have been fetched from https://free-proxy-list.net/' %(len(self.Proxy)-n))

    def geonode(self):
        page = []
        for i in range(1, 15):
            URL = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=%s&sort_by=lastChecked&sort_type=desc' %i
            page.extend(requests.get(URL).json()['data'])
            print('Page %s of geonode API has been loaded' %i)
        n = len(self.Proxy)
        for dict in page:
            if dict['protocols'][0] == 'http':
                proxy = 'http://' + dict['ip'] + ':' + dict['port']
                self.Proxy.append(proxy)
                
        print('%s proxies have been fetched from https://geonode.com/' %(len(self.Proxy)-n))

    def proxyscrape(self):
        URL = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=1000&country=all&ssl=all&anonymity=all'
        resp = requests.get(URL).text
        resp = resp.strip()
        resp = resp.split('\n')
        n = len(self.Proxy)
        for proxy in resp:
            proxy = 'http://' + proxy[:-1]
            self.Proxy.append(proxy)
        print('%s proxies have been fetched from https://proxyscrape.com/' %(len(self.Proxy)-n))

    def Select(self, Next=False):
        if Next == True:
            self.i += 1
            print('The proxy changed to number %s' %self.i)
        
        if self.i >= (len(self.Proxy) - 1):
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

        f = open(self.path + 'Black_List.txt', 'r')
        lines = f.readlines()
        blackList = []
        for line in lines:
            line = line.strip()
            blackList.append(line)

        path = self.path + 'Brands/'
        picturPath = self.path + 'Pictures/'
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
                
                if deviceFullName in blackList:
                    print('Skiped %s because it is in the black list' %deviceFullName)
                    continue
                
                print('Crawling %s has been started' %deviceFullName)
                brandPicturePath = picturPath + '%s' %brandName
                if not os.path.exists(brandPicturePath):
                    os.makedirs(brandPicturePath)

                Mobile = Mobile_Page(URL=URL, proxy=Proxy.Select())

                # If the proxy does not work change it
                while Mobile.status == 'Banned' or Mobile.status == 'error':
                    
                    proxy = Proxy.Select(Next=True)          
                    if proxy == None:
                        Mobile.status = 'Banned'
                        Proxy = Proxies()
                    
                    try: 
                        Mobile = Mobile_Page(URL=URL, proxy=proxy)
                    except:
                        Mobile.status = 'Banned'
                
                print(Mobile.image_url)
                # Image downloading
                while Mobile.imageFlag:
                    Mobile.Image(URL=Mobile.image_url, proxy=proxy)
                    
                    if Mobile.imageFlag:
                        proxy = Proxy.Select(Next=True)

                # Image saving
                imageName = deviceFullName.lower().split(' ')
                if 'android' in imageName:
                    imageName.remove('android')
                
                imageName = '-'.join(imageName[:-1]) + '-00'
                with open('%s/%s.jpg' %(brandPicturePath, imageName), 'wb') as f:
                    f.write(Mobile.Picture)

                # Crawl Mobile data
                try:
                    Mobile.Crawl()
                    if Mobile.Table['Launch']['Status'] == 'Cancelled':
                        f = open(self.path + 'Black_List.txt', 'a')
                        f.write(deviceFullName + '\n')
                        f.close
                    else:
                        Mobile.Export_Json(path + '%s/' %brandName, fileName=deviceFullName)
                except:
                    f = open(self.path + 'Black_List.txt', 'a')
                    f.write(deviceFullName + '\n')
                    f.close

            try: 
                if Mobile.status == 'Banned':
                    print('GSM Arena banned crawling')
                    break
            except:
                pass


def main ():
    DF = DataFlow()
    #DF.Brands()
    #DF.Brand_General_Info()
    DF.Crawl_Mobile()


if __name__ == "__main__":
    main()

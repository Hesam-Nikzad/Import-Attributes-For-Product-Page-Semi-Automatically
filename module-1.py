import json

class GSM_Arena:
    
    def __init__(self, path='', fileName=''):
        self.path = path
        path_in = path + fileName
        self.fileName = fileName[:-4]
        with open(path_in) as f:
            self.lines = f.readlines()
        self.keywords = ['NETWORK', 'LAUNCH', 'BODY', 'DISPLAY', 'PLATFORM', 'MEMORY', 'MAIN CAMERA', 
            'SELFIE CAMERA', 'SOUND', 'COMMS', 'FEATURES', 'BATTERY', 'MISC', 'TESTS']
        
    def txt2dict(self):
        dict = {}
        for j in range(len(self.keywords)):                                  # Crawl the keywords

            keyword = self.keywords[j]                                       # Set the keyword as a major KEY
            try:
                next_keyword = self.keywords[j+1]                            # Set the next keyword
            except:
                next_keyword = 'Disclaimer'

            for i in range(len(self.lines)):                                 # Read each line separately
                line = self.lines[i].strip()
                
                if line.split('\t')[0] == keyword:                      # Find the first minor key
                    key = line.split('\t')[1]
                    dict[keyword] = {key: ''}                          # Make a dictionary for the major KEY

                    while self.lines[i].strip().split('\t')[0] != next_keyword:
                        list = self.lines[i].strip().split('\t')
                        
                        if list[-1] == key: 
                            dict[keyword][key] = [self.lines[i+1].strip().split('\t')[0]]
                            i += 1
                        
                        else:
                            #print(list)

                            if len(list) == 3:
                                key = list[1]
                                dict[keyword][key] = [list[2]]

                            if len(list) == 2:
                                key = list[0]
                                dict[keyword][key] = [list[1]]

                            if len(list) == 1 and list[0] not in dict[keyword][key]:
                                dict[keyword][key].append(list[0])

                            i += 1
                            if next_keyword in ['Disclaimer', 'TESTS']: break

        return dict

    def dict2json(self, dict):
        fileName = self.path + self.fileName + '.json'
        with open(fileName, 'w') as f:
            json.dump(dict, f)

path = 'C:/Users/Hessum/OneDrive/Python Projects/bitt/Import-Attributes-For-Product-Page-Semi-Automatically/'
object = GSM_Arena(path=path, fileName='xiaomi.txt')
dict = object.txt2dict()
object.dict2json(dict)
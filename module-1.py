import json

path = ''
#path = 'C:/Users/Hessum/Desktop/'
path_in = path + 's22.txt'

with open(path_in) as f:
    lines = f.readlines()

keywords = ['NETWORK', 'LAUNCH', 'BODY', 'DISPLAY', 'PLATFORM', 'MEMORY', 'MAIN CAMERA', 
            'SELFIE CAMERA', 'SOUND', 'COMMS', 'FEATURES', 'BATTERY', 'MISC', 'TESTS']
dict = {}
for j in range(len(keywords)):                                  # Crawl the keywords

    keyword = keywords[j]                                       # Set the keyword as a major KEY
    try:
        next_keyword = keywords[j+1]                            # Set the next keyword
    except:
        next_keyword = 'Disclaimer'

    for i in range(len(lines)):                                 # Read each line separately
        line = lines[i].strip()
        
        if line.split('\t')[0] == keyword:                      # Find the first minor key
            key = line.split('\t')[1]
            dict[keyword] = {key: ''}                          # Make a dictionary for the major KEY

            while lines[i].strip().split('\t')[0] != next_keyword:
                list = lines[i].strip().split('\t')
                
                if list[-1] == key: 
                    dict[keyword][key] = [lines[i+1].strip().split('\t')[0]]
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
                    if next_keyword == 'Disclaimer': break


print(dict)

with open('data.json', 'w') as f:
    json.dump(dict, f)
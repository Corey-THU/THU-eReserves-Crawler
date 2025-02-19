import os
import re
import sys
import json
import random
import requests
from time import sleep
from bs4 import BeautifulSoup

# initialize
try:
    with open("config.json", "r", encoding='utf-8') as f:
        config         = json.load(f)
        jcclient       = config["jcclient"]
        BotuReadKernel = config["BotuReadKernel"]
        bookId         = config["bookId"]
        start          = config["start"]
        end            = config["end"]        
except:
    print("Failed to load config.json. Please check the file.\n")
    sys.exit()
    
num      = 0
finished = False
cookie   = 'BotuReadKernel=' + BotuReadKernel
url      = 'https://ereserves.lib.tsinghua.edu.cn'
headers  = {
    'botureadkernel': BotuReadKernel,
    'cookie'        : cookie,
    'jcclient'      : jcclient,
    'user-agent'    : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}

# get book detail
readurl  = json.loads(requests.get(f'{url}/userapi/MyBook/getBookDetail?bookId={bookId}', headers=headers).text)['data']['jc_ebook_vo']['urls'][0]['READURL']
sleep(random.uniform(0.5, 1.5))
url      = url + '/readkernel'
soup     = BeautifulSoup(requests.get(f'{url}/ReadJPG/JPGJsNetPage/{readurl}', headers=headers).text, 'lxml')
title    = soup.find('title').text
print(f'title: {title}\n')

# create directory
title = re.sub(r'[\\/:*?"<>|]', '.', title)
os.makedirs(title, exist_ok=True)

# selectJgpBookChapters
sleep(random.uniform(0.5, 1.5))
data     = {'SCANID': soup.find('input', {'name': 'scanid'}).get('value')}
chapters = json.loads(requests.post(f'{url}/KernelAPI/BookInfo/selectJgpBookChapters', headers=headers, data=data).text)['data']

# selectJgpBookChapter
for chapter in chapters:
    sleep(random.uniform(0.5, 1.5))
    data     = {'EMID': chapter['EMID'], 'BOOKID': readurl}
    # retry 5 times if failed
    for i in range(6):
        response = requests.post(f'{url}/KernelAPI/BookInfo/selectJgpBookChapter', headers=headers, data=data)
        if response.status_code == 200:
            break
        else:
            if i != 5:
                sleep(random.uniform(2*i+1, 4*i+2))
            else:
                print(f'Failed to get chapter "{chapter['EFRAGMENTNAME']}". Please retry later.\n')
                sys.exit()
    response = json.loads(response.text)['data']['JGPS']
    # download JPG files
    for item in response:
        num += 1
        if num < start:
            continue
        if end != -1 and num > end:
            finished = True
            break
        sleep(random.uniform(1, 2))
        # retry 5 times if failed
        for i in range(6):
            page = requests.get(f'{url}/JPGFile/DownJPGJsNetPage?filePath={item["hfsKey"]}', headers=headers)
            if page.status_code == 200:
                with open(f'{title}/{num}.jpg', 'wb') as f:
                    f.write(page.content)
                break
            else:
                if i != 5:
                    sleep(random.uniform(2*i+1, 4*i+2))
                else:
                    print(f'Failed to download {num}.jpg.\n')     
    if finished:
        break

print(f'Finished downloading.\n')

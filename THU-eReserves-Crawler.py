import re
import sys
import json
import random
import requests
from fpdf import FPDF
from PIL import Image
from io import BytesIO
from time import sleep
from bs4 import BeautifulSoup

# initialize
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config         = json.load(f)
        jcclient       = config['jcclient']
        BotuReadKernel = config['BotuReadKernel']
        bookId         = config['bookId']
        start          = config['start']
        end            = config['end']        
except:
    print('Failed to load config.json. Please check the file.')
    sys.exit()
    
num      = 0
flag     = False
cookie   = 'BotuReadKernel=' + BotuReadKernel
url      = 'https://ereserves.lib.tsinghua.edu.cn'
headers  = {
    'botureadkernel': BotuReadKernel,
    'cookie'        : cookie,
    'jcclient'      : jcclient,
    'user-agent'    : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}

# get book detail
response = json.loads(requests.get(f'{url}/userapi/MyBook/getBookDetail?bookId={bookId}', headers=headers).text)['data']['jc_ebook_vo']
sources  = response['urls']
title    = response['EBOOKNAME']
for source in sources:
    if source['SOURCE_NAME'] == '数字资源平台':
        flag = True
        break
if not flag:
    print(f'The source of {title} is not 数字资源平台.')
    sys.exit()
print(f'Downloading {title}...')
sleep(random.uniform(0.5, 1.5))

# selectJgpBookChapters
readurl  = source['READURL']
url      = url + '/readkernel'
title    = re.sub(r'[\\/:*?"<>|]', '.', title)
data     = {'SCANID': BeautifulSoup(requests.get(f'{url}/ReadJPG/JPGJsNetPage/{readurl}', headers=headers).text, 'lxml').find('input', {'name': 'scanid'}).get('value')}
sleep(random.uniform(0.5, 1.5))
chapters = json.loads(requests.post(f'{url}/KernelAPI/BookInfo/selectJgpBookChapters', headers=headers, data=data).text)['data']
pdf      = FPDF()
flag     = False

# selectJgpBookChapter
for chapter in chapters:
    sleep(random.uniform(0.5, 1.5))
    data = {'EMID': chapter['EMID'], 'BOOKID': readurl}
    # retry 5 times if failed
    for i in range(6):
        response = requests.post(f'{url}/KernelAPI/BookInfo/selectJgpBookChapter', headers=headers, data=data)
        if response.status_code == 200:
            response = response.json()
            if response['code'] != 1:
                print(f'Failed to get chapter "{chapter["EFRAGMENTNAME"]}". Info: {response['info']}.')
                sys.exit()
            break
        else:
            if i != 5:
                sleep(random.uniform(2*i+1, 4*i+2))
            else:
                print(f'Failed to get chapter "{chapter['EFRAGMENTNAME']}". Please retry later.')
                sys.exit()
    response = response['data']['JGPS']
    # download JPG files and add to PDF
    for item in response:
        num += 1
        if num < start:
            continue
        if end != -1 and num > end:
            flag = True
            break
        sleep(random.uniform(1, 2))
        # retry 5 times if failed
        for i in range(6):
            page = requests.get(f'{url}/JPGFile/DownJPGJsNetPage?filePath={item['hfsKey']}', headers=headers)
            if page.status_code == 200:
                img = Image.open(BytesIO(page.content))
                width, height = img.size
                pdf.add_page(format=(width*25.4/72, height*25.4/72))
                pdf.image(BytesIO(page.content), x=0, y=0, w=width*25.4/72, h=height*25.4/72)
                break
            else:
                if i != 5:
                    sleep(random.uniform(2*i+1, 4*i+2))
                else:
                    print(f'Failed to download page {num}.')
                    pdf.add_page(format=(width*25.4/72, height*25.4/72))
    if flag:
        break

pdf.output(f'{title}.pdf')
print(f'Finished downloading {title}.pdf.')

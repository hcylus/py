#coding=utf-8
from bs4 import BeautifulSoup
import urllib2

url = 'http://www.pythontab.com/html/pythonhexinbiancheng/index.html'
url_list = [url]
for i in range(2,19):
    url_list.append('http://www.pythontab.com/html/pythonhexinbiancheng/%s.html'%i)
source_list = []
for j in url_list:
    request = urllib2.urlopen(j)
    html = request.read()
    suop = BeautifulSoup(html,'lxml')
    titles = suop.select('#catlist > li > a')
    links = suop.select('#catlist > li > a')
    for title, link in zip(titles, links):
        data = {
            "title" : title.get_text(),
            "link" : link.get('href')
        }
        source_list.append(data)
    for l in source_list:
        request = urllib2.urlopen(l['link'])
        html = request.read()
        suop = BeautifulSoup(html,'lxml')
        text_p = suop.select('#Article > div.content > p')
        text = []
        print(text_p)
        for t in text_p:
            text.append(t.get_text().encode('utf-8'))
        title_text  = l['title']
        title_text = title_text.replace('*','').replace('/','or').replace('"',' ').replace('?','wenhao').replace(':',' ')

        with open('%s.txt'%title_text, 'wb') as f:
            for a in text:
                f.write(a)

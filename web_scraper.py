import requests
import re
import html
import time
import sys

#destination folder for the articles
DEST = "/Users/melissaguo/techcrunch/"
robots_disallow = []
article_urls = set()
page_count = 1

def readHTML(response):
    with open("techcrunch.html", "w") as file:
        file.write(response.text)
    with open("techcrunch.html", 'r', encoding='utf-8') as file:
        input_file = file.read()
    return input_file

def getURLs(html_content):
    url_pattern = r'https?://[^\s"<>\']+'
    urls = re.findall(url_pattern, html_content)
    return urls

def extractTitle(title):
    title_start = title.find("<title>") + 7 
    title_end = title.find("</title>") - 13
    file_title = title[title_start:title_end]
    decoded_title = html.unescape(file_title)
    safe_title = re.sub(r'[^\w\s-]|/', '_', decoded_title).replace(" ", "_")
    return safe_title + ".html"

def parse_robots():
    response = requests.get("https://techcrunch.com/robots.txt")
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for {url}")
        sys.exit(1)
    begin_parse = False
    for line in response.text.split("\n"):
        if line.startswith('User-agent: *'): 
            begin_parse = True
        elif line.startswith('Disallow') & begin_parse == True:  
            robots_disallow.append(line.split(': ')[1].split(' ')[0])
        elif line == "":
            begin_parse = False 

def is_article(url):
    url_tag = "https://techcrunch.com/"
    article_tag = '<meta name="author"'
    time.sleep(1) #allowing for a pause between requests
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for {url}")
        return False

    #saving the html file if it has an author and is from the techcrunch website
    if (article_tag in response.text) & (url_tag in url):
        file_name = extractTitle(response.text)
        with open(DEST + file_name, "w") as file:
            file.write(response.text)
        return True
    return False

def is_crawlable(url):
    for disallow in robots_disallow:
        if disallow in url:
            return False
    return True    

count = 1
while count < 50:
    #getting urls 
    category_url = "https://techcrunch.com/latest/"
    curr_page = f'{category_url}/page/{page_count}'
    response = requests.get(curr_page)
    if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} for {curr_page}")
            continue

    urls_in_page = readHTML(response)
    urls = getURLs(urls_in_page)
    page_count += 1

    #saving 50 articles to a designated directory
    for url in urls:   
        if (url not in article_urls) & (is_crawlable(url)):
            if is_article(url):
                article_urls.add(url)
                count += 1
            if count == 50:
                break

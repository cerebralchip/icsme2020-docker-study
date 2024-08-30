import requests
import json
from fake_headers import Headers
import time
import string
import os
import time

class DockerImageMiner:
    def __init__(self):
        self.DockerHubSearchAPIURL="https://hub.docker.com/api/content/v1/products/search"
        self.DockerHubSourceRepoQueryURL = 'https://hub.docker.com/api/build/v1/source/?image='
        self.ImageNameCrawlerTaskURL= 'http://localhost:8000/image_name_crawler_task/'
        self.PostImageURL= 'http://localhost:8000/create_image/'
        self.PostDockerHubUserURL= 'http://localhost:8000/dockerhub_user/'
        self.HEADER = {  
          'Host': 'hub.docker.com',
          'Connection': 'keep-alive',
          'Search-Version': 'v3',
          'Accept': '*/*',
          'Sec-Fetch-Dest': 'empty',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
          'Content-Type': 'application/json',
          'Sec-Fetch-Site': 'same-origin',
          'Sec-Fetch-Mode': 'cors',
          'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Language': 'en'
        }
        self.SEARCH_PARAMETERS = {
            'architecture':'arm%2Carm64%2Cppc%2Cs390x%2Cppc64le%2C386%2Camd64',
            'order':'desc',
            'page':1,
            'page_size':100,
            'q':'example',
            'sort':'updated_at',
            'type':'image'
        }
    
    def search_url_generator(self, q, page, order, page_size=10):
        url = self.DockerHubSearchAPIURL + '?'
        if(order == 'desc'):
            search_parameters_dict = self.SEARCH_PARAMETERS.copy()
            search_parameters_dict['q'] = q
            search_parameters_dict['page'] = page
            search_parameters_dict['order'] = order
            search_parameters_dict['page_size'] = page_size
            for para_name in search_parameters_dict:
                url += para_name + '=' + str(search_parameters_dict[para_name]) + '&'
            return url[:-1]
        elif(order == 'asc'):
            search_parameters_dict = self.SEARCH_PARAMETERS.copy()
            url+='order=asc&page={}&page_size={}&q={}&sort=updated_at&type=image'.format(page, page_size, q)
            return url
    
    def header_generator(self):
        headers = self.HEADER
        headers['User-Agent'] = Headers(headers=False).generate()['User-Agent']
        return headers
    
    def parsePullCount(self, pull_count):
        try:
            # Remove any non-numeric characters except for 'K' and 'M'
            pull_count = pull_count.replace('+', '').strip()
            
            if 'K' in pull_count:
                return int(float(pull_count[:-1]) * 1000)
            elif 'M' in pull_count:
                return int(float(pull_count[:-1]) * 1000000)
            elif 'B' in pull_count:
                return int(float(pull_count[:-1]) * 1000000000)
            else:
                return int(pull_count)
        except ValueError as e:
            # Handle the case where conversion fails
            print(f"Error parsing pull count: {e}")
            return None

    def image_parser(self, image_dict):
        res_dict = {}
        res_dict['image_name'] = image_dict['name']
        res_dict['publisher'] = image_dict['publisher']['name']
        res_dict['created_at'] = image_dict['created_at']
        res_dict['updated_at'] = image_dict['updated_at']
        res_dict['short_description'] = image_dict['short_description']
        res_dict['source'] = image_dict['source']
        res_dict['pull_count'] = self.parsePullCount(image_dict['pull_count'])
        res_dict['complete'] = False
        return res_dict

    def dockerhubuser_parser(self, image_dict):
        res_dict = {}
        res_dict['username'] = image_dict['publisher']['name']
        res_dict['uid'] = image_dict['publisher']['id']
        return res_dict
    
    def crawl_task(self, order='desc'):
        query_session = requests.Session()
        keyword = query_session.get(self.ImageNameCrawlerTaskURL).json()['keyword']
        query_url = self.search_url_generator(q = keyword, page = 1, order = order, page_size=10)
        try:
            res = query_session.get(query_url, headers = self.header_generator())
            image_count = res.json()['count']
            res_images_list = []
            if (image_count<=2500):
                start_time = time.time()  # Record the start time

                for i in range(0, image_count, 100):
                    query_url = self.search_url_generator(q=keyword, page=int(i/100+1), order=order, page_size=100)
                    res = query_session.get(query_url, headers=self.header_generator())
                    res_images_list += res.json()['summaries']

                end_time = time.time()  # Record the end time

                elapsed_time = end_time - start_time  # Calculate the elapsed time
                # time.sleep(0.1)
                images = [self.image_parser(item) for item in res_images_list]
                r = requests.post(self.PostImageURL, json=images)
                r_updates = json.loads(r.text)['updates']
                r = requests.post(self.ImageNameCrawlerTaskURL, json=[{'keyword':keyword, 'complete':True, 'image_count':image_count}])
                r_percentage = (r_updates/image_count)*100
                print(f"Keyword: {keyword}\nTime taken to execute the loop: {elapsed_time:.2f} seconds\ntotal images: {image_count}\nimages updated: {r_updates}\npercentage: {r_percentage}")
            else:
                characters = list(string.ascii_lowercase) + [str(i) for i in range(10)]
                characters = [keyword + item for item in characters if len(keyword + item) <= 5]
                new_keywords = [{'keyword': word} for word in characters]
                new_keywords.append({'keyword': keyword, 'complete': True, 'image_count': image_count})
                print(new_keywords)
            
                r = requests.post(self.ImageNameCrawlerTaskURL, json=new_keywords)
        except Exception as e:
            r = requests.post(self.ImageNameCrawlerTaskURL, json=[{'keyword':keyword, 'complete':False, 'error_response':str(e)}]) 
            
    def run_task(self, order='desc'):
        while True:
            self.crawl_task(order)
            # time.sleep(0.1)

if __name__== '__main__':
    order = os.getenv('ORDER')
    if(order == None):
        order = 'desc'
    miner = DockerImageMiner()
    miner.run_task(order)

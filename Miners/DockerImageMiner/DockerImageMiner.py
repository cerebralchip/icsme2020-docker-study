import requests
import json
from fake_headers import Headers
import time
import string
import itertools
import os

class DockerImageMiner:
    """
    A class for mining Docker images from Docker Hub.
    Attributes:
    - DockerHubSearchAPIURL (str): The URL for Docker Hub search API.
    - DockerHubSourceRepoQueryURL (str): The URL for querying Docker Hub source repositories.
    - ImageNameCrawlerTaskURL (str): The URL for the image name crawler task.
    - PostImageURL (str): The URL for posting images.
    - PostDockerHubUserURL (str): The URL for posting Docker Hub users.
    - HEADER (dict): The header for API requests.
    - SEARCH_PARAMETERS (dict): The search parameters for Docker Hub search API.
    Methods:
    - search_url_generator(q, page, order, page_size): Generates the search URL based on the given parameters.
    - header_generator(): Generates the header for API requests.
    - image_parser(image_dict): Parses the image dictionary and returns a parsed dictionary.
    - dockerhubuser_parser(image_dict): Parses the image dictionary and returns a parsed dictionary.
    - crawl_task(order='desc'): Performs the crawling task to mine Docker images.
    - run_task(order='desc'): Runs the crawling task continuously.
    """

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
        """
        Generates a search URL for DockerHub based on the given parameters.

        Parameters:
        - q (str): The search query.
        - page (int): The page number.
        - order (str): The order of the search results. Can be 'desc' for descending order or 'asc' for ascending order.
        - page_size (int): The number of results per page. Default is 10.

        Returns:
        - str: The generated search URL.
        """
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
        """
        Generates the headers for the HTTP request.

        Returns:
            dict: The generated headers.
        """
        headers = self.HEADER
        headers['User-Agent'] = Headers(headers=False).generate()['User-Agent']
        return headers
    
    def image_parser(self, image_dict):
        """
        Parses the given image dictionary and returns a dictionary with the following keys:
        
        - 'image_name': The name of the image.
        - 'publisher': The name of the publisher.
        - 'created_at': The creation date of the image.
        - 'updated_at': The last update date of the image.
        - 'short_description': The short description of the image.
        - 'source': The source of the image.
        - 'certification_status': The certification status of the image.
        - 'complete': A boolean indicating if the parsing is complete.
        
        Parameters:
        - image_dict (dict): The dictionary containing the image information.
        
        Returns:
        - res_dict (dict): The parsed image dictionary.
        """
        res_dict = {}
        res_dict['image_name'] = image_dict['name']
        res_dict['publisher'] = image_dict['publisher']['name']
        res_dict['created_at'] = image_dict['created_at']
        res_dict['updated_at'] = image_dict['updated_at']
        res_dict['short_description'] = image_dict['short_description']
        res_dict['source'] = image_dict['source']
        res_dict['certification_status'] = image_dict['certification_status']
        res_dict['complete'] = False
        return res_dict

    def dockerhubuser_parser(self, image_dict):
        """
        Parses the given image dictionary and returns a dictionary containing the username and UID of the image publisher.

        Parameters:
        - image_dict (dict): A dictionary containing information about the Docker image.

        Returns:
        - res_dict (dict): A dictionary containing the username and UID of the image publisher.
        """
        res_dict = {}
        res_dict['username'] = image_dict['publisher']['name']
        res_dict['uid'] = image_dict['publisher']['id']
        return res_dict
    
    def crawl_task(self, order='desc'):
        """
        Crawls Docker images based on a given keyword and retrieves information about the images and their respective DockerHub users.
        
        Args:
            order (str, optional): The order in which the images should be retrieved. Defaults to 'desc'.
        
        Returns:
            None
        """
        query_session = requests.Session()
        keyword = query_session.get(self.ImageNameCrawlerTaskURL).json()['keyword']
        query_url = self.search_url_generator(q = keyword, page = 1, order = order, page_size=10)
        try:
            res = query_session.get(query_url, headers = self.header_generator())
            image_count = res.json()['count']
            res_images_list = []
            if (image_count<=2500):
                for i in range(0, image_count, 100):
                    query_url = self.search_url_generator(q = keyword, page = int(i/100+1), order = order, page_size=100)
                    res = query_session.get(query_url, headers = self.header_generator())
                    res_images_list += res.json()['summaries']
                    # time.sleep(0.1)
                images = [self.image_parser(item) for item in res_images_list]
                dockerhubusers = [self.dockerhubuser_parser(item) for item in res_images_list]
                r = requests.post(self.PostImageURL, json=images)
                r = requests.post(self.PostDockerHubUserURL, json=dockerhubusers)
                r = requests.post(self.ImageNameCrawlerTaskURL, json=[{'keyword':keyword, 'complete':True, 'image_count':image_count}])
            else:
                characters = list(string.ascii_lowercase)+ [str(i) for i in range(10)]
                characters = [keyword + item for item in characters]
                new_keywords = [{'keyword': word} for word in characters]
                new_keywords.append({'keyword':keyword, 'complete':True, 'image_count':image_count})
                r = requests.post(self.ImageNameCrawlerTaskURL, json=new_keywords)
        except Exception as e:
            r = requests.post(self.ImageNameCrawlerTaskURL, json=[{'keyword':keyword, 'complete':False, 'error_response':str(e)}]) 
            
    def run_task(self, order='desc'):
        """
        Executes the task continuously by crawling the task with the specified order.

        Parameters:
            order (str): The order in which the task should be crawled. Defaults to 'desc'.

        Returns:
            None
        """
        while True:
            self.crawl_task(order)
            # time.sleep(0.1)

if __name__== '__main__':
    order = os.getenv('ORDER')
    if(order == None):
        order = 'desc'
    miner = DockerImageMiner()
    miner.run_task(order)

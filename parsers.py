import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup as bs
import re
import yaml

# Settings are stored in settings.yaml, for example 'about us' URL patterns
f = open('settings.yaml', mode='r', encoding='utf-8')
settings = yaml.safe_load(f)

# Create headers
headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}


# Get SimilarWeb.com data
def similar_web(website_query):
    similar_web_url = 'https://data.similarweb.com/api/v1/data?domain=' + website_query
    session = requests.Session()
    request = session.get(similar_web_url, headers=headers, timeout=10)
    if request.status_code == 200:
        similar_web_data = request.json()
        return similar_web_data
    else:
        error = 'Cannot connect to SimilarWeb'
        return error


# Get Alexa.com data
def alexa(website_query):
    alexa_data = {}
    alexa_url = 'https://www.alexa.com/siteinfo/' + website_query
    session = requests.Session()
    try:
        request = session.get(alexa_url, headers=headers, timeout=10)
        if request.status_code == 200:
            soup = bs(request.content, 'lxml')
            try:
                alexa_rank = soup.find('section', class_='rank')
                alexa_rank = alexa_rank.find('p', class_='big data').text
                alexa_rank = re.sub('\t| |\n|[#]', '', alexa_rank)
                alexa_data['Global rank'] = alexa_rank
            except:
                alexa_data['Global rank'] = 'N/a'

        else:
            error = 'Cannot connect to Alexa'
            return error

    except requests.exceptions.ConnectionError:
        alexa_data['Error'] = 'Connection refused'

    return alexa_data


def plot_similar_web(similar_web_data):
    plot_data = {}

    if similar_web_data != 'Cannot connect to SimilarWeb':

        # TrafficSources Chart
        plot_data['chart'] = {'renderTo': 'chart_ID', 'type': 'column', 'height': 500}
        plot_data['series'] = [{'name': 'Traffic Share', 'data': list(similar_web_data['TrafficSources'].values())}]
        plot_data['title'] = {'text': ''}
        plot_data['xAxis'] = {'categories': list(similar_web_data['TrafficSources'].keys())}
        plot_data['yAxis'] = {'title': {'text': ''}}

        # EstimatedMonthlyVisits Chart
        plot_data['chart_2'] = {'renderTo': 'chart_ID_2', 'type': 'column', 'height': 500}
        plot_data['series_2'] = [
            {'name': 'Traffic volume', 'data': list(similar_web_data['EstimatedMonthlyVisits'].values())}]
        plot_data['title_2'] = {'text': ''}
        plot_data['xAxis_2'] = {'categories': list(similar_web_data['EstimatedMonthlyVisits'].keys())}
        plot_data['yAxis_2'] = {'title': {'text': ''}}

    else:

        # If data is not found TrafficSources
        plot_data['chart'] = None
        plot_data['series'] = None
        plot_data['title'] = None
        plot_data['xAxis'] = None
        plot_data['yAxis'] = None

        # If data is not found EstimatedMonthlyVisits
        plot_data['chart_2'] = None
        plot_data['series_2'] = None
        plot_data['title_2'] = None
        plot_data['xAxis_2'] = None
        plot_data['yAxis_2'] = None

    return plot_data


# Get data from home page
def website_info(website_query):
    url = 'http://' + website_query
    session = requests.Session()
    website_data = {}
    try:
        request = session.get(url, headers=headers, timeout=10)
        if request.status_code == 200:

            # Get data from main page
            soup = bs(request.content, 'lxml')

            # Search title
            try:
                title = soup.find('title').text
            except:
                title = 'Title is not found'

            # Search description
            try:
                description = soup.find('meta', attrs={'name': 'description'})['content']
            except:
                description = 'Description is not found'

            # Search links
            links = []
            try:
                for link in soup.findAll('a'):
                    for pattern in settings['contact_page_pattern']:
                        if re.search(pattern, link['href'], re.IGNORECASE):
                            if re.search(website_query, link['href']):
                                links.append(link['href'])
                            elif re.search('https?:\/\/', link['href']):
                                links.append(link['href'])
                            else:
                                links.append(url + link['href'])
            except:
                pass

            # Search emails. Create a list to store them
            emails = []
            # Search emails on main page
            try:
                email = re.findall(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', soup.text)
                emails.extend(email)
            except:
                pass
                # Search emails on about us pages
            try:
                for link in links:
                    session = requests.Session()
                    request = session.get(link, headers=headers)
                    soup = bs(request.content, 'lxml')
                    email = re.findall(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', soup.text)
                    emails.extend(email)
            except:
                pass

            # Save collected data
            website_data['Title'] = title
            website_data['Description'] = description
            if len(list(dict.fromkeys(links))) > 0:
                website_data['Contact pages'] = list(dict.fromkeys(links))
            else:
                website_data['Contact pages'] = ['Contact us pages not found']
            if len(list(dict.fromkeys(emails))) > 0:
                website_data['Emails'] = list(dict.fromkeys(emails))
            else:
                website_data['Emails'] = ['Emails not found']

        else:
            website_data['Error'] = str(request.status_code) + 'request code'

    except:
        website_data['Error'] = 'Connection refused'

    return website_data


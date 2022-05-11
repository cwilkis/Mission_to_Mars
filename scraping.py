# Import SPlinter and BeautifulSoup
from xmlrpc.client import Marshaller
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt
import pandas as pd
import Mission_to_Mars

def scrape_all():
    #Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)

    data = {
        "news_title": news_title, 
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemiScrape(browser)
    }
    browser.quit()
    return data



def mars_news(browser):
    # Visit the mars nasa news website
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the borwser html to a soup object then quit the broswer
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')


        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        # reformat to get article teaser body
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

def mars_facts():
    try:
        galaxyfacts_df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    galaxyfacts_df.columns=['description', 'Mars', 'Earth']
    galaxyfacts_df.set_index('description', inplace=True)
    
    return galaxyfacts_df.to_html()

def hemiScrape(browser):

    url = 'https://marshemispheres.com/'
    browser.visit(url)

    #Create a list to hold the images and titles.
    hemisphere_image_urls = []

    html = browser.html
    hiRes_soup = soup(html, 'html.parser')
    items = hiRes_soup.find_all('div', 'item')
    
    for item in items:
        hiResLink = 'https://marshemispheres.com/' + str(item.a['href'])
        browser.visit(hiResLink)
        photoSoup = soup(browser.html, 'html.parser')
        title = photoSoup.find('h2', 'title').text
        photo = 'https://marshemispheres.com/' + photoSoup.find('img', 'wide-image')['src']
        hemisphere_image_urls.append({'title': title, 'img_url': photo})
    
    return hemisphere_image_urls

if __name__ == '__main__':
    # If running as script, print scraped data
    print(scrape_all())
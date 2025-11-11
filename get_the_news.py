import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import json

def scrape_news():
   
    url = "https://spbu.ru/news-events"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_data = []
        

        news_section = soup.find('section', class_='section-indent')
        cards = news_section.find_all(class_='page-headline__title')
            
        for card in cards:
            process_data(card, news_data)


        news_section = soup.find('section', class_='section-indent section-clear-sm')
        cards = news_section.find_all(class_='card__title')
            
        for card in cards:
            process_data(card, news_data)
        
        return news_data
        

    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def process_data(card_element, news_data):
   
    try:
        card_container = card_element.find_parent('div', class_=lambda x: x and 'card' in x)
        if not card_container:
            card_container = card_element.find_parent('div')
        
        title = card_element.get_text(strip=True)

        link = ''
        link_element = card_element.find('a') or card_container.find('a') if card_container else None
        if link_element and link_element.get('href'):
            link = link_element['href']
            if link.startswith('/'):
                link = 'https://spbu.ru' + link

        
        description = ''
        if card_container:
            desc_element = card_container.find(class_='content-crop js-crop-text')
            if desc_element:
                description = desc_element.get_text(strip=True)
            else:
                desc_elements = card_container.find_all(['p', 'div'], class_=lambda x: x and x != 'card__title')
                for elem in desc_elements:
                    text = elem.get_text(strip=True)
                    if text and text != title and len(text) > 20:
                        description = text
                        break
        
        date = ''
        if card_container:
            date_elements = card_container.find_all(['time', 'span', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['date', 'time']))
        
            if date_elements:
                date = date_elements[0].get_text(strip=True)
            else:
                date_elements = card_container.find_all(class_='page-headline__date')
                date = date_elements[0].get_text(strip=True)
        
        news_item = {
            'title': title,
            'link': link,
            'date': date,
            'description': description,
        }
        
        news_data.append(news_item)

        
    except Exception as e:
        print(f"Error processing news card: {e}")


def save_data(news_data):

    if not news_data:
        print('')
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    df = pd.DataFrame(news_data)
    csv_filename = f'spbu_news_{timestamp}.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"Data saved as CSV: {csv_filename}")
    

def display_data(news_data):

    if not news_data:
        print('')
        return
    
    for i, news in enumerate(news_data, 1):
        
        print(f"\n Title: {news['title']}")
        print(f"Date: {news['date']}")
        print(f"Description: {news['description'][:100]}..." if len(news['description']) > 100 else f"Description: {news['description']}")
        print(f"Link: {news['link']}")

def main():

    print("URL: https://spbu.ru/news-events")
    
    news_data = scrape_news()
    
    if news_data:
       display_data(news_data)
       save_data(news_data)


main()

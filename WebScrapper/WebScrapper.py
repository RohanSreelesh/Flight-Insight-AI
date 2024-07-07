import time
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests

def fetch_value(soup, tag, key, value):
    element = soup.find(tag, {key: value})
    return element.text if element else np.nan

def parse_rating_table(table):
    ratings = {
        'Aircraft': np.nan, 'Type Of Traveller': np.nan, 'Seat Type': np.nan,
        'Route': np.nan, 'Date Flown': np.nan, 'Seat Comfort': np.nan,
        'Cabin Staff Service': np.nan, 'Food & Beverages': np.nan,
        'Inflight Entertainment': np.nan, 'Ground Service': np.nan,
        'Wifi & Connectivity': np.nan, 'Value For Money': np.nan,
        'Recommended': np.nan
    }
    
    for row in table.find_all('tr'):
        header = row.find('td', class_='review-rating-header').text
        value = row.find('td', class_='review-value')
        if header in ratings:
            if header in ['Seat Comfort', 'Cabin Staff Service', 'Food & Beverages', 
                          'Inflight Entertainment', 'Ground Service', 'Value For Money', 'Wifi & Connectivity']:
                ratings[header] = len(row.find_all('span', class_='star fill'))
            else:
                ratings[header] = value.text if value else np.nan
    
    return ratings

def scrape_airline(airline_name, airline_url, max_pages=5):
    all_reviews = []
    
    for page in range(1, max_pages + 1):
        url = f"{airline_url}/page/{page}/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            articles = soup.find_all('article', {'itemprop': 'review'})
            
            for article in articles:
                review = {}
                review['airline'] = airline_name
                review['overall_rating'] = fetch_value(article, 'span', 'itemprop', 'ratingValue')
                
                div = article.find('div', class_='tc_mobile')
                content = div.find('div', class_='text_content').text.split('|')
                review['verification'] = content[0].strip() if len(content) == 2 else np.nan
                review['review_text'] = content[-1].strip()
                
                table = div.find('table', class_='review-ratings')
                review.update(parse_rating_table(table))
                
                all_reviews.append(review)
            
            print(f"Scraped page {page} for {airline_name}")
            time.sleep(2)
            
        except requests.RequestException as e:
            print(f"Error scraping {airline_name} page {page}: {e}")
            break
    
    return pd.DataFrame(all_reviews)

# List of top airlines to scrape
airlines = [
    ("Air Canada", "https://www.airlinequality.com/airline-reviews/air-canada"),
    ("Lufthansa", "https://www.airlinequality.com/airline-reviews/lufthansa"),
    ("Emirates", "https://www.airlinequality.com/airline-reviews/emirates"),
    ("Qatar Airways", "https://www.airlinequality.com/airline-reviews/qatar-airways"),
    ("Singapore Airlines", "https://www.airlinequality.com/airline-reviews/singapore-airlines"),
    ("ANA", "https://www.airlinequality.com/airline-reviews/ana-all-nippon-airways"),
    ("Etihad Airways", "https://www.airlinequality.com/airline-reviews/etihad-airways"),
    ("Qantas", "https://www.airlinequality.com/airline-reviews/qantas-airways"),
    ("Japan Airlines", "https://www.airlinequality.com/airline-reviews/japan-airlines"),
    ("British Airways", "https://www.airlinequality.com/airline-reviews/british-airways")
]

# Scrape data for each airline
for airline_name, airline_url in airlines:
    print(f"Scraping data for {airline_name}...")
    df = scrape_airline(airline_name, airline_url)
    df.to_csv(f"{airline_name.replace(' ', '_')}_reviews.csv", index=False)
    print(f"Data for {airline_name} saved to {airline_name.replace(' ', '_')}_reviews.csv")
    time.sleep(5)  # Wait between airlines to avoid overloading the server

print("Scraping completed for all airlines.")
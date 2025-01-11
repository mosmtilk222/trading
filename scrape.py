import requests

def get_crypto_news():
    url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
    response = requests.get(url)
    news = response.json()
    
    # Extract and format just the important information
    formatted_news = []
    for article in news['Data']:
        formatted_article = {
            'title': article['title'],
            'source': article['source'],
            'published_at': article['published_on'],
            'url': article['url'],
            'summary': article['body']
        }
        formatted_news.append(formatted_article)
    
    return formatted_news

def print_news_nicely(news_list):
    for i, article in enumerate(news_list, 1):
        print(f"\n{'-'*80}")
        print(f"Article {i}:")
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"URL: {article['url']}")
        print(f"\nSummary: {article['summary']}")
        print(f"{'-'*80}")

# Get and print the news
news = get_crypto_news()
print_news_nicely(news)

# Alternatively, for raw JSON formatting:
# print(json.dumps(news, indent=2))

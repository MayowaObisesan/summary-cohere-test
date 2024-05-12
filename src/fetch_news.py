from newsapi import NewsApiClient

# Init
newsapi = NewsApiClient(api_key='5e53adf3f76e4563a808311fbdf158f9')

top_headlines = newsapi.get_top_headlines(q="", sources="fox-news")

print(top_headlines)
# print(newsapi.get_sources())
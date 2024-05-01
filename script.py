import requests
from bs4 import BeautifulSoup
import datetime
import time

def fetch_details(article_url):
    try:
        response = requests.get(article_url)  # Запрос к странице статьи
        response.raise_for_status()  # Проверка на успешный ответ от сервера
        soup = BeautifulSoup(response.text, 'html.parser')  # Создание объекта BeautifulSoup для парсинга HTML
        author_tag = soup.find('span', class_='byline__author__text')  # Поиск тега с информацией об авторе
        author = author_tag.get_text(strip=True) if author_tag else "Unknown author"  # Извлечение имени автора
        article_text = ' '.join(p.get_text(strip=True) for p in soup.find_all('p'))  # Извлечение текста статьи
        keywords = ["Republican", "Democratic", "GOP", "Democrats"]  # Ключевые слова для поиска
        found_keywords = [keyword for keyword in keywords if keyword in article_text]  # Поиск ключевых слов в тексте
        return author, article_text, found_keywords
    except Exception as e:
        print(f"Error fetching article details: {e}")
        return "Unknown author", "", []

def fetch_news(processed_urls):
    url = "https://www.cbsnews.com/"  # URL главной страницы новостного сайта
    try:
        response = requests.get(url)  # Запрос к главной странице
        response.raise_for_status()  # Проверка на успешный ответ от сервера
        soup = BeautifulSoup(response.text, 'html.parser')  # Создание объекта BeautifulSoup для парсинга HTML
        articles = soup.find_all('article')  # Поиск всех статей на странице
        news_list = []  # Список для хранения информации о новостях
        for article in articles:
            link = article.find('a')  # Поиск ссылки на статью
            if link and 'href' in link.attrs and link['href'].startswith('http'):
                article_url = link['href']  # URL статьи
                if article_url not in processed_urls:  # Проверка, не обрабатывалась ли статья ранее
                    processed_urls.add(article_url)  # Добавление URL в список обработанных
                    title_tag = article.find('h4', class_='item__hed')  # Поиск тега с заголовком статьи
                    title = title_tag.get_text(strip=True) if title_tag else "No title"  # Извлечение заголовка
                    summary_tag = article.find('p', class_='item__dek')  # Поиск тега с кратким описанием статьи
                    summary = summary_tag.get_text(strip=True) if summary_tag else "No summary"  # Извлечение описания
                    author, full_text, found_keywords = fetch_details(article_url)  # Извлечение дополнительной информации о статье
                    if found_keywords:  # Проверка на наличие ключевых слов
                        news_list.append((title, author, summary, article_url, found_keywords))  # Добавление новости в список
        return news_list
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def log_news(news_list, file_path):
    with open(file_path, 'a', encoding='utf-8') as file:
        for title, author, summary, url, keywords in news_list:
            file.write('--------------------------------------------------------\n')
            file.write(f"Title: {title}\n")
            file.write(f"Author: {author}\n")
            file.write(f"Summary: {summary}\n")
            file.write(f"URL: {url}\n")
            file.write(f"Found Keywords: {', '.join(keywords)}\n")
            file.write('--------------------------------------------------------\n')

def main(duration_hours=4):
    processed_urls = set()  # Множество для отслеживания обработанных URL
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # Текущее время для создания имени файла
    log_file = f"cbsnews_log_{current_time}.txt"  # Имя лог-файла
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Log started at {datetime.datetime.now()}\n")  # Запись времени начала лога
    end_time = datetime.datetime.now() + datetime.timedelta(hours=duration_hours)  # Рассчитываем время окончания работы скрипта
    while datetime.datetime.now() < end_time:
        news = fetch_news(processed_urls)  # Получаем список новостей
        log_news(news, log_file)  # Записываем новости в лог-файл
        time.sleep(600)  # Пауза 10 минут перед следующим запросом
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Log ended at {datetime.datetime.now()}\n")  # Запись времени завершения лога

if __name__ == "__main__":
    main()

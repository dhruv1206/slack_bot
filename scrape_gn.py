from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService


def scrape_google_news(topic:str):
    print("Scraping Google News")
    # Create a ChromeOptions object to disable the browser notification
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode
    chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration (necessary for headless mode)

    # Create a Chrome web driver
    driver = webdriver.Chrome(options=chrome_options)

    topic = '+'.join(topic.split(" "))
    # Open Google News
    driver.get(f'https://news.google.com/search?q={topic}&hl=en-IN&gl=IN&ceid=IN%3Aen')

    # Find the top 5 news articles and print their titles and URLs
    results = driver.find_elements(
        By.XPATH, "//a[@class='JtKRv']")
    top_5_results = results[:5]

    news_data = []
    for result in top_5_results:
        title = result.text
        url = result.get_attribute('href')
        news_data.append({'title': title, 'url': url})

    # Close the browser window
    driver.quit()

    return news_data

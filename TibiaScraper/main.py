from scraper import Scraper
from DatabaseConnector import DatabaseConnector
from multiprocessing import Process, Queue

queue = Queue()
connector = DatabaseConnector.DatabaseConnector()
scraper1 = Scraper()
scraper2 = Scraper()

first_url = 'https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades&currentpage=1'
second_url = 'https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades&currentpage=100'


if __name__ == "__main__":
    Process(target=scraper1.scrape_site, args=(first_url, queue)).start()
    # Process(target=scraper2.scrape_site, args=(second_url, queue)).start()
    Process(target=connector.store, args=(queue,)).start()

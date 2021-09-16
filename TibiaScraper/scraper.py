import re
from bs4 import BeautifulSoup
import requests
import random
import time
from DatabaseConnector.DatabaseConnector import Characters


class Scraper:
    def __init__(self):
        pass

    def startup(self, url):
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)"
            "AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept": "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/webp,*/*;q=0.8",
        }
        req = session.get(url, headers=headers)
        bs = BeautifulSoup(req.text, "html.parser")
        return bs

    def get_auctions(self, bs):
        auctions = bs.find_all(class_="Auction")
        return auctions

    def get_char_info(self, auction):
        raw_character_info = auction.find(class_="AuctionHeader").text
        return raw_character_info

    def get_auction_end_date(self, auction):
        auction_end = (
            auction.find(class_="AuctionBodyBlock ShortAuctionData")
            .find_all(class_="ShortAuctionDataValue")[1]
            .text
        )
        auction_end = auction_end.split(",")
        auction_end = auction_end[0].replace(u"\xa0", u" ")
        return auction_end

    def get_character_price(self, auction):
        current_bid = (
            auction.find(class_="ShortAuctionDataBidRow")
            .find(class_="ShortAuctionDataValue")
            .text
        )
        current_bid = current_bid.replace(",", "")
        return current_bid

    def get_auction_id(self, auction):
        auction_link = auction.find(class_="AuctionCharacterName").find("a")["href"]
        auction_id = re.match(".*auctionid=(\d*)", auction_link).group(1)
        return auction_id

    def get_current_page(self, url):
        current_page = re.match(".*page=(\d*)", url).group(1)
        current_page = int(current_page)
        return current_page

    def get_last_page(self, bs):
        link = bs.find_all(class_="PageLink FirstOrLastElement")[1].find("a")["href"]
        last_page = re.match(".*page=(\d*)", link).group(1)
        return last_page

    def format_character_info(self, auction):
        raw_character_info = self.get_char_info(auction)
        # gets string in form:
        # nameLevel: number | Vocation: vocation | gender | World: world
        formatted_char_info = re.match(
            "(.*)Level:\s(\d+) \| Vocation: (\w+\s?\w+?) \| (\w+) \| World: (\w+)",
            raw_character_info,
        )

        basic_char_info = {
            "name": "name",
            "level": "level",
            "vocation": "vocation",
            "gender": "gender",
            "world": "world",
        }
        i = 1
        for key in basic_char_info.keys():
            basic_char_info[key] = formatted_char_info.group(i)
            i += 1

        return basic_char_info

    def create_orm(self, auction):
        """Format character info into ORM."""

        basic_char_info = self.format_character_info(auction)
        name = basic_char_info["name"]
        level = basic_char_info["level"]
        vocation = basic_char_info["vocation"]
        gender = basic_char_info["gender"]
        world = basic_char_info["world"]
        auction_end = self.get_auction_end_date(auction)
        current_price = self.get_character_price(auction)
        auction_id = self.get_auction_id(auction)

        character_info = Characters(
            name,
            level,
            vocation,
            gender,
            world,
            auction_end,
            current_price,
            auction_id,
        )

        return character_info

    def scrape_site(self, url, queue):
        bs = self.startup(url)
        auctions = self.get_auctions(bs)

        for auction in auctions:
            orm = self.create_orm(auction)
            queue.put(orm)

        current_page = self.get_current_page(url)
        last_page = self.get_last_page(bs)
        print("scraping site", current_page)
        if current_page == last_page:
            print("finished scraping, starting anew")
            current_page = 1

        time.sleep(10)
        try:
            self.scrape_site(
                "https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades&currentpage={}".format(
                    current_page + 1
                ),
                queue,
            )
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

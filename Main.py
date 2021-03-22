import json

import requests
import re


# REGEX HELPER FUNCTION
def parseInfo(i, namePattern, pricePattern, hRefPattern, printing=False):
    nameVal, priceVal, linkVal = '', '', ''

    name = re.search(namePattern, i)
    price = re.search(pricePattern, i)
    link = re.search(hRefPattern, i)

    if name[0]:
        nameVal = name.group(1)
        if printing: print("name: ", )

    if price[0]:
        priceVal = price.group(1)
        if printing: print("price: ", price.group(1))

    if link[0]:
        linkVal = link.group(1)
        if printing: print("href: ", link.group(1))

    if printing: print('---------------------------')
    return nameVal, priceVal, linkVal


# Master Ebay Parser, Create 1 per session
class EbayParser:
    ebayRegexPattern = r'<li class="s-item.+?s-item--watch-at-corner" data-view=mi:\d{0,10}\|iid:\d{0,10}\>(.+?)\<!--M\/--><\/li><!--F\/--><!--F#p_0-->'
    pricePattern = r'<span.{0,100}?price>(\$.+?)</span>'
    namePattern = r'<h3.+?>(.+?)</h3>'
    hRefPattern = r'class=s-item__link href=(https:\/\/www.ebay.com\/.+?\?)'
    listings = []

    def __init__(self):
        self.listings: [VideoCardListing] = []

    def parsePage(self, pageUrl):
        user_agent_str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                         + "AppleWebKit/537.36 (KHTML, like Gecko) " \
                         + "Chrome/78.0.3904.97 " \
                         + "Safari/537.36"
        headers = {
            "user-agent": user_agent_str
        }
        req = requests.get(pageUrl, headers)

        text = req.text
        # print(text)

        # PARSE WHOLE PAGE ON EBAY TO SINGLE DOWN TO AN ARRAY OF LISTINGS
        x = re.findall(self.ebayRegexPattern, text)

        # PARSE THROUGH EACH LISTING FOUND ON PAGE
        for i in range(len(x)):
            # CONVERT HTML INFO TO PYTHON CLASS AND SAVE IN AN ARRAY FOR EASY ACCESS
            newItem = parseInfo(x[i], self.namePattern, self.pricePattern, self.hRefPattern)
            self.addListingWO(VideoCardListing(newItem[0], newItem[1], newItem[2]))

    def addListing(self, name, price, href):
        self.listings.append(VideoCardListing(name, price, href))

    def addListingWO(self, jsonEbayListing):
        self.listings.append(jsonEbayListing)
        print(len(self.listings))

    def printAllListings(self):
        for c in self.listings:
            print("Name: " + c.name)
            print("Price: " + c.price)
            print("Link: " + c.href)
            print('------------------------')

    def dumpAllListingsToJson(self) -> str:
        returnString = '['
        for c in self.listings:
            j = json.dumps(c.__dict__)
            print(j)
            if j != "{}":
                returnString = returnString + j + ", "
        return returnString[0:-2] + ']'

    @staticmethod
    def saveToFile(string, path) -> None:
        with open(path, 'w') as f:
            f.write(string)

    def saveCurrentListingsToFIle(self, path) -> None:
        j = self.dumpAllListingsToJson()
        self.saveToFile(j, path)

    def prettyPrintJsonToFile(self, path):
        with open(path, 'w') as f:
            f.write('[\n')
            c = 0
            for i in self.listings:
                if c != len(self.listings):
                    f.write('\t' + i.getJson() + ', \n')
                else:
                    f.write('\t' + i.getJson() + '\n')
                c += 1
            f.write(']')


# Ebay Listing Class for easy serialization to JSON
class VideoCardListing:
    name, href = '', ''
    price = 0

    def __init__(self, name, price, href):
        self.name = name
        self.price = price
        self.href = href

    def getJson(self):
        return json.dumps(self.__dict__)


# CREATE AN INSTANCE OF OUR PARSER
ebayParser = EbayParser()

# PARSE AN EBAY PAGE // MAYBE SET UP CODE TO HAVE IT SEARCH FOR A KEYWORD AND THEN PARSE THE FOLLOWING PAGE?
ebayParser.parsePage("https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=gpu&_sacat=0")

# SAVE OUR LISTINGS TO A JSON FILE
ebayParser.prettyPrintJsonToFile('testingEbay.json')

# ITERATES THROUGH ALL LISTINGS IN OUR MAIN ARRAY AND PRINTS THEM 1 by 1
ebayParser.printAllListings()

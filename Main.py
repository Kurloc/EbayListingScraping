import json
import time

import requests
import re

# # # STATIC METHODS # # #
# REGEX HELPER FUNCTION #
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

# PRINT JSON TO FILE WITH NICE NEWLINES AND TABS #
def prettyPrintJsonToFile(path, array) -> None:
    with open(path, 'w') as f:
        f.write('[\n')
        c = 0
        for listing in array:
            if c != len(array):
                f.write('\t' + listing.getJson() + ', \n')
            else:
                f.write('\t' + listing.getJson() + '\n')
            c += 1
        f.write(']')

# SAVE STRING STRAIGHT TO FILE ON TOP LINE #
def saveToFile(string, path) -> None:
    with open(path, 'w') as f:
        f.write(string)


# Master Ebay Parser, Create 1 per session
class EbayScrapeNParser:
    currentPage = 0

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
        self.currentPage += 1

    # Pass in the front page for a search result and go
    # Pass in how many pages, back pages can be junk so guess on how many good pages there are
    def parseAllPages(self, pageUrl, howManyPages):
        for i in range(howManyPages):
            pageInfo = '&_pgn=' + str(self.currentPage) + '&rt=nc'
            self.parsePage(pageUrl + pageInfo)
            time.sleep(2)

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

    def saveCurrentListingsToFile(self, path) -> None:
        j = self.dumpAllListingsToJson()
        saveToFile(j, path)

    def loadJsonFromFile(self, path):
        with open(path, 'r') as f:
            jsonTextArray = f.readlines()
            print(len(jsonTextArray))
            jsonTextArray = jsonTextArray[1:-1]
            self.listings = []
            for line in jsonTextArray:
                cleanLine = (line.replace('\t', '', 1).replace('\n', '', 1))
                cleanLine = cleanLine[:-2]
                j = json.loads("[" + cleanLine + "]")[0]
                self.addListing(j['name'], j['price'], j['href'])

    def prettyPrintJsonToFile(self, path):
        prettyPrintJsonToFile(path, self.listings)

    def searchMyListingsByPrice(self, minPrice, maxPrice) -> []:
        returnArray = []
        for listing in self.listings:
            price = float(listing.price.replace('$', '').replace(',', ''))
            if float(maxPrice) >= price >= float(minPrice):
                returnArray.append(listing)
        return returnArray

# Ebay Listing Class for easy serialization to JSON #
class VideoCardListing:
    name, href = '', ''
    price = 0

    def __init__(self, name, price, href):
        self.name = name
        self.price = price
        self.href = href

    def getJson(self):
        return json.dumps(self.__dict__)


# # # DO A WEB SCRAPE ON SOME EBAY PAGES # # #
# CREATE AN INSTANCE OF OUR PARSER #
ebayParser = EbayScrapeNParser()

# PARSE AN EBAY PAGE // MAYBE SET UP CODE TO HAVE IT SEARCH FOR A KEYWORD AND THEN PARSE THE FOLLOWING PAGE? #
# Seems to crash after 5 pages by hanging up, I haven't debugged what is going on. #
ebayParser.parseAllPages("https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=gpu&_sacat=0", 5)

# Save Json to a file
ebayParser.prettyPrintJsonToFile('testingEbay.json')
# # # END OF A WEB SCRAPE # # #


# # # LOAD AND ANALYSIS ON SAVED LISTINGS # # #
# SAVE OUR LISTINGS TO A JSON FILE
ebayParser.loadJsonFromFile('testingEbay.json')

# ITERATES THROUGH ALL LISTINGS IN OUR MAIN ARRAY AND PRINTS THEM 1 by 1 #
ebayParser.printAllListings()

# SOME CODE TO SEARCH CURRENT LISTINGS SCRAPED/LOADED AND SAVE RESULTS TO A FILE FOR FURTHER ANALYSIS
x = ebayParser.searchMyListingsByPrice(50, 500)
for i in x:
    print('name: ' + i.name)
    print('price: ' + i.price)

prettyPrintJsonToFile('testingEbayPriceSearch.json', x)
# # # END OF ANALYSIS ON SAVED LISTINGS # # #

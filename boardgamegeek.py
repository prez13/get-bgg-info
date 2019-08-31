from selenium import webdriver
import bs4
import requests
import math
import os
import pygsheets
import pandas as pd
from datetime import datetime


class BGG:

    # Class Object Attributes
    browse_boardgame_url = r'https://boardgamegeek.com/browse/boardgame/page'
    boardgame_url_root = 'https://boardgamegeek.com/boardgame/'
    browse_pages_filename = r'browse_pages_content.txt'
    cache_game_pages_rel_path = r'./cache/game_pages/'  # ./ is important
    class_name_type = "Type"
    class_name_category = "Category"
    class_name_mechanism = "Mechanism"
    class_name_family = "Family"
    classifications = (class_name_type,
                       class_name_category,
                       class_name_mechanism,
                       class_name_family,
                       )
    google_drive_folder_id = '1crYljyXOyZjEE0pou_irdihXh205e7mW'  # '1WFwSv2g2tltsdDtmzka_BuyFhag8sPaP'
    google_sheet_col_names = {'age': 'Age',
                              'age_community': 'Age comm',
                              'id': 'ID',
                              'players_community': 'Num pl comm',
                              'players_community_best': 'Num pl comm best',
                              'playing_time_max': 'Pl time max',
                              'playing_time_min': 'Pl time min',
                              'rank_overall': 'Rank',
                              'rating': 'Rating',
                              'avg_rating': 'Avg rating',
                              'geek_rating': 'Geek rating',
                              'num_voters': 'Num voters',
                              'title': 'Title',
                              'title_url': 'Title URL',
                              'year': 'Year',
                              'weight': 'Weight',
                              'playstyle': 'Playstyle',
                              class_name_type.lower(): class_name_type,
                              class_name_category.lower(): class_name_category,
                              class_name_mechanism.lower(): class_name_mechanism,
                              class_name_family.lower(): class_name_family,
                              'link': 'Link',
                              'price_list': 'Price list',
                              'price_amazon_lowest': 'Price Amz lowest',
                              'price_amazon_new': 'Price Amz new',
                              'price_ios':'Price iOS',
                              'all_time_plays':'Plays all',
                              'fans' : 'Fans',
                              'all_time_plays_year' : 'Plays year',
                              'own' : 'Own',
                              }
    google_sheet_col_order = [
        'Rank',
        'Title',
        'Year',
        'Rating',
        'Avg rating',
        'Geek rating',
        'Num voters',
        'Plays all',
        'Plays year',
        'Fans',
        'Own',
        'Num pl comm',
        'Num pl comm best',
        'Pl time min',
        'Pl time max',
        'Age',
        'Age comm',
        'Playstyle',
        'Weight',
        'Price list',
        'Price Amz lowest',
        'Price Amz new',
        'Price iOS',
        class_name_type,
        class_name_category,
        class_name_mechanism,
        class_name_family,
        'Link',
        # 'ID',
        # 'Title URL',
    ]
    google_worksheet_name = 'BGG'
    google_worksheet_cols = 20


    def __init__(self, number_of_games):
        self.number_of_games = number_of_games
        print("Initializing instance")

        #from selenium import webdriver
        self.browser = webdriver.Chrome("C:\Program Files (x86)\Chromedriver\chromedriver.exe")


    def get_bggratings(self, soup, x):
        """Returns geek rating, avg rating, and num voters as list
        """

        #import bs4

        tdtags = soup.find_all("td", {"class": "collection_bggrating"})[3*x:3*x+3]
        tdvalues = []
        for t in tdtags:
            tdvalues.append(t.getText().strip())
        print(tdvalues)
        return tdvalues


    def get_prices(self, browser):
        """Returns all prices from BGG browse page"""

        elms = browser.find_elements_by_class_name("collection_shop")
        l = []  # list of games

        for el in elms:
            d = {}  # dict of prices per game

            try:
                d['price_list'] = el.get_attribute("innerHTML").split("List:&nbsp;")[1].split('\n\t\t')[0]
                #print("YAY price list!")
            except:
                d['price_list'] = ''
                #pass

            try:
                d['price_amazon_lowest'] = el.get_attribute("innerHTML").split('Lowest Amazon:&nbsp;<span class="positive">')[1].split(
                    '</span>')[0]
                #print("YAY lowest amazon list!")
            except:
                d['price_amazon_lowest'] = ''
                #pass

            try:
                d['price_amazon_new'] = el.get_attribute("innerHTML").split('New Amazon:&nbsp;<span class="positive">')[1].split(
                    '</span>')[0]
                #print("YAY amazon new!")
            except:
                d['price_amazon_newest'] = ''
                #pass

            try:
                d['price_ios'] = el.get_attribute("innerHTML").split('iOS App: <span class="positive">')[1].split('</span>')[0]
            except:
                d['price_ios'] = ''

            l.append(d)

        del l[0]  # remove first, empty element

        return l


    def get_browse_page_attrs(self, content, browser):
        """Get titles and ids from content
        to be able to call the individual pages
        of games later on

        Output: list of dicts that contain both keys and values
                for title and it
        """

        #import bs4

        list_w_titles_ids = []

        soup = bs4.BeautifulSoup(content, "lxml")
        #print(soup)
        #print(content)

        prices = self.get_prices(browser)
        print(prices)

        # Loop through all css ids (one cssid for each game)
        for x in range(1, 101):  # not including 101

            d = {}
            css_id = 'results_objectname{}'.format(x)
            # print(css_id)
            print(x)

            # Get relevant html section for a game
            results = soup.select('#{}'.format(css_id))
            #print("-------------------------------")
            #print(results)
            """
            [<div id="results_objectname66" onclick="" style="z-index:1000;">
<a href="/boardgame/150376/dead-winter-crossroads-game">Dead of Winter: A Crossroads Game</a>
<span class="smallerfont dull">(2014)</span>
</div>]
            """
            #print("-------------------------------")
            if len(results) == 0:
                # Means we went through all the 100 games on the page
                break
            results2 = results[0].select('a')
            # print(results2)

            # Get title, title_url, and id
            title = results2[0].getText()
            title_url = str(results2[0]).split('/')[3].split('"')[0]
            id_ = int(str(results2[0]).split('/')[2])
            try:
                year = results[0].select('span')[0].getText()[1:-1]
            except:
                year = ''

            # Build dict
            (
                d['geek_rating'],
                d['avg_rating'],
                d['num_voters']
            ) = self.get_bggratings(soup, x-1)

            #(
            #    d['price_list'],
            #    d['price_amazon_lowest'],
            #    d['price_amazon_new'],
            #) = prices[x-1]

            d['title'] = title
            d['title_url'] = title_url
            d['id'] = id_
            d['year'] = year
            d['link'] = f'{self.boardgame_url_root}{id_}/{title_url}'
            # https://boardgamegeek.com/boardgame/174430/gloomhaven

            d_prices = prices[x-1]
            d.update(d_prices)

            list_w_titles_ids.append(d)

        return list_w_titles_ids


    def scrape_browse_pages(self):
        """Scrape browse boardgame pages
        Input: number_of_pages (optional) as integer
        Ouput: content (of pages) as string
        """
        #import requests
        #import math

        list_w_titles_ids = []

        number_of_pages = int(math.ceil(self.number_of_games / 100))

        for page_number in range(1, number_of_pages + 1):
            print(page_number)

            url_w_page_number = '{}/{}'.format(self.browse_boardgame_url, page_number)
            print(url_w_page_number)

            # With selenium
            self.browser.get(url_w_page_number)
            b_page_content = self.browser.page_source
            titles_and_ids_per_browse_page = self.get_browse_page_attrs(b_page_content, self.browser)

            list_w_titles_ids = list_w_titles_ids + titles_and_ids_per_browse_page

        return list_w_titles_ids


    def write_content_to_file(self, content, filename=browse_pages_filename):
        """Write content to file
        Input: content as string
        Output: None
        """

        with open(filename, 'wb+') as f:
            f.write(str(content).encode('utf-8', 'replace'))


    def read_content_from_file(self, filename=browse_pages_filename):
        """Read browse games pages content from file"""
        # content = ''

        with open(filename, 'rb') as f:
            content = f.read()

        return content


    def get_info_per_game(self, list_games, use_cache=True):
        """Open the individual game pages and get info
        Input: list of dict with titles and ids
        Output list of dics with additional info like
               recommended age.
        """

        #from selenium import webdriver
        #import os

        # Build abs. from rel. path
        cache_game_pages_abs_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                 self.cache_game_pages_rel_path)
        print(cache_game_pages_abs_path)

        l_d = []
        #browser = webdriver.Chrome("C:\Program Files (x86)\Chromedriver\chromedriver.exe")
        counter = 0

        for game in list_games:
            if counter >= self.number_of_games:
                break

            local_game_file = f'{cache_game_pages_abs_path}{game["title_url"]}_{game["id"]}.html'

            # If the html page source exists in a local file (cache), use this
            if os.path.isfile(local_game_file) and os.path.getsize(local_game_file) > 0 and use_cache == True:
                print("Reading game content from file...")
                with open(local_game_file, 'rb') as f:
                    page_content = f.read()

            # If there is no local version of the html page source, get
            # it from the net and write it into a file
            else:
                # File does not exists, so get page source from the net and write into file
                # Build URL
                print("Reading game content from Internet")
                boardgame_url = '{}{}/{}'.format(self.boardgame_url_root, game['id'], game['title_url'])
                print(boardgame_url)

                self.browser.get(boardgame_url)
                page_content = self.browser.page_source

                with open(local_game_file, 'wb+') as f:
                    f.write(str(page_content).encode('utf-8', 'replace'))

            d_attributes = self.get_attributes(page_content)
            d_attributes.update(game)  # add id, title, and title_url to dict (game is dict, too)

            # NEW: get stats (e.g. all time plays)
            d_stats = self.get_stats(boardgame_url, game['id'], d_attributes['year2'])
            d_attributes.update(d_stats)

            l_d.append(d_attributes)

            counter += 1

        #browser.quit()

        return l_d


    def get_stats(self, boardgame_url, game_id, year2):
        """Get more numbers from separate stats page,
        such as all time plays.
        
        return:
            d_stats (dict): stats
        """

        boardgame_stats_url = f'{boardgame_url}/stats'

        self.browser.get(boardgame_stats_url)
        page_content = self.browser.page_source        

        game_name = boardgame_url.split('/')[-1]

        d_stats_attributes = self.get_stats_attributes(page_content, game_id, year2, game_name)

        return d_stats_attributes


    def get_stats_attributes(self, html_text, game_id, year2, game_name):
        """Get statistics attributes from separate page,
        such as all time plays.

        Input:
            page_content (str): html
        Return:
            dict
        """

        #import bs4

        d = {}
        soup = bs4.BeautifulSoup(html_text, "lxml")

        #import pdb; pdb.set_trace()

        # ALl time plays
        try:
            d['all_time_plays'] = soup.findAll("a", {"ng-href" : f"/playstats/thing/{game_id}"})[0].getText().replace(',','')
        except:
            d['all_time_plays'] = 'Could not get'


        # All time plays, per year
        year_on_market = datetime.now().year - int(year2)
        if year_on_market != 0:
            d['all_time_plays_year'] = int(int(d['all_time_plays']) / year_on_market)
        else:
            d['all_time_plays_year'] = 'not old enough'

        #import pdb; pdb.set_trace()

        # Fans
        try:
            d['fans'] = soup.findAll("a", {"href" : f"/fans/thing/{game_id}"})[2].getText().replace(",", "")
        except:
            d['fans'] = 'Could not get'

        # Own
        try:
            d['own'] = soup.findAll("a", {"href" : f"/boardgame/{game_id}/{game_name}/ratings?status=own"})[0].getText().replace(',','')
        except:
            d['own'] = 'Could not get'
            # soup.findAll("a", {"href":"/boardgame/174430/gloomhaven/ratings?status=own"})[0].getText()

        #import pdb; pdb.set_trace()

        print(d)
        return d


    def get_playstyle(self, soup):
        """Get playstyle (competitive or cooperative) from soup object.
        bs4 already needs to be imported."""

        r = soup.find("ul", class_="features")
        if "operative Play" in str(r):
            return "Co-operative"
        else:
            return "Competitive"


    def get_classification(self, soup):
        """Get game classification. BS4 already needs to be imported.
        Return: dictionary with keys being the classifictation types
        """

        r = soup.find("ul", class_="features")
        d = {}

        for c in self.classifications:
            for litag in r.find_all('li'):
                if c in litag.getText():
                    for atag in litag.find_all('a'):
                        if not " more " in atag.getText():
                            d[c] = d.get(c, "")  + atag.getText() + ";"  # d.get to avoid keyError
        return d


    def get_attributes(self, html_text):
        """Extract attributes
        Input: html
        Output: list of dicts"""

        #import bs4

        d = {}
        sep = "–"
        soup = bs4.BeautifulSoup(html_text, "lxml")

        try:
            d['age'] = soup.findAll("span",
                               {"ng-if": "::geekitemctrl.geekitem.data.item.minage > 0"})[0].getText().split()[0][:-1]  # everything except last item (+ sign, e.g. 14+)
        except:
            d['age'] = ''

        try:
            d['age_community'] = \
            soup.findAll("span",
                         {"ng-bind-html": "geekitemctrl.geekitem.data.item.polls.playerage|to_trusted"})[0].getText()
        except:
            d['age_community'] = ''

        try:
            d['rank_overall'] = soup.select('.rank-value')[0].getText().split()[0]
        except:
            d['rank_overall'] = ''

        players_community = None
        try:
            players_community_list = soup.findAll("span",
           {"ng-show": "::geekitemctrl.geekitem.data.item.polls.userplayers.totalvotes > 0"})[0].getText().split()
        except:
            players_community_list = ''

        if len(players_community_list) > 1:  # Has '2, 4' for example
            players_community = '{}, {}'.format(players_community_list[0][:-1], players_community_list[1])
        elif len(players_community_list) == 1:
            players_community = players_community_list[0]

        d['players_community'] = players_community

        """
        # NOT IN USE
        players_community_min = players_community.split(sep)[0]  # 1-2 or 2

        players_community_max = players_community_min
        if "–" in players_community:
            players_community_max = players_community.split("–")[1]
        """

        try:
            d['players_community_best'] = \
            soup.findAll("span",
                         {"ng-show": "::geekitemctrl.geekitem.data.item.polls.userplayers.totalvotes > 0"})[
                1].getText().split("Best: ")[1].strip()
        except:
            d['players_community_best'] = ''

        try:
            d['rating'] = soup.findAll("span", {"ng-show": "showRating"})[0].getText().split()[0]
        except:
            d['rating'] = ''

        try:
            playing_time = soup.findAll("span", {"min": "::geekitemctrl.geekitem.data.item.minplaytime"})[0].getText()
        except:
            playing_time = ''
        if sep in playing_time:
            playing_time_min = playing_time.split(sep)[0]
            playing_time_max = playing_time.split(sep)[1]
        else:
            playing_time_min = playing_time_max = playing_time

        d['playing_time_min'] = playing_time_min
        d['playing_time_max'] = playing_time_max

        try:
            d['weight'] = soup.findAll("span",
                {"ng-show": "geekitemctrl.geekitem.data.item.polls.boardgameweight.votes > 0"})[0].getText().split()[0].strip()
        except:
            d['weight'] = ''

        d['playstyle']= self.get_playstyle(soup)

        d_classifications = self.get_classification(soup)  # need to make this right here
        d[self.class_name_type.lower()] = d_classifications.get(self.class_name_type, "None")
        d[self.class_name_category.lower()] = d_classifications.get(self.class_name_category, "None")
        d[self.class_name_mechanism.lower()] = d_classifications.get(self.class_name_mechanism, "None")
        d[self.class_name_family.lower()] = d_classifications.get(self.class_name_family, "None")

        d['year2'] = soup.findAll("span", {'ng-if' : 'geekitemctrl.geekitem.data.item.yearpublished && geekitemctrl.geekitem.data.item.yearpublished !=="0"'})[0].getText().replace("(", "").replace(")", "").strip()

        print(d)
        return d


    def bgg2gsheets(self, d):
        """Write dict into Google sheet
        """

        #import pygsheets
        #import pandas as pd
        #from datetime import datetime

        df = pd.DataFrame(d)
        df.rename(columns=self.google_sheet_col_names, inplace=True)
        df = df[self.google_sheet_col_order]

        gc = pygsheets.authorize(outh_file='client_secret_734903773822-0vv2nu579q13i9v236mbl27o317icmij.apps.googleusercontent.com.json')
        #gc = pygsheets.authorize()  # previously
        gsheet_name = datetime.now().strftime("%Y%m%d-%H%M%S")
        sh = gc.create(gsheet_name, parent_id=self.google_drive_folder_id)
        wks = sh.add_worksheet(self.google_worksheet_name,
                               rows=self.number_of_games + 2,
                               cols=self.google_worksheet_cols)
        wks.set_dataframe(df, (1, 1))

        # Remove default worksheet 'Sheet1'
        wks_del = sh.worksheet_by_title('Sheet1')
        sh.del_worksheet(wks_del)

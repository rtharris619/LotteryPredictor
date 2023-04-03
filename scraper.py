from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime

# For a list of winners from 5 years ago:
# https://www.lottoland.co.za/lotto/results-winning-numbers

# For a list of winning numbers only but from as far back as 2000
# https://www.lottery.co.za/lotto/results/2023


def driver():
    lottery_scraper = LotteryScraper()
    # lottery_scraper.scrape()


class LotteryItem:
    def __init__(self, date, draw_number, ball1, ball2, ball3, ball4, ball5, ball6, bonus_ball, jackpot):
        self.date = date
        self.draw_number = draw_number
        self.ball1 = ball1
        self.ball2 = ball2
        self.ball3 = ball3
        self.ball4 = ball4
        self.ball5 = ball5
        self.ball6 = ball6
        self.bonus_ball = bonus_ball
        self.jackpot = jackpot


class LotteryScraper:
    def __init__(self):
        self.soup = None
        self.base_url = f'https://www.lottery.co.za/lotto/results'
        self.current_year = 2023
        self.lottery_data = []

    def scrape(self):
        """Scrape function to scrape all the pages."""
        self.scrape_pages()
        self.write_to_csv(self.lottery_data)

    def scrape_pages(self):
        self.scrape_webpage(f'{self.base_url}/{self.current_year}')
        anchors = self.soup.find_all('a', attrs={'class': 'button-blue'})

        for a in anchors:
            year = a.get_text()
            print(f'starting processing for {year}')
            self.scrape_webpage(f'{self.base_url}/{year}')
            self.get_results()
            print(f'finished processing for {year}')

    def scrape_webpage(self, url):
        html = self.get_html(url)
        if html:
            self.soup = BeautifulSoup(html, 'html.parser')

    def get_html(self, url):
        r = requests.get(url)
        if r:
            results = r.text
            if results:
                return results

        return None

    def get_results(self):
        result = self.soup.find('table', class_='lotto')
        body = result.find('tbody')
        trs = body.find_all('tr')

        for tr in trs:
            date = None
            draw_number = None
            ball_numbers = []
            bonus_ball = None
            jackpot = None
            tds = tr.find_all('td')
            for i, td in enumerate(tds):
                if i == 0:
                    date_string = td.getText(strip=True)
                    date = self.convert_to_datetime(date_string)
                elif i == 1:
                    draw_number = td.getText(strip=True)
                elif i == 2:
                    balls = td.find_all('div', class_='lotto-ball')
                    for ball in balls:
                        ball_number = ball.get_text()
                        ball_numbers.append(ball_number)
                    bonus = td.find('div', class_='lotto-bonus-ball')
                    bonus_ball = bonus.get_text()
                elif i == 3:
                    jackpot_str = td.getText(strip=True)
                    jackpot = self.convert_to_float(jackpot_str)

            lottery_item = LotteryItem(date, draw_number, ball_numbers[0], ball_numbers[1], ball_numbers[2],
                                       ball_numbers[3], ball_numbers[4], ball_numbers[5],
                                       bonus_ball, jackpot)
            self.lottery_data.append(lottery_item)

        # self.write_to_csv(data)

    def convert_to_datetime(self, date_str):
        format = '%A, %d %B %Y'
        datetime_str = datetime.datetime.strptime(date_str, format)

        return datetime_str

    def convert_to_float(self, flt_str):
        flt_str = ''.join(c for c in flt_str if c.isdigit())
        return float(flt_str)

    def write_to_csv(self, data):
        df = pd.DataFrame([vars(x) for x in data])
        df.to_csv('./LotteryResults.csv', index=False)

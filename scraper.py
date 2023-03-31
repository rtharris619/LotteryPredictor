from bs4 import BeautifulSoup
import requests

# For a list of winners from 5 years ago:
# https://www.lottoland.co.za/lotto/results-winning-numbers

# For a list of winning numbers only but from as far back as 2000
# https://www.lottery.co.za/lotto/results/2023


def driver():
    lottery_scraper = LotteryScraper(2023)
    lottery_scraper.get_results()


class LotteryItem:
    def __init__(self, date, draw_number, balls, bonus_ball, jackpot):
        self.date = date
        self.draw_number = draw_number
        self.balls = balls
        self.bonus_ball = bonus_ball
        self.jackpot = jackpot

    def __repr__(self):
        result = 'Balls: '
        for ball in self.balls:
            result += ball + '; '
        return f'{result}'


class LotteryScraper:
    def __init__(self, year):
        self.soup = None
        self.base_url = f'https://www.lottery.co.za/lotto/results/{year}'
        self.scrape_webpage()

    def scrape_webpage(self):
        html = self.get_html()
        if html:
            self.soup = BeautifulSoup(html, 'html.parser')

    def get_html(self):
        r = requests.get(self.base_url)
        if r:
            results = r.text
            if results:
                return results

        return None

    def get_results(self):
        result = self.soup.find('table', class_='lotto')
        body = result.find('tbody')
        trs = body.find_all('tr')

        data = []

        for tr in trs:
            date = None
            draw_number = None
            ball_numbers = []
            bonus_ball = None
            jackpot = None
            tds = tr.find_all('td')
            for i, td in enumerate(tds):
                if i == 0:
                    date = td.getText(strip=True)
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
                    jackpot = td.getText(strip=True)

            lottery_item = LotteryItem(date, draw_number, ball_numbers, bonus_ball, jackpot)
            data.append(lottery_item)

        print(data[0])

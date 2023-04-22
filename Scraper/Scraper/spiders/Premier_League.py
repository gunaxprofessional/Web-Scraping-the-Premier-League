import scrapy
import json

class ExampleSpider(scrapy.Spider):
    name = "example01"

    def start_requests(self):
        matchId = 75221
        for id in range(matchId,8062,-1):
            yield scrapy.Request(url=f'https://www.premierleague.com/match/{id}', callback=self.parse)

    def parse(self, response):
        # with open("sample.html",'w') as f:
        #     f.write(response.text)

        item={}
        try:
            item['Home_team_score'] = response.xpath('//div[@class="score fullTime"]/text()').getall()[0]
            item['Home_team_name'] = response.xpath("//span[@class='long']/text()").getall()[0]
            item['Away_team_score'] = response.xpath('//div[@class="score fullTime"]/text()').getall()[1]
            item['Away_team_name'] = response.xpath("//span[@class='long']/text()").getall()[1]
            item['attendance'] = response.xpath("//div[@class='attendance hide-m']/text()").get()
            item['referee'] = response.xpath("//div[@class='referee']/text()").getall()[1].strip()
            item['stadium'] = response.xpath("//div[@class='stadium']/text()").get().strip()
        except:
            item['Home_team_score'] = response.xpath('//div[@class="score fullTime"]/text()').getall()[0]
            item['Home_team_name'] = response.xpath("//span[@class='long']/text()").getall()[0]
            item['Away_team_score'] = response.xpath('//div[@class="score fullTime"]/text()').getall()[1]
            item['Away_team_name'] = response.xpath("//span[@class='long']/text()").getall()[1]
            item['attendance'] = response.xpath("//div[@class='attendance hide-m']/text()").get()
            item['referee'] = None
            item['stadium'] = response.xpath("//div[@class='stadium']/text()").get().strip()            

        id = response.url.split('/')[-1]
        url = f"https://footballapi.pulselive.com/football/stats/match/{id}"
        payload = {}
        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ta;q=0.7',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'dnt': '1',
            'origin': 'https://www.premierleague.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        }
        
        yield scrapy.Request(url,headers=headers,callback=self.pares_one,meta={'item':item})

    def pares_one(self,response):
        # with open('sample_json.json','w')as f:
        #     f.write(response.text)

        item = response.meta['item']
        jsonFile = json.loads(response.text)
        
        item['Season'] = jsonFile['entity']['gameweek']['compSeason']['label']
        item['Date'] = jsonFile['entity']['provisionalKickoff']['label']
        item['kickOff'] = jsonFile['entity']['provisionalKickoff']['millis']
        
        Team_Id = jsonFile['entity']['teams']
        ids = []
        for jsonValues in Team_Id:
            ids.append(jsonValues['team']['id'])

        try:
            Home_team_Details = jsonFile['data'][str(ids[0])]['M']
            Away_team_Details = jsonFile['data'][str(ids[1])]['M']

            for index in Home_team_Details:
                values = list(index.values())
                item['Home_Team_'+values[0]] = values[1]

            for index in Away_team_Details:
                values = list(index.values())
                item['Away_Team_'+values[0]] = values[1]

            yield item
        except:
            print("\nData is unavailable\n")
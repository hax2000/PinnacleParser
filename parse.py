import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from models import *

from database import init_db, db_Session

static = {
		'targetGame' : 'League of Legends',
		'headerOfTournamentSpanClass' : 'style_marketHeading__3vRHe style_label__2U08n text-left ellipsis bold',
		'headerOfMatchDivClass' : 'style_col__ncUvn style_colGame__3zQv8 overflow-visible',
		'teamNameLabelClass' : 'style_participantName__3EhkD',
		'collapsbleElementsXPATH' : '//div[@data-test-id="Collapse"]',
		'infoBlockDivClass' : 'style_primary__awRGO style_marketGroup__1LRLw',
		'counterSpanClass' : 'style_titleText__jlbrV ellipsis',
		'infoButtonEventFunction' : 'Event.MarketBtn'
	}


class Browser(object):

	def __init__(self):
		""" Конструктор класса, инициализируемся и ждём прогрузки хрома """
		self.targetUrl = 'https://www.pinnacle.com' # Основной домен страницы, которую будем парсить. В дальнейшем к этому юрлу будут дописываться целевые страницы
		self.driver = webdriver.Chrome()
		
		"""Контролируем, на каком юрле находимся и что перед собой видим"""
		self.currentPageUrl = '' 
		self.currentPageHtml = ''
		self.currentPageSoup = ''
		
		self.databuffer = {}

	def OpenPage(self,page,RequiredText):
		""" Функция перехода браузера на страницу
			page : целевая страница сайта, которую припишем в дальнейшем к домену
			RequredText : какой-либо текст, означающий что необходимая страница прогрузилась. До тех пор пока не увидим этого текста, не продолжаем парсинг
		"""
		self.currentPageUrl = self.targetUrl+page
		self.driver.get(self.currentPageUrl)

		while(self.Loading(RequiredText)):
			time.sleep(0.7)

	def Loading(self,RequiredText):
		""" Функция, которая проверяет, загрузилась ли страница
		"""
		self.currentPageHtml = self.driver.page_source
		self.currentPageSoup = BeautifulSoup(self.currentPageHtml, 'lxml')

		if RequiredText in self.currentPageHtml:
			return False # Дальнейшая загрузка страницы не требуется
		else:
			return True # Загрузка страницы всё ещё идёт

	def CollapseAllDropBoxes(self):
		""" Функция, открывающая все открывающиеся элементы на странице
			Бывает что при заходе на страницу матча, не все дропбоксы открыты
		"""
		elements = self.driver.find_elements(By.XPATH, static.get('collapsbleElementsXPATH'))
		for DropBox in elements:
			DropBox.click()
		time.sleep(0.5)

		self.currentPageHtml = self.driver.page_source
		self.currentPageSoup = BeautifulSoup(self.currentPageHtml, 'lxml')


def writeToDB(dataset):
	""" Глобальная функция записи в БД
		dataset : все собранные данные со страницы ОДНОГО матча ОДНОГО турнира
		при записи смотрим, нет ли уже подобных турниров,матчей,команд,показателей в базе
	"""
	tournament_title = dataset['Tournament']
	tournament = db_Session.query(Tournament).filter_by(fullTitle=tournament_title).first()
	
	if tournament == None:
		new_tournament = Tournament(fullTitle=tournament_title)
		db_Session.add(new_tournament)
		db_Session.commit()
		tournament_id=new_tournament.id
	else:
		tournament_id=tournament.id

	teamids = []
	for team_name in dataset['Match']:
		team = db_Session.query(Team).filter_by(name=team_name).first()
		
		if team == None:
			new_team = Team(name=team_name)
			db_Session.add(new_team)
			db_Session.commit()
			team_id=new_team.id
		else:
			team_id=team.id
		
		teamids.append(team_id)
	
	firstOpponent_id = teamids[0]
	secondOpponent_id = teamids[1]

	match = db_Session.query(Match).filter_by(tournament_id=tournament_id,
		firstOpponent_id=firstOpponent_id,secondOpponent_id=secondOpponent_id).first()

	if match == None:
		new_match = Match(tournament_id=tournament_id,
			firstOpponent_id=firstOpponent_id,secondOpponent_id=secondOpponent_id)
		db_Session.add(new_match)
		db_Session.commit()
		match_id = new_match.id
	else:
		match_id = match.id


	for team_name in dataset['commands']:
		
		team_id = db_Session.query(Team).filter_by(name=team_name).first().id
		
		for counter_name in dataset['commands'][team_name]:
			counter = db_Session.query(Counter).filter_by(name=counter_name).first()
			if counter == None:
				new_counter = Counter(name=counter_name)
				db_Session.add(new_counter)
				db_Session.commit()
				counter_id=new_counter.id
			else:
				counter_id=counter.id

			for line_info in dataset['commands'][team_name][counter_name]:
				for line_label in line_info:
					new_line = Line(label=line_label,value=line_info[line_label])
					db_Session.add(new_line)
					db_Session.commit()
					line_id=new_line.id

					new_statistics = Statistics(match_id=match_id,team_id=team_id,
						counter_id=counter_id,line_id=line_id)
					db_Session.add(new_statistics)
					db_Session.commit()
    	



def main():
	init_db() # создаём таблицы в БД из мета-классов (см. database.py)

	parser = Browser()

	parser.OpenPage('/ru/esports/matchups/highlights',static.get('targetGame')) #переходим на страницу с турнирами и ищем нужную нам игру с которой будем парсить
	
	structuredGamesList = parser.currentPageSoup.find_all('div')[1:] # из объекта soup выбираем блок с заголовками турниров и матчами

	isParse = False # сначала нужно добраться до нужной игры, чтобы её парсить
	
	for TournamentsAndMatches in structuredGamesList: #проходимся по всем блокам

		if len(TournamentsAndMatches.find_all('span',static.get('headerOfTournamentSpanClass'))) != 0: #если в заголовке турнира есть нужная игра

			if('Денежная линия' not in TournamentsAndMatches.text): #отсеиваем дубликаты одних и тех же блоков
				Game,TournamentFullTitle = TournamentsAndMatches.text.split(' - ')
				parser.databuffer = {
						'Tournament' : TournamentFullTitle #запомнили название турнира
					} 

				if(static.get('targetGame') == Game and not isParse): # если дошли до нужной игры проваливаем одну итерацию и начинаем парсинг
					isParse=True
					continue

				if(static.get('targetGame') != Game and isParse):
					isParse=False
					continue

		if(isParse):
			matchDiv = TournamentsAndMatches.find('div',static.get('headerOfMatchDivClass')) # берём конкретный блок с матчем нужной нам игры

			if(matchDiv != None): # отсеиваем лишнее
				href = matchDiv.find('a')['href'] #выбираем ссылку на полную инфу о матче
				parser.OpenPage(href,'против') # и идём на неё

				structuredMatchList = parser.currentPageSoup
				firstOpponent,secondOpponent = structuredMatchList.find_all('label',static.get('teamNameLabelClass'))[0:2] #выбираем названия команд

				firstOpponent_name = firstOpponent.text ; secondOpponent_name = secondOpponent.text
				match_info = [firstOpponent_name,secondOpponent_name]
				parser.databuffer['Match'] = match_info # запоминаем участников матча

				parser.CollapseAllDropBoxes() # разворачиваем все дропбоксы
				structuredMatchList = parser.currentPageSoup # и ещё раз осматриваем всю страницу

				oneTeamCounterValues = 0 # будем следить, сколько линий к каждому показателю мы записываем
				parser.databuffer['commands'] = {}
				parser.databuffer['commands'][firstOpponent_name] = {} # заранее разбиваем датасет на 2 команды
				parser.databuffer['commands'][secondOpponent_name] = {}

				for InfoBlock in structuredMatchList.find_all('div',static.get('infoBlockDivClass')): # идём по каждому дропбоксу
					"""
					 так как нам нужна статистика по каждой команде, а не по двум сразу, смотрим чтобы хоть где то упоминалось название хоть одной команды
					 к примеру, нам не обязательно знать линии матча "закончится ли игра за 30 минут"
					"""
					if firstOpponent_name in str(InfoBlock) and secondOpponent_name in str(InfoBlock): 
						CurrentCounter = InfoBlock.find('span',static.get('counterSpanClass')).text # запоминаем показатель линии

						for Button in InfoBlock.find_all('a'): # выбираем из кнопки название линии и её значение 
							try:
								if Button['data-test-id']==static.get('infoButtonEventFunction'): # из именно той кнопки, которая нам нужна
									oneTeamCounterValues += 1
									countertext = Button.find_all('span')[0].text # текст показателя линии
									countertextvalue = Button.find_all('span')[1].text # значение
								
								if(oneTeamCounterValues//2==oneTeamCounterValues/2): # сейчас у нас есть значение для второй команды
									"""
									Смотрим, есть ли уже в датасете такой показатель по такой команде. Если нету - создаём, если есть - добавляем новое значение в лист
									"""
									try:
										parser.databuffer['commands'][secondOpponent_name][CurrentCounter].append({countertext:countertextvalue})
									except KeyError:
										parser.databuffer['commands'][secondOpponent_name][CurrentCounter] = [{countertext:countertextvalue}]

								else: # а сейчас для первой
									try:
										parser.databuffer['commands'][firstOpponent_name][CurrentCounter].append({countertext:countertextvalue})
									except KeyError:
										parser.databuffer['commands'][firstOpponent_name][CurrentCounter] = [{countertext:countertextvalue}]
									
							
							except KeyError:
								pass
						
						oneTeamCounterValues = 0 # переходим к следующему показателю
				
				writeToDB(parser.databuffer) # пишем данные в бд

	"""
	К этому моменту все данные уже в базе. Выводим, всё что спарсили.
	"""
	for item in db_Session.query(Statistics):
		print(item)
		print()

	parser.driver.quit() # закрываем браузер
	db_Session.remove() # выходим из сессии орм
	

if __name__ == '__main__':
	main()
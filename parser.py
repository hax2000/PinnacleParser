import requests
import json
import time
from models import *

from database import init_db, db_Session

headers = {
	'Accept': 'application/json',
	'Content-Type': 'application/json',
	'Referer': 'https://www.pinnacle.com/ru/esports/matchups/highlights/',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
	'X-API-Key': 'CmX2KcMrXuFmNg6YFbmTxE0y9CIrOi0R'
}

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

	participantsids = {}
	for team_name in dataset['Match']:
		team = db_Session.query(Team).filter_by(name=team_name).first()
		
		if team == None:
			new_team = Team(name=team_name)
			db_Session.add(new_team)
			db_Session.commit()
			team_id=new_team.id
		else:
			team_id=team.id
		
		participantsids[team_name]=team_id
	
	firstOpponent_id,secondOpponent_id = [participantsids[dataset['Match'][i]] for i in range(2)]

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

	
	for counter_id in dataset:
		if(counter_id=='Tournament' or counter_id=='Match'):
			continue
		else:
			currentCounter = dataset[counter_id]
			counter_name = currentCounter['counter']
			
			counter = db_Session.query(Counter).filter_by(name=counter_name).first()
			if counter == None:
				new_counter = Counter(name=counter_name)
				db_Session.add(new_counter)
				db_Session.commit()
				counter_id=new_counter.id
			else:
				counter_id=counter.id

			for participantId in currentCounter['participants']:
				participant = currentCounter['participants'][participantId]
				if(len(participant)==2):
					team_name, linevalue = participant
				else:
					continue

				new_line = Line(label=team_name,value=linevalue)
				db_Session.add(new_line)
				db_Session.commit()
				line_id = new_line.id

				new_statistics = Statistics(match_id=match_id,team_id=participantsids[team_name],
					counter_id=counter_id,line_id=line_id)
				db_Session.add(new_statistics)
				db_Session.commit()
    	

def getParsingProcess(currentPart,totalParts):
	return str(int(round(currentPart/totalParts,2)*100))


def main():
	init_db() # создаём таблицы в БД из мета-классов (см. database.py)

	highlightedMatchesUrl = 'https://guest.api.arcadia.pinnacle.com/0.1/sports/12/markets/highlighted/straight?primaryOnly=false' 
	rawMatchList = requests.get(highlightedMatchesUrl,headers=headers)
	matchList = json.loads(rawMatchList.text)

	parsedMatches = [] # Не парсим матчи, которые уже парсили
	currentMatch = 0 # Для отслеживания статуса парсинга
	for match in matchList:
		print('Parsing process: {}%'.format(getParsingProcess(currentMatch,len(matchList))))
		matchupId = match.get('matchupId')
		if matchupId not in parsedMatches:
			matchInfo = requests.get('https://guest.api.arcadia.pinnacle.com/0.1/matchups/'+str(matchupId),headers=headers) 
			"""
			В этом API-методе можно найти данные о матче:
			Игра, Турнир, Тип ссылки (Ставка на матч или ставка по киллам), названия комманд, дата+время и т.д.
			"""
			matchInfoJson = json.loads(matchInfo.text)
			try:	#Иногда запрос может ответить, что для этого матча нет подробной информации
				Game,fullTournamentName = matchInfoJson['league']['name'].split(' - ')
				if Game == 'League of Legends':
					if '(Kills)' not in matchInfoJson['participants'][0]['name']: # не парсим дубликаты
						time.sleep(0.5) #для стабильности, тк сайт может временно заблочить наш ip
						data = {}
						data['Tournament'] = fullTournamentName
						firstOpponent_name,secondOpponent_name = [matchInfoJson['participants'][i]['name'] for i in range(2)]
						data['Match'] = [firstOpponent_name,secondOpponent_name]

						relatedMatch = requests.get('https://guest.api.arcadia.pinnacle.com/0.1/matchups/{}/related'.format(matchupId),headers=headers)
						'''
						В этом API методе можно получить:
						id показателя
						тексты показателей
						id+тексты линий
						'''
						relatedMatchJson = json.loads(relatedMatch.text)

						for Infoblock in relatedMatchJson:
							if Infoblock['type']=="special":
								name = Infoblock['special']['description']
								participantsMasssive = [temp['name'].lower() for temp in Infoblock['participants']]
								if(firstOpponent_name.lower() in participantsMasssive and secondOpponent_name.lower() in participantsMasssive):
									participants = {str(temp['id']):[temp['name']] for temp in Infoblock['participants']}
									key = str(Infoblock['id'])
									data[key]= {'counter':name,'participants':participants}
							else:
								continue

						straightMatch = requests.get('https://guest.api.arcadia.pinnacle.com/0.1/matchups/{}/markets/related/straight'.format(matchupId),headers=headers)
						straightMatchJson = json.loads(straightMatch.text)
						"""
						В этом API методе можно получить значения линий, по id который мы запомнили в предыдущем методе
						"""
						for Infoblock in straightMatchJson:
							try:
								for price in Infoblock['prices']:
									participantId = price['participantId']
									priceValue = price['price']
									data[str(Infoblock['matchupId'])]['participants'][str(participantId)].append(priceValue)
							except KeyError:
								pass

						writeToDB(data)


			except KeyError:
				pass
		parsedMatches.append(matchupId)
		currentMatch=currentMatch+1


	"""
	К этому моменту все данные уже в базе. Выводим, всё что спарсили.
	"""
	for item in db_Session.query(Statistics):
		print(item)
		print()

	db_Session.remove() # выходим из сессии орм
	

if __name__ == '__main__':
	main()
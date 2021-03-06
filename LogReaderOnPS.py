#!/usr/bin/python

import string
import sys
import json
import copy
#import cPickle as pickle
import math
import os

filename = str(sys.argv[1])
file = open(filename)
raw = file.readline()
file.close()
tier = sys.argv[2]

if raw=='"log"': #https://github.com/Zarel/Pokemon-Showdown/commit/92a4f85e0abe9d3a9febb0e6417a7710cabdc303
	sys.exit(0)
log = json.loads(raw)

#determine log type
spacelog = True
if 'log' in log.keys():
	if log['log'][0][0:2] != '| ':
		spacelog = False

#check for log length
longEnough = False
if 'log' not in log.keys():
	if int(log['turns']) > 5: 
		longEnough = True
else:
	for line in log['log']:
		if (spacelog and line[2:10] == 'turn | 6') or (not spacelog and line[1:7] == 'turn|6'):
			longEnough = True
			break
if not longEnough:
	sys.exit(0)


#now that we've determined that we're cooking with gas, we can load all the good stuff
#file = open('baseStats.pickle')
#baseStats = pickle.load(file)
#file = open('baseStats.json')
#baseStats = json.loads(file.readline())
#file.close()

from TA import *

def keyify(s):
	sout = ''
	for c in s:
		if c in string.uppercase:
			sout = sout + c.lower()
		elif c in string.lowercase + '1234567890':
			sout = sout + c
	return sout

aliases={
	'NidoranF': ['Nidoran-F'],
	'NidoranM': ['Nidoran-M'],
	'Pichu': ['Spiky Pichu'],
	'Rotom-Mow': ['Rotom-C'],
	'Rotom-Heat': ['Rotom-H'],
	'Rotom-Frost': ['Rotom-F'],
	'Rotom-Wash': ['Rotom-W'],
	'Rotom-Fan': ['Rotom-S'],
	'Deoxys-Attack': ['Deoxys-A'],
	'Deoxys-Defense': ['Deoxys-D'],
	'Deoxys-Speed': ['Deoxys-S'],
	'Wormadam-Sandy': ['Wormadam-G'],
	'Wormadam-Trash': ['Wormadam-S'],
	'Shaymin-Sky': ['Shaymin-S'],
	'Giratina-Origin': ['Giratina-O'],
	'Unown': ['Unown-B','Unown-C','Unown-D','Unown-E','Unown-F','Unown-G','Unown-H','Unown-I','Unown-J','Unown-K','Unown-L','Unown-M','Unown-N','Unown-O','Unown-P','Unown-Q','Unown-R','Unown-S','Unown-T','Unown-U','Unown-V','Unown-W','Unown-X','Unown-Y','Unown-Z','Unown-!','Unown-?'],
	'Burmy': ['Burmy-G','Burmy-S'],
	'Castform': ['Castform-Snowy','Castform-Rainy','Castform-Sunny'],
	'Cherrim': ['Cherrim-Sunshine'],
	'Shellos': ['Shellos-East'],
	'Gastrodon': ['Gastrodon-East'],
	'Deerling': ['Deerling-Summer','Deerling-Autumn','Deerling-Winter'],
	'Sawsbuck': ['Sawsbuck-Summer','Sawsbuck-Autumn','Sawsbuck-Winter'],
	'Tornadus-Therian': ['Tornadus-T'],
	'Thundurus-Therian': ['Thundurus-T'],
	'Landorus-Therian': ['Landorus-T'],
	'Keldeo': ['Keldeo-R','Keldeo-Resolution'],
	'Meloetta': ['Meloetta-S','Meloetta-Pirouette'],
	'Genesect': ['Genesect-Douse','Genesect-Burn','Genesect-Shock','Genesect-Chill','Genesect-D','Genesect-S','Genesect-B','Genesect-C'],
	'Darmanitan': ['Darmanitan-D','Darmanitan-Zen'],
	'Basculin': ['Basculin-Blue-Striped','Basculin-A'],
	'Kyurem-Black': ['Kyurem-B'],
	'Kyurem-White': ['Kyurem-W']
}

#fix species
replacements = {
	'Rotom-H' : 'Rotom-Heat',
	'Rotom-W' : 'Rotom-Wash',
	'Rotom-F' : 'Rotom-Frost',
	'Rotom-S' : 'Rotom-Fan',
	'Rotom-C' : 'Rotom-Mow',
	'Rotom- H' : 'Rotom-Heat',
	'Rotom- W' : 'Rotom-Wash',
	'Rotom- F' : 'Rotom-Frost',
	'Rotom- S' : 'Rotom-Fan',
	'Rotom- C' : 'Rotom-Mow',
	'Rotom-h' : 'Rotom-Heat',
	'Rotom-w' : 'Rotom-Wash',
	'Rotom-f' : 'Rotom-Frost',
	'Rotom-s' : 'Rotom-Fan',
	'Rotom-c' : 'Rotom-Mow',
	'Tornadus-T' : 'Tornadus-Therian',
	'Thundurus-T' : 'Thundurus-Therian',
	'Landorus-T' : 'Landorus-Therian',
	'Deoxys-D' : 'Deoxys-Defense',
	'Deoxys-A' : 'Deoxys-Attack',
	'Deoxys-S' : 'Deoxys-Speed',
	'Kyurem-B' : 'Kyurem-Black',
	'Kyurem-W' : 'Kyurem-White',
	'Shaymin-S' : 'Shaymin-Sky',
	'Ho-oh' : 'Ho-Oh',
	"Birijion": "Virizion",
	"Terakion": "Terrakion",
	"Agirudaa": "Accelgor",
	"Randorosu": "Landorus",
	"Urugamosu": "Volcarona",
	"Erufuun": "Whimsicott",
	"Doryuuzu": "Excadrill",
	"Burungeru": "Jellicent",
	"Nattorei": "Ferrothorn",
	"Shandera": "Chandelure",
	"Roobushin": "Conkeldurr",
	"Ononokusu": "Haxorus",
	"Sazandora": "Hydreigon",
	"Chirachiino": "Cinccino",
	"Kyuremu": "Kyurem",
	"Jarooda": "Serperior",
	"Zoroaaku": "Zoroark",
	"Shinboraa": "Sigilyph",
	"Barujiina": "Mandibuzz",
	"Rankurusu": "Reuniclus",
	"Borutorosu": "Thundurus",
	"Mime Jr" : "Mime Jr.", #this one's my fault
	#to be fair, I never observed the following, but better safe than sorry
	'Giratina-O' : 'Giratina-Origin',
	'Keldeo-R' : 'Keldeo-Resolution',
	'Wormadam-G' : 'Wormadam-Sandy',
	'Wormadam-S' : 'Wormadam-Trash',
	"Dnite": "Dragonite",
	"Ferry": "Ferrothorn",
	"Forry": "Forretress",
	"Luke":  "Lucario",
	"P2": "Porygon2",
	"Pory2": "Porygon2",
	"Pz": "Porygon-Z",
	"Poryz": "Porygon-Z",
	"Rank": "Reuniclus",
	"Ttar": "Tyranitar"
}

#get info on the trainers & pokes involved
ts = []
teams = {}

#get pokemon info
for team in ['p1team','p2team']:

	if team == 'p1team':
		trainer = log['p1']
	else:
		trainer = log['p2']

	teams[team]=[]

	for i in range(len(log[team])):
		if 'species' in log[team][i].keys():
			species = log[team][i]['species']
		else: #apparently randbats usually don't contain the species field?
			species = log[team][i]['name']

		#very odd that these == needed--I've seen ".Species", "(Species)", "species", "Species)", "SPECIES"...
		if species[0] not in string.lowercase + string.uppercase:
			species=species[1:]
		while species[len(species)-1] in ')". ':
			species=species[:len(species)-1]
		if species[0] in string.lowercase or species[1] in string.uppercase:
			species = species.title()
		if species in replacements.keys():
			species = replacements[species]

		for s in aliases: #combine appearance-only variations and weird PS quirks
			if species in aliases[s]:
				species = s
				break
		
		ts.append([trainer,species])

		if 'item' in log[team][i].keys():
			item = keyify(log[team][i]['item'])
			if item == '':
				item = 'nothing'
		else:
			item = 'nothing'
		if 'nature' in log[team][i].keys():
			nature = keyify(log[team][i]['nature'])
			if nature not in nmod.keys(): #zarel said this is what PS does
				nature = 'hardy'
		else:
			nature = 'hardy'
		evs = {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0}
		if 'evs' in log[team][i].keys():
			for stat in log[team][i]['evs']:
				evs[stat]=int(log[team][i]['evs'][stat])	
		ivs = {'hp': 31, 'atk': 31, 'def': 31, 'spa': 31, 'spd': 31, 'spe': 31}
		if 'ivs' in log[team][i].keys():
			for stat in log[team][i]['ivs']:
				ivs[stat]=int(log[team][i]['ivs'][stat])
		if 'moves' in log[team][i].keys():
			moves = log[team][i]['moves']
		else:
			moves = []
		while len(moves)<4:
			moves.append('')
		for j in range(len(moves)): #make all moves lower-case and space-free
			moves[j] = keyify(moves[j])
		#figure out Hidden Power from IVs
		if 'ability' in log[team][i].keys():
			ability = keyify(log[team][i]['ability'])
		else:
			ability = 'unknown'
		if 'level' in log[team][i].keys():
			level = int(log[team][i]['level'])
		else:
			level = 100
		teams[team].append({
			'species': keyify(species),
			'nature': nature,
			'item': item,
			'evs': {},
			'moves': [],
			'ability': ability,
			'level': level,
			'ivs': {}})
		for stat in evs:
			teams[team][len(teams[team])-1]['evs'][stat] = evs[stat]
			teams[team][len(teams[team])-1]['ivs'][stat] = ivs[stat]
		for move in moves:
			teams[team][len(teams[team])-1]['moves'].append(move)

		#write to moveset file
		outname = "Raw/moveset/"+tier+"/"+keyify(species)+".txt"
		d = os.path.dirname(outname)
		if not os.path.exists(d):
			os.makedirs(d)
		outfile=open(outname,'a')
		outfile.write(str(level)+'\t'+ability+'\t'+item+'\t'+nature+'\t')
		for iv in ivs:
			outfile.write(str(iv)+'\t')
		for ev in evs:
			outfile.write(str(ev)+'\t')
		for move in moves:
			outfile.write(str(move)+'\t')
		outfile.write('\n')
		outfile.close()

	if len(log[team]) < 6:
		for i in range(6-len(log[team])):
			ts.append([trainer,'empty'])
	analysis = analyzeTeam(teams[team])
	teams[team].append({'bias': analysis['bias'], 'stalliness' : analysis['stalliness'], 'tags' : analysis['tags']})


#nickanmes
nicks = []
for i in range(0,6):
	if len(log['p1team'])>i:
		if 'name' in log['p1team'][i].keys():
			nicks.append("p1: "+log['p1team'][i]['name'])
		else:
			nicks.append("p1: "+log['p1team'][i]['species'])
	else:
		nicks.append("p1: empty")
	if len(log['p2team'])>i:
		if 'name' in log['p2team'][i].keys():
			nicks.append("p2: "+log['p2team'][i]['name'])
		else:
			nicks.append("p2: "+log['p2team'][i]['species'])
	else:		
		nicks.append("p1: empty")

if ts[0][0] == ts[11][0]: #trainer battling him/herself? WTF?
	sys.exit(0)


#metrics get declared here
turnsOut = [] #turns out on the field (a measure of stall)
KOs = [] #number of KOs in the battle
matchups = [] #poke1, poke2, what happened

for i in range(0,12):
	turnsOut.append(0)
	KOs.append(0)

if 'log' in log.keys():
	#determine initial pokemon
	active = [-1,-1]
	for line in log['log']:
		if (spacelog and line[0:14] == "| switch | p1:") or (not spacelog and line[0:11] == "|switch|p1:"):
			end = string.rfind(line,'|')-1*spacelog
			species = line[string.rfind(line,'|',12+3*spacelog,end-1)+1+1*spacelog:end]
			while ',' in species:
				species = species[0:string.rfind(species,',')]
			for s in aliases: #combine appearance-only variations and weird PS quirks
				if species in aliases[s]:
					species = s
					break
			active[0]=ts.index([ts[0][0],species])
		if (spacelog and line[0:14] == "| switch | p2:") or (not spacelog and line[0:11] == "|switch|p2:"):
			end = string.rfind(line,'|')-1*spacelog
			species = line[string.rfind(line,'|',12+3*spacelog,end-1)+1+1*spacelog:end]
			while ',' in species:
				species = species[0:string.rfind(species,',')]
			for s in aliases: #combine appearance-only variations and weird PS quirks
				if species in aliases[s]:
					species = s
					break
			active[1]=ts.index([ts[11][0],species])
			break
	start=log['log'].index(line)+1
		
	#metrics get declared here
	turnsOut = [] #turns out on the field (a measure of stall)
	KOs = [] #number of KOs in the battle
	matchups = [] #poke1, poke2, what happened

	for i in range(0,12):
		turnsOut.append(0)
		KOs.append(0)

	#parse the damn log

	#flags
	roar = False
	uturn = False
	ko = [False,False]
	switch = [False,False]
	uturnko = False
	mtemp = []

	for line in log['log'][start:]:
		#print line
		#identify what kind of message is on this line
		linetype = line[1+1*spacelog:string.find(line,'|',1+1*spacelog)-1*spacelog]

		if linetype == "turn":
			matchups = matchups + mtemp
			mtemp = []

			#reset for start of turn
			roar = uturn = uturnko = False
			ko = [False,False]
			switch = [False,False]

			#Mark each poke as having been out for an additional turn
			turnsOut[active[0]]=turnsOut[active[0]]+1
			turnsOut[active[1]]=turnsOut[active[1]]+1

		elif linetype == "win": 
			#close out last matchup
			if ko[0] or ko[1]: #if neither poke was KOed, match ended in forfeit, and we don't care
				pokes = [ts[active[0]][1],ts[active[1]][1]]
				pokes=sorted(pokes, key=lambda pokes:pokes)
				matchup=pokes[0]+' vs. '+pokes[1]+': '
				if ko[0] and ko[1]:
					KOs[active[0]] = KOs[active[0]]+1
					KOs[active[1]] = KOs[active[1]]+1
					matchup = matchup + "double down"
				else:
					KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
					matchup = matchup + ts[active[ko[1]]][1] + " was "
					if uturnko: #would rather not use this flag...
						mtemp=mtemp[:len(mtemp)-1]
						matchup = matchup + "u-turn "
					matchup = matchup + "KOed"
				mtemp.append(matchup)
			matchups=matchups+mtemp
			

		elif linetype == "move": #check for Roar, etc.; U-Turn, etc.
			#identify attacker and skip its name
			found = False
			for nick in nicks:
				if line[6+3*spacelog:].startswith(nick):
					if found: #the trainer was a d-bag
						if len(nick) < len(found):
							continue	
					found = nick
			tempnicks = copy.copy(nicks)
			while not found: #PS fucked up the names. We fix by shaving a character at a time off the nicknames
				foundidx=-1	
				for i in range(len(tempnicks)):
					if len(tempnicks[i])>1:
						tempnicks[i]=tempnicks[i][:len(tempnicks[i])-1]
					if line[6+3*spacelog:].startswith(tempnicks[i]):
						if found:
							if len(tempnicks[i]) < len(found):
								continue
						found = tempnicks[i]
						foundidx = i
				if found:
					nicks[i]=found
				else:
					tryAgain = False
					for i in range(len(tempnicks)):
						if len(tempnicks[i])>1:
							tryAgain = True
							break
					if not tryAgain:
						sys.stderr.write("Nick not found.\n")
						sys.stderr.write("In file: "+sys.argv[1]+"\n")
						sys.stderr.write(line[6+3*spacelog:]+"\n")
						sys.stderr.write(str(nicks)+"\n")
						sys.exit(1)
						
					
		
			move = line[7+5*spacelog+len(found):string.find(line,"|",7+5*spacelog+len(found))-1*spacelog]
			if move in ["Roar","Whirlwind","Circle Throw","Dragon Tail"]:
				roar = True
			elif move in ["U-Turn","U-turn","Volt Switch","Baton Pass"]:
				uturn = True

		elif linetype == "-enditem": #check for Red Card, Eject Button
			#search for relevant items
			if string.rfind(line,"Red Card") > -1:
				roar = True
			elif string.rfind(line,"Eject Button") > -1:
				uturn = True

		elif linetype == "faint": #KO
			#who fainted?
			ko[int(line[8+3*spacelog])-1]=1

			if uturn:
				uturn=False
				uturnko=True

		elif linetype in ["switch","drag"]: #switch out: new matchup!
			if linetype == "switch":
				p=9+3*spacelog
			else:
				p=7+3*spacelog	
			switch[int(line[p])-1]=True

			if switch[0] and switch[1]: #need to revise previous matchup
				matchup=mtemp[len(mtemp)-1][:string.find(mtemp[len(mtemp)-1],':')+2]
				if (not ko[0]) and (not ko[1]): #double switch
					matchup = matchup + "double switch"
				elif ko[0] and ko[1]: #double down
					KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
					matchup = matchup + "double down"
				else: #u-turn KO (note that this includes hit-by-red-card-and-dies and roar-then-die-by-residual-dmg)
					KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
					matchup = matchup + ts[active[ko[1]]][1]+" was u-turn KOed"
				mtemp[len(mtemp)-1]=matchup
			else:
				#close out old matchup
				pokes = [ts[active[0]][1],ts[active[1]][1]]
				pokes=sorted(pokes, key=lambda pokes:pokes)
				matchup=pokes[0]+' vs. '+pokes[1]+': '
				#if ko[0] and ko[1]: #double down
				if ko[0] or ko[1]:
					KOs[active[ko[0]]] = KOs[active[ko[0]]]+1
					matchup = matchup + ts[active[ko[1]]][1]+" was KOed"
				else:
					matchup = matchup + ts[active[switch[1]]][1]
					if roar:
						matchup = matchup + " was forced out"
					else:
						matchup = matchup + " was switched out"
				mtemp.append(matchup)
		
			#new matchup!
			uturn = roar = False
			#it matters whether the poke is nicknamed or not
			end = string.rfind(line,'|')-1*spacelog
			species = line[string.rfind(line,'|',0,end-1)+1+1*spacelog:end]
			while ',' in species:
				species = species[0:string.rfind(species,',')]
			for s in aliases: #combine appearance-only variations and weird PS quirks
				if species in aliases[s]:
					species = s
					break
			active[int(line[p])-1]=ts.index([ts[11*(int(line[p])-1)][0],species])

#totalTurns = log['turns']
#totalKOs = sum(KOs)

outname = "Raw/"+tier+".txt"
d = os.path.dirname(outname)
if not os.path.exists(d):
	os.makedirs(d)
outfile=open(outname,'a')

teamtags = teams['p1team'][len(teams['p1team'])-1]

outfile.write(ts[0][0].encode('ascii','replace'))
outfile.write(' (bias:'+str(teamtags['bias'])+', stalliness:'+str(teamtags['stalliness'])+', tags:'+','.join(teamtags['tags'])+')')
outfile.write("\n")
i=0
while (ts[i][0] == ts[0][0]):
	outfile.write(ts[i][1]+" ("+str(KOs[i])+","+str(turnsOut[i])+")\n")
	i = i + 1
	if i>=len(ts):
		sys.stderr.write("Something's wrong here.\n")
		sys.stderr.write("In file: "+sys.argv[1]+"\n")
		sys.stderr.write(str(ts)+"\n")
		sys.exit(1)	
outfile.write("***\n")
teamtags = teams['p2team'][len(teams['p2team'])-1]
outfile.write(ts[len(ts)-1][0].encode('ascii','replace'))
outfile.write(' (bias:'+str(teamtags['bias'])+', stalliness:'+str(teamtags['stalliness'])+', tags:'+','.join(teamtags['tags'])+')')
outfile.write("\n")
for j in range(i,len(ts)):
	outfile.write(ts[j][1]+" ("+str(KOs[j])+","+str(turnsOut[j])+")\n")
outfile.write("@@@\n")
for line in matchups:
	outfile.write(line+"\n")
outfile.write("---\n")
outfile.close()	


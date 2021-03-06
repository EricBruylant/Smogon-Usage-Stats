#!/usr/bin/python
import string
import sys
import json
import cPickle as pickle

def keyify(s):
	sout = ''
	for c in s:
		if c in string.uppercase:
			sout = sout + c.lower()
		elif c in string.lowercase + '1234567890':
			sout = sout + c
	return sout

def readTable(filename,col,weight,usage):
	file = open(filename)
	table=file.readlines()
	file.close()

	#'real' usage screwed me over--I can't take total count from header
	#using percentages is a bad idea because of roundoff

	tempUsage = {} #really dumb that I have to do this

	for i in range(6,len(table)):
		name = table[i][10:29]
	
		if (name[0] == '-'):
			break

		while name[len(name)-1] == ' ': 
			#remove extraneous spaces
			name = name[0:len(name)-1]
	
		count = table[i][31:38]
		while count[len(count)-1] == ' ':
			#remove extraneous spaces
			count = count[0:len(count)-1]
			tempUsage[keyify(name)]=float(count)

	for i in tempUsage:
		if i not in usage:
			usage[i]=[0,0,0,0]
		if i != 'empty':
			usage[i][col] = usage[i][col]+weight*6.0*tempUsage[i]/sum(tempUsage.values())/24

def makeTable(table,name,newTiers):

	print "[HIDE="+name+"][CODE]"
	print "Three-month usage for Standard "+name
	print " + ---- + ------------------ + ------- + "
	print " | Rank | Pokemon            | Percent | "
	print " + ---- + ------------------ + ------- + "
	print ' [B]| %-4d | %-18s | %6.3f%% |' % (1,keyLookup[table[0][0]],table[0][1]*100)
	for i in range(1,len(table)):
		if table[i][1] < 0.0340636711:
			start = i
			break
		print ' | %-4d | %-18s | %6.3f%% |' % (i+1,keyLookup[table[i][0]],100.0*table[i][1])
	print '[/B] | %-4d | %-18s | %6.3f%% |' % (i+1,keyLookup[table[i][0]],100.0*table[i][1])
	for i in range(0,start):
		if (newTiers[table[i][0]] == 'PU'):
			newTiers[table[i][0]] = name
	for i in range(start+1,len(table)):
		print ' | %-4d | %-18s | %6.3f%% |' % (i+1,keyLookup[table[i][0]],100.0*table[i][1])
	print " + ---- + --------------- + ------- +[/CODE][/HIDE]"


file = open('keylookup.pickle')
keyLookup = pickle.load(file)
file.close()
file=open('showdowntierstuff.json')
raw = file.readlines()
file.close()
formatsData = json.loads(raw[0])



curTiers = {}
newTiers = {}
NFE=[]
for poke in formatsData:
	if poke in ['pichuspikyeared', 'unownb', 'unownc', 'unownd', 'unowne', 'unownf', 'unowng', 'unownh', 'unowni', 'unownj', 'unownk', 'unownl', 'unownm', 'unownn', 'unowno', 'unownp', 'unownq', 'unownr', 'unowns', 'unownt', 'unownu', 'unownv', 'unownw', 'unownx', 'unowny', 'unownz', 'unownem', 'unownqm', 'burmysandy', 'burmytrash', 'cherrimsunshine', 'shelloseast', 'gastrodoneast', 'deerlingsummer', 'deerlingautumn', 'deerlingwinter', 'sawsbucksummer', 'sawsbuckautumn', 'sawsbuckwinter', 'keldeoresolution', 'genesectdouse', 'genesectburn', 'genesectshock', 'genesectchill', 'basculinbluestriped', 'darmanitanzen']:
		continue
	if 'isNonstandard' in formatsData[poke]:
		if formatsData[poke]['isNonstandard']:
			continue
	old = formatsData[poke]['tier']
	if old in ['NFE','LC']:
		NFE.append(poke)
	if old == 'Illegal':
		continue
	elif old not in ['Uber','OU','BL','UU','BL2','RU','BL3']:
		old = 'PU'
	curTiers[poke]=old
	newTiers[poke]='PU'

formats = json.loads(raw[1])
for poke in formats['pu']['banlist']:
	curTiers[keyify(poke)]='NU'

#that was the easy part. Now the fun begins. Read in the usage stats for...

usage = {} #track usage across all relevant tiers [OU,UU,RU,NU]

#...first month's...
readTable(str(sys.argv[1])+"/Stats/ou.txt",0,1.0,usage) #OU
readTable(str(sys.argv[1])+"/Stats/uu.txt",1,1.0,usage) #UU
readTable(str(sys.argv[1])+"/Stats/ru.txt",2,1.0,usage) #RU
readTable(str(sys.argv[1])+"/Stats/nu.txt",3,1.0,usage) #NU

#...second month
readTable(str(sys.argv[2])+"/Stats/ou.txt",0,3.0,usage)
readTable(str(sys.argv[2])+"/Stats/uu.txt",1,3.0,usage)
readTable(str(sys.argv[2])+"/Stats/ru.txt",2,3.0,usage)
readTable(str(sys.argv[2])+"/Stats/nu.txt",3,3.0,usage)

#...third month
readTable(str(sys.argv[3])+"/Stats/ou.txt",0,20.0,usage)
readTable(str(sys.argv[3])+"/Stats/uu.txt",1,20.0,usage)
readTable(str(sys.argv[3])+"/Stats/ru.txt",2,20.0,usage)
readTable(str(sys.argv[3])+"/Stats/nu.txt",3,20.0,usage)


#generate three-month tables and start working on that new tier list
OU = []
UU = []
RU = []
NU = []
for i in usage:
	if usage[i][0] > 0.0:
		OU.append([i,usage[i][0]])
	if usage[i][1] > 0.0:
		UU.append([i,usage[i][1]])
	if usage[i][2] > 0.0:
		RU.append([i,usage[i][2]])
	if usage[i][3] > 0.0:
		NU.append([i,usage[i][3]])
OU = sorted(OU, key=lambda OU:-OU[1])
UU = sorted(UU, key=lambda UU:-UU[1])
RU = sorted(RU, key=lambda RU:-RU[1])
NU = sorted(NU, key=lambda NU:-NU[1])

print "[B]Three-month statistics[/B]"
print "Three month usage = (20*Dec+3*Nov+1*Oct)/24"
makeTable(OU,"OU",newTiers)
makeTable(UU,"UU",newTiers)
makeTable(RU,"RU",newTiers)
makeTable(NU,"NU",newTiers)

#correct based on current tiers
poke = []
for i in curTiers:
	#put in all the non-usage tiers
	if curTiers[i] == 'Uber':
		newTiers[i] = curTiers[i]
	elif curTiers[i] == 'BL':
		if newTiers[i] != 'OU':
			newTiers[i] = 'BL'
	elif curTiers[i] == 'BL2':
		if newTiers[i] not in ['OU','UU']:
			newTiers[i] = 'BL2'
	elif curTiers[i] == 'BL3':
		if newTiers[i] in ['NU', 'PU']:
			newTiers[i] = 'BL3'
	#now to prevent multi-tier drops
	elif curTiers[i] == 'OU':
		if newTiers[i] in ['RU','NU','PU']:
			newTiers[i] = 'UU'
	elif curTiers[i] == 'UU':
		if newTiers[i] in ['NU','PU']:
			newTiers[i] = 'RU'
	elif curTiers[i] == 'RU':
		if newTiers[i] == 'PU':
			newTiers[i] = 'NU'

	#replace names with numbers (really should have used numbers from the beginning) so it's sortable
	if newTiers[i] == 'Uber':
		poke.append([i,0.0])
	elif newTiers[i] == 'OU':
		poke.append([i,1.0])
	elif newTiers[i] == 'BL':
		poke.append([i,1.5])
	elif newTiers[i] == 'UU':
		poke.append([i,2.0])
	elif newTiers[i] == 'BL2':
		poke.append([i,2.5])
	elif newTiers[i] == 'RU':
		poke.append([i,3.0])
	elif newTiers[i] == 'BL3':
		poke.append([i,3.5])
	elif newTiers[i] == 'NU':
		poke.append([i,4.0])
	elif newTiers[i] == 'PU':
		if i not in NFE:
			poke.append([i,5.0])
		else:
			poke.append([i,5.1])

#print tier list
poke = sorted(poke, key=lambda poke:poke[1])

print "[B]Ubers[/B]"
print "[CODE]"
print keyLookup[poke[0][0]]
for i in range(1,len(poke)):
	if poke[i][1] != poke[i-1][1]:
		print "[/CODE]"
		print ""
		if poke[i][1] == 1.0:
			print "[B]OU[/B]"
		elif poke[i][1] == 1.5:
			print "[B]BL[/B]"
		elif poke[i][1] == 2.0:
			print "[B]UU[/B]"
		elif poke[i][1] == 2.5:
			print "[B]BL2[/B]" 
		elif poke[i][1] == 3.0:
			print "[B]RU[/B]"
		elif poke[i][1] == 3.5:
			print "[B]BL3[/B]"
		elif poke[i][1] == 4.0:
			print "[B]NU[/B]"
		elif poke[i][1] == 5.0:
			print "[B]PU[/B]"
			print 'Note that "PU" is not a real tier and will NOT be supported on the simulator. I post the list here just as a point of reference--these pokemon are the NU of NU.'
			print "[HIDE]"
		elif poke[i][1] == 5.1:
			print "NFEs:"	
		print "[CODE]"
	
	printme=keyLookup[poke[i][0]]
	if newTiers[poke[i][0]] != curTiers[poke[i][0]]:
		#if newTiers[poke[i][0]] != 'PU':
		printme="[B]"+printme
		if newTiers[poke[i][0]] == 'OU':
			printme=printme+" up"
		elif newTiers[poke[i][0]] == 'UU':
			if curTiers[poke[i][0]] == 'OU':
				printme=printme+" down"
			else:
				printme=printme+" up"
		elif newTiers[poke[i][0]] == 'RU':
			if curTiers[poke[i][0]] in ['BL3','NU','PU']:
				printme=printme+" up"
			else:
				printme=printme+" down"
		elif newTiers[poke[i][0]] == 'NU':
			if curTiers[poke[i][0]] == 'RU':
				printme=printme+" down"
			else:
				printme=printme+" up"
		else:
			printme=printme+" down"
		#if newTiers[poke[i][0]] != 'PU':
		printme=printme+" from "+curTiers[poke[i][0]]+"[/B]"
	print printme

print "[/CODE][/HIDE]"

#!/usr/bin/env python2.7

# This script implements the Cocke-Younger-Kasami algorithm to parse a 
# context-free grammar in Chomsky Normal Form.
# Written by Tristan Euan Chong on 2/8/2013

from collections import defaultdict

class BackPointer(object):
	def __init__(self, givenRule, givenKIndex):
		self.rule = givenRule
		self.kIndex = givenKIndex
		self.visited = False

class TreeNode(object):
	def __init__(self, givenData):
		self.parent = None
		self.children = []
		self.data = givenData.strip("'")

	def makeChild(self, inputData):
		newchild = TreeNode(inputData)
		newchild.parent = self
		self.children.append(newchild)
		return newchild

def buildTree(root, backpointers, rootRow, rootColumn, startResult):
	currentNode = root
	currentNodeData = root.data
	backPointerSet = backpointers[rootRow][rootColumn]

	for backPointer in backPointerSet:
		if "->" in backPointer.rule and not backPointer.visited:
			ruleSplit = backPointer.rule.split("->")
			ruleSplit[0] = ruleSplit[0].strip()
			ruleSplit[1] = ruleSplit[1].strip()
			backPointer.visited = True

			if ruleSplit[0] == currentNodeData:
				if "'" in ruleSplit[1]:
					currentNode.makeChild(ruleSplit[1].strip())
					return
				else:
					RHSSplit = ruleSplit[1].split(" ")
					bData = RHSSplit[0].strip()
					cData = RHSSplit[1].strip()
					bNode = currentNode.makeChild(bData)
					cNode = currentNode.makeChild(cData)

					buildTree(bNode, backpointers, rootRow, backPointer.kIndex,
                              "")
					buildTree(cNode, backpointers, backPointer.kIndex, 
                              rootColumn, "")
					return

def printTable(table, numberOfWords):
	for i in range(0, numberOfWords + 1):
		currentString = ""
		for j in range(0, numberOfWords + 1):
			currentString += "\t" + str(i) + ":" + str(j) + " "
			if table[i][j] != None:
				if len(table[i][j]) > 0:
					for item in table[i][j]:
						currentString += item + ","
				else:
					currentString += "empty,"
			else:
				currentString += "null,"
		print currentString

def printTree(rootNode):
	childrenString = ""
	for child in rootNode.children:
		childrenString += printTree(child)
	if childrenString == "":
		return rootNode.data
	else:
		return "\n(" + rootNode.data + " " + childrenString + ")"

def formatTreeResult(inp):
	tokened = inp.split("\n")
	spacesToAdd = 0
	prevSpacesToAdd = 0
	position = 0
	result = ""

	for token in tokened:
		spacesToAdd += 1
		position = 0
		while position < len(token) and position >= 0:
			position = token.find(")", position)
			if position > 0:
				spacesToAdd -= 1
				position += 1
		for i in range(0, prevSpacesToAdd):
			result += " "
		prevSpacesToAdd = spacesToAdd
		result += token + "\n"
	return result

def isUniqueTree(givenTree, treesSoFar):
	for treeSoFar in treesSoFar:
		if givenTree == treeSoFar:
			return False
	return True


nonTerminals = defaultdict(list)
terminals = defaultdict(list)

for line in open("cnf.cfg", "r").readlines():
	if "->" in line:
		splitRule = line.split("->")
		LHS = splitRule[0].strip()
		RHS = splitRule[1].strip()
		
		if "'" in RHS:
			terminals[RHS].append(LHS)
		else:
			nonTerminals[RHS].append(LHS)

count = 0

f = open("project1.out", "w")

for sentence in open("sentences.txt", "r").readlines():
	count += 1
	preparedSentence = sentence.strip("\r\n")
	preparedSentence = preparedSentence.replace(".", " .")
	preparedSentence = preparedSentence.replace("!", " !")
	preparedSentence = preparedSentence.replace("?", " ?")

	words = preparedSentence.split(" ")
	numberOfWordsInSentence = len(words)
	table = [[None for x in range(numberOfWordsInSentence + 1)] 
             for y in range(numberOfWordsInSentence + 1)]
	backpointers = [[None for x in range(numberOfWordsInSentence + 1)] 
                     for y in range(numberOfWordsInSentence + 1)]

	for j in range(1, numberOfWordsInSentence + 1):
		StringA = "'" + words[j-1] + "'"
		table[j-1][j] = []
		backpointers[j-1][j] = []
		if StringA in terminals.keys():
			placeHolderListA = terminals[StringA]
			for terminalString in placeHolderListA:
				table[j-1][j].append(terminalString)
				backpointers[j-1][j].append(BackPointer(terminalString + 
                                                        " -> " + StringA, -1))
		for i in range(j-2, -1, -1):
			table[i][j] = []
			backpointers[i][j] = []
			for k in range(i+1, j):
				placeHolderListB = table[i][k]
				placeHolderListC = table[k][j]
				for StringB in placeHolderListB:
					for StringC in placeHolderListC:
						placeHolderStringRHS = (StringB.strip() + " " + 
                                                StringC.strip())
						if placeHolderStringRHS in nonTerminals.keys():
							placeHolderListLHS = nonTerminals[placeHolderStringRHS]
							for nonTerminal in placeHolderListLHS:
								if nonTerminal != "":
									table[i][j].append(nonTerminal)
									backpointers[i][j].append(BackPointer(nonTerminal + " -> " + placeHolderStringRHS, k))

	resultParses = table[0][numberOfWordsInSentence]

	treeResults = []
	currentTreeResult = ""

	for resultParse in resultParses:

		if resultParse == "TOP":
			root = TreeNode("TOP")
			buildTree(root, backpointers, 0, numberOfWordsInSentence, resultParse)
			currentTreeResult = printTree(root)
			currentTreeResult = formatTreeResult(currentTreeResult)

			if isUniqueTree(currentTreeResult, treeResults):
				treeResults.append(currentTreeResult)
				break

	for treeResult in treeResults:
		f.write(treeResult)

	f.write("\n\n%i\n" % count)
	f.write("---------------------------------------\n")

f.close()

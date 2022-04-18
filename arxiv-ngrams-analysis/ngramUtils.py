# TODO get rid of these globals

noiseBigrams = [('experimental', 'results'), ('experimental', 'result'),
('paper', 'propose'), ('paper', 'proposes'), 
('paper','consider'), ('paper','consider'),
('proposed', 'method'), ('proposed', 'methods'),
('proposed', 'approach'),('proposed', 'approaches'),
('propose', 'novel'), ('proposes', 'novel'), 
('paper', 'presents'), ('paper','present'),
('results', 'show'), ('results', 'showing'),
('show', 'proposed'), 
('paper', 'study'), ('paper', 'studies'),
('allows', 'us'), ('allowed','us'),
('upper', 'bound'),('upper', 'bounds'),
('also', 'show'), 
('extensive','experiments'),
('experiments','show'),
('effectiveness','proposed'),
('recent','years'),
('publicly','available'),
('main', 'result'), ('main', 'results'),
('also','prove'),('et','al'),
('lower', 'bound'), ('lower', 'bounds'), 
('work','propose'), ('work','proposes'),
('work','demonstrates'), ('work','demonstrates'),
('results','demonstrate'), ('results','demonstrated'),]



noiseTrigrams = [ ('experimental', 'results', 'show'), ('experimental', 'results', 'showing'), ('experimental', 'result', 'shows'),
('results', 'show', 'proposed'),('show','proposed','method'),
('paper', 'propose', 'novel'), ('paper', 'proposes', 'novel'),
('demonstrate', 'effectiveness', 'proposed'), ('effectiveness', 'proposed', 'method'),
('necessary', 'sufficient', 'condition'), ('necessary', 'sufficient', 'conditions'),
('experimental','results','demonstrate')]

# really memory inneficient top N bigrams
# where top is defined as the most frequent
# no tie breaking system is put in place
# plural bigrams are attempted to be joined such that [('quantum','field',3),('quantum','fields',2)] --> [('quantum','fields',5)]
# Assuming the case where the pluran and singular appear in similar frequency
# for the case where the singular/plural appears far more frequently, then only
# one will be selected

def topBigrams(freqDist,numBigrams, combinePlurals = True,bigramCountThreshold = 0):
    totalTuples = []
    for bigram,freq in freqDist.items():
        if freq > bigramCountThreshold:
            totalTuples.append((bigram[0],bigram[1],freq))

    # sort by the frequency count
    totalTuples.sort(key=lambda threeTuple: threeTuple[2],reverse=True)
    frequentTuples =[]
    for tupleInd in range(min(2*numBigrams + len(noiseBigrams),len(totalTuples))):
        frequencyTuple = totalTuples[tupleInd]
        aTuple = (frequencyTuple[0],frequencyTuple[1])
        if aTuple not in noiseBigrams:         
            frequentTuples.append(totalTuples[tupleInd])

    if combinePlurals:
        # sort by the second tuple for plural analysis 
        frequentTuples.sort(key=lambda threeTuple: (threeTuple[1],threeTuple[0]))
        indicesToPop = []
        # join plurals
        for tupleIndex in range(len(frequentTuples)):
            if tupleIndex < len(frequentTuples) - 1:
                nextIndex = tupleIndex + 1
                if frequentTuples[nextIndex][1] == frequentTuples[tupleIndex][1] + 's' and frequentTuples[nextIndex][0] == frequentTuples[tupleIndex][0]:
                    indicesToPop.append(tupleIndex)
                    newTuple = (frequentTuples[nextIndex][0],frequentTuples[nextIndex][1],frequentTuples[tupleIndex][2]+frequentTuples[nextIndex][2])
                    frequentTuples[nextIndex] = newTuple
        # remove indeces to pop
        for popIndex in sorted(indicesToPop, reverse=True):
            del frequentTuples[popIndex]

    # sort by the frequency count
    frequentTuples.sort(key=lambda threeTuple: threeTuple[2],reverse=True)
    return frequentTuples[0:numBigrams]


# really memory inneficient top N bigrams
# where top is defined as the most frequent
# no tie breaking system is put in place
# plural bigrams are joined such that [('quantum','field',3),('quantum','fields',2)] --> [('quantum','fields',5)]
def topTrigrams(freqDist,numTrigrams, combinePlurals = True,trigramCountThreshold = 0):
    totalTuples = []
    for ngram,freq in freqDist.items():
        if freq > trigramCountThreshold:
            totalTuples.append((ngram[0],ngram[1],ngram[2],freq))

    # sort by the frequency count
    totalTuples.sort(key=lambda fourTuple: fourTuple[3],reverse=True)
    frequentTuples =[]
    for tupleInd in range(min(2*numTrigrams + len(noiseTrigrams),len(totalTuples))):
        frequencyTuple = totalTuples[tupleInd]
        aTuple = (frequencyTuple[0],frequencyTuple[1],frequencyTuple[2])
        if aTuple not in noiseTrigrams:         
            frequentTuples.append(totalTuples[tupleInd])

    if combinePlurals:
        # sort by the second tuple for plural analysis 
        frequentTuples.sort(key=lambda fourTuple: (fourTuple[2],fourTuple[1],fourTuple[0]))
        indicesToPop = []
        # join plurals
        for tupleIndex in range(len(frequentTuples)):
            if tupleIndex < len(frequentTuples) - 1:
                nextIndex = tupleIndex + 1
                if frequentTuples[nextIndex][2] == frequentTuples[tupleIndex][2] + 's' and frequentTuples[nextIndex][0] == frequentTuples[tupleIndex][0] and frequentTuples[nextIndex][1] == frequentTuples[tupleIndex][1]:
                    indicesToPop.append(tupleIndex)
                    newTuple = (frequentTuples[nextIndex][0],frequentTuples[nextIndex][1],frequentTuples[nextIndex][2],frequentTuples[tupleIndex][3]+frequentTuples[nextIndex][3])
                    frequentTuples[nextIndex] = newTuple
        # remove indeces to pop
        for popIndex in sorted(indicesToPop, reverse=True):
            del frequentTuples[popIndex]

    # sort by the frequency count
    frequentTuples.sort(key=lambda fourTuple: fourTuple[3],reverse=True)
    return frequentTuples[0:numTrigrams]


#TODO: clean up repeated code

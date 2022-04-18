# system imports
import time
import json
import boto3
import calendar
from datetime import datetime
from datetime import date

# arxiv download imports
from arxivOAIUtils import get_list_record_chunk,check_xml_errors,parse_record,parse_xml_listrecords
import xml.etree.ElementTree as ET

# ngram util imports
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.collocations import BigramCollocationFinder
from nltk.corpus import stopwords
from ngramUtils import topBigrams
from ngramUtils import topTrigrams
from tabulate import tabulate

#email imports
from utils import sendHtmlEmailFromGoogleAccount
from config import emailInformation

##########################################################
################ Begin Metadata ##########################

# the analysis file is used in a website so must be js which we generate
trendAnalysisFile = "trendAnalysisResults.js"
BIGRAM_THRESHOLD = 10 # Top N bigrams to get
TRIGRAM_TRESHOLD = 10 # Top N trigrams to get
NUM_DISPLAY_BIGRAMS = 5 # display these many bigrams in email
NUM_DISPLAY_TRIGRAMS = 5 # display this many trigrams in email
MAIL_TRIGRAMS = True
MAIL_TRENDS = True
SEND_TO_S3 = True
trendSiteUrl = "http://arxivtrendsite.s3-website.us-east-2.amazonaws.com/"



# s3 info
from config import s3Info
BUCKET_NAME = s3Info['bucketName']

REGION = s3Info['region']
ACCESS_KEY_ID = s3Info['accessKeyId'] 
SECRET_ACCESS_KEY = s3Info['secretAccessKey'] 
PATH_IN_COMPUTER = trendAnalysisFile 
KEY = trendAnalysisFile # file path in S3 

##########################################################
############### End Metadata #############################


englishStopWords = set(stopwords.words('english'))

trendData = {}

currentYear = datetime.now().year
currentMonth = datetime.now().month
lastMonth = currentMonth -1 if currentMonth !=1 else 12
currentYear = currentYear if currentMonth !=1 else currentYear - 1
_, num_days = calendar.monthrange(currentYear, lastMonth)
first_day = date(currentYear, lastMonth, 1)
last_day = date(currentYear, lastMonth, num_days)
firstDayOfMonth = first_day.strftime('%Y-%m-%d')
lastDayOfMonth = last_day.strftime('%Y-%m-%d')
FIRST_DAY_OF_MONTH=firstDayOfMonth
LAST_DAY_OF_MONTH=lastDayOfMonth 

# taken from: http://export.arxiv.org/oai2?verb=ListSets
arxivSets=["cs",
"econ",
"eess",
"math",
"physics:astro-ph",
"physics:cond-mat",
"physics:gr-qc",
"physics:hep-ex",
"physics:hep-lat",
"physics:hep-ph",
"physics:hep-th",
"physics:math-ph",
"physics:nlin",
"physics:nucl-ex",
"physics:nucl-th",
"physics:physics",
"physics:quant-ph",
"q-bio",
"q-fin",
"stat"]

for site in arxivSets:
    arxivSite=site
    arxivSiteRecords=[]
    resumptionToken = None
    records=[]
    time.sleep(20)  # wait time to prevent OAI server duplicates

    while True:
        xml_root = ET.fromstring(get_list_record_chunk(resumptionToken=resumptionToken,
                                                        set=arxivSite,
                                                        fromDate=FIRST_DAY_OF_MONTH,
                                                        toDate=LAST_DAY_OF_MONTH))
        check_xml_errors(xml_root)
        records, resumptionToken = parse_xml_listrecords(xml_root)
        for record in records:
            arxivSiteRecords.append(record)
        if resumptionToken:
            print('continuing getting records for ' + arxivSite)
            time.sleep(12)  # OAI server usually requires a 10s wait
            continue
        else:
            print('No resumption token, query finished')
            break

    titleTexts = ""
    abstractTexts = ""
    for record in arxivSiteRecords:
        titleTexts += " " + record['title']
        abstractTexts += " " + record['abstract']

    translate_table = dict((ord(char), None) for char in string.punctuation)   
    abstractTexts = abstractTexts.lower()
    abstractTexts = abstractTexts.translate(translate_table)
    titleTexts = titleTexts.lower()
    titleTexts = titleTexts.translate(translate_table)

    # tokenization
    abstractTokens = nltk.word_tokenize(abstractTexts)
    titleTokens = nltk.word_tokenize(titleTexts)
    abstractTokens = [token for token in abstractTokens if not token in englishStopWords]
    titleTokens = [token for token in titleTokens if not token in englishStopWords]
    # bigrams
    abstractBigrams = nltk.bigrams(abstractTokens)
    abstractFreqDistribution = nltk.FreqDist(abstractBigrams)
    titleBigrams = nltk.bigrams(titleTokens)
    titleFreqDistribution = nltk.FreqDist(titleBigrams)
    topAbstractBigrams = topBigrams(abstractFreqDistribution,BIGRAM_THRESHOLD,bigramCountThreshold=5)
    topTitleBigrams = topBigrams(titleFreqDistribution,BIGRAM_THRESHOLD)
    # trigrams
    abstractTrigrams = nltk.ngrams(abstractTokens,3)
    abstractTrigramFreqDist = nltk.FreqDist(abstractTrigrams)
    titleTrigrams = nltk.ngrams(titleTokens,3)
    titleTrigramFreqDist = nltk.FreqDist(titleTrigrams)
    topAbstractTrigrams = topTrigrams(abstractTrigramFreqDist,TRIGRAM_TRESHOLD,trigramCountThreshold=3)       
    topTitleTrigrams = topTrigrams(titleTrigramFreqDist,TRIGRAM_TRESHOLD)

    # replace the arxivesite with a printable version (non-query)
    arxivSite = arxivSite.replace(":"," ")
    trendData[arxivSite] = {'titleBigrams':topTitleBigrams,'titleTrigrams':topTitleTrigrams,'abstractBigrams':topAbstractBigrams,'abstractTrigrams':topAbstractTrigrams}


    # ----------- Begin e-mail logic ------------
    if MAIL_TRENDS:

        resultText = ""
        htmlText = """\
        <html>
        <head>
        <style>
        table {
            font-family: arial, sans-serif;
            border-collapse: collapse;
            width: 80%;
        }

        td, th {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }

        tr:nth-child(even) {
            background-color: #dddddd;
        }
        </style>
        </head>
        <body>
        """
        resultText += "Top Title Bigram Trends for " + arxivSite + "\n"
        htmlText += """<p><a href=" """ + trendSiteUrl + """ ">Trend Site</a></p><br></br>"""
        htmlText +="""<div><center><h2>Top Title Bigram Trends for """ + arxivSite + """</h2></center></div><br><div>"""

        titleBigramDataTable = [['Title Bigram','Count']]
        for loopIndex in range(min(len(topTitleBigrams),NUM_DISPLAY_BIGRAMS)):
            bigram = topTitleBigrams[loopIndex]
            titleBigramDataTable.append([bigram[0]+ " " + bigram[1],bigram[2]])

        resultText += tabulate(titleBigramDataTable, headers="firstrow", tablefmt="grid")
        htmlText += """<center>"""
        tableHtmlText = tabulate(titleBigramDataTable, headers="firstrow", tablefmt="html")
        # tableHtmlText = tableHtmlText.replace("<table>","""<table width="600" style="border:1px solid #333">""")
        htmlText += tableHtmlText
        htmlText += """</center>"""
        htmlText += """<br><br></div>"""

        resultText += "Top Summary Bigram Trends for " + arxivSite + "\n"
        htmlText +="""<div><center><h2>Top Summary Bigram Trends for """ + arxivSite + """</h2></center></div><br><div>"""

        summaryBigramDataTable = [['Summary Bigram','Count']]
        for loopIndex in range(min(len(topAbstractBigrams),NUM_DISPLAY_BIGRAMS)):
            bigram = topAbstractBigrams[loopIndex]
            summaryBigramDataTable.append([bigram[0]+ " " + bigram[1],bigram[2]])

        resultText += tabulate(summaryBigramDataTable, headers="firstrow", tablefmt="grid")
        htmlText += """<center>"""
        tableHtmlText = tabulate(summaryBigramDataTable, headers="firstrow", tablefmt="html")
        # tableHtmlText = tableHtmlText.replace("<table>","""<table width="600" style="border:1px solid #333">""")
        htmlText += tableHtmlText
        htmlText += """</center>"""
        htmlText += """<br><br></div>"""

        if MAIL_TRIGRAMS:
            resultText += "Top Title Trigram Trends for " + arxivSite + "\n"
            htmlText +="""<div><center><h2>Top Title Trigram Trends for """ + arxivSite + """</h2></center></div><br><div>"""
            titleTrigramTable = [['Title Trigram','Count']]
            for loopIndex in range(min(len(topTitleTrigrams),NUM_DISPLAY_TRIGRAMS)):
                trigram = topTitleTrigrams[loopIndex]
                titleTrigramTable.append([trigram[0]+ " " + trigram[1] + " " + trigram[2],trigram[3]])
            resultText += tabulate(titleTrigramTable, headers="firstrow", tablefmt="grid")
            htmlText += """<center>"""
            tableHtmlText = tabulate(titleTrigramTable, headers="firstrow", tablefmt="html")
            # tableHtmlText = tableHtmlText.replace("<table>","""<table width="600" style="border:1px solid #333">""")
            htmlText += tableHtmlText
            htmlText += """</center>"""
            htmlText += """<br><br></div>"""
            resultText += "Top Summary Trigram Trends for " + arxivSite + "\n"
            htmlText +="""<div><center><h2>Top Summary Trigram Trends for """ + arxivSite + """</h2></center></div><br><div>"""
            summaryTrigramTable = [['Summary Trigram','Count']]
            for loopIndex in range(min(len(topAbstractTrigrams),NUM_DISPLAY_TRIGRAMS)):
                trigram = topAbstractTrigrams[loopIndex]
                summaryTrigramTable.append([trigram[0]+ " " + trigram[1] + " " + trigram[2],trigram[3]])
            resultText += tabulate(summaryTrigramTable, headers="firstrow", tablefmt="grid")
            htmlText += """<center>"""
            tableHtmlText = tabulate(summaryTrigramTable, headers="firstrow", tablefmt="html")
            # tableHtmlText = tableHtmlText.replace("<table>","""<table width="600" style="border:1px solid #333">""")
            htmlText += tableHtmlText
            htmlText += """</center>"""
            htmlText += """<br><br></div>"""            
            htmlText += """</body>
            </html>"""

            sendHtmlEmailFromGoogleAccount(toEmail=emailInformation['toEmail'],
            fromEmail=emailInformation['fromEmail'],
            subject="Filtered Arxiv " + arxivSite,
            plainText=resultText,
            htmlText=htmlText,
            username=emailInformation['username'],
            password=emailInformation['password'])



# Write the trend file
stringBuffer = "var trendData = " + json.dumps(trendData)
with open(trendAnalysisFile, "w") as trend_data:
    trend_data.write(stringBuffer)

if SEND_TO_S3:
    s3_resource = boto3.resource(
        's3',
        region_name = REGION, 
        aws_access_key_id = ACCESS_KEY_ID,
        aws_secret_access_key = SECRET_ACCESS_KEY
    )
    s3_resource.Bucket(BUCKET_NAME).put_object(
        Key = KEY, 
        Body = open(PATH_IN_COMPUTER, 'rb')
    )

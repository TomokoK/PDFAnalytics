#
# Script to batch parse PDF input files and generate data analytics based on some input
# DEPS: matplotlib, PyPDF2
# v. 1.x: 2019-07-05
# v. 2.0: 2020-11-15
# Contact: TomokoK @ Github
#


from PyPDF2 import PdfFileReader
from os.path import isfile, join
from os import remove, listdir
import matplotlib.pyplot as plt
import re
import collections
import csv
import sys
import glob
import time


# Format values for the charts
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return '{p:.2f}% ({v:d})'.format(p=pct, v=val)

    return my_autopct


def main():
    # Clear out the output directory if it is not already empty
    print("Program will now clear out the files in the output directory")
    print("Press Ctrl+C to cancel")
    print("5...")
    time.sleep(1)
    print("4...")
    time.sleep(1)
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Deleting files...")
    outputFiles = glob.glob('./output/*', recursive=True)
    for files in outputFiles:
        try:
            remove(files)
        except OSError as e:
            print("ERROR: " + str(e) + " in: " + files)

    # Get a list of files in the pdf directory
    pdfsInDirectory = [f for f in listdir("./pdfs") if isfile(join("./pdfs", f))]

    # Remove non-pdfs from the pdf list
    for i in pdfsInDirectory:
        if i == "mvPDFs.sh" or i == "getPDFs.sh":
            pdfsInDirectory.remove(i)

    # Open the keywords file for reading
    keywordsFile = open("keywords.txt", "r")

    # Create a dictionary of keywords, one for current iteration and one for total
    dictOfKeywords = {}  # current iteration
    totalDictOfKeywords = {}  # running total

    # Populate the dictionaries with the keywords we are looking for
    for line in keywordsFile:
        dictOfKeywords.update({line.rstrip("\n"): 0})
        totalDictOfKeywords.update({line.rstrip("\n"): 0})
    keywordsFile.close()
    # Clear unneeded vars from memory
    del line

    # Create a csv file for each keyword
    keywords = dictOfKeywords.keys()
    for key in keywords:
        try:
            with open('./output/' + str(key) + '.csv', mode='w') as keywordCSV:
                writer = csv.writer(keywordCSV)
                writer.writerow(['Year', 'Page', 'Context: ' + str(key)])
                keywordCSV.close()
        except Exception as e:
            print("ERROR: " + str(e) + ". Check keywords file and retry.")
            sys.exit(1)
    # Clear unneeded vars from memory
    del key
    del keywords

    # Write the csv descriptors (i.e. year and keyword) to the first row
    with open('./output/data.csv', mode='w') as csv_file:
        fieldNames = list(dictOfKeywords.keys())  # convert the dict descriptors into a list
        fieldNames.insert(0, "Year")  # manually insert 'year' into 0,0 as it is not in the dict
        writer = csv.writer(csv_file)
        writer.writerow(fieldNames)
        csv_file.close()

    # Open each pdf in a for loop
    for i in pdfsInDirectory:
        try:
            pdfInput = PdfFileReader(open("./pdfs/" + str(i), "rb"))  # Open pdf
        except Exception as e:
            print("ERROR: " + str(e) + " in file: " + str(i) + ". Please rerun.")
            sys.exit(1)

        numOfPages = pdfInput.getNumPages()  # Get number of pages in open pdf

        # Check for hits page by page
        for j in range(numOfPages):
            currentPage = pdfInput.getPage(j)
            # Extract text on current page into string
            allText = currentPage.extractText()
            # Strip punctuation and numbers from text
            allText = re.sub(r'[.,#!$%/^&*;:\[\]{}=_`~()\\]|\d+|\n', ' ', allText)
            # Format the text into all lowercase
            allText = allText.lower()
            # Iterate through each keyword
            for k in dictOfKeywords:
                try:
                    foundWords = re.findall(r'\s' + k + r'\s', allText)  # Find the keyword in the text
                    #foundWords = re.findall(r'^' + k + r'$', allText)
                    #numOfFoundWords = allText.count(k)
                except Exception as e:
                    print("ERROR: " + str(e) + " in file: " + str(i) +
                          " with keyword: " + str(k) + " on page: " + str(j) +
                          " on word: " + str(l))
                    sys.exit(1)
                numOfFoundWords = len(foundWords)
                if numOfFoundWords != 0:  # Only update the dict if there are keywords
                    valueOfKey = int(dictOfKeywords.get(k)) + numOfFoundWords
                    dictOfKeywords.update({k: valueOfKey})
                    valueOfLongTermKey = int(totalDictOfKeywords.get(k)) + numOfFoundWords
                    totalDictOfKeywords.update({k: valueOfLongTermKey})
                    # Write reference data for each keyword while we are checking for it
                    with open('./output/' + str(k) + '.csv', mode='a') as keywordCSV:
                        writer = csv.writer(keywordCSV)
                        # Hacky BS as above regex will count words with a hyphen even if it shouldn't
                        # e.g. hockey-stick will count as hockey
                        # TODO: bring this up in my next email
                        if k.find('-') == -1:  # If the keyword is unhyphenated, remove hyphens from text
                            allTextFiltered = re.split('[- ]', allText)
                        else:  # If not, just split it into a list based on whitespace
                            allTextFiltered = allText.split()
                        # Iterate over each word in the list
                        for l in range(len(allTextFiltered)):
                            if allTextFiltered[l] == k:  # Check if current iteration matches keyword
                                preKeyword = allTextFiltered[(l - 15):l]  # Extract 10 words before hit
                                postKeyword = allTextFiltered[l:(l + 15)]  # Extract hit and 10 words after
                                snippet = preKeyword + postKeyword  # concat the context
                                # Remove whitespace indices from context list
                                for m in range(len(snippet)):
                                    if snippet[m].isspace():
                                        snippet.pop(m)
                                formattedContext = ' '.join([str(i) for i in snippet])  # Cast from list -> str
                                writer.writerow([i, j, formattedContext])
                        keywordCSV.close()

        # Write the findings to the CSV file
        with open('./output/data.csv', mode='a') as csv_file:
            writer = csv.writer(csv_file)
            csvList = list(dictOfKeywords.values())
            csvList.insert(0, str(i))
            writer.writerow(csvList)
            csv_file.close()

        # Black magic
        sortedDictOfKeywords = collections.OrderedDict(
            sorted(dictOfKeywords.items(), key=lambda kv: (kv[1], kv[0])))
        count = sortedDictOfKeywords.values()
        label = sortedDictOfKeywords.keys()

        # If there are no hits for a keyword, remove it from the chart
        for j in list(sortedDictOfKeywords):
            if sortedDictOfKeywords.get(j) == 0:
                sortedDictOfKeywords.pop(j)

        # Chart formatting
        plt.pie(list(count), labels=list(label), autopct=make_autopct(list(count)), radius=2.0)
        plt.title("Count for the year " + str(i) + "\nPage count (PDF): " + str(numOfPages))
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig('./output/' + str(i) + '-PIE.png')
        plt.show()

        y_pos = [i for i, _ in enumerate(list(label))]
        plt.barh(y_pos, list(count), align='center', alpha=0.5)
        plt.xlabel('Word Count')
        plt.ylabel('Words')
        plt.title("Count for the year " + str(i) + "\nPage count (PDF): " + str(numOfPages))
        plt.yticks(y_pos, list(label))
        plt.savefig('./output/' + str(i) + '-BAR.png')
        plt.show()

        dictOfKeywords = dictOfKeywords.fromkeys(dictOfKeywords, 0)

    # If there are no hits for a keyword, remove it from the final chart
    for i in list(totalDictOfKeywords):
        if totalDictOfKeywords.get(i) == 0:
            totalDictOfKeywords.pop(i)

    # Black magic
    sortedTotalDictOfKeywords = collections.OrderedDict(
        sorted(totalDictOfKeywords.items(), key=lambda kv: (kv[1], kv[0])))
    totalCount = sortedTotalDictOfKeywords.values()
    totalLabels = sortedTotalDictOfKeywords.keys()

    # Chart formatting
    plt.pie(totalCount, labels=totalLabels, autopct=make_autopct(totalCount), radius=2.0)
    plt.title("Total word count for every PDF")
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('./output/totalPie.png')
    plt.show()

    y_pos = [i for i, _ in enumerate(totalLabels)]
    plt.barh(y_pos, totalCount, align='center', alpha=0.5)
    plt.xlabel('Total Word Count')
    plt.ylabel('Words')
    plt.title("Total word count for every PDF")
    plt.yticks(y_pos, totalLabels)
    plt.savefig('./output/totalBar.png')
    plt.show()


if __name__ == "__main__":
    main()

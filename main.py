from PyPDF2 import PdfFileReader
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import re
import collections
import csv


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return '{p:.2f}% ({v:d})'.format(p=pct, v=val)

    return my_autopct


def main():
    pdfsInDirectory = [f for f in listdir("./pdfs") if isfile(join("./pdfs", f))]
    keywordsFile = open("keywords.txt", "r")
    dictOfKeywords = {}
    totalDictOfKeywords = {}

    for line in keywordsFile:
        dictOfKeywords.update({line.rstrip("\n"): 0})  # Create a dict of keywords from the keywords file
        totalDictOfKeywords.update({line.rstrip("\n"): 0})
    keywordsFile.close()

    with open('./output/data.csv', mode='w') as csv_file:
        fieldnames = list(dictOfKeywords.keys())
        fieldnames.insert(0, "Year")
        writer = csv.writer(csv_file)
        writer.writerow(fieldnames)

    for i in pdfsInDirectory:
        if i != ".gitignore":
            try:
                pdfInput = PdfFileReader(open("./pdfs/" + str(i), "rb"))  # open pdf
            except Exception as e:
                print("ERROR: " + str(e) + " in file: " + str(i))
            numOfPages = pdfInput.getNumPages()
            for j in range(numOfPages):
                currentPage = pdfInput.getPage(j)
                allText = currentPage.extractText()  # extract text into array
                allText = allText.lower()
                allText = re.sub(r'[.,\/#!$%/^&\*;:{}=_`~()]', ' ', allText)
                allText = re.sub("\d+", " ", allText)
                for k in dictOfKeywords:
                    foundWords = re.findall(r'\b' + k + r'\b', allText)
                    numOfFoundWords = len(foundWords)
                    if numOfFoundWords != 0:
                        valueOfKey = int(dictOfKeywords.get(k)) + numOfFoundWords
                        dictOfKeywords.update({k: valueOfKey})
                        valueOfLongTermKey = int(totalDictOfKeywords.get(k)) + numOfFoundWords
                        totalDictOfKeywords.update({k: valueOfLongTermKey})

            with open('./output/data.csv', mode='a') as csv_file:
                writer = csv.writer(csv_file)
                csvList = list(dictOfKeywords.values())
                csvList.insert(0, str(i))
                writer.writerow(csvList)

            sortedDictOfKeywords = collections.OrderedDict(
                sorted(dictOfKeywords.items(), key=lambda kv: (kv[1], kv[0])))
            count = sortedDictOfKeywords.values()
            label = sortedDictOfKeywords.keys()

            for j in list(sortedDictOfKeywords):
                if sortedDictOfKeywords.get(j) == 0:
                    sortedDictOfKeywords.pop(j)

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

    for i in list(totalDictOfKeywords):
        if totalDictOfKeywords.get(i) == 0:
            totalDictOfKeywords.pop(i)

    sortedTotalDictOfKeywords = collections.OrderedDict(
        sorted(totalDictOfKeywords.items(), key=lambda kv: (kv[1], kv[0])))
    totalCount = sortedTotalDictOfKeywords.values()
    totalLabels = sortedTotalDictOfKeywords.keys()

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

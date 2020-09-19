from setting import PATH_OF_COMMENTFILE, PATH_OF_SATD_COMMENTFILE, PATH_OF_SATDPATTERN
from tqdm import tqdm
import os
import re
import pandas as pd
import chardet


def getTargetCSV():
    csvfiles = os.listdir(PATH_OF_COMMENTFILE)
    targetCsvfiles = []
    for csvfile in csvfiles:
        if csvfile in os.listdir(PATH_OF_SATD_COMMENTFILE):
            print(f"Already Exists! {csvfile}")
            continue
        if csvfile == ".DS_Store":
            print("CSV file Error: .DS_Store")
            continue

        targetCsvfiles.append(csvfile)
    
    return targetCsvfiles


def readSatdPattern():
    with open(PATH_OF_SATDPATTERN) as f:
        satdPatternList = f.readlines()
        satdPatternList = list(map(lambda s: s.replace('\n', ''), satdPatternList))

        return satdPatternList


def isSATD(comment):
    global satdPatternList

    # パターンが一つでも含まれていたらSATD
    for satdPattern in satdPatternList:
        if satdPattern.lower() in str(comment).lower():
            return True
    return False


def detectSATD(csvfile):
    df = pd.read_csv(f'./{PATH_OF_COMMENTFILE}/{csvfile}', index_col=0, encoding='utf-8-sig')

    df = df[ df['Comments'].apply(lambda com: isSATD(com))]
    df = df.assign(isSATD=1)
    
    df.to_csv(f'./{PATH_OF_SATD_COMMENTFILE}/{csvfile}')


if __name__ == "__main__":
    satdPatternList = readSatdPattern()
    csvfiles = getTargetCSV()

    for csvfile in tqdm(csvfiles):
        detectSATD(csvfile)




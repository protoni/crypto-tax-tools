from datetime import datetime

# Constants
TYPE_FIN_DEPOSIT   = "Talletus"
TYPE_FIN_FAST_BUY  = "Pikaosto"
TYPE_FIN_SENT      = "Lähetetty maksu"
TYPE_FIN_WITHDRAW  = "Nosto"
TYPE_FIN_FAST_SELL = "Pikamyynti"
TYPE_FIN_RECEIVE   = "Vastaanotettu maksu"

STATE_FIN_READY    = "Valmis"
                   
TYPE_ENG_DEPOSIT   = "Deposit"
TYPE_ENG_TRADE     = "Trade"
TYPE_ENG_WITHDRAW  = "Withdrawal"


# Timezone offset ( hours )
TIME_OFFSET        = -2

file = "balances-20210622-211215.csv"
#file = "balances-20200807-235453.csv"
exports = "exports"
path = exports + "/" + file

print("File: " + path)


def readFile(path):
    f = open(path, "r")
    data = f.read()
    f.close()
    return data

# Returns a list of lines in reversed order by date
def reverseDateOrder(data):
    data = data.split("\n")
    data.reverse()
    
    # Delete trailing empty line
    data.pop(0)
    
    # Delete info row
    data.pop(-1)
    
    return data
    

# Convert ' 11.11.2017 16:35 ' date to ' 2019-06-26 23:11:00 '
# params:
#  date - raw date string
#  offset - hours as offset
def convertDate(date, offset):
    
    separated = date.split(" ")

    YMD = separated[0].split(".")
    
    year = YMD[2]
    month = YMD[1]
    day = YMD[0]
    
    if int(month) < 10:
        month = "0" + month
        
    if int(day) < 10:
        day = "0" + day
    
    newYmd = year + "-" + month + "-" + day + " " + separated[1] + ":00"
    
    # Change timezone
    if offset != 0:
        
        dt = datetime.strptime(newYmd, '%Y-%m-%d %H:%M:%S')
        ms = (dt.timestamp() * 1000) + ( offset * 3600000)
        
        newYmd = datetime.fromtimestamp(float(ms)/1000).strftime('%Y-%m-%d %H:%M:%S')
        
    return newYmd

def convertRow(row):
    splitted = row.split(',')
    
    date = convertDate(splitted[0], TIME_OFFSET)
    
    return "null"

# Remove trailing € sign and space
def getFee(fee):
    trailingCount = len(fee.split(" ")[1])
    
    return fee[0: (trailingCount+1) * -1]

# Remove first character ( - or + sign ) and trailing € sign and space
def getValue(val):
    trailingCount = len(val.split(" ")[1])
    
    return val[1: (trailingCount+1) * -1]

def get(val):
    return "\"" + val + "\", "

def getEnd(val):
    return "\"" + val + "\""

def createRow(type, buy, cur1, sell, cur2, fee, cur3, exc, grp, cmnt, ts):
    #newLine += "\"" + type + "\"," + "\"" + trimVal(splitted[4]) + "\", " + "\"" + splitted[1] + "\", " + "\"\", " + "\"\", " + "\"\", " + "\"\", " + "\"Coinmotion\", " + "\"\", " + "\"EUR deposit\", " + "\"" + convertDate(splitted[0]) + "\""
    
    return get(type) + get(buy) + get(cur1) + get(sell) + get(cur2) + get(fee) + get(cur3) + get(exc) + get(grp) + get(cmnt) + getEnd(ts)

def convertRows(data):
    newData = []
    recognized = 0
    notRecognized = 0
    skippedCount = 0
    skippedLines = []
    
    print("Found rows: " + str(len(data)))
    
    for x in range(len(data)):
        line = data[x]
        
        # convert
        splitted = line.split(',')
        date = convertDate(splitted[0], TIME_OFFSET)
        
        oldRecognized = recognized
        cryptoLine = ""
        # If buying crypto with Fiat
        if splitted[1] == 'EUR' and splitted[2] == TYPE_FIN_FAST_BUY:
            cryptoLine = data[x+1]
            cryptoLineSplitted = cryptoLine.split(',')
            #print("Trading " + splitted[4] + " EUR to" + cryptoLineSplitted[4] + " with fee " + splitted[5])
            newLine = ""
            newLine = createRow("Trade", getValue(cryptoLineSplitted[4]), cryptoLineSplitted[1], getValue(splitted[4]), splitted[1], getFee(splitted[5]), splitted[1], "Coinmotion", "", "EUR to Crypto trade", convertDate(splitted[0], TIME_OFFSET))
            print(newLine)
            recognized += 1
        
        # If selling crypto to Fiat
        if splitted[1] == 'EUR' and splitted[2] == TYPE_FIN_FAST_SELL:
            cryptoLine = data[x+1]
            cryptoLineSplitted = cryptoLine.split(',')
            newLine = ""
            newLine = createRow("Trade", getValue(splitted[4]), splitted[1], getValue(cryptoLineSplitted[4]), cryptoLineSplitted[1], getFee(splitted[5]), splitted[1], "Coinmotion", "", "EUR to Crypto trade", convertDate(splitted[0], TIME_OFFSET))
            print(newLine)
            recognized += 1
            
        # If Depositing Fiat
        if splitted[2] == TYPE_FIN_DEPOSIT and splitted[1] == 'EUR':
            #print("Depositing " + splitted[4])
            newLine = ""
            #newLine += "\"Deposit\", " + "\"" + trimVal(splitted[4]) + "\", " + "\"" + splitted[1] + "\", " + "\"\", " + "\"\", " + "\"\", " + "\"\", " + "\"Coinmotion\", " + "\"\", " + "\"EUR deposit\", " + "\"" + convertDate(splitted[0]) + "\""
            newLine = createRow("Deposit", getValue(splitted[4]), splitted[1], "", "", "", "", "Coinmotion", "", "EUR deposit", convertDate(splitted[0], TIME_OFFSET))
            print(newLine)
            recognized += 1
        
        # If Depositing Crypto
        if splitted[2] == TYPE_FIN_RECEIVE and splitted[1] != 'EUR':
            newLine = ""
            newLine = createRow("Deposit", getValue(splitted[4]), splitted[1], "", "", "", "", "Coinmotion", "", "Crypto deposit", convertDate(splitted[0], TIME_OFFSET))
            print(newLine)
            recognized += 1
        
        # If Withdrawing Fiat
        if splitted[2] == TYPE_FIN_WITHDRAW:
            #print("Withdrawing " + splitted[4])
            newLine = createRow("Withdrawal", "", "", getValue(splitted[4]), splitted[1], getFee(splitted[5]), splitted[1], "Coinmotion", "", "Fiat withdrawal", convertDate(splitted[0], TIME_OFFSET))
            print(newLine)
            recognized += 1
            
        # If Withdrawing Crypto
        if splitted[2] == TYPE_FIN_SENT:
            #print("Sending " + splitted[4] + " with fee " + splitted[5])
            newLine = createRow("Withdrawal", "", "", getValue(splitted[4]), splitted[1], getFee(splitted[5]), splitted[1], "Coinmotion", "", "Crypto transfer", convertDate(splitted[0], TIME_OFFSET))
            print(newLine)
            recognized += 1
                
        if oldRecognized == recognized:
            skippedCount += 1
            skippedLines.append(splitted)
                
        if oldRecognized == recognized  and cryptoLine != "":
            notRecognized += 1
            pass
            
        
            
    print("recognized: " + str(recognized) + " lines")
    print("notRecognized: " + str(notRecognized))
    
    # Skips lines like these:
    # ['28.7.2020 00:05', 'XLM', 'Pikaosto', 'Valmis', '+615.3501901 XLM', '', '0.080442 € / 1 XLM', '', '+0.0000000 XLM', '+1506.6318350 XLM']
    print("skippedCount: " + str(skippedCount))
    
    # Check that skipped lines contains only uninformative lines
    # Uncomment this to inspect skipped lines
    #if skippedCount > 0:
    #    for line in skippedLines:
    #        print(line)


data = reverseDateOrder(readFile(path))

convertRows(data)


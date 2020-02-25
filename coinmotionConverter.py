
# Constants
TYPE_FIN_DEPOSIT  = "Talletus"
TYPE_FIN_FAST_BUY = "Pikaosto"
TYPE_FIN_SENT     = "Lähetetty maksu"
TYPE_FIN_WITHDRAW = "Nosto"

STATE_FIN_READY   = "Valmis"

TYPE_ENG_DEPOSIT  = "Deposit"
TYPE_ENG_TRADE    = "Trade"
TYPE_ENG_WITHDRAW = "Withdrawal"


file = "coinmotion-balances-20200216-223558.csv"
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
def convertDate(date):
    
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
    
    return newYmd

def convertRow(row):
    splitted = row.split(',')
    
    date = convertDate(splitted[0])
    
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

    for x in range(len(data)):
        line = data[x]
        
        # convert
        splitted = line.split(',')
        date = convertDate(splitted[0])
        
        # If buying crypto with Fiat
        if splitted[1] == 'EUR' and splitted[2] == TYPE_FIN_FAST_BUY:
            cryptoLine = data[x+1]
            cryptoLineSplitted = cryptoLine.split(',')
            #print("Trading " + splitted[4] + " EUR to" + cryptoLineSplitted[4] + " with fee " + splitted[5])
            recognized += 1
            
        # If Depositing Fiat
        if splitted[2] == TYPE_FIN_DEPOSIT:
            #print("Depositing " + splitted[4])
            newLine = ""
            #newLine += "\"Deposit\", " + "\"" + trimVal(splitted[4]) + "\", " + "\"" + splitted[1] + "\", " + "\"\", " + "\"\", " + "\"\", " + "\"\", " + "\"Coinmotion\", " + "\"\", " + "\"EUR deposit\", " + "\"" + convertDate(splitted[0]) + "\""
            newLine = createRow("Deposit", getValue(splitted[4]), splitted[1], "", "", "", "", "Coinmotion", "", "EUR deposit", convertDate(splitted[0]))
            print(newLine)
            recognized += 1
            
        # If Withdrawing Fiat
        if splitted[2] == TYPE_FIN_WITHDRAW:
            #print("Withdrawing " + splitted[4])
            newLine = createRow("Withdrawal", "", "", getValue(splitted[4]), splitted[1], getFee(splitted[5]), splitted[1], "Coinmotion", "", "Fiat withdrawal", convertDate(splitted[0]))
            print(newLine)
            recognized += 1
            
        # If Withdrawing Crypto
        if splitted[2] == TYPE_FIN_SENT:
            #print("Sending " + splitted[4] + " with fee " + splitted[5])
            newLine = createRow("Withdrawal", "", "", getValue(splitted[4]), splitted[1], getFee(splitted[5]), splitted[1], "Coinmotion", "", "Crypto transfer", convertDate(splitted[0]))
            print(newLine)
            recognized += 1
            
    print("recognized + " + str(recognized) + " lines")


data = reverseDateOrder(readFile(path))

convertRows(data)


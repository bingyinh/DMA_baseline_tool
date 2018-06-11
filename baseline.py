## Input: csv file, col 1 X, col 2 Y
import csv
import copy
import glob

def interpolation(coord1,coord2,y):
    slope = (coord2[1] - coord1[1])/(coord2[0] - coord1[0])
    x = coord2[0] - (coord2[1] - y)/slope
    return (x,y)

def myJade(csvDir):
    DATA_raw = [] # list storing coordinate tuples
    # read data points
    with open(csvDir, "rb") as f:
        for row in csv.reader(f):
            DATA_raw.append((float(row[0]), float(row[1])))
    # find the original peak
    DATAcopy = copy.deepcopy(DATA_raw)
    DATAcopy.sort(key=lambda tup: tup[1])
    ypeakorg = DATAcopy[-1][1]
    xpeakorg = DATAcopy[-1][0]
    # remove the right tail
    yRightTailMin = ypeakorg # initialize the min y of the right tail using ypeakorg
    index = 0
    minIndex = 0
    for coord in DATA_raw:
        if coord[0] > xpeakorg and coord[1] < yRightTailMin:
            yRightTailMin = coord[1]
            minIndex = index
        index += 1
    DATA = DATA_raw[0:minIndex+1]
    # sort
    DATA.sort(key=lambda tup: tup[0])
    # compute the baseline function
    left = DATA[0]
    xl = left[0]
    yl = left[1]
    right = DATA[-1]
    xr = right[0]
    yr = right[1]
    kbase = (yr - yl)/(xr - xl)
    bbase = yl - kbase * xl
    # baseline standardization and find the peak
    DATA_BL = []
    ypeak = -999999999999999.0
    xpeak = -999999999999999.0
    for coord in DATA:
         x = coord[0]
         y = coord[1]
         ynew = y - (kbase * x + bbase)
         if ynew > ypeak:
            ypeak = ynew
            xpeak = x
         DATA_BL.append((x,ynew))
    # find the peak
    halfpeak = ypeak*0.5
    # find the half width
    # init
    leftInterPo = (-999999999999999.0,-999999999999999.0) # a coord for left interpolation
    rightInterPo = (-999999999999999.0,-999999999999999.0) # a coord for right interpolation
    (prevx, prevy) = DATA_BL[0]
    for coord in DATA_BL:
        if prevy < halfpeak and coord[1] >= halfpeak:
            leftInterPo = interpolation((prevx,prevy),coord,halfpeak)
        elif prevy > halfpeak and coord[1] <= halfpeak:
            rightInterPo = interpolation((prevx,prevy),coord,halfpeak)
        (prevx, prevy) = coord # update prevx
        
    halfwidth = rightInterPo[0] - leftInterPo[0]
##    print "Before baseline redefinition, peak is at coordinate: " + str((xpeakorg,ypeakorg))
##    print "After baseline redefinition, peak is at coordinate: " + str((xpeak,ypeak))
##    print "Halfwidth is: " + str(halfwidth)
    return (xpeakorg, ypeakorg, xpeak, ypeak, halfwidth)

def myJadeReport(csvDir):
    csvFiles = glob.glob(csvDir + "*.csv")
    output = []
    for csvfile in csvFiles:
        try:
            (xpeakorg, ypeakorg, xpeak, ypeak, halfwidth) = myJade(csvfile)
            csvDict = {'csv file':csvfile.split('\\')[-1], 'Peak X': xpeakorg, 'Peak Y':ypeakorg, 'Peak X (baseline tuned)': xpeak, 'Peak Y (baseline tuned)': ypeak, 'Halfwidth (deg C)':halfwidth}
            output.append(csvDict)
        except:
             print csvfile + " is spicy chicken!"   
    with open(csvDir + 'summary.csv', 'wb') as f:
        writer = csv.DictWriter(f, fieldnames = ['csv file', 'Peak X', 'Peak Y', 'Peak X (baseline tuned)', 'Peak Y (baseline tuned)', 'Halfwidth (deg C)'])
        writer.writeheader()
        for cd in output:
            writer.writerow(cd)
    print "Summary generated at: " + csvDir + 'summary.csv'
    return
    
if __name__ == "__main__":
    csvDir = raw_input("Please specify the directory of csv files:")
    csvDir = csvDir.strip()
    if csvDir[-1] != "/":
        csvDir += "/"
    myJadeReport(csvDir)
    

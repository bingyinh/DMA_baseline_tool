## Input: csv file, col 1 X, col 2 Y
import csv
import copy
import glob

def interpolation(coord1,coord2,y):
    slope = (coord2[1] - coord1[1])/(coord2[0] - coord1[0])
    x = coord2[0] - (coord2[1] - y)/slope
    return (x,y)

# a helper method that finds the coordinate of the "foot" of the peak.
# sortedDATA: a list of sorted coordinates tuples
# direction: "left" finds the left foot, "right" finds the right foot
# threshold: the largest slope considered as flat
# xpeakorg: the original x-coordinate of the peak
def footFinder(sortedDATA, direction, threshold, xpeakorg):
    myDATA = copy.deepcopy(sortedDATA)
    slope_init = 1e9
    slope_prev = slope_init
    if direction.lower() == 'right':
        myDATA = list(reversed(myDATA)) # reverse the list
        (prevx, prevy) = myDATA[0] # record the previous coordinate
        for coord in myDATA:
            # skip the first coordinates
            if coord == (prevx, prevy):
                continue
            # start from the second coordinates
            (x, y) = coord
            # if we move to the other side of the peak, return the outmost coord on the right
            if x < xpeakorg:
                return (myDATA[0][0], myDATA[0][1], slope_init)
            # else check the slope
            slope = (y - prevy) / float(x - prevx)
            # if the slope exceeds the threshold, return the previous coord
            if abs(slope) > threshold:
                return (prevx, prevy, slope_prev)
            (prevx, prevy) = (x, y) # update (prevx, prevy)
            slope_prev = slope # update slope_prev
    else:
        (prevx, prevy) = myDATA[0] # record the previous coordinate
        for coord in myDATA:
            # skip the first coordinates
            if coord == (prevx, prevy):
                continue
            # start from the second coordinates
            (x, y) = coord
            # if we move to the other side of the peak, return the outmost coord on the left
            if x > xpeakorg:
                return (myDATA[0][0], myDATA[0][1], slope_init)
            # else check the slope
            slope = (y - prevy) / float(x - prevx)
            # if the slope exceeds the threshold, return the previous coord
            if abs(slope) > threshold:
                return (prevx, prevy, slope_prev)
            (prevx, prevy) = (x, y) # update (prevx, prevy)
            slope_prev = slope # update slope_prev
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
    # find the left end of the peak
    threshold = 0.005
    (xl, yl, slopel) = footFinder(DATA, 'left', threshold, xpeakorg)    
    # find the right end of the peak
    (xr, yr, sloper) = footFinder(DATA, 'right', threshold, xpeakorg)
    if slopel < threshold and sloper < threshold:
        kbase = (yr - yl)/(xr - xl)
        bbase = yl - kbase * xl
    elif slopel < threshold and sloper >= threshold:
        kbase = 0
        bbase = yl
    elif slopel >= threshold and sloper < threshold:
        kbase = 0
        bbase = yr
    else: # both slopel and sloper >= threshold
        return (xpeakorg, ypeakorg, xpeak, 'Are you sure you plot all the data points? Too steep on both ends!', 'N/A')
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
    halfwidth = 'N/A' if halfwidth < 0 else halfwidth
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
    

from mongodb import *


indexer = 0
_ADMIN = [712156622]
_Courses = OutlineCollection.find_one()['vals']
_List = OutlineCollection.find_one()['courses']
_CODE = OutlineCollection.find_one()['code']
availableCourses = list(_CODE.keys())
_OPTION = []
reset = 0
tempL = []
for code in range(0, len(availableCourses)-1, 2):
    if reset == 5:
        reset = 0
        _OPTION.append(tempL)
        tempL = []
    else:
        tempL.append(availableCourses[code] +
                     "        "+availableCourses[code+1])
        reset += 1

meetings = [
  ['tom', 1230, 1300],
  ['nick', 845, 900],
  ['tom', 1300, 1500],
  ['tom', 1700, 1710],
  ['nick', 1449, 1501]
]

def can_take_meeting(name, starttime, endtime):
    for item in meetings:
        if name== item[0]:
            availablestarttime=item[1]
            availableendtime=item[2]
            if endtime<availablestarttime:
                return True
            if starttime>availableendtime:
                return True
    return False

print(can_take_meeting('tom', 850, 855))

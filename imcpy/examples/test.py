import csv
import numpy as np
import imcpy
from imcpy.actors.dynamic import DynamicActor
from imcpy.decorators import Subscribe, RunOnce


def ExtractChallCords(fn):
    with open(fn, 'r') as file:
        reader = csv.reader(file)
        chall_coord = list(map(tuple, reader))
        chall_coord = [t[0] for t in chall_coord]
        #print(chall_coord)
    
    # Add to PlanSpecification
    spec = imcpy.PlanSpecification()
    spec.plan_id = 'TestPlan'
    spec.start_man_id = 'maneuver0'
    spec.description = 'A test plan sent from imcpy'

    for i in range(int(len(chall_coord)/2)):
        # Define manouver name according to waypoint
        man = "man" + str(i)
        print(man)

        man = imcpy.Goto()
        man.z = 0.0
        man.z_units = imcpy.ZUnits.DEPTH
        
        #man.lat, man.lon = imcpy.coordinates.WGS84.displace(lat, lon, n=100.0, e=0.0)
        man.lat = float(chall_coord[2*i])*np.pi/180     #0,2,4..
        man.lon = float(chall_coord[2*i+1])*np.pi/180    #1,3,5..
        print(man.lat,man.lon,'\n')
    
        man.speed = 5
        man.speed_units = imcpy.SpeedUnits.METERS_PS
    
        # Add to PlanManeuver message
        pman = imcpy.PlanManeuver()
        pman.data = man
        pman.maneuver_id = 'maneuver' + str(i)
        print(man)

        spec.maneuvers.append(pman)

    print(spec)    


    return chall_coord


if __name__ == '__main__':
    # Get the set of destination coordinates 
    chall_coord = ExtractChallCords('coord.csv')

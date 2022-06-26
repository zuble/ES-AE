"""
Addapted from gh imcpy/examples/keyboard_input_example.py

Communication over terminal with any running dune instance in the same lan/wifi-acess-point
"""

import logging
import sys
from typing import Tuple
import asyncio
import numpy as np
import csv
import imcpy
from imcpy.actors.dynamic import DynamicActor
from imcpy.decorators import Subscribe, RunOnce

logger = logging.getLogger('Gambozino')

def ExtractChallCords(fn):
    with open(fn, 'r') as file:
        reader = csv.reader(file)
        coord = list(map(tuple, reader))
        chall_coord = [t[0] for t in coord]
        chall_coord_rad = [float(t[0]) * np.pi/180 for t in coord]
    return chall_coord, chall_coord_rad


class KeyboardActor(DynamicActor):
    def __init__(self, target_name):
        """
        Initialize the actor
        :param target_name: The name of the target system
        """
        super().__init__()
        self.target_name = target_name
        self.estate = None

        # This list contains the target systems to maintain communications with
        self.heartbeat.append(target_name)

    def from_target(self, msg):
        try:
            node = self.resolve_node_id(msg)
            return node.name == self.target_name
        except KeyError:
            return False

    @Subscribe(imcpy.EstimatedState)
    def recv_estate(self, msg: imcpy.EstimatedState):
        if self.from_target(msg):
            if self.estate is None:
                logger.info('Target connected')
            self.estate = msg

    def on_console(self, line):
        if line == 'exit':
            # Exit actor (terminate)
            logger.info('Stopping...')
            self.stop()

        elif line == 'stop':
            # Stop vehicle
            try:
                logger.info('Aborting...')
                abort = imcpy.Abort()
                self.send(self.target_name, abort)
            except KeyError:
                logger.error('Failed to send abort')

        elif line == 'wp':
            # Load destinatnion coordinates
            if self.estate is None:
                print()
                logger.info('Vehicle not connected')
            else:
                print()
                logger.info('Waypoints Description')

                lat_rad, lon_rad, hae = imcpy.coordinates.toWGS84(self.estate)
                print('\n-SELF: ',lat_rad,',',lon_rad,'||',lat_rad*180/np.pi,',',lon_rad*180/np.pi)

                for i in range(int(len(chall_coord)/2)):
                    wp = "-wp"+str(i)+": "
                    print(wp,float(chall_coord_rad[2*i]),',',float(chall_coord_rad[2*i+1]),'||',float(chall_coord[2*i]),',',float(chall_coord[2*i+1]))
                    
                print('.\n.\n.\n.')

        elif line == 'start':
            # Send vehicle 100 meters north of its current position
            if self.estate is None:
                print()
                logger.info('Vehicle not connected')
            else:
                print()
                logger.info('IMC Plan Definition Phase\n')

                print("Creating a PlanSpecification")
                spec = imcpy.PlanSpecification()
                spec.plan_id = 'TestPlan'
                spec.start_man_id = 'maneuver0'
                spec.description = 'A test plan sent from imcpy'

                print(".\n.\n.\n.\nCreating a PlanManeuver w/ a Goto message for each wp")
                for i in range(int(len(chall_coord)/2)):
                    #Goto message 4 each pair of entries in coord.csv ((lat0,lon0);(lat1,lon1)..)
                    man = imcpy.Goto()
                    man.z = 0.0
                    man.z_units = imcpy.ZUnits.DEPTH
                    #man.lat, man.lon = imcpy.coordinates.WGS84.displace(lat, lon, n=100.0, e=0.0)
                    man.lat = chall_coord_rad[2*i]      #0,2,4..
                    man.lon = chall_coord_rad[2*i+1]    #1,3,5..
                    man.speed = 5
                    man.speed_units = imcpy.SpeedUnits.METERS_PS

                    goto = "goto"+str(i)+": "
                    print('\n',goto,man.lat,',',man.lon,', speed',man.speed)
                
                    # Add it to PlanManeuver message
                    pman = imcpy.PlanManeuver()
                    pman.data = man
                    pman.maneuver_id = 'maneuver' + str(i)

                    spec.maneuvers.append(pman)
                    print("PlanManeuver",i," added to PlanSpecification")


                print(".\n.\n.\n.\nCreating a PlanTransition between the wp")
                for i in range(int(len(chall_coord)/2)-1):
                    
                    trans = imcpy.PlanTransition()
                    man_src = 'maneuver'+str(i)
                    trans.source_man = man_src

                    man_dest = 'maneuver'+str(i+1)
                    trans.dest_man = man_dest

                    tr = "tr"+str(i)+": "
                    print('\n',tr,man_src,'->',man_dest)

                    spec.transitions.append(trans)
                    print("Transition",i," added to PlanSpecification")


                print(".\n.\n.\nCreating PlanControl")
                pc = imcpy.PlanControl()
                pc.type = imcpy.PlanControl.TypeEnum.REQUEST
                pc.op = imcpy.PlanControl.OperationEnum.START
                pc.plan_id = 'TestPlan'
                pc.arg = spec

                
                self.send(self.estate, pc)
                print(".\n.\n.\nPlan sent to Gambozino aquatic voiture")
        else:
            logger.error('Unknown command')

    @RunOnce()
    async def aio_readline(self):
        try:
            while True:
                # TODO: this causes the stop() function to hang, as run_in_executor is not cancelled
                #       and waits for the next keyboard input before returning. Consider using
                #       the aioconsole package instead.
                rd = await self._loop.run_in_executor(None, sys.stdin.readline)
                for line in rd.splitlines():
                    self.on_console(line.strip())
        except RuntimeError:
            pass


if __name__ == '__main__':
    # Setup logging level and console output
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    chall_coord, chall_coord_rad = ExtractChallCords('waypoints.csv')

    # Create an actor, targeting the caravela system
    actor = KeyboardActor('caravela')

    # This command starts the asyncio event loop
    actor.run()

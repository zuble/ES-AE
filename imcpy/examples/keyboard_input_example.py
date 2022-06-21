"""
Illustrates how to run an actor which responds to console input (e.g. over ssh).
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

logger = logging.getLogger('examples.KeyboardActor')

def ExtractChallCords(fn):
    with open(fn, 'r') as file:
        reader = csv.reader(file)
        chall_coord = list(map(tuple, reader))
        chall_coord = [t[0] for t in chall_coord]
        #print(chall_coord)
    return chall_coord


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
        elif line == 'start':
            # Send vehicle 100 meters north of its current position
            if self.estate is None:
                logger.info('Vehicle not connected')
            else:
                logger.info('Starting...')

                print("Creating PlanSpecification")
                spec = imcpy.PlanSpecification()
                spec.plan_id = 'TestPlan'
                spec.start_man_id = 'maneuver0'
                spec.description = 'A test plan sent from imcpy'

                # Compute vehicle atual lat/lon
                lat, lon, hae = imcpy.coordinates.toWGS84(self.estate)
                print('SELF_WGS84(rads):',lat,lon,'\n')

                # plan maneuver creation for each pair of entries in coord.csv (lat, lon..)
                print(chall_coord)
                for i in range(int(len(chall_coord)/2)):
                    # Define manouver name according to waypoint
                    man = "man" + str(i)
                    print(man)

                    man = imcpy.Goto()
                    man.z = 0.0
                    man.z_units = imcpy.ZUnits.DEPTH
                    
                    #man.lat, man.lon = imcpy.coordinates.WGS84.displace(lat, lon, n=100.0, e=0.0)
                    man.lat = float(chall_coord[2*i])*np.pi/180      #0,2,4..
                    man.lon = float(chall_coord[2*i+1])*np.pi/180    #1,3,5..
                    print(man.lat,man.lon,'\n')
                
                    man.speed = 5
                    man.speed_units = imcpy.SpeedUnits.METERS_PS
                
                    # Add to PlanManeuver message
                    pman = imcpy.PlanManeuver()
                    pman.data = man
                    pman.maneuver_id = 'maneuver' + str(i)
                    print(man)

                    print("Adding Maneuver",2*i," to PlanSpecification")
                    spec.maneuvers.append(pman)
                
                # plan transition for each pair of plan maneuvers
                for i in range(int(len(chall_coord)/2)):
                    
                    trans = imcpy.PlanTransition()
                    maneuver_id = 'maneuver' + str(2*i)
                    trans.source_man = maneuver_id
                    maneuver_id = 'maneuver' + str(2*i+1)
                    trans.dest_man = maneuver_id

                    print("Adding Transition",2*i," to PlanSpecification")
                    spec.transitions.append(trans)

                print("Starting plan\n",spec,"\n")
                pc = imcpy.PlanControl()
                pc.type = imcpy.PlanControl.TypeEnum.REQUEST
                pc.op = imcpy.PlanControl.OperationEnum.START
                pc.plan_id = 'TestPlan'
                pc.arg = spec

                print("Plan sent to caravela")
                self.send(self.estate, pc)
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

    # Get the set of destination coordinates 
    chall_coord = ExtractChallCords('coord.csv')

    # Create an actor, targeting the lauv-simulator-1 system
    actor = KeyboardActor('caravela')

    # This command starts the asyncio event loop
    actor.run()



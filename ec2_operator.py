#!/usr/bin/python

import boto.ec2
import croniter
import datetime

def change_state (state, sched_start, sched_stop, now):
   '''Determine if timeis within the start and stop window and return that the state should be changed'''      

   changeState = False
   
   try:
      cronStart = croniter.croniter(sched_start,now)
      nextStart = cronStart.get_next(datetime.datetime)

      cronStop = croniter.croniter(sched_stop,now)
      nextStop = cronStop.get_next(datetime.datetime)

      if (state == 'running' and (nextStop >= nextStart)):
         changeState = True
      elif (state == 'stopped' and (nextStart >= nextStop)):
         changeState = 'True'
   except:
      return False

   return changeState

now = datetime.datetime.now()

conn=boto.ec2.connect_to_region('us-west-2')
reservations = conn.get_all_instances()

start_list = []
stop_list = []
for res in reservations:
   for inst in res.instances:
      name = inst.tags['Name'] if 'Name' in inst.tags else 'Unknown'
      start_sched = inst.tags['auto:start'] if 'auto:start' in inst.tags else None
      stop_sched = inst.tags['auto:stop'] if 'auto:stop' in inst.tags else None
      state = inst.state
      print "%s (%s) [%s] [%s] [%s]" % (name, inst.id, state, start_sched, stop_sched)
      if start_sched != None and state == "stopped" and change_state(state, sched_start, sched_stop, now):
        start_list.append(inst.id)
      if stop_sched != None and state == "running" and change_state(state, sched_start, sched_stop, now):
        stop_list.append(inst.id)

if len(start_list) > 0:
   ret = conn.start_instances(instance_ids=start_list, dry_run=False)
   print "start_instances %s" % ret
if len(stop_list) > 0:
   ret = conn.stop_instances(instance_ids=stop_list, dry_run=False)
   print "stop_instances %s" % ret

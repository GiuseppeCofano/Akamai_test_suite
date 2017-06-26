#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#last edit 21/03/2010
import os, sys
import time
import csv
import re
from array import *
import string
#ip.src == 192.168.0.10 and tcp.dstport == 80 and http.request.method == POST

import dpkt


class AkamaiLog:
   def __init__(self,filename,suffix, tcp_port):
      self.header = '%ts buffer buff_target x1 fps x2 x3 bwe_h bwe_l level_n level_kbps x4 ts2 throttle'
      self.suffix = suffix
      self.tcp_port = tcp_port
      self.tcp_port2 = 1235
      try:
         self.filep = open(filename)
      except IOError:
         return 

   def parsedump(self):
	pcap = dpkt.pcap.Reader(self.filep)
	self.logs = dict()
        self.tsamp = 1
        #print '#ts  buffer buff_target x1 fps x2 x3 bwe_h bwe_l level_n level_kbps x4 ts2'
        throttle = 0 
        datareceived = 0
        ts_old = 0
        tcp_datasum = 0
        ts_old_tcp = 0
        video_name = ''
        video_old = ''
 	self.datasum = dict()
	for ts, buf in pcap:
	    #l2 = dpkt.sll.SLL(buf)
	    try:
	        l2 = dpkt.ethernet.Ethernet(buf)
	    except:
		break;
	    try:
               ip = l2.data
	       tcp = ip.data
               dport = tcp.dport
               sport = tcp.sport
	       #print ts,'dport', dport,'sport', sport, len(tcp.data)
            except AttributeError:
               #print 'not tcp'
               #ip = eth.data
	       #print len(ip.data)
               continue
            
            if (sport == self.tcp_port or sport == self.tcp_port2 ) and len(video_name)>0:
                tcp_datasum += len(tcp.data)
                if ts-ts_old_tcp > self.tsamp:
                   if ts_old_tcp == 0:
                      ts_old_tcp = ts
                   else:
                      r_tcp = float(tcp_datasum)/float(ts-ts_old_tcp)/1000.0*8.0
                      self.logs[g]['tcp'].append([str(ts), str(r_tcp)]);
                      tcp_datasum = 0
                      ts_old_tcp = ts                   
                      #print ts, r_tcp 

            if sport == 80 and len(video_name)>0:
                #r = float(datasum)/float(ts-ts_old)/1000.0*8.0
	        if(not self.logs.has_key(g)):
	           self.logs[g] = dict()
		   self.logs[g]['video_name'] = video_name
		   self.logs[g]['vals'] = []
		   self.logs[g]['cmds'] = []
		   self.logs[g]['data'] = []
		   self.datasum[g] = 0
                   print 'New video', video_name, ts, g, self.datasum[g]
                      
                self.datasum[g] += len(tcp.data)
		self.logs[g]['data'].append([str(ts),str(self.datasum[g])])
                     
	    if dport == 80 and len(tcp.data) > 0:
	        try:
		    spl = tcp.data.splitlines()
		    m = re.search(r'POST (.*)',spl[0])
		    uri = m.group(1)
		except:
		    continue

		#print 'Uri: ', uri
	        if 1:
		 try:
		    m = re.search(r'\/control\/(\w+)_(\w+)_(\w+)\@(\d+)\?cmd=&?([-\w\s=]+)[,&]',uri)
		    video_name = m.group(1)
		    codec = m.group(2)
		    encrate = m.group(3)
		    cmd = m.group(5)
		 except AttributeError:
		    continue

		 if(cmd == 'throttle'):
		     m = re.search('\/control\/\w+_\w+_\w+\@\d+\?cmd=throttle,(\w+)&.*&g=(.*)&lvl1=(.*) HTTP',uri)
 		     g = m.group(2) + '_' + video_name
		     arr = m.group(3).split(',')
		     throttle = m.group(1)
		     #print 'THROTTLE', g
		     cmd_num = 1
		 elif(cmd == 'rtt-test'):
		     m = re.search('\/control\/\w+_\w+_\w+\@\d+\?cmd=rtt-test&.*&g=(.*)&lvl1=(.*) HTTP',uri)
 		     g = m.group(1) + '_' + video_name
		     arr = m.group(2).split(',')
		     cmd_num = 2
		     #print 'RTT-TEST', g
		 elif(cmd == 'log'):
		     m = re.search('\/control\/\w+_\w+_\w+\@\d+\?cmd=log.*&g=(.*)&lvl1=(.*) HTTP',uri)
 		     g = m.group(1) + '_' + video_name
		     arr = m.group(2).split(',')
		     cmd_num = 3
		     #print 'LOG', g
		 elif(cmd == 'reason=SWITCH_UP'):
		     m = re.search('\/control\/\w+_\w+_\w+\@\d+\?cmd=&reason=SWITCH_UP.*&g=(.*)&lvl1=(.*) HTTP',uri)
 		     g = m.group(1) + '_' + video_name
		     arr = m.group(2).split(',')
                     #print 'SWITCH_UP', g
		     cmd_num = 4
		 elif(cmd == 'reason=BUFFER_FAILURE'):
		     m = re.search('\/control\/\w+_\w+_\w+\@\d+\?cmd=&reason=BUFFER_FAILURE.*&g=(.*)&lvl1=(.*) HTTP',uri)
 		     g = m.group(1) + '_' + video_name
		     arr = m.group(2).split(',')
		     arr = m.group(2).split(',')
		     cmd_num = 6
		     #print 'BUFFER_FAILURE', g
		 else:
		     print cmd, 'command not parsed'
		 #first sample for this video
		 newarr = []
		 newarr.append(str(ts))
		 for a in arr: 
		    if a == 'NaN' or float(a)<0:
		       a = '0'
		    newarr.append(str(a))
		 newarr.append(str(throttle))
		 if(not self.logs.has_key(g)):
                     print 'New video', video_name, ts, g
		     self.logs[g] = dict()
                     self.logs[g]['video_name'] = video_name
		     self.logs[g]['vals'] = []
		     self.logs[g]['cmds'] = []
		     self.logs[g]['data'] = []
                     self.logs[g]['tcp'] = []
		     self.datasum[g] = 0
		 self.logs[g]['vals'].append(newarr)
		 self.logs[g]['cmds'].append([str(ts),str(cmd_num)])
        print 'last ts', ts_old 
   def writetofile(self):
      for k in self.logs.keys():
         print 'Printing logs for', k
         fname_vals = self.logs[k]['video_name'] +'_' + k + '_' + self.suffix +  '.vals'
         fname_cmds = self.logs[k]['video_name'] +'_' + k + '_' + self.suffix +  '.cmds'
         fname_data = self.logs[k]['video_name'] +'_' + k + '_' + self.suffix +  '.data'
         fv = open(fname_vals,'w')
         fc = open(fname_cmds,'w')
         fr = open(fname_data,'w')
         fv.write(self.header+'\n')
         for row in self.logs[k]['vals']:
             fv.write(string.join(row,' ')+'\n')
         for row in self.logs[k]['cmds']:
             fc.write(string.join(row,' ')+'\n')
         for row in self.logs[k]['data']:
             fr.write(string.join(row,' ')+'\n')
         if self.logs[k].has_key('tcp'):
             fname_tcp = self.logs[k]['video_name'] +'_' + k + '_' + self.suffix +  '.tcp'
             ft = open(fname_tcp,'w')
             for row in self.logs[k]['tcp']:
                ft.write(string.join(row,' ')+'\n')
             
if __name__ == '__main__':

   if len(sys.argv) == 3:
      al = AkamaiLog(sys.argv[1],sys.argv[2],8025)
      al.parsedump()
      al.writetofile()


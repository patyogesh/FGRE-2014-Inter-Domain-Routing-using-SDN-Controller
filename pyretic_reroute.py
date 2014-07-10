#######################################################
#
# FGRE 2014, Interdomain reroute flow application
#
#######################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.modules.mac_learner import mac_learner

#########################
##
## IP Prefixes
##
#########################

ISP_prefix = IPPrefix('20.0.0.0/16')
CLIENT_prefix = IPPrefix('30.0.100.0/24')

#########################
##
## MAC addresses
##
#########################

MAC_ISP_left = MAC('66:66:66:66:66:aa')
MAC_ISP_right = MAC('66:66:66:66:66:ab')
MAC_CLIENT = MAC('66:66:66:66:66:ac')

MAC_left_edge = MAC('00:0a:aa:bb:cc:da')
MAC_right_edge = MAC('00:0a:aa:bb:cc:db')
MAC_netflix_gw = MAC('00:0a:aa:bb:cc:dc')

#########################
##
## Switch Port IDs
##
#########################

SWITCH1_PORT_SWITCH2 = 2
SWITCH1_EXTERNAL_PORT = 3

SWITCH2_PORT_CLIENT = 1
SWITCH2_PORT_SWITCH1 = 2
SWITCH2_PORT_SWITCH3 = 3
SWITCH2_PORT_SWITCH4 = 4

SWITCH3_PORT_SWITCH2 = 1
SWITCH3_PORT_SWITCH4 = 2
SWITCH3_PORT_SWITCH5 = 3

SWITCH4_PORT_SWITCH2 = 2
SWITCH4_PORT_SWITCH3 = 1

SWITCH5_PORT_SWITCH3 = 2
SWITCH5_EXTERNAL_PORT = 3

###############################
##
##  default pyretic policies
##
###############################

infrastructure_routing_policy = (
	(match(dstip=ISP_prefix, inport=SWITCH1_PORT_SWITCH2, switch=1) >> modify(srcmac=MAC_left_edge, dstmac=MAC_ISP_left) >> fwd(SWITCH1_EXTERNAL_PORT)) +
	(match(dstip=ISP_prefix, inport=SWITCH5_PORT_SWITCH3, switch=5) >> modify(srcmac=MAC_right_edge, dstmac=MAC_ISP_right) >> fwd(SWITCH5_EXTERNAL_PORT)) +

	(match(dstip=CLIENT_prefix, inport=SWITCH1_EXTERNAL_PORT, switch=1) >> modify(srcmac=MAC_netflix_gw, dstmac=MAC_CLIENT) >> fwd(SWITCH1_PORT_SWITCH2)) +
	(match(dstip=CLIENT_prefix, inport=SWITCH5_EXTERNAL_PORT, switch=5) >> modify(srcmac=MAC_netflix_gw, dstmac=MAC_CLIENT) >> fwd(SWITCH5_PORT_SWITCH3)) +
	
	(match(dstip=CLIENT_prefix, switch=2) >> fwd(SWITCH2_PORT_CLIENT)) +
	(match(dstip=CLIENT_prefix, switch=3) >> fwd(SWITCH3_PORT_SWITCH2)) +
	(match(dstip=CLIENT_prefix, switch=4) >> fwd(SWITCH4_PORT_SWITCH2))
)

to_ISP_left = (
	(match(dstip=ISP_prefix, switch=2) >> fwd(SWITCH2_PORT_SWITCH1))
)

to_ISP_right = (
	(match(dstip=ISP_prefix, switch=2) >> fwd(SWITCH2_PORT_SWITCH3)) +
	(match(dstip=ISP_prefix, switch=3) >> fwd(SWITCH3_PORT_SWITCH5))
)

class reroute_interdomain(DynamicPolicy):
	
	def __init__(self):
		print "Initializing reroute policy"
		super(reroute_interdomain,self).__init__(identity)
		import threading
		self.direction = "left"
		self.policy = infrastructure_routing_policy + to_ISP_left
		self.ui = threading.Thread(target=self.ui_loop)
		self.ui.daemon = True
		self.ui.start()
		
	def update_policy (self, direction="left"):
		if direction == "left":
			self.direction = "left"
			self.policy = infrastructure_routing_policy + to_ISP_left
		else:
			self.direction = "right"
			self.policy = infrastructure_routing_policy + to_ISP_right
		print "Current policy: ", self.policy
	
	def ui_loop(self):
		while(True):
			nb = raw_input('(r)eroute, (s)ee, or (q)uit? ')
			if nb == 'r':
				nb = raw_input('enter "left" or "right" ')
				if nb == "left":
					self.update_policy("left")
				elif nb == "right":
					self.update_policy("right")
				else:
					print 'Incorrect direction. Correct directions are "left" or "right" '
			elif nb == 's':
				print "Current policy being implemented is going to %s: %s" % (self.direction, self.policy)
			elif nb == 'q':
				print "Quitting"
				import os, signal
				os.kill(os.getpid(), signal.SIGINT)
				return
			else:
				print "Invalid option"

def main ():
	return if_(
			(match(dstip=ISP_prefix) | match(dstip=CLIENT_prefix)),
			reroute_interdomain(),
			mac_learner()
		)
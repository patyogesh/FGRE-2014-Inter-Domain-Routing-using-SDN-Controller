"""
Custom Topology

5 Hosts (1 controller; 2 edge hosts; 1 ISP; 1 client) and 6 switches

"""


from mininet.topo import Topo


class MyTopo (Topo):

	def __init__( self ):

		# Initialize topology
		Topo.__init__( self )
				
		# Add hosts 
		mhost1 = self.addHost('mh1')
		mhost2 = self.addHost('mh2')
		isp = self.addHost('isp1')
		client = self.addHost('cli1')
		controller = self.addHost('c1')

		# Add switches
		switch1 = self.addSwitch('s1')
		switch2 = self.addSwitch('s2')
		switch3 = self.addSwitch('s3')
		switch4 = self.addSwitch('s4')
		switch5 = self.addSwitch('s5')
		switch6 = self.addSwitch('s6')

		# Add links
		self.addLink(mhost1, switch1)
		self.addLink(client, switch2)
		self.addLink(mhost2, switch5)
		self.addLink(controller, switch4)
		self.addLink(isp, switch6)
		self.addLink(switch1, switch2)
		self.addLink(switch2, switch3)
		self.addLink(switch2, switch4)
		self.addLink(switch3, switch4)
		self.addLink(switch3, switch5)
		self.addLink(switch1, switch6)	
		self.addLink(switch5, switch6)

topos = { 'mytopo': ( lambda: MyTopo() ) }

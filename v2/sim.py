from SimPkg import Road, EnvironmentVars, Simulator

# Init model variables with default Params
env_vars = EnvironmentVars()
print(env_vars.state())

# Define road network
roads = [Road('1', '2', 720, 20), Road('2', '3', 720, 12), Road('1', '4', 480, 15), Road('2', '5', 360, 12),
	        Road('3', '6', 720, 12), Road('4', '5', 300, 10), Road('5', '6', 360, 12), Road('4', '7', 480, 15),
	        Road('5', '8', 300, 10), Road('6', '9', 720, 30), Road('7', '8', 480, 15) ,Road('8', '9', 480, 15)]

# Build and run model with vars, network, logger
sim = Simulator(env_vars, roads, log = False)
sim.run()
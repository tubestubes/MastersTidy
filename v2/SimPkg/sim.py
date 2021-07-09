# Class based simulator
from .environment import Network, Road
from .agents import HV, AV


class EnvironmentVars:
    """ Struct to store all environment variables for a simulation, with default values for quick init """

    def __init__(
        self,
        hv: int = 500,
        av: int = 500,
        N: int = 500,
        orig: str = "1",
        dest: str = "9",
        hv_err: float = 5,
        hv_theta: float = 0.5,
        hv_beta: float = 0.5,
        hv_len: int = 3,
        hv_atis_bias: float = 0,
        av_err: float = 0,
        av_theta: float = 1,
        av_len: int = 1000,
        av_atis_bias: float = 0,
    ):

        self.hv = hv
        self.av = av
        self.N = N
        self.orig = orig
        self.dest = dest
        self.hv_err = hv_err
        self.hv_theta = hv_theta
        self.hv_beta = hv_beta
        self.hv_len = hv_len
        self.hv_atis_bias = hv_atis_bias
        self.av_err = av_err
        self.av_theta = av_theta
        self.av_len = av_len
        self.av_atis_bias = av_atis_bias

    def state(self):
        return f"{self.av =}; {self.av = }; {self.N = }; {self.orig = }; {self.dest = }; {self.hv_err = }; {self.hv_theta = }; {self.hv_beta = }; {self.hv_len = }; {self.hv_atis_bias = }; {self.av_err = }; {self.av_theta = }; {self.av_len = }; {self.av_atis_bias = }"


class Logger:
    """ Records data to pd.DataFrames
        one DataFrame -> traffic per road, rows = days
        one DataFrame -> traffic per route, rows = days
    """

    def __init__(self, n_roads: int, n_routes:int ) -> None:
        """ n_roads = len(network.roadlist)
            n_routes = len(drivers[0].routes)
        """

        import pandas as pd
        self.road_log = pd.DataFrame( columns=[f"Road{i}" for i in range(n_roads) ] )
        self.route_log = pd.DataFrame( columns=[f"Route{i}" for i in range(n_routes) ] )

    def log(self, day: int, network: Network, drivers: list):

        # Add Road counts to db row
        self.road_log.loc[day] = [road.count for road in network.roadlist]

        # Add route counts to db row by:
        # inits row as zeros,
        # Add one to route i, if driver took root i
        route_count = [0 for _ in range(len(drivers[0].routes))]
        for driver in drivers:
            route_count[driver.i] = route_count[driver.i] + 1
        self.route_log.loc[day] = route_count

    def save(self, env: EnvironmentVars ):
        """ Save data as pickle file, """
        route_dir = f"data/sim-ROUTES-N{env.N}-hv{env.hv}at{env.hv_err}_{env.hv_theta}_{env.hv_beta}_{env.hv_len}_{env.hv_atis_bias}-av{env.av}at{env.av_err}_{env.av_theta}_{env.av_len}_{env.av_atis_bias}.pickle"
        roads_dir = f"data/sim-ROADS-N{env.N}-hv{env.hv}at{env.hv_err}_{env.hv_theta}_{env.hv_beta}_{env.hv_len}_{env.hv_atis_bias}-av{env.av}at{env.av_err}_{env.av_theta}_{env.av_len}_{env.av_atis_bias}.pickle"

        import pickle
        pickle.dump(self.route_log, open(route_dir, "wb" ))
        pickle.dump(self.road_log, open(roads_dir, "wb" ))


class Simulator:

    def __init__(self, env: EnvironmentVars, roads: list, log = True) -> None:

        self.env = env
        self.log = log
        self.network = Network(roads)

        drivers = [HV(env.orig, env.dest, err = env.hv_err, theta = env.hv_theta, beta = env.hv_beta, L = env.hv_len) for i in range(0, env.hv)]
        if env.av > 0:
            drivers = drivers + [AV(env.orig, env.dest, theta = env.av_theta, err = env.av_err, L = env.av_len, atis_bias = env.av_atis_bias) for i in range(0, env.av)]
        self.drivers = drivers


    def run(self, logger: Logger = None ):
    
        # tqdm adds a progress bar to a for loop
        from tqdm import tqdm

        # Drivers must learn network on day 0. learn method also completes day 0 drive
        for driver in self.drivers:
            driver.learn(self.network)
        self.network.update(self.drivers) # Network records state, logger stores states
        if self.log:
            logger.log(day = 0 , network = self.network, drivers = self.drivers)

        # Day > 0
        for i in tqdm(range(1, self.env.N)):
            for driver in self.drivers:
                driver.drive(self.network)
            self.network.update(self.drivers)
            if self.log:
                logger.log(day = i , network = self.network, drivers = self.drivers)


if __name__ == "__main__":

    env_vars = EnvironmentVars()
    roads = [Road('1', '2', 720, 20), Road('2', '3', 720, 12), Road('1', '4', 480, 15), Road('2', '5', 360, 12),
	        Road('3', '6', 720, 12), Road('4', '5', 300, 10), Road('5', '6', 360, 12), Road('4', '7', 480, 15),
	        Road('5', '8', 300, 10), Road('6', '9', 720, 30), Road('7', '8', 480, 15) ,Road('8', '9', 480, 15)]
    sim = Simulator(env_vars, roads, log = False)
    sim.run()
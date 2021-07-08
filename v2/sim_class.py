# Class based simulator
from environment import Network


class EnvironmentVars:
    """ Struct to store all environment variables for a simulation """

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


class Logger:
    """ Stores and controls data store """

    def __init__(self, n_roads: int, n_routes:int ) -> None:
        """ Create data store:
        pd data frame for road counts and rout counts
        n_roads = len(network.roadlist)
        n+routes = len(drivers[0].routes)
        """

        import pandas as pd
        self.road_log = pd.DataFrame( columns=[f"Road{i}" for i in range(n_roads) ] )
        self.route_log = pd.DataFrame( columns=[f"Route{i}" for i in range(n_routes)])

    def log(self, day: int, network: Network, drivers: list):

        # Add Road counts to db row
        self.road_log.loc[day] = [road.count for road in network.roadlist]

        # Add route counts to db row
        # inits row as zeros,
        # Add one to route i, if driver took root i
        route_count = [0 for _ in range(len(drivers[0].routes))]
        for driver in drivers:
            route_count[driver.i] = route_count[driver.i] + 1
        self.route_log.loc[day] = route_count

    def save(self, env: EnvironmentVars ):
        route_dir = f"data/sim-ROUTES-N{env.N}-hv{env.hv}at{env.hv_err}_{env.hv_theta}_{env.hv_beta}_{env.hv_len}_{env.hv_atis_bais}-av{env.av}at{env.av_err}_{env.av_theta}_{env.av_len}_{env.av_atis_bias}.pickle"
        roads_dir = f"data/sim-ROADS-N{env.N}-hv{env.hv}at{env.hv_err}_{env.hv_theta}_{env.hv_beta}_{env.hv_len}_{env.hv_atis_bais}-av{env.av}at{env.av_err}_{env.av_theta}_{env.av_len}_{env.av_atis_bias}.pickle"

        import pickle
        pickle.dump(self.route_log, open(route_dir, "wb" ))
        pickle.dump(self.road_log, open(roads_dir, "wb" ))


class Simulator:

    def __init__(self, env: EnvironmentVars, roads: list, log = True) -> None:

        self.env = env
        self.logger = logger

        import environment as e
        self.network = e.Network(roads)

        drivers = [HV(env.orig, env.dest, err = env.hv_err, theta = env.hv_theta, beta = env.hv_beta, L = env.hv_len) for i in range(0, env.hv)]
        if env.av > 0:
            drivers = drivers + [AV(env.orig, env.dest, theta = env.av_theta, err = env.av_err, L = env.av_len, atis_bias = env.av_atis_bias) for i in range(0, env.av)]
        self.drivers = drivers


    def run(self, logger: Logger):

        for i in range(0, self.env.N):
            for driver in self.drivers:
                driver.drive(self.network)
            self.network.update(self.drivers)
            logger.log(day = i , network = self.network, drivers = self.drivers)

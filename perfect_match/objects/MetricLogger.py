import logging
import math
import time
import matplotlib.pyplot as plt

BRUTO_MOV = "algorithm bruto move"


class MetricLogger(object):
    def __init__(self, level=logging.INFO):
        super().__init__()
        self.level = level
        self.__set_logger(__name__)
        self._experiment = None
        self._experiments = {}
        self.timings = None
        self.metrics = None
        self._experiment = "default"
        self.__init_experiment(self._experiment)
        self.logger.info('MetricLogger has started')

    @property
    def experiment(self):
        return self._experiment

    @experiment.setter
    def experiment(self, value):
        self.__set_logger(value)
        self._experiment = value
        self.__init_experiment(self._experiment)

    def __set_logger(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        c_handler = logging.StreamHandler()
        c_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(c_handler)

    def __init_experiment(self, value):
        self._experiments[value] = {}
        self._experiments[value]["metrics"] = {}
        self._experiments[value]["timings"] = {}
        self.timings = self._experiments[value]["timings"]
        self.metrics = self._experiments[value]["metrics"]

    def log_max_time(self, key, start_time):
        elapsed = time.time() - start_time
        self.log_max(key, elapsed)

    def log_max(self, key, value):
        if key in self.timings:
            self.timings[key] = value if value > self.timings[key] else self.timings[key]
        else:
            self.timings[key] = value

    def create_full_move_plot(self):
        xs = [int(x) for x in self._experiments.keys() if x != 'default']
        experiments = [expname for expname in self._experiments if expname != 'default']
        ys = [self._experiments[y]["metrics"][BRUTO_MOV] for y in experiments if y != 'default']
        ys.sort()
        xs.sort()
        plt.plot(xs, ys, '-b', label='number of moves in total')
        logxs = [math.log2(x) * x*2 for x in xs]
        logxs.sort()
        plt.plot(xs, logxs, '-r', label='log(n)*n*2')
        plt.legend()
        plt.show()

    def trunc_walk_per_match(self):
        experiments = [expname for expname in self._experiments if expname != 'default']
        for expname in experiments:
            ys = self._experiments[expname]["metrics"]["truncated_walk_moves"]
            xs = [x for x in range(1, len(ys) + 1)]
            n = self._experiments[expname]["metrics"]["n"]
            d = self._experiments[expname]["metrics"]["d"]
            ys.sort()
            xs.sort()
            plt.plot(xs, ys, '--b',
                     label='number of moves in truncated walk n:{0}, d:{1}'.format(n, d))
            plt.legend()
            plt.show()

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def inc_metric(self, key):
        if key in self.metrics:
            self.metrics[key] += 1
        else:
            self.metrics[key] = 1

    def append_metric(self, key, val):
        if key in self.metrics:
            if type(self.metrics[key]) == list:
                self.metrics[key].append(val)
            else:
                raise Exception("this is not a list")
        else:
            self.metrics[key] = [val]

    def set_metric(self, key, val):
        self.metrics[key] = val

    def dec_metric(self, key):
        if key in self.metrics:
            self.metrics[key] += 1
        else:
            self.metrics[key] = 1

    def zero_metric(self, key):
        self.metrics[key] = 0

    def flush_metric(self, key):
        self.logger.info("metric {0} : {1}".format(key, self.metrics[key]))

    def flush_all(self):
        for k in self.metrics.keys():
            self.logger.info("metric {0} : {1}".format(k, self.metrics[k]))
        self.flush_timings()

    def flush_timings(self):
        for k in self.timings.keys():
            self.logger.info("timing for {0} : {1}".format(k, self.timings[k]))

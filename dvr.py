import sys
import math
from threading import Thread, Lock
import time

LOCK = Lock()


class Buffer():

    def __init__(self, router_names):
        self.queue = []

        for router in router_names:
            self.queue.append((router, []))

    def all_tables_received(self, router):

        for x in self.queue:
            if x[0] == router.name:
                if len(x[1]) == len(router.neighbours):
                    return True

        return False

    def insert_buffer(self, router, r):
        for x in self.queue:
            if x[0] == router.name:
                x[1].append((r.name, r.dv))

    def all_neighbours_received(self, router):
        for x in self.queue:
            if x[0] == router.name:
                if len(x[1]) == len(router.neighbours):
                    return True

        return False

    def show_B(self):

        print(" BUFFER :")

        for x in self.queue:
            print(f"Queue for {x[0]}")
            print(x[1])


class Network():

    def __init__(self, routers):
        self.routers = routers

    def initialize_modified(self):
        for router in self.routers:
            len_dv = len(router.dv)
            router.modified = [0] * len_dv

    def get_router_by_name(self, name):
        for r in self.routers:
            if r.name == name:
                return r

    def Show(self):

        for r in self.routers:
            r.Show()

    def check_if_coverged(self):

        for r in self.routers:

            if r.has_changed():
                return False
        return True


class Router():

    def __init__(self, name, dv, neighbours):
        self.name = name
        self.dv = dv
        self.neighbours = neighbours
        self.modified = []

    def update_dv_value(self, dest, val):

        for x in self.dv:

            if x[0] == dest:
                x[1] = val

    def initialize_mod(self):

        len_mod = len(self.modified)

        for i in range(len_mod):
            self.modified[i] = 0

    def has_changed(self):

        for mod in self.modified:

            if mod == 1:
                return True

        return False

    def Show(self):

        print(f"\nRouter Name - {self.name}")
        print(f"Distance Vector - \n")

        len_dv = len(self.dv)

        print(f"Dest \t Cost ")
        for i in range(len_dv):

            if self.modified[i] == 0:

                print(f"{self.dv[i][0]} \t {self.dv[i][1]} ")
            else:

                print(f"{self.dv[i][0]} \t {self.dv[i][1]} \t modified*")



def thread_target(network, buffer, r):
    for i in range(4):

        with LOCK:
            print(f"Itreation : {i + 1}")
            r.Show()
            r.initialize_mod()

        DV_2_Neighbour(network, buffer, r)

        # sleep thread for 2 sec
        time.sleep(2)

        # proceed only when all neighbours received
        while buffer.all_neighbours_received(r) == False:
            pass

        get_tables_from_buffer(buffer, r)


def BellmanFord(router, dv_list):
    num_routers = len(router.dv)

    for i in range(num_routers):

        for x in dv_list:

            for r_dv in router.dv:

                if r_dv[0] == x[0]:
                    val = r_dv[1]

            val = val + x[1][i][1]

            if val < (router.dv[i][1]):
                router.dv[i][1] = val
                router.modified[i] = 1


def get_tables_from_buffer(buffer, router):
    with LOCK:
        for x in buffer.queue:
            if x[0] == router.name:

                dv_list = []
                values = len(x[1])
                for i in range(values):
                    dv_list.append(x[1].pop(0))

    BellmanFord(router, dv_list)

# forward DV to neighbour
def DV_2_Neighbour(network, buffer, router):
    for n in router.neighbours:
        r = network.get_router_by_name(n)
        with LOCK:
            buffer.insert_buffer(router, r)


# Initialize Distance vector
def initialize_dv(network, router_names, edge_list, router_list):
    for router in router_list:

        dv = []

        for r in router_names:

            if r == router.name:
                dv.append([r, 0])
            else:
                dv.append([r, math.inf])

        router.dv = dv

    for edge in edge_list:
        u = network.get_router_by_name(edge[0])
        v = network.get_router_by_name(edge[1])

        u.update_dv_value(edge[1], int(edge[2]))
        v.update_dv_value(edge[0], int(edge[2]))


# Initialize Neighbour
def init_N(router_names, edge_list):
    router_list = []
    for router in router_names:

        rt = Router(router, [], [])

        for edge in edge_list:

            if edge[0] == router:
                rt.neighbours.append(edge[1])

        for edge in edge_list:

            if edge[1] == router:
                rt.neighbours.append(edge[0])

        router_list.append(rt)

    return router_list


def scan_input(filename):
    # open the file
    f = open(filename, "r")
    # first line has number of routers
    num_routers = f.readline()
    router_names = f.readline()
    router_names = router_names.split()

    edge_list = []

    # read the  next lines till EOF
    for x in f:

        if x == 'EOF':
            break

        x = x.split()

        edge_list.append(x)

    # close file
    f.close()

    return router_names, edge_list


if __name__ == "__main__":

    # file name passed in cmd args
    filename = sys.argv[1]
    router_names, edge_list = scan_input(filename)
    router_list = init_N(router_names, edge_list)
    network = Network(router_list)
    initialize_dv(network, router_names, edge_list, router_list)
    print("-------------------INITIAL NETWORK -----------------------")
    network.initialize_modified()
    network.Show()
    buffer = Buffer(router_names)

    start = time.time()

    flag = 0
    it = 1

    threads = []

    for router in router_names:
        r = network.get_router_by_name(router)
        th = Thread(target=thread_target, args=(network, buffer, r))
        threads.append(th)

    for th in threads:
        th.start()

    for th in threads:
        th.join()

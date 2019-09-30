import getopt
import sys


class ArgParse(object):
    def __init__(self):
        print("Arg Parse has started...")

    @staticmethod
    def parse(argv):
        try:
            opts, args = getopt.getopt(argv, "Hc:h:n:p:s:")
        except getopt.GetoptError:
            raise ArgumentError

        network = ""
        ports = ""
        config = ""
        subnet = ""
        hosts = ""

        for opt, arg in opts:
            if opt in ("-H", "--help"):
                print("main.py -n <network> -p <ports> -c <config> -s <subnet count> -h <hosts for subnets>")
                sys.exit(1)
            if opt in ("-n", "--network"):
                network = arg
            if opt in ("-p", "--ports"):
                ports = arg
            if opt in ("-c", "--config"):
                config = arg
            if opt in ("-s", "--subnets"):
                subnet = arg
            if opt in ("-h", "--hosts"):
                hosts = arg
        return network, ports, config, subnet, hosts


class ArgumentError(getopt.GetoptError):
    @staticmethod
    def what():
        return "Invalid argument passed!"

# main.py 
# -n --network /network
# -p --ports /port mapping
# -c --config /external config linking
# -s --subnets /number of subnets
# -h --hosts /number of hosts in each subnet
# -H --help /print help 
#
# main.py -n 192.168.10.0/24 -p 80,443 11180,11443 -s 1 -h 1

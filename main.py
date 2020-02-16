import getopt
import sys

from argparser import ArgParser, ArgumentError


def main(argv):
    print('YML Config Generator')
    params: dict = {}
    try:
        params = ArgParser.parse(argv)
    except ArgumentError:
        print("Invalid arguments!")
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])

# main.py 
# -n --network /network ip
# -p --port /port mapping
# -c --config /external config linking
# -s --subnets /number of subnets
# -h --hosts /number of hosts in each subnet
#
# main.py -a 192.168.10.0/24 -p 80,443 11180,11443 -s 1 -h 1

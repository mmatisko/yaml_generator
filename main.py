import sys

from argparser import ArgParser, ArgumentError, ArgumentModeError
from data_processing import DataProcessing


def main(argv):
    print('YML Config Generator')
    params: dict = {}
    try:
        params = ArgParser.parse(argv=argv)
    except (ArgumentError, ArgumentModeError) as err:
        print(err.what())
        sys.exit(2)

    dp = DataProcessing(params=params)
    dp.process()


if __name__ == "__main__":
    main(sys.argv[1:])

# main.py 
# -n --network /network ip
# -p --port /port mapping
# -c --config /external config linking
# -s --subnets /number of subnets
# -f --file /list of variables to random pick from
#
# main.py -a 192.168.10.0/24 -p 80,443 11180,11443 -s 1

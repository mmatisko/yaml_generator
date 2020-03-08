from argparser import ArgParser, ArgumentError, ArgumentModeError
from data_processing import DataProcessing
from logger import Logger

import sys


def main(argv):
    print('YML Config Generator')
    params: dict = {}
    try:
        params = ArgParser.parse(argv=argv)
    except (ArgumentError, ArgumentModeError) as err:
        print(err.what())
        sys.exit(2)

    if ArgParser.params_are_valid(params=params):
        dp = DataProcessing(params=params)
        dp.process()
    else:
        print(Logger.get_error_log(argv))
        raise ValueError("Invalid arguments provided! See help for valid inputs")


if __name__ == "__main__":
    main(sys.argv[1:])

# main.py
# -d --dir / input config directory
# -c --config / generating mode configuration file
# -n --network /network ip
# -p --port / port mapping
# -f --file / list of variables to random pick from
# -k --key / key of edited item
# -v --value / value of edited item
#
# edit mode with static value:
    # main.py -k key -v static_value
# edit mode with value generation (ip/port/value from list)
    # main.py -k network|port|password -n 192.168.10.0/24 -p 11180-11443 -f passwords.txt
# generating mode
    # main.py -c config.yml -d input_directory/ -o output_directory/

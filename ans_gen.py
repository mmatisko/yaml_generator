"""
 Main source file, runs generator

 Usage help:
 ans_gen.py <mode -e/g> [options] -d <input_directory>
  -d --dir / input config directory
  -c --config / generating mode configuration file
  -n --network /network ip
  -p --port / port mapping
  -f --file / list of variables to random pick from
  -k --key / key of edited item
  -v --value / value of edited item

 edit mode with static value:
    ans_gen.py -k key -v static_value
 edit mode with value generation (ip/port/value from list)
    ans_gen.py -k network -n 192.168.10.0/24
    ans_gen.py -k port -p 11180-11443
    ans_gen.py -k password -f passwords.txt
 supported generating mode
    ans_gen.py -c config.yml
    ans_gen.py -c config.yml -d input_dir/
    ans_gen.py -c config.yml -o output_dir/
    ans_gen.py -c config.yml -o output_dir/ -d input_dir/
"""

from processing import ArgParser, ArgumentError, ArgumentModeError, DataProcessing
from file_io import Logger

import sys


def main(argv):
    Logger.write_log('YAML Config Generator has started!')

    try:
        params: dict = ArgParser.parse(argv=argv)
    except (ArgumentError, ArgumentModeError) as err:
        print(err.what())
        sys.exit(2)

    if ArgParser.params_are_valid(params=params):
        Logger.write_debug_log('Params validated, processing...')
        dp = DataProcessing(params=params)
        dp.process()
    else:
        Logger.write_error_log(''.join(argv))
        raise ValueError("Invalid arguments provided! See help for valid inputs")

    Logger.write_log('Generator is done :)')


if __name__ == "__main__":
    main(sys.argv[1:])

REM TODO:
REM
REM 1. Get arguments from the terminal (input, output).
REM 2. Create a temporal JSON file config file, so MATLAB
REM    can grab the input file, this is because it is not
REM    possible for MATLAB to receive get the arguments
REM    from the terminal.

REM Finally execute the MATLAB command.
matlab -batch "erebus; exit"
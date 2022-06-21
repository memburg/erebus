:: STEPS:
::
:: 1. Get arguments from the terminal (input, output).
:: 2. Create a temporal JSON file config file, so MATLAB
::    can grab the input file, this is because it is not
::    possible for MATLAB to receive get the arguments
::    from the terminal.
:: 3. Finally execute the MATLAB command.
@echo off
echo { ^"input^": ^"%1^", ^"output^": ^"%2^" } > ./config.json
matlab -batch "erebus; exit"
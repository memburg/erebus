:: STEPS:
::
:: 1. Get arguments from the terminal (input, output).
:: 2. Create a temporal JSON file config file, so MATLAB
::    can grab the input file, this is because it is not
::    possible for MATLAB to receive get the arguments
::    from the terminal.
:: 3. Execute the MATLAB command.
:: 4. Delete 'config.json' file.
@echo off
echo { ^"input^": ^"%1^", ^"output^": ^"%2^", ^"iterations^": %3 } > ./config.json
mkdir outputs
matlab -batch "index; exit"
del config.json
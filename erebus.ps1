param(
    [Parameter()]
    [String]$i,
    [String]$its
)

# STEPS:
#
# 1. Get arguments from the terminal (input, output).
# 2. Create a temporal JSON file config file, so MATLAB
#    can grab the input file, this is because it is not
#    possible for MATLAB to receive get the arguments
#    from the terminal.
# 3. Execute the MATLAB command.
# 4. Delete 'config.json' file.
New-Item ./config.json | Out-Null
Set-Content ./config.json "{ `"inputFile`": `"$i`", `"iterations`": $its }"
matlab -batch "index; exit"
Remove-Item ./config.json
New-Item -ItemType Directory -Force -Path ./outputs | Out-Null
param(
    [Parameter()]
    [String]$action,
    [String]$inputFile,
    [String]$iterations,
    [String]$keyPath
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

if ($action -eq "protect")
{
    New-Item ./config.json | Out-Null
    Set-Content ./config.json "{ `"action`": `"$action`", `"inputFile`": `"$inputFile`", `"iterations`": $iterations }"
    New-Item -ItemType Directory -Force -Path ./outputs | Out-Null
    matlab -batch "index; exit"
    Remove-Item ./config.json
}
elseif ($action -eq "unprotect")
{
    New-Item ./config.json | Out-Null
    Set-Content ./config.json "{ `"action`": `"$action`", `"inputFile`": `"$inputFile`", `"keyPath`": `"$keyPath`" }"
    New-Item -ItemType Directory -Force -Path ./outputs | Out-Null
    matlab -batch "index; exit"
    Remove-Item ./config.json
}
else
{
    Write-Output "Unknown action: $action"
}
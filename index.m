clc;
clear;
close all;

% Import 'src' folder into the main script.
addpath(pwd + "/src");

% Read command line arguments from
% config.json file.
jsonConfig = jsondecode(fileread("./config.json"));
args.action = jsonConfig.("action");
args.inputFile = jsonConfig.("inputFile");

if strcmp(args.action, "protect")
    % Get required attributes to perform
    % the protection process.
    args.iterations = jsonConfig.("iterations");

    % Create an image in the traditional way.
    imageCPU = imread(args.inputFile);
    Erebus.protect(imageCPU, args.iterations);
elseif strcmp(args.action, "unprotect")
    % Get required attributes to perform
    % the unprotection process.
    args.keyPath = jsonConfig.("keyPath");

    % TODO
end

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
imageCPU = imread(args.inputFile);

if strcmp(args.action, "protect")
    % Get required attributes to perform
    % the protection process.
    args.iterations = jsonConfig.("iterations");

    % Proceed and encrypt the image
    Erebus.protect(imageCPU, args.iterations);
elseif strcmp(args.action, "unprotect")
    % Get required attributes to perform
    % the unprotection process.
    args.keyPath = jsonConfig.("keyPath");
    encryptionKey = readmatrix(args.keyPath);

    % Proceed and decrypt the image
    Erebus.unprotect(imageCPU, encryptionKey);
end

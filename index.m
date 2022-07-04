clc;
clear;
close all;

% Import 'src' folder into the main script.
addpath(pwd + "/src");

% Read command line arguments from
% config.json file.
jsonConfig = jsondecode(fileread("./config.json"));
args.inputFile = jsonConfig.("inputFile");
args.iterations = jsonConfig.("iterations");

% Create an image in the traditional way.
imageCPU = imread(args.inputFile);
Erebus.protect(imageCPU, args.iterations);
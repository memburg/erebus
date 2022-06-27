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

% Set GPU configuration
GPU.configureGPU();

% Create an image in the traditional way.
imageCPU = imread(args.inputFile);
Erebus.protect(args.iterations);

%{
    TODO: Image processing (cypher)
    gpuImage = gpuArray(original);
    Igray_gpu = arrayfun(@rgb2gray_custom, Igpu(:,:,1), Igpu(:,:,2), Igpu(:,:,3));
    protectedCPU = gather(gpuImage);
%}

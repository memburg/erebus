clc;
clear;
close all;

% Import 'src' folder into the main script.
addpath(pwd + "/src");

% Default is zero since it cannot be chosen.
DEFAULT_GPU_DEVICE = 0;

% This will select the last GPU device
% available from the list of available
% devices.
if gpuDeviceCount("available") > 0
    % By getting the amount of available device
    % we can set
    DEFAULT_GPU_DEVICE = gpuDeviceCount("available");
    gpuDevice(DEFAULT_GPU_DEVICE);

    % Get GPU properties
    GPU_PROPS = gpuDeviceTable;
    GPU_NAME = GPU_PROPS(DEFAULT_GPU_DEVICE, 2).Name;

    % Display GPU name
    disp("Selected device: " + GPU_NAME);
else
    % This will cause the program to fail in
    % case there"s no GPU device available.
    gpuDevice(DEFAULT_GPU_DEVICE);
end

% Read JSON properties (input and output files)
jsonConfig = jsondecode(fileread("./config.json"));
inputPath = jsonConfig.("input");
iterations = jsonConfig.("iterations");

% Create an image in the traditional way.
imageCPU = imread(inputPath);
Erebus.protect(imageCPU, iterations);

%{
    TODO: Image processing (cypher)
    gpuImage = gpuArray(original);
    Igray_gpu = arrayfun(@rgb2gray_custom, Igpu(:,:,1), Igpu(:,:,2), Igpu(:,:,3));
    protectedCPU = gather(gpuImage);
%}
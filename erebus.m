clc;
clear;
close all;

% Default is zero since it cannot be chosen.
DEFAULT_GPU_DEVICE = 0;

if gpuDeviceCount("available") > 0
    % This will select the last GPU device
    % available from the list of available
    % devices.
    DEFAULT_GPU_DEVICE = gpuDeviceCount("available");
    gpuDevice(DEFAULT_GPU_DEVICE);

    % Get GPU properties
    GPU_PROPS = gpuDeviceTable;
    GPU_NAME = GPU_PROPS(DEFAULT_GPU_DEVICE, 2).Name;

    % Display GPU name
    disp('Selected device: ' + GPU_NAME);
else
    % This will cause the program to fail in
    % case there's no GPU device available.
    gpuDevice(DEFAULT_GPU_DEVICE);
end
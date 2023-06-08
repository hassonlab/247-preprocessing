clc;clear all;close all;

% input parameters:
sid = '798';
fs_new = 512;

main_dir = ['/Volumes/Research/Epilepsy_ECOG/ecog/data/NY' sid];
audio_dir = [main_dir '/ZoomAudioFiles/'];
down_dir = [main_dir 'DownsampledAudioFiles/'];
if ~ isfolder(down_dir); mkdir(down_dir); end

% find audio files to downsample
list_files = dir([audio_dir '*/*.WAV']);

for f = 1:length(list_files)
    current_file = list_files(f).name;
    basic_name = strrep(current_file, '.WAV', '');
    
    % read signal
    [signal,fs] = audioread(fullfile(list_files(f).folder, current_file));
    x = size(signal);
    signal = signal(:,x(2));
  
    % resample
    [P,Q] = rat(fs_new/fs); 
    signal_new = resample(signal,P,Q);

    % write
    audiowrite([down_dir, basic_name '_downsampled.wav'], signal_new, fs_new);
end 

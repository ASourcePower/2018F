tic;clc;clear;
load('data.mat');
figure(1)
% T10
[nrow, ~] = size(T1);
for idx=1:nrow
    x = T1(idx, 2:5);
    y = T1(idx, 6:9);
    fill(x, y, 'b');
    hold on;
    ylim([0, 30]);
end

% T21
[nrow, ~] = size(T2);
for idx=1:nrow
    x = T2(idx, 2:5);
    y = T2(idx, 6:9);
    fill(x, y, 'b');
    hold on;
    ylim([0, 30]);
end

% S9
[nrow, ~] = size(T3);
for idx=1:nrow
    x = T3(idx, 2:5);
    y = T3(idx, 6:9);
    fill(x, y, 'b');
    hold on;
    ylim([0, 30]);
end

% T25
[nrow, ~] = size(T4);
for idx=1:nrow
    x = T4(idx, 2:5);
    y = T4(idx, 6:9);
    fill(x, y, 'b');
    hold on;
    ylim([0, 25]);
end
toc;
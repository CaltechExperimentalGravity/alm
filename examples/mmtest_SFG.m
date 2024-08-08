%% a la mode demonstration
% mode matching and beam propagation solutions in MATLAB.
%
% a la mode is a stimple library of gaussian ABCD matrix tools intended to 
% optimize and visualize optical systems.

%% simple beam path
%
% In this example, we will design a simple beam path and then define a target
% beam for modematchin, and choose an optimum configuration from a list of possible
% lens choices.

% here we design an initial simple beam path 

goo = beamPath;
goo.addComponent(component.lens(-1, 0.05, 'lens1'));
goo.addComponent(component.lens(.5, -1, 'lens2'));
goo.seedWaist(.086e-3, -37.0e-3);
%I assume waist z-position is also measured in meters?
goo.addComponent(component.lens(.075, -.07, 'lens3')); %this lens is fixed

% plot the results
zplot = -1:0.01:2;
goo.components
goo.plotSummary(zplot);

%% mode matching optimization
goo.targetWaist(200e-6, 0); %want it at center of crystal

% we create a list of possible lens choices
%focalLengthList = [-.75; .5; 1.75; -2; -1; 2; 3; 1; 2.5; 1.25]; % [meters]
%focalLengthList = linspace(0.03, 2, 30); % [meters]
%f_tlist = [25.4; 50.8; 100; 150; 200; 250; 300; 500; 1000; 2000]/1000;
f_tlist = [ -200; 40; 75; 125; 175; 200; 200; 300; 500]/1000; %in meters
focalLengthList = f_tlist;

lensList = component.lens(focalLengthList);

tic;
[pathList,overlapList] = goo.chooseComponents(...
                'lens1',lensList,[-.1 -0.3],...  % choose lens1 from the list,
                'lens2',lensList.duplicate,[-1, -.3],... %duplicate the list, this allows
                ...                                    %  the same component to be chosen more than once
                'target',[-0.05, 0.05]... % we can also allow the target waist position to vary while optimizing the overlap
                ,'-vt',0.05); % set the minimum initial overlap to 0.25, if a combination of components
                             % has an overlap less than this, it will be skipped without trying to optimize the lens positions
toc
                  
%% select the best solution and plot it
% from the list of all solutions, we may choose the one which has good
% modematching, but also has minimal sensitivity to component location.
pathList = pathList(overlapList >= 0.80);

sensitivityList = pathList.positionSensitivity;

[sensitivityList,sortIndex] = sort(sensitivityList);

pathList = pathList(sortIndex);

bestPath = pathList(1);


% print the component list to the command window
disp(' ')
disp(' Optimized Path Component List:')
display(bestPath.components)
%disp(bestPath.components.parameters)
bestPath.plotSummary(zplot);

%% other features and limitations
% 
% Features:
%
% * lives inside MATLAB
% * built-in beam width measurement fitting
% * define beams as eigenmodes
% * angular, lateral, and positional motion sensitivity calculations
% * calculate gouy phase seperations of optical elements
% * comprehensive, cross referenced help documentation
% 
% Limitations:
%
% * Totally 1-D
% * all components are 'thin'

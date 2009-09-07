% test the list search thing
close all
clear classes

lensList = [component.lens(-.75);...
            component.lens(.5);...
            component.lens(1.75);...
            component.lens(-2);...
            component.lens(-1);...
            component.lens(2);...
            component.lens(3);...
            component.lens(1);...
            component.lens(2.5);...
            component.lens(1.25)];

goo = beamPath;

goo.addComponent(component.lens(1.25,.75,'lens1'));
goo.addComponent(component.lens(1.75,3.25,'lens2'));

goo.seedWaist(.2e-3,0);
goo.targetWaist(.4e-3,5);

zdomain = -1:.01:6;

figure(2)
hold on
goo.plotBeamWidth(zdomain)
goo.plotComponents(zdomain)

[pathList,overlapList] = goo.chooseComponents(...
                'lens1',lensList,[0.5 3],...
                'lens2',lensList.duplicate,[3.5 4],...
                'target',[4.5,6]...
                ,'-vt',.25);

pathList(1).plotBeamWidth(zdomain,'r')
pathList(1).plotComponents(zdomain,'r*')
pathList(1).plotBeams(zdomain,'k')

hold off


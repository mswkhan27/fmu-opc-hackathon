%% General
cp_water = 4190; %specific heat capacity side 1 [J/kg/K]
cp_oil = 2300;

%% Heat Exchangr
% general parameters
HE_surface_area = 380; %total surface area [m^2]
HE_heat_transfer_coefficient = 6800/10; %heat transfer coefficient 1 [W/m^2/K]
% side 1
HE_T1_ini = 65; %Initial temperature [degC]
HE_m1 = 234; %liquid mass [kg]
% side 2
HE_T2_ini = 65; %Initial temperature [degC]
HE_m2 = 234; %liquid mass [kg]


%% Lube-Oil Cooler
LO_heat_transfer_coefficient = 500e4; %Heat transfer coefficient LO
LO_mass_flow = 20; %kg/s
LO_cooling_mass_water_side = 500;
LO_cooling_mass_oil_side = 200;
LO_initial_temperatures = 75;

%% Control
PID_parameter_P_ideal = -0.01*5;
PID_parameter_I_ideal = 1/120;

%% Engine
engine_max_load = 5850e3;
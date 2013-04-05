#!/usr/bin/python 
import optparse, sys, os
import numpy as np
import pylab as py 
import optparse, sys, os
from math import pi 
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

# Import functions external files
import lib.NLD_Functions as NLD_Functions
import lib.GSL_ODE_Functions as GSL_ODE_Functions
import lib.File_Functions as File_Functions
import lib.Physics_Functions as Physics_Functions 
import lib.Plotting_Functions as Plotting_Functions


# Plotting functions

def Simple_Plot(file_name,OD):
	""" Plots the given in as a function of time, it is assumed the columns of data are given by time , omega_x , omega_y and omega_z"""
		
	# Import the data 
	(time,x,y,z) = File_Functions.Import_Data(file_name)

	# Handle any additional options which are in the dictionary
	if OD.has_key('tmax') : tmax = OD['tmax'] 
	else : tmax = max(time)
	if OD.has_key('tmin') : tmin  = OD['tmin']
	else : tmin = min(time)

	fig1=py.subplot(3,1,1) ; fig1.set_xticklabels([])
	fig1.plot(time,x)
	py.ylabel(r"$\omega_{x}$",fontsize=20,rotation="horizontal")
	py.yticks(fig1.get_yticks()[1:-1])
	py.xlim(tmin,tmax)

	fig2=py.subplot(3,1,2) ; fig2.set_xticklabels([])
	fig2.plot(time,y)
	py.yticks() 
	py.ylabel("$\omega_{y}$",fontsize=20,rotation="horizontal")
	py.yticks(fig2.get_yticks()[1:-1])
	py.xlim(tmin,tmax)

	fig2=py.subplot(3,1,3)
	fig2.plot(time,z)
	py.ylabel("$\omega_{z} $",fontsize=20,rotation="horizontal")
	py.xlim(tmin,tmax)

	py.xlabel(r"$t$",fontsize=20)

	py.show()





def main():

	# A function which translates the options.opts input into a dictionary of parameters
	def Create_Option_Dictionary(opts):
		Option_Dictionary={}
		for item in opts.split(","):
			if "=" in item: Option_Dictionary[item.split("=")[0]] = float(item.split("=")[1])
		else : Option_Dictionary[item] = True
		return Option_Dictionary

	def parse_command_line(argvs):

		parser = optparse.OptionParser()
	

		parser.add_option("-p","--plot",help="Plot the last three colums in FILE against the first column it is assumed this refer to wx,wy and wz", metavar="FILE")

		parser.add_option("-s","--splot",help="Plot the last three colums in FILE against the first column converting to spherical polars", metavar="FILE")


		parser.add_option("-c", "--Cplot", help ="Same as plot but transforming coordinates to principle axis of the effective moment of inertia tensor ", metavar="FILE")

		parser.add_option("-d", "--Csplot", help ="Same as splot but transforming coordinates to principle axis of the effective moment of inertia tensor", metavar="FILE")

		parser.add_option("-a", "--alpha",help = "Plot the allignment of omega with the magnetic dipole axis ", metavar="FILE")



		# Options to be called with above


		parser.add_option("-o", "--opts")


		(options,arguments) = parser.parse_args(argvs)
		return options, arguments

	options, arguments = parse_command_line(sys.argv)

	if options.opts : Option_Dictionary = Create_Option_Dictionary(options.opts)
	else : Option_Dictionary = {}

	if options.plot: Simple_Plot(options.plot,Option_Dictionary)

	if options.splot: Spherical_Plot(options.splot,options.opts,)

	if options.Cplot: Simple_Plot_Transform(options.Cplot,options)

	if options.Csplot: Spherical_Plot_Transform(options.Csplot,options)

	if options.alpha : Alpha_Plot(options)


if __name__ == "__main__":
    main()

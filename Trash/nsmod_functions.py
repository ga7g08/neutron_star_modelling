#!/usr/bin/python 

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


# Set the default font for all plots 
from matplotlib import rc
rc('font',**{'family':'serif','serif':['Computer Modern Roman']})
rc('text', usetex=True)

# Set the defaults for axis
py.rcParams['axes.color_cycle'] = ['k', 'r', 'cyan']
py.rcParams['font.size'] = 16
py.rcParams['lines.linewidth'] = 2
py.rcParams['axes.grid']=True
py.rcParams['figure.figsize']= (10.0, 8.0)
py.subplots_adjust(left=0.13, right=0.9, top=0.9, bottom=0.12,hspace=0.0)


def Save_Figure(file_name,type_of_plot,format_type=".png"):
	plot_file_name = type_of_plot+"_"+file_name+format_type
	py.savefig(plot_file_name)
	print "Saving figure as %s" % plot_file_name


def Fit_Function(x,y,n):
	""" Fits a polynomial of degree n to y at the points x. Note that len(x)=len(y) """

	f_p=py.polyfit(x,y,n)

	y_fit=[] ; x_fit=py.linspace(x[0],x[-1],100*len(x))  
	for i in range(len(x_fit)):
		f_val=0.0
		for j in range(n+1): f_val+=f_p[j]*pow(x_fit[i],n-j)
		y_fit.append(f_val)

	return x_fit,y_fit ,f_p


def Magnetic_Field_to_Epsilon_A(options):
	Bs = float(options.b_2_e)
	R = 1e6 #cm
	c=3e10 #cm/s
	I0=1e45
	m=0.5*Bs*pow(R,3)
	epsA=pow(m,2)/(I0*R*pow(c,2))
	print "Bs="+str(Bs)+" Epsilon_A="+str(epsA)

def Epsilon_A_to_Magnetic_Field(options):
	Epsilon_A = float(options.e_2_b)
	R = 1e6 #cm
	c=3e10 #cm/s
	I0=1e45
	m = py.sqrt(Epsilon_A*I0*R*pow(c,2))
	Bs = 2*m/pow(R,3)
	print "Bs="+str(Bs)+" Epsilon_A="+str(Epsilon_A)

def Simple_Plot(options):
	""" Plots the given in as a function of time, it is assumed the columns of data are given by time , omega_x , omega_y and omega_z"""
	# Import the data 
	file_name = options.plot
	(time,x,y,z) = File_Functions.Import_Data(file_name)

	fig1=py.subplot(3,1,1) ; fig1.set_xticklabels([])
	fig1.plot(time,x)
	py.ylabel(r"$\omega_{x}$",fontsize=20,rotation="horizontal")
	py.yticks(fig1.get_yticks()[1:-1])

	fig2=py.subplot(3,1,2) ; fig2.set_xticklabels([])
	fig2.plot(time,y)
	py.yticks() 
	py.ylabel("$\omega_{y}$",fontsize=20,rotation="horizontal")
	py.yticks(fig2.get_yticks()[1:-1])


	fig2=py.subplot(3,1,3)
	fig2.plot(time,z)
	py.ylabel("$\omega_{z} $",fontsize=20,rotation="horizontal")

	py.xlabel(r"$t$",fontsize=20)
	py.show()

def Simple_Plot_Transform(options):
	""" Same as Simple_Plot() except transform to the effective MOI tensor principle axis """
	file_name = options.Cplot
	data=open(file_name,"r")	
	time=[] ; x=[] ; y=[] ; z=[] ; params=[]

	for line in data:
		line=line.split()
		if len(params)==0:
			params=(line)
		else:
			time.append(float(line[0]))
			x.append(float(line[1]))
			y.append(float(line[2]))
			z.append(float(line[3]))

	epsI=float(params[2].split("=")[1])
	epsA=float(params[1].split("=")[1])
	chi=float(params[0].split("=")[1])
	beta=Beta_func(epsI,epsA,chi)

	Cb=py.cos(beta) ; Sb=py.sin(beta)
	xprime=[x[i]*Cb - z[i]*Sb for i in range(len(x))]
	zprime=[z[i]*Cb + x[i]*Sb for i in range(len(x))]
	yprime = y

	fig1=py.subplot(3,1,1)
	py.title(params)
	fig1.plot(time,xprime)
	py.ylabel(r"$\omega_{x}' $",fontsize=20,rotation="horizontal")

	fig2=py.subplot(3,1,2)
	fig2.plot(time,yprime)
	py.yticks() 
	py.ylabel("$\omega_{y}' $",fontsize=20,rotation="horizontal")


	fig2=py.subplot(3,1,3)
	fig2.plot(time,zprime)
	py.xlabel(r"$t$",fontsize=20)
	py.ylabel("$\omega_{z}' $",fontsize=20,rotation="horizontal")

	py.show()


def Spherical_Plot(file_name,opts):
	""" Plot the input data after transforming to spherical polar coordinates 
	The opts dictionary may contain """
	# Default settings 
	labelx = -0.1  # x position of the yaxis labels

	# Import the data in components x,y,z
	max_n = -1
	if opts.has_key('max_n'):
		max_n = opts['max_n']	

	(time,omega_x,omega_y,omega_z)= File_Functions.Import_Data(file_name,max_n) 

	# Transform to spherical polar coordinates
	(omega,a,phi) = Physics_Functions.Transform_Cartesian_2_Spherical(omega_x,omega_y,omega_z)
	
	# Function to help scale the x-axis
	(t_scaled,scale_val) = Plotting_Functions.Sort_Out_Some_Axis(time)	

	# Plot omega(t)
	ax1=py.subplot(3,1,1) ; ax1.set_xticklabels([])
	ax1.plot(t_scaled,omega)

	ax1.set_ylim(0,1.1*max(omega))
	#py.yticks(fig1.get_yticks()[1:-1])
	ax1.set_ylabel(r"$\omega$  [Hz] ",rotation="vertical")
	ax1.yaxis.set_label_coords(labelx, 0.5)

	# Plot a(t)
	ax2=py.subplot(3,1,2) ; ax2.set_xticklabels([])
	ax2.plot(t_scaled,a)
	#py.axhline(90,ls="--",color="k")

	ax2.set_ylim(0,105)
	#py.yticks(fig2.get_yticks()[0:-2])
	ax2.set_yticks(py.arange(0,105,15))
	ax2.set_ylabel("$a $ [deg]",rotation="vertical")
	ax2.yaxis.set_label_coords(labelx, 0.5)

	# Plot phi(t)
	ax3=py.subplot(3,1,3) 
	phi=Physics_Functions.Fix_Phi(phi) # By default we assume the phi is broken so fix it
	ax3.plot(t_scaled,phi)

	#Ploptions
	#ax3.set_ylim(0,110)
	#ax3.set_yticks(py.arange(0,105,15))
	ax3.set_yticks(ax3.get_yticks()[0:-1])
	ax3.set_ylabel("$\phi$ [deg]",rotation="vertical")
	ax3.yaxis.set_label_coords(labelx, 0.5)
	py.xlabel(r"time  [$1\times 10^{"+str(scale_val)+"}$ s]",fontsize=16)

	if opts.has_key('end_val') :
		print " Data on the end value of the spherical components of omega"
		omega_end = omega[-100:-1]
		print " Average of |omega| :  %s s^-1  \n Range of omega : %s"	% (py.average(omega_end),max(omega_end)-min(omega_end))
		a_end = a[-100:-1]
		print " Average of a  : %s s^-1 \n Range of a : %s"	% (py.average(a_end),max(a_end)-min(a_end))
		phi_end = omega[-100:-1]
		print " Average of phi :  %s s^-1 \n Range of phi : %s"	% (py.average(phi_end),max(phi_end)-min(phi_end))


	if opts.has_key('save_fig'):
		Save_Figure(file_name,"Spherical_Plot")
	else:
		py.show()

def Spherical_Plot_Transform(file_name,options):
	""" Plot the input data after transforming to spherical polar coordinates in the primed coordinates 
	options should be passed as a dictionary with the following arguments:
	opts : max_len ~ A maximum number of points to include
	end_val : True ~ Prints an average of the last 100 points in the plot
	save_fig : True ~ Save the figure in an appropriate way """


	# Default settings 
	labelx = -0.1  # x position of the yaxis labels

	# Import the data in components x,y,z
	data=open(file_name,"r")	
	if options['opts']: 
		max_len = int(options.opts)
	else : max_len=-1

	(time,omega_x,omega_y,omega_z)= File_Functions.Import_Data(file_name,max_len)

	# Get parameters of the run from the file name
	p_d = File_Functions.Params_From_File_Name(file_name)
	epsI = p_d["epsI"]
	epsA = p_d["epsA"]
	chi = p_d["chi"]
	

	# Calculate the angle through which the effective mody frame has been rotated and print the result
	beta=Beta_func(epsI,epsA,chi)
	#print epsI,epsA,chi
	print "Transforming to effective body frame rotating by angle beta = ",beta*180/pi

	# Transform to the x',y',z' coordinates
	(xprime,yprime,zprime)=Physics_Functions.Transform_Cartesian_Body_Frame_2_Effective_Body_Frame(omega_x,omega_y,omega_z,beta)

	# Transform to the spherical polar coordinates
	(omegaprime , aprime ,phiprime) = Physics_Functions.Transform_Cartesian_2_Spherical(xprime,yprime,zprime)
	

	if "no_omega" not in sys.argv:

		# Function to help scale the x-axis
		(t_scaled , scale_val) = Plotting_Functions.Sort_Out_Some_Axis(time)	

		# Plot omegaprime(t)
		ax1=py.subplot(311) 
		ax1.set_xticklabels([])
		ax1.plot(t_scaled,omegaprime)

		ax1.set_ylim(0,1.1*max(omegaprime))
		#py.yticks(fig1.get_yticks()[1:-1])
		ax1.set_ylabel(r"$\omega'$ [Hz]",rotation="vertical")
		ax1.yaxis.set_label_coords(labelx, 0.5)

		# Plot aprime(t)
		ax2=py.subplot(312) 
		ax2.set_xticklabels([])
		ax2.plot(t_scaled,aprime)
		#py.axhline(90,ls="--",color="k")

		y_max = 105
		ax2.set_ylim(0,y_max)
		#py.yticks(fig2.get_yticks()[0:-2])
		ax2.set_yticks(py.arange(0,y_max,15))
		ax2.set_ylabel("$a'$ [deg]",rotation="vertical")
		ax2.yaxis.set_label_coords(labelx, 0.5)

		# Plot phiprime(t)
		ax3=py.subplot(313) 

		# Check and fix rotations of 2pi in phi
		phiprime = Physics_Functions.Fix_Phi(phiprime)

		# Often phi becomes very large in which case we scale the axis
		if abs(phiprime[-1])>100:
			#def Scale_Axis(axis):
			#	max_item = max(axis) ; min_item = min(axis)
			#	if abs(max_item) < abs(min_item): max_item = abs(min_item)
			#	scale = round_to_n(max_item,0)
			#	axis_scaled = [ ai/scale for ai in axis]
			#	return (axis_scaled , scale)

			
			(phiprime_scaled , scale) = Plotting_Functions.Sort_Out_Some_Axis(phiprime)
			ax3.plot(t_scaled,phiprime_scaled)
			ax3.set_ylabel(r"$\phi' [\;1\times 10^{"+str(int(py.log10(scale)))+"} $deg]",rotation="vertical")

		else : 
			ax3.plot(t_scaled,phiprime)
			ax3.set_ylabel("$\phi'$  [deg]",rotation="vertical")

		#Ploptions
		ax3.set_xlabel(r"time  [$1\times 10^{"+str(scale_val)+"}$ s]",fontsize=16)		
		ax3.yaxis.set_label_coords(labelx, 0.5)
		ax3.set_yticks(ax3.get_yticks()[0:-2])

	
	else : 
			# Function to help scale the x-axis
		(t_scaled,scale_val) = Plotting_Functions.Sort_Out_Some_Axis(time)	

		fig=py.figure()

		ax1 = py.subplot(111)

		# Plot aprime(t)
		ax1.plot(t_scaled,aprime,lw=1.0)
		#py.axhline(90,ls="--",color="k")

		# Ploptions
		y_max = 105
		py.ylim(0,y_max)
		#py.yticks(fig2.get_yticks()[0:-2])
		py.yticks(py.arange(0,y_max,15))
		py.ylabel("$a' \;[^{\circ}]$",rotation="horizontal",fontsize=18)


		# Plot phiprime(t)
		ax2 = ax1.twinx()

		phiprime = Physics_Functions.Fix_Phi(phiprime)
		if abs(phiprime[-1])>100:
			def Scale_Axis(axis):
				max_item = max(axis) ; min_item = min(axis)
				if abs(max_item) < abs(min_item): max_item = abs(min_item)
				scale = round_to_n(max_item,0)
				axis_scaled = [ ai/scale for ai in axis]
				return (axis_scaled , scale)

			(phiprime_scaled , scale) = Scale_Axis(phiprime)
			ax2.plot(t_scaled,phiprime_scaled,color="b",lw=1.0)

			py.ylabel(r"$\phi' \; 1\times 10^{"+str(int(py.log10(scale)))+"} [^{\circ}]$",rotation="vertical")

		else : 
			ax2.plot(t_scaled,phiprime,color="b",lw=1.0)
			py.ylabel("$\phi' \; [^{\circ}]$",rotation="vertical")
		#Ploptions
		ax2.tick_params(axis='y', colors='blue')
		ax2.yaxis.label.set_color('blue')
		py.xlabel(r"time  [$1\times 10^{"+str(scale_val)+"}$ s]",fontsize=16)
	
		
	if options['end_val'] :
		print " Data on the end value of the spherical components of omega"
		omega_end = omegaprime[-100:-1]
		print " Average of |omega| :  %s s^-1  \n Range of omega : %s"	% (py.average(omega_end),max(omega_end)-min(omega_end))
		a_end = aprime[-100:-1]
		print " Average of a  : %s s^-1 \n Range of a : %s"	% (py.average(a_end),max(a_end)-min(a_end))
		phi_end = omegaprime[-100:-1]
		print " Average of phi :  %s s^-1 \n Range of phi : %s"	% (py.average(phi_end),max(phi_end)-min(phi_end))

	if options['save_fig']:
		Save_Figure(file_name,"Spherical_Plot_Transform")
	
	py.show()

	
def ThreeD_Plot_Cartesian(options):
	d = 1000 ; po = 0.5 # default values 

	# Import the data in components x,y,z
	file_name = options.ThreeD
	(time,omega_x,omega_y,omega_z)= File_Functions.Import_Data(file_name) 

	# Get the paramters of the run
	p_d = File_Functions.Params_From_File_Name(file_name)


	# Options
	if options.opts : 	
		ops = options.opts.split(",")
		start = ops[0] ; stop = ops[1]
		n_start=int(float(start)*len(x)) ; n_stop=int(float(stop)*len(x))
		
		# Inform the user of the restriction in time range 
		print 
		print " Reducing plotted data size from "+str(len(x))+" to "+str(n_stop-n_start)
		print " The time change is from t="+str(time[n_start])+" to t="+str(time[n_stop])
		print 
	
		time = time[n_start:n_stop] ; x = x[n_start:n_stop] ; y = y[n_start:n_stop] ; z = z[n_start:n_stop]

		if len(ops) > 1 :
 			po = float(ops[2]) # options to change the grade of colouring
			d = int(ops[3])


		

	# Extract some parameters from the first line in the file 
	epsI=p_d["epsI"]
	epsA=p_d["epsA"]
	chi=p_d["chi"]

	# Compute the rotation angle of primed axis and transform the solution omega_{xyz} into these coordinates
	beta=Beta_func(epsI,epsA,chi)

	Cb=py.cos(beta) ; Sb=py.sin(beta)

	xprime=[x[i]*Cb - z[i]*Sb for i in range(len(x))]
	zprime=[z[i]*Cb + x[i]*Sb for i in range(len(x))]
	yprime = y

	#fig = py.figure()
	ax = py.subplot(111, projection='3d')


	# Compute same variables used for colouring and plot the x',y' and z' transforming the colour as time changes
	n=len(xprime) ; s=n/d 
	
	for i in range(1,d-1):
		ax.plot(xprime[s*i:s*i+s],yprime[s*i:s*i+s],zprime[s*i:s*i+s],color=(0.0,1-float(pow(i,po)*1.0/pow(d,po)),0.8),alpha=0.5)

	# Create and label the primed axis
	ax.plot(py.zeros(100),py.zeros(100),py.linspace(-max(zprime),max(zprime),100),color="k")
	ax.text(0,0,max(zprime)*1.1,"$z'$")
	ax.plot(py.zeros(100),py.linspace(max(yprime),min(yprime),100),py.zeros(100),color="k")
	ax.text(0,max(yprime)*1.1,0,"$y'$")
	ax.plot(py.linspace(max(xprime),min(xprime),100),py.zeros(100),py.zeros(100),color="k")
	ax.text(max(xprime)*1.1,0,0,"$x'$")

	#py.ylabel(r"$\omega_{y}'$")
	#py.zlabel(r"$\omega_{z}'$")

	ax.set_xticklabels([])
	ax.set_yticklabels([])
	ax.set_zticklabels([])


	if options.save_fig:
		Save_Figure(file_name,"ThreeD_Plot_Cartesian")
	else:
		py.show()

	if options.save_data:
		file_name=options.save_data
		write_file=open(file_name,"w+")
		for i in range (len(xprime)):
			write_file.write(str(time[i])+" "+str(xprime[i])+" "+str(yprime[i])+" "+str(zprime[i])+"\n")
		write_file.close()



def Alpha_Plot(options):
	""" Plots the alignment of the input file [t,omega_x , omega_y and omega_z] against the magnetic dipole"""

	# Import the data in components x,y,z
	file_name = options.alpha
	(time,omega_x,omega_y,omega_z)= File_Functions.Import_Data(file_name) 

	# Get the paramters of the run
	p_d = File_Functions.Params_From_File_Name(file_name)


	# Extract some parameters from the first line in the file 
	epsI=p_d["epsI"]
	epsA=p_d["epsA"]
	chi=p_d["chi"]
	
	# Transform to spherical polar coordinates specifying that we wish the angles to be in Radians rather than degrees
	(omega,a,phi) = Physics_Functions.Transform_Cartesian_2_Spherical(omega_x,omega_y,omega_z,"Radian")
	
	# Function to help scale the t-axis
	(t_scaled,scale_val) = Plotting_Functions.Sort_Out_Some_Axis(time)	

	# Calculate the angle made with the magnetic dipole assumed to lie at chi to the z axis in the x-z plane
	Sx=py.sin(chi) ; Cx=py.cos(chi)
	alpha = [py.arccos(Sx*py.sin(a[i])*py.cos(phi[i]) + Cx*py.cos(a[i]))*180/pi for i in range(len(a))]

	ax1=py.subplot(111)
	ax1.plot(t_scaled,alpha,lw=2)
	ax1.set_ylabel(r"$\alpha$ [deg]",fontsize=20,rotation="horizontal")
	ax1.set_xlabel(r"time  [$1\times 10^{"+str(scale_val)+"}$ s]",fontsize=16)

	if options.save_fig:
		Save_Figure(file_name,"Alpha")
	else:
		py.show()

	if options.end_val: 
		frac = float(options.end_val)
		n = int(len(alpha)*frac)	
		print " Average of the last "+str(frac*100.0)+"% is "+str(py.average(alpha[-1-n:-1]))+" degrees"


def Plot_Angular_Momentum_and_Energy(options):
	
	# Import the data in components x,y,z
	file_name = options.plot_angular_momentum_and_energy
	(time,omega_x,omega_y,omega_z)= File_Functions.Import_Data(file_name) 

	# Get the paramters of the run
	p_d = File_Functions.Params_From_File_Name(file_name)

	n = len(time)

	# Get parameters of the run from the 1st line the file
	epsI=p_d["epsI"]
	epsA=p_d["epsA"]
	chi=p_d["chi"]

	# Calculate the angle through which the effective mody frame has been rotated and print the result
	beta=Beta_func(epsI,epsA,chi)
	print epsI,epsA,chi
	print "Transforming to effective body frame rotating by angle beta = ",beta*180/pi
	
	# Transformations 
	(omega_x_prime,omega_y_prime,omega_z_prime)  = Physics_Functions.Transform_Cartesian_Body_Frame_2_Effective_Body_Frame(omega_x,omega_y,omega_z,beta)

	print "SHould this be primed or not? Check before using"
	(omega_prime,a_prime,phi_prime) = Physics_Functions.Transform_Cartesian_2_Spherical(omega_x,omega_y,omega_z)
	
	# Compute the Eigenvalues
	Io=1e45
	Lambda_plus = 0.5*Io*(2+epsI-epsA+py.sqrt(pow(epsI,2)+pow(epsA,2)-2*epsI*epsA*py.cos(2*chi)) ) 
	Lambda_minus = 0.5*Io*(2+epsI-epsA-py.sqrt(pow(epsI,2)+pow(epsA,2)-2*epsI*epsA*py.cos(2*chi)) )
	Iy = Io 

	# Here we make a choice of Ix,Iz depending on if the mass distribution is prolate/oblate
	if epsI >= 0 :
		Iz = Lambda_plus ; Ix = Lambda_minus
	else : 
		Ix = Lambda_plus ; Iz = Lambda_minus

	# Compute and the angular momentum as a function on time
	M_list=[py.norm([Ix*omega_x_prime[i],Iy*omega_y_prime[i],Iz*omega_z_prime[i]]) for i in range(len(time))]

	# Compute the energy dissipated by the magnetic dipole torque. Function integrand gives the integrand of the work done integral.
	from pylab import sin,cos
	Lambda = 2*1e6/(3*3e10) ; Sx = sin(chi) ; Cx = cos(chi)

	def integrand(epsA,Io,Lambda,omega_x,omega_y,omega_z):
		omega_squared = pow(omega_x,2)+pow(omega_y,2)+pow(omega_z,2)
		return epsA* Lambda *Io*omega_squared*(2*omega_x*omega_z*Sx*Cx-pow(omega_y,2)-pow(Cx*omega_x,2)-pow(Sx*omega_z,2))


	# Initial energy
	Eo = Physics_Functions.Rotational_Kinetic_Energy(Ix,Iy,Iz,omega_x_prime[0],omega_y_prime[0],omega_z_prime[0])

	Work_done=[] ; dW_dt=[integrand(epsA,Io,Lambda,omega_x[0],omega_y[0],omega_z[0])] ; prior= None
	for i in range(1,n):
		dt = time[i]-time[i-1]
		I = integrand(epsA,Io,Lambda,omega_x[i],omega_y[i],omega_z[i])+integrand(epsA,Io,Lambda,omega_x[i-1],omega_y[i-1],omega_z[i-1])
		Work_done.append(0.5*I*dt)
		#dW_dt.append(integrand(epsA,Io,Lambda,omega_x[i],omega_y[i],omega_z[i]))

	# Compute the energy lost due to the dipole 
	Energy_lost_due_to_dipole=py.zeros(n)+Eo ; sumV=0.0
	for i in range(0,n-1):
		sumV+=Work_done[i]
		Energy_lost_due_to_dipole[i+1]+=sumV
	ax1 = py.subplot(111)
	ax1.plot(time,Energy_lost_due_to_dipole,label="Energy lost due to dipole")

	# Plot the actual energy calculated exactly from omega we do this in the body frame axis (rather than effective).
	Energy = [Physics_Functions.Rotational_Kinetic_Energy(Io,Io,Io*(1+epsI),omega_x[i],omega_y[i],omega_z[i]) for i in range(len(time)) ] 

	ax1.plot(time,Energy,label="Exact energy",ls="--")






	#ax3.plot(time,Energy_two,color="b")
	#SA_x = [py.sqrt(2*Ix*Energy[i]) for i in range(len(time)) ] 
	#SA_z = [py.sqrt(2*Iz*Energy[i]) for i in range(len(time)) ] 
	#f = SA_z[0] - SA_x[0]
	#diff_x = [(M_list[i] - SA_x[i])/f for i in range(len(time)) ]  
	#diff_z = [(SA_z[i]-M_list[i])/f  for i in range(len(time)) ]  
	#ax2.plot(time,diff_x,color="r")
	#ax2.plot(time,diff_z,color="b")
	#py.legend(loc="best")

	py.legend()
	if options.save_fig:
		Save_Figure(file_name,"Angular_Momentum_and_Energy")
	else:
		py.show()



def Beta_func(epsI,epsA,chi):
	if epsI>=0:
		sign=-1.0
	else: sign=1.0

	b=py.sqrt(epsA*epsA+epsI*epsI-2*epsA*epsI*py.cos(2*chi))
	return py.arctan((epsI+epsA*(1-2*pow(py.cos(chi),2.0))+sign*b)/(2*epsA*py.sin(chi)*py.cos(chi)))

def Print_Beta(options):
	"""This functions takes as input the three parameters epsI,epsA and chi and returns Beta the angle between the principle axis of the new MOI tensor which aligns with the original z axis, and the original z axis."""
	foptions=options.Beta.split(",")
	sign=float(foptions[0])
	epsI=sign*pow(10,float(foptions[1]))
	epsA=pow(10,float(foptions[2]))
	chi=float(foptions[3])*pi/180.0
	print "epsI="+str(epsI)+"  epsA="+str(round_to_n(epsA,2))+"  chi="+str(foptions[3])
	print "beta=" , Beta_func(epsI,epsA,chi)*180.0/pi, " degrees"


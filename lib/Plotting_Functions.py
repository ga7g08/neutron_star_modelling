#!/usr/bin/python 
""" Some commonly used functions in plotting called from tools"""

import pylab as py 
from math import floor

def Texify_Float(f,n=1,power=True):
	"""This isn't really a Plotting function, but the other functions are in here. 
		Takes a float and returns a string that looks nice in Latex, takes arguments 
	n=int ~ Number of sig.fig
	power = Bool ~ Whether to produce a *10^{x} or just a regular number"""
	# Ensure the input is a float
	f = float(f)
	if power==True:
		f_power = int(py.log10(Round_To_n(f,0)))
		f_SF = Round_To_n(f,n)*pow(10,-f_power)
		return r" %s\times 10^{%s} " % (f_SF,f_power)
	else :
		print f
		f_SF = Round_To_n(f,n)
		return  str(f_SF)

# Generic functions 

def Sort_Out_Some_Axis(x):
	largest_value = max(x)
	largest_value_0sf = Round_To_n(largest_value,0)
        
    # This next line finds the order of magnitude of the maximum value so it can be appropriately scaled
	Scale = largest_value_0sf/float(str(largest_value_0sf)[0]) 
	Order_of_Magnitude = int(py.log10(Scale))
        
	x_scaled=[xi/Scale for xi in x]
	return (x_scaled,Order_of_Magnitude)
	

def Round_To_n(x,n):
	return round(x, -int(floor(py.sign(x)*py.log10(abs(x))))+n)



def Plot_a_phi(time,a,phi):
	# Function to help scale the x-axis
	(scale_val,t_scaled) = sort_out_time_axis(time)	

	ax1 = py.subplot(111)

	# Plot aprime(t)
	ax1.plot(t_scaled,aprime)
	#py.axhline(90,ls="--",color="k")

	# Ploptions
	y_max = 105
	py.ylim(0,y_max)
	#py.yticks(fig2.get_yticks()[0:-2])
	py.yticks(py.arange(0,y_max,15))
	py.ylabel("$a' \;[^{\circ}]$",rotation="vertical")


	# Plot phiprime(t)
	ax2 = ax1.twinx()

	phiprime = Fix_Phi_Degrees(phiprime)
	if abs(phiprime[-1])>100:
		def Scale_Axis(axis):
			max_item = max(axis) ; min_item = min(axis)
			if abs(max_item) < abs(min_item): max_item = abs(min_item)
			scale = round_to_n(max_item,0)
			axis_scaled = [ ai/scale for ai in axis]
			return (axis_scaled , scale)

		(phiprime_scaled , scale) = Scale_Axis(phiprime)
		ax2.plot(t_scaled,phiprime_scaled)

		py.ylabel("$\phi' \; 10^{"+str(int(py.log10(scale)))+"} [^{\circ}]$",rotation="vertical")

	else : 
		ax2.plot(t_scaled,phiprime)
		py.ylabel("$\phi' \; [^{\circ}]$",rotation="vertical")
	#Ploptions
	
	py.xlabel(r"$t\;  [1\times 10^{"+str(scale_val)+"}s]$",fontsize=16)

	py.show()

def ThreeD_Sphere(axis,elevation,azimuth,x,y,z,color="b",ls=".",lw=1):
	"""Function which given an axis with 3D projection and the azimuth and elevation plots the x,y,z shading the values which are on the opposite side of the unit sphere to the viewer. This should primarily only be used with drawing on the unit sphere.""" 

	# Set the viewing angle
	axis.view_init(elevation, azimuth)

	# Init. lists for the front and back 
	front_x = [] ; front_y=[] ; front_z=[]
	back_x = [] ; back_y=[] ; back_z=[]

	# Get the viewing limits from the azimuth
	view_angle_low = azimuth-90
	view_angle_high = azimuth + 90
	if view_angle_low < -180 :
		view_angle_low_2 = view_angle_low+360
	else : view_angle_low_2 = 180

	# Cycle through points and check which list they should be added to
	for i in range(len(x)):
		
		if view_angle_low -5 < py.arctan2(y[i],x[i])*180/py.pi < view_angle_high +5:
			front_x.append(x[i])
			front_y.append(y[i])
			front_z.append(z[i])
		if view_angle_low_2 < py.arctan2(y[i],x[i])*180/py.pi < 180 :
			front_x.append(x[i])
			front_y.append(y[i])
			front_z.append(z[i])
		if	-180 < py.arctan2(y[i],x[i])*180/py.pi <  view_angle_low  :
			back_x.append(x[i])
			back_y.append(y[i])
			back_z.append(z[i])
		if	view_angle_high   < py.arctan2(y[i],x[i])*180/py.pi <  180 :
			back_x.append(x[i])
			back_y.append(y[i])
			back_z.append(z[i])

	
	# Plot the points using plot3D 
	if ls in ["-","--",":","-."]:
		def plot(x,y,z,alpha,delta=1.0):
			j=0
			for i in range(1,len(x)):
				#if py.norm([x[i]-x[i-1],y[i]-y[i-1],z[i]-z[i-1]]) < delta:
				if x[i]*x[i-1] > 0.0 and y[i]*y[i-1]>0.0 :
					pass
				else :
					axis.plot3D(x[j:i-1],y[j:i-1],z[j:i-1],ls,alpha=alpha,color=color,lw=lw)
					j=i
			if i !=j :
				axis.plot3D(x[j:i-1],y[j:i-1],z[j:i-1],ls,alpha=alpha,color=color,lw=lw )

		plot(front_x,front_y,front_z,alpha=1.0)
		plot(back_x,back_y,back_z,alpha=0.4)
	else :
		axis.plot3D(front_x,front_y,front_z,ls,alpha=1.0,color=color,lw=lw )
		axis.plot3D(back_x,back_y,back_z,ls,alpha=0.3,color=color,lw=lw )


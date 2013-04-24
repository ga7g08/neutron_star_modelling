#!/usr/bin/python 

import pylab as py
from pylab import sin,cos

import Physics_Functions
import File_Functions

def Parameter_Space_Plot(file_name,Option_Dictionary):
	"""

	Plots the paramaters omega_dot,a_dot and phi_dot in a 3D projection

	Option Dictionary takes

    """

	# Handle any additional options which are in the dictionary
	if Option_Dictionary.has_key("nmax"):
		max_n = int(Option_Dictionary['nmax']) 
	else : max_n = -1
	
	(time,x,y,z)= File_Functions.Import_Data(file_name,max_n)


	# Transform to spherical polar coordinates in radians
	(omega,a,phi) = Physics_Functions.Transform_Cartesian_2_Spherical(x,y,z,Angle_Type="Radians")

	# Fix phi
	phi = Physics_Functions.Fix_Phi(phi,Angle_Type="Radians")

	# Calculate the differentials from Goldreich equations

	# Import data from params
	Parameter_Dictionary = File_Functions.Parameter_Dictionary(file_name)
	epsI=float(Parameter_Dictionary["epsI"])
	epsA=float(Parameter_Dictionary["epsA"])
	chi=float(Parameter_Dictionary["chi"])*py.pi/180 # This will be returned in radians

	# Calculate some constants
	epsI_prime=epsI/(1+epsI)
	Sx= sin(chi) ; Cx = cos(chi)
	Lambda=2*1e6/(3*3e10)         # 2R/3c

	omega_dot = [] ; a_dot=[] ; phi_dot=[]
	for i in xrange(len(omega)):
		cosa=cos(a[i]) ; sina=sin(a[i])
		cosphi=cos(phi[i]) ; sinphi=sin(phi[i])
		Tsx = Cx*Sx*cosa - Cx*Cx*sina*cosphi 
		Tsy = -1.0*sina*sinphi 
		Tsz = Sx*Cx*sina*cosphi-Sx*Sx*cosa 

		pre = (Sx*sina*cosphi+Cx*cosa) 
		Tax = pre*sina*sinphi*Cx 
		Tay = pre * (cosa*Sx - sina*cosphi*Cx) 
		Taz = pre*(-1.0*sina*sinphi*Sx) 

		Tsdotomega = 2*Sx*Cx*sina*cosa*cosphi-pow(sina*sinphi,2)-pow(Sx*cosa,2)-pow(Cx*sina*cosphi,2)

		omega_dot.append( Lambda*epsA*pow(omega[i],3)*(Tsdotomega-epsI_prime*Tsz*cosa) - epsA*epsI_prime*pow(omega[i],2)*Taz*cosa)

		a_dot.append(Lambda*epsA*pow(omega[i],2)*pow(sina,-1)*(Tsdotomega*cosa-(1-epsI_prime*pow(sina,2))*Tsz) - epsA*omega[i]*Taz*(1-epsI_prime*pow(sina,2))*pow(sina,-1)
		)

		phi_dot.append(pow(omega[i],2)*Lambda*epsA*pow(sina,-1)*(Tsy*cosphi-Tsx*sinphi)+omega[i]*epsA*pow(sina,-1)*(Tay*cosphi-Tax*sinphi))

	# Plot the data in 3d
	ax = py.subplot(111, projection='3d')

	# Plot the 'shadows'
	#ax.plot(omega_dot, a_dot, 2.1*min(phi_dot),zdir='z',color="k",alpha=0.2,lw=0.8)
	#ax.plot(a_dot, phi_dot,0.5*max(omega_dot),zdir='x',color="k",alpha=0.2,lw=0.8) 
	#ax.plot(omega_dot,phi_dot,1.1*max(a_dot),zdir='y',color="k",alpha=0.2,lw=0.8)

	ax.plot(omega_dot,a_dot,phi_dot,"-",lw=0.8,color="b")

	#py.xlim(min(omega_dot) , max(omega_dot))




	# Ploptions 
	py.rcParams['font.size'] = 14
	ax.set_xlabel(r"$\dot{\omega}$",size=20)
	ax.set_ylabel(r"$\dot{a}$",size=20)
	ax.set_zlabel(r"$\dot{\phi}$",size=20)
	ax.set_xticks(ax.get_xticks()[0:-1:2])   # Reduce the # of ticks
	ax.set_yticks(ax.get_yticks()[0:-1:2])
	ax.set_zticks(ax.get_zticks()[0:-1:2])

	if Option_Dictionary.has_key('save_fig'):
		File_Functions.Save_Figure(file_name,"Parameter_Space_Plot")
	else : 
		py.show()


	
	



def Correlation_Sum():

	# --Options n element reduction , R_min , R_max , Number of Rs to consider
	#print arguments
	file_name = options.correlation_sum
	foptions = options.opts.split(",")
	# Extract data from a dotted_variable_XXX file
	data=open(file_name,"r")	
	time=[] ; omega_dot=[] ; a_dot=[] ; phi_dot=[] ; params=[]

	for line in data:
		line=line.split()
		time.append(float(line[0]))
		omega_dot.append(float(line[1]))
		a_dot.append(float(line[2]))
		phi_dot.append(float(line[3]))

	# Use first option argument to reduce the data by only considering every nth element. We do not cut a chunk out here as this would change the shape of the data substantially
	n=int(foptions[0]) ; N = len(time) 
	time=time[0:N:n]
	omega_dot=omega_dot[0:N:n]
	a_dot=a_dot[0:N:n]
	phi_dot=phi_dot[0:N:n]
	N=len(time) # length of data after reduction

	# Second and third options arguments specify the natural exponents with which R the sphere radius should vary
	R_min=float(foptions[1]) ; R_max=float(foptions[2]) ; Number=int(float(foptions[3]))
	R_list=py.logspace(R_min,R_max,Number) 

	def abs_val(x1,y1,z1,x2,y2,z2):
		return py.sqrt((x1-x2)**2.0+(y1-y2)**2.0+(z1-z2)**2.0)	

	# Calculate C(R) for each R and record natural log of both. This is not an elegant way to do this can we do better?
	lnC_list=[] ; lnR_list=[] ; lnC_outsiders_list=[] ; lnR_outsiders_list=[]
	for R in R_list:
		sumV=0.0
		for i in range(N):
			for j in range(i+1,N):
				if R > abs_val(omega_dot[i],a_dot[i],phi_dot[i],omega_dot[j],a_dot[j],phi_dot[j]):
					sumV+=1.0	
		# Check there is a satisfactory number of points in the sum

		# Lower bound 
		if sumV==0.0: 
			print "No points in R=",R , " consider a larger R_min. Ignoring this point	"
		else : 	
			C = 2.0*sumV/(float(N)*(float(N)-1.0))		
			if C < 10.0/float(N) :
				print " Only ",sumV,"points in R=",R , " consider a larger R_min. This data will not be used in calculating the best fit	"
				lnC_outsiders_list.append(py.log(C))
				lnR_outsiders_list.append(py.log(R))
		
				# Upper bound
			
			elif C > 0.1 :	
				print "More than 10% of all points in the test sphere, this data will not be used in calculating the best fit"
				print sumV , N
				lnC_outsiders_list.append(py.log(C))
				lnR_outsiders_list.append(py.log(R))
			else : 
				C = 2.0*sumV/(float(N)*(float(N)-1.0))
				lnC_list.append(py.log(C))
				lnR_list.append(py.log(R))
				# Print some data for the user 
				print "R =",R," ln(R)=",py.log(R),"C =",C," ln(C)=",py.log(C)," Sum_total = ",sumV

	# Linear fit
	(x_fit,y_fit,f_p)=Fit_Function(lnR_list,lnC_list,1)
	
	# Plot 
	py.plot(x_fit,y_fit,color="b",label="$\ln(c)="+str(round(f_p[0],2))+"\ln(R)  +"+str(round(f_p[1],2))+"$")
	py.plot(lnR_list,lnC_list,"o",color="r",label="Data used in fit")
	py.plot(lnR_outsiders_list,lnC_outsiders_list,"x",color="r",label="Data not used in fit")

	# Give upper and lower bounds on C(R)
	py.axhline(py.log(0.1),ls="--",color="k",alpha=0.6)
	py.axhline(py.log(10.0/float(N)),ls="--",color="k",label="Bounds on $\ln(C(R))$",alpha=0.6)

	leg = py.legend(loc=2,fancybox=True)
	leg.get_frame().set_alpha(0.6)
	py.ylabel(r"$\ln(C)$")
	py.xlabel(r"$\ln(R)$")

	py.title(r"Correlation plot for $\chi = $"+file_name.split("_")[4])
	if options.save_fig : 
		py.savefig("correlated_dimensions_"+file_name.lstrip("dotted_variables").rstrip("txt")+"png")

	py.show()

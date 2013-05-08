from cython_gsl cimport *
import math
#from tables import *
import numpy as np

# Functions to solve
cdef int with_anom_torque (double t, double y[], double f[], void *params) nogil:
	""" Function defining the ODEs with the anomalous torque """
	# Define the variables used in the calculation
	cdef double wx,wy,wz,w_2,epsI,epsA,chi,Lambda

	# Import the three time dependant variables from y[] 
	wx=y[0]
	wy=y[1]
	wz=y[2]
	Ox=y[3]
	Oy=y[4]
	Oz=y[5]

	w_2 = pow(wx,2)+pow(wy,2)+pow(wz,2)

	# Import the constant variables from params
	Lambda = (<double *> params)[0]    #= 2R/3C */
	epsI= (<double *> params)[1]
	epsA = (<double *> params)[2]
	chi = (<double *> params)[3] 
	K = (<double *> params)[4] 
	Ishell = (<double *> params)[5] 
	Icore = (<double *> params)[6]

	# Calculate the angular parts of the three equations to avoid repeated calculation
	cdef double Cx,Sx
	Cx = cos(chi) 
	Sx = sin(chi) 

	#  Define the three ODEs in f[] as functions of the above variables
	f[0] = epsA*(Lambda*w_2*Cx*(wz*Sx-wx*Cx)+(Sx*wx+Cx*wz)*wy*Cx) - wy*wz*epsI +  K*(Ox-wx)*pow(Ishell,-1);

	f[1] = epsA*(-Lambda*w_2*wy+(Sx*wx+Cx*wz)*(wz*Sx-wx*Cx)) + wx*wz*epsI  + K*(Oy-wy)*pow(Ishell,-1);

	f[2] = epsA*pow(1+epsI,-1) * (Lambda*w_2*Sx*(wx*Cx - wz*Sx) -(Sx*wx+Cx*wz)*wy*Sx)  + K*(Oz-wz)*pow(Ishell,-1) ;

	f[3] = -K*(Ox-wx)*pow(Icore,-1) - wy*Oz + wz*Oy ;

	f[4] = -K*(Oy-wy)*pow(Icore,-1) - wz*Ox + wx*Oz ;

	f[5] = -K*(Oz-wz)*pow(Icore,-1) - wx*Oy + wy*Ox ;

	return GSL_SUCCESS



#cdef int no_anom_torque (double t, double y[], double f[], void *params) nogil:
#	""" Function defining the ODEs with the anomalous torque """
#	# Define the variables used in the calculation
#	cdef double wx,wy,wz,w_2,epsI,epsA,chi,Lambda

#	# Import the three time dependant variables from y[] 
#	wx=y[0]
#	wy=y[1]
#	wz=y[2]
#	w_2 = pow(wx,2)+pow(wy,2)+pow(wz,2)

#	# Import the constant variables from params
#	Lambda = (<double *> params)[0]    #= 2R/3C */
#	epsI= (<double *> params)[1]
#	epsA = (<double *> params)[2]
#	chi = (<double *> params)[3] 

#	# Calculate the angular parts of the three equations to avoid repeated calculation
#	cdef double Cx,Sx
#	Cx = cos(chi) 
#	Sx = sin(chi) 

#	#  Define the three ODEs in f[] as functions of the above variables
#	f[0] = epsA*(Lambda*w_2*Cx*(wz*Sx-wx*Cx)) - wy*wz*epsI

#	f[1] = epsA*(-Lambda*w_2*wy) + wx*wz*epsI

#	f[2] = epsA*pow(1+epsI,-1) * (Lambda*w_2*Sx*(wx*Cx - wz*Sx)) 
#	return GSL_SUCCESS

# Currently jac is unused by the ODE solver so is left empty
cdef int jac (double t, double y[], double *dfdy, double dfdt[], void *params) nogil:

	return GSL_SUCCESS



def main (epsI=1.0e-2, epsA=1.0e-3 , omega0=1.0e4, error=1e-5, t1=1.0e6 , chi_degrees = 30.0 ,anom_torque=True,file_name = "generic.txt", K=0.0, Ishell=1e45, Icore=145):
	"""  """
#	# Define the vector class
#	class time (IsDescription):
#		name = StringCol(16)	
#		t = Int32()

#	class vector(IsDescription):
#		name= StringCol(16)   # 16-character String
#		i  = Int32Col()			# 32-bit integer
#		j  = Int32Col() 			# 32-bit integer
#		k = Int32Col() 			# 32-bit integer

#	h5file = tables.openFile("tutorial1.h5", mode = "r", title = "Test file")
#	group = h5file.createGroup("/", 'spin_vectors',"Spin vectors of the crust and core")
#	shell_table = h5file.createTable(group, 'shellvector', vector, "	")
#	core_table = h5file.createTable(group, 'corevector',vector," ")
#	time_table = h5file.createTable(group,'time',time," " )

	# Define default variables
	cdef double chi,R,c_speed,Lambda

	chi=math.pi*chi_degrees/180.0
	R = 1.0e6            
	c_speed = 3e10          
	Lambda = 2*R / (3*c_speed) 
	a_int=math.pi*50.0/180; 

	# Pass them to params list
	cdef double params[7]
	params[0] = Lambda
	params[1] = epsI
	params[2] = epsA
	params[3] = chi
	params[4] = K
	params[5] = Ishell
	params[6] = Icore

	# Setup the solver
	cdef gsl_odeiv_step_type * T
	T = gsl_odeiv_step_rk8pd

	cdef gsl_odeiv_step * s
	s = gsl_odeiv_step_alloc (T, 6)
	cdef gsl_odeiv_control * c
	c = gsl_odeiv_control_y_new (error, error)
	cdef gsl_odeiv_evolve * e
	e = gsl_odeiv_evolve_alloc (6)

	cdef gsl_odeiv_system sys

	# Test if the anomalous torque is required or not
	if anom_torque :
		sys.function = with_anom_torque 
#	else :
#		sys.function = no_anom_torque

	sys.jacobian = jac
	sys.dimension = 6
	sys.params = params


	cdef int i
	cdef double t, y[6] ,h
	h = 1e-10   # Initial step size
	t = 0.0
	y[0] = omega0*sin(a_int)
	y[1] = 0.0
	y[2] = omega0*cos(a_int)
	y[3] = omega0*sin(a_int)
	y[4] = 0.0
	y[5] = omega0*cos(a_int)


	cdef int status
	# Currently we use python to write to file, would it be quicker to do this in C?
	#write_file = open(file_name,"w+")

	x = []
	while (t < t1):
		status = gsl_odeiv_evolve_apply (e, c, s, &sys, &t, t1, &h, y)

		if (status != GSL_SUCCESS):
			break

		#write_file.write("%.16e %.16e %.16e %.16e %.16e %.16e %.16e\n" %(t, y[0], y[1],y[2],y[3], y[4],y[5]) )	
#			time_table.row['t'] =t
#			shell_table.row['i']=y[0]
#			shell_table.row['j']=y[1]
#			shell_table.row['k']=y[2]
#			shell_table.row.append()
		x.append(y[0])
	

		

	gsl_odeiv_evolve_free (e)
	gsl_odeiv_control_free (c)
	gsl_odeiv_step_free (s)
	return x
	#write_file.close()

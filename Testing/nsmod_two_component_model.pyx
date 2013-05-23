from cython_gsl cimport *
import math

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

	# Calculate the angular parts of the three equations to avoid repeated calculation
	cdef double Cx,Sx
	Cx = cos(chi) 
	Sx = sin(chi) 

	#  Define the three ODEs in f[] as functions of the above variables
	f[0] = epsA*(Lambda*w_2*Cx*(wz*Sx-wx*Cx)+(Sx*wx+Cx*wz)*wy*Cx) - wy*wz*epsI + K*(Ox-wx)

	f[1] = epsA*(-Lambda*w_2*wy+(Sx*wx+Cx*wz)*(wz*Sx-wx*Cx)) + wx*wz*epsI + K*(Oy-wy)

	f[2] = epsA*pow(1+epsI,-1) * (Lambda*w_2*Sx*(wx*Cx - wz*Sx) -(Sx*wx+Cx*wz)*wy*Sx) + K*(Oz-wz) 

	# For the Isuperluid is not implemented correctly
	f[3] = -K*(Ox-wx) + wy*Oz - wz*Oy

	f[4] = -K*(Oy-wy) + wz*Ox - wx*Oz

	f[5] = -K*(Oz-wz) + wx*Oy - wy*Ox

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

## Currently jac is unused by the ODE solver so is left empty
cdef int jac (double t, double y[], double *dfdy, double dfdt[], void *params) nogil:

	return GSL_SUCCESS



def main (epsI=1.0e-6, epsA=1.0e-8 , omega0=1.0e4, error=1e-4, t1=1.0e8 , chi_degrees = 30.0 ,anom_torque=True,file_name = "generic.txt",K=0.0):
	"""  """

	# Define default variables
	cdef double chi,R,c_speed,Lambda

	chi=math.pi*chi_degrees/180.0
	R = 1.0e6            
	c_speed = 3e10          
	Lambda = 2*R / (3*c_speed) 
	a_int=math.pi*50.0/180; 

	# Pass them to params list
	cdef double params[5]
	params[0] = Lambda
	params[1] = epsI
	params[2] = epsA
	params[3] = chi
	params[4] = K

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
	h = 1e-6   # Initial step size
	t = 0.0
	y[0] = omega0*sin(a_int)
	y[1] = 0.0
	y[2] = omega0*cos(a_int)
	y[3] = omega0*sin(a_int)
	y[4] = 0.0
	y[5] = omega0*cos(a_int)


	cdef int status
	# Currently we use python to write to file, would it be quicker to do this in C?
	write_file = open(file_name,"w+")

	while (t < t1):
		status = gsl_odeiv_evolve_apply (e, c, s, &sys, &t, t1, &h, y)

		if (status != GSL_SUCCESS):
			break

		write_file.write("%.16e %.16e %.16e %.16e \n" %(t, y[0], y[1],y[2]) )
		
		

	gsl_odeiv_evolve_free (e)
	gsl_odeiv_control_free (c)
	gsl_odeiv_step_free (s)

	write_file.close()
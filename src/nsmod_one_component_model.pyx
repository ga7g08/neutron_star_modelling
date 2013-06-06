"""
Solver for three coupled ODEs which define the single component system

The solver used GSL odeint to actually solve the odes and Cython_GSL
as a python interface documentation can be found at

    http://www.gnu.org/software/gsl/manual/
    html_node/Ordinary-Differential-Equations.html

and

    https://github.com/twiecki/CythonGSL

any changes to these files will require recompiling using the setup.py in
the home directory.

"""

from cython_gsl cimport *
import math
import numpy as np
import h5py

# Need to add in anom_torque

cdef int no_anom_torque (double t, double y[], double f[], void *params) nogil:
    """ Function defining the ODEs with the anomalous torque """
    # Define the variables used in the calculation
    cdef double wx,wy,wz,w_2,epsI1,epsI3,epsA,chi,Lambda

    # Import the three time dependant variables from y[]
    wx=y[0]
    wy=y[1]
    wz=y[2]
    w_2 = pow(wx,2)+pow(wy,2)+pow(wz,2)

    # Import the constant variables from params
    Lambda = (<double *> params)[0]    #= 2R/3C */
    epsA = (<double *> params)[1]
    chi = (<double *> params)[2]
    epsI1 = (<double *> params)[3]
    epsI3 = (<double *> params)[4]

    # Calculate the angular parts of the three equations to avoid repeated calculation
    cdef double Cx,Sx
    Cx = cos(chi)
    Sx = sin(chi)

    #  Define the three ODEs in f[] as functions of the above variables
    f[0] = epsA * (Lambda * w_2 * Cx * (wz * Sx - wx * Cx)) * pow(1 + epsI1, -1) - wy * wz * epsI3 * pow(1 +epsI1, -1)

    f[1] = epsA * (- Lambda * w_2 * wy) - wx * wz * (epsI1 - epsI3)

    f[2] = epsA * pow(1 + epsI3, -1) * (Lambda * w_2 * Sx * (wx * Cx - wz * Sx)) + wx * wy * epsI1 * pow(1 + epsI3, -1)
    return GSL_SUCCESS

# Currently jac is unused by the ODE solver so is left empty
cdef int jac (double t, double y[], double *dfdy, double dfdt[], void *params) nogil:

    return GSL_SUCCESS



def main (epsI1=-1.0e-6, epsI3=1.0e-6, epsA=1.0e-8 , omega0=1.0e1,
    error=1e-10, t1=1.0e3 , eta=0.0 ,chi_degrees = 30.0 ,anom_torque=True ,
    file_name="generic.hdf5",n=None):
    """ Solve the one component model  using gsl_odeiv2_step_rk8pd """

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
    params[1] = epsA
    params[2] = chi
    params[3] = epsI1
    params[4] = epsI3

    # Initial values and calculate eta_relative
    cdef int i
    cdef double t , y[3] ,h , eta_relative
    eta_relative = eta*pow(omega0,2)
    h = 1e-15   # Initial step size
    t = 0.0
    y[0] = omega0*sin(a_int)
    y[1] = 0.0
    y[2] = omega0*cos(a_int)
    print y[0],y[1],y[2]

    # Inititate the system and define the set of functions
    cdef gsl_odeiv2_system sys

    # Test if the anomalous torque is required or not
    #if anom_torque :
    #    sys.function = with_anom_torque
    #else :
    sys.function = no_anom_torque

    sys.jacobian = jac
    sys.dimension = 3
    sys.params = params


    # Setup the solver ~ Note not all of these cdefs are always used.
    # It seems cython won't accept a cdef inside an if statement.

    # For n
    cdef gsl_odeiv2_driver * d
    d = gsl_odeiv2_driver_alloc_y_new(
    &sys, gsl_odeiv2_step_rk8pd,
    error, error, 0.0)

    # Setup the solver alternative to n
    cdef gsl_odeiv2_step_type * T
    T = gsl_odeiv2_step_rk8pd

    cdef gsl_odeiv2_step * s
    s = gsl_odeiv2_step_alloc (T, 3)
    cdef gsl_odeiv2_control * c
    c = gsl_odeiv2_control_y_new (error, error)
    cdef gsl_odeiv2_evolve * e
    e = gsl_odeiv2_evolve_alloc (3)

    cdef int status
    cdef double ti

    time = []
    w1=[]
    w2=[]
    w3=[]

    if n :

        # Run saving at discrete time values

        for i from 1 <= i <= n:
            ti = i * t1 / n
            status = gsl_odeiv2_driver_apply (d, &t, ti, y)

            if (status != GSL_SUCCESS):
                print("error, return value=%d\n" % status)
                break

            time.append(t)
            w1.append(y[0])
            w2.append(y[1])
            w3.append(y[2])

        gsl_odeiv2_driver_free(d)

    else:

        while (pow(y[0],2)+pow(y[1],2)+pow(y[2],2) > eta_relative and t < t1 ):
            status = gsl_odeiv2_evolve_apply (e, c, s, &sys, &t, t1, &h, y)

            if (status != GSL_SUCCESS):
                break

            time.append(t)
            w1.append(y[0])
            w2.append(y[1])
            w3.append(y[2])

        gsl_odeiv2_evolve_free (e)
        gsl_odeiv2_control_free (c)
        gsl_odeiv2_step_free (s)



    f = h5py.File(file_name,'w')
    f.create_dataset("time",data=time)
    f.create_dataset("w1",data=w1)
    f.create_dataset("w2",data=w2)
    f.create_dataset("w3",data=w3)
    return file_name


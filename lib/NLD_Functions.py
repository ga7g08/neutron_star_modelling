#!/usr/bin/python
"""

Contains the functions associated with Non-Linear dynamics
such as Paramater space plot and Correlation dimension

"""

import pylab as py
from pylab import sin, cos
import Physics_Functions
import File_Functions
import Plot
import Useful_Tools

# Import defaults for plotting
Plot.Defaults()


def Parameter_Space_Plot(file_name, Option_Dictionary={}):
    """

    Plots the paramaters omega_dot,a_dot and phi_dot in a 3D projection

    Option Dictionary takes
    azim:float [degs] ~ Default is 15.0
    elev:float [degs] ~ Default is 150.0

    Additonal close up plot takes string "axis/xmin/max/ymin/ymax "
    where the axis is the projection of "z" along which the 2D plot is made:
    axis = 0 ~ omega_dot axis
           1 ~ a_dot axis
           2 ~ phi_dot axis
    if you wish to view the entire range simply leave xmin etc empty e.g 1////

    """

    # Handle any additional options which are in the dictionary

    if "elev" in Option_Dictionary:
        elev = float(Option_Dictionary['elev'])
    else:
        elev = 15.0
    if "azim" in Option_Dictionary:
        azim = float(Option_Dictionary['azim'])
    else:
        azim = 150

    if 'nmax' in Option_Dictionary:
        nmax = int(Option_Dictionary['nmax'])
    else:
        nmax = -1

    (time, omega_dot, a_dot, phi_dot) = Dotted_Variable(file_name)

    # Plot the data in 3d
    fig = py.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Set the view angle
    ax.view_init(elev, azim)

    ax.plot(omega_dot, a_dot, phi_dot, "-", lw=0.8, color="b")

    # Plot the 'shadows'
    ax.plot(omega_dot, a_dot, min(phi_dot),
        zdir='z', color="k", alpha=0.2, lw=0.8)
    #ax.plot(a_dot, phi_dot,min(omega_dot),zdir='x',color="k",alpha=0.2,lw=0.8)
    #ax.plot(omega_dot,phi_dot,max(a_dot),zdir='y',color="k",alpha=0.2,lw=0.8)

    # Plotting options, remove ticks and add labels
    ax.set_xlabel(r"$\dot{\omega}$")
    ax.set_ylabel(r"$\dot{a}$")
    ax.set_zlabel(r"$\dot{\phi}$")
    ax.set_xticks([])  # ax.get_xticks()[1:-2:3])   # Reduce the # of ticks
    ax.set_yticks([])
    ax.set_zticks([])

    if 'save_fig' in Option_Dictionary:
        File_Functions.Save_Figure(file_name, "Parameter_Space_Plot")
    else:
        py.show()

    # Additional plot may be made if required
    if "close" in Option_Dictionary:
        axis_label_list = [r"$\dot{\omega}$", r"$\dot{a}$", r"$\dot{\phi}$"]
        axis_list = [omega_dot, a_dot, phi_dot]
        try:
            (axis, xmin, xmax, ymin, ymax) = \
                Option_Dictionary['close'].split("/")
        except ValueError:
            print (" ERROR: close should have value 'axis/xmin/max/ymin/ymax'"
                   "no plot will be produced")
            return
        # Remove the axis
        axis_label_list.pop(int(axis))
        axis_list.pop(int(axis))

        fig2 = py.figure()
        ax2 = fig2.add_subplot(111)
        ax2.plot(axis_list[0], axis_list[1])

        try:
            float(xmin)
            float(xmax)
            float(ymin)
            float(ymax)

            ax2.set_xlim(float(xmin), float(xmax))
            ax2.set_ylim(float(ymin), float(ymax))
        except ValueError:
            print ("x and y lims are not properly defined"
                    "these should be floats. Using full range instead")

        ax2.set_xlabel(axis_label_list[0])
        ax2.set_ylabel(axis_label_list[1])

        if 'save_fig' in Option_Dictionary:
            File_Functions.Save_Figure(file_name, "Parameter_Space_Plot_Close")
        else:
            py.show()


def Correlation_Sum(file_name, Option_Dictionary={}, verbose=False):
    """ Plots the correlation sum of the input file """

    (time, omega_dot, a_dot, phi_dot) = Dotted_Variable(file_name)
    N = len(time)

    # If required reduce the data size
    if "ith" in Option_Dictionary:
        ith = int(Option_Dictionary['ith'])
        time = time[0:N:ith]
        omega_dot = omega_dot[0:N:ith]
        a_dot = a_dot[0:N:ith]
        phi_dot = phi_dot[0:N:ith]
        N = len(time)  # length of data after reduction

    # Second and third options arguments specify the natural exponents
    # with which R the sphere radius should vary
    try:
        R_min = float(Option_Dictionary['R_min'])
        R_max = float(Option_Dictionary['R_max'])
        Number = int(Option_Dictionary['Number'])
    except KeyError:
        print ("You must specify R_min,R_max "
               " and Number in the Option_Dictionary")
        return

    R_list = py.logspace(R_min, R_max, Number)

    def abs_val(x1, y1, z1, x2, y2, z2):
        return py.sqrt((x1 - x2) ** 2.0 + (y1 - y2) ** 2.0 + (z1 - z2) ** 2.0)

    # Calculate C(R) for each R and record natural log of both.
    lnC_list = []
    lnR_list = []
    lnC_outsiders_list = []
    lnR_outsiders_list = []

    for R in R_list:
        sumV = 0.0
        for i in range(N):
            for j in range(i + 1, N):
                if R > abs_val(omega_dot[i], a_dot[i], phi_dot[i],
                               omega_dot[j], a_dot[j], phi_dot[j]):
                    sumV += 1.0
        # Check there is a satisfactory number of points in the sum

        if sumV == 0.0:
            print ("No points in R={0} consider a larger R_min."
                  "Ignoring this point".format(R))
        else:
            C = 2.0 * sumV / (float(N) * (float(N) - 1.0))

            # Test lower bound
            if C < 10.0 / float(N):
                print ("Only {0} points in R={1}  consider a larger Rmin."
                       " This data will not be used in calculating"
                       " the best fit".format(sumV, R))

                # Add outsider to seperate lists
                lnC_outsiders_list.append(py.log(C))
                lnR_outsiders_list.append(py.log(R))

            # Test upper bound
            elif C > 0.1:
                print ("More than 10 percent of all points in the test sphere "
                       "of radius {}, this data will not be used "
                       "in calculating"" the best fit".format(R))

                lnC_outsiders_list.append(py.log(C))
                lnR_outsiders_list.append(py.log(R))

            # Add data to list
            else:
                lnC_list.append(py.log(C))
                lnR_list.append(py.log(R))
                # Print some data for the user
                if verbose:
                    print ("Point added R ={} ln(R)={} C ={} ln(C)={} "
                    " Sum_total = {}".format(R, py.log(R), C, py.log(C), sumV))
    # Linear fit
    (x_fit, y_fit, f_p) = Useful_Tools.Fit_Function(lnR_list, lnC_list, 1)

    # Plot
    fig = py.figure()
    ax = fig.add_subplot(111)
    ax.plot(x_fit, y_fit,
            color="b", label=("$\ln(c)={0} \ln(R)={1}$"
                        .format(str(round(f_p[0], 2)), str(round(f_p[1], 2)))))
    ax.plot(lnR_list, lnC_list,
            "o", color="r", label="Data used in fit")
    ax.plot(lnR_outsiders_list, lnC_outsiders_list,
            "x", color="r", label="Data not used in fit")

    # Give upper and lower bounds on C(R)
    ax.axhline(py.log(0.1), ls="--", color="k", alpha=0.6)
    ax.axhline(py.log(10.0 / float(N)),
        ls="--", color="k", label="Bounds on $\ln(C(R))$", alpha=0.6)

    leg = py.legend(loc=2, fancybox=True)
    leg.get_frame().set_alpha(0.6)
    ax.set_ylabel(r"$\ln(C)$")
    ax.set_xlabel(r"$\ln(R)$")

    #py.title(r"Correlation plot for $\chi = $"+file_name.split("_")[4])

    if 'save_fig' in Option_Dictionary:
        File_Functions.Save_Figure(file_name, "Correlation_Plot")
    else:
        py.show()


# Theiler window
def Correlation_Sum_W(file_name, Option_Dictionary={}, verbose=False):
    """ Plots the correlation sum of the input file """

    (time, omega_dot, a_dot, phi_dot) = Dotted_Variable(file_name)
    N = len(time)
    w = 100  # Theiler window number

    # If required reduce the data size
    if "ith" in Option_Dictionary:
        ith = int(Option_Dictionary['ith'])
        time = time[0:N:ith]
        omega_dot = omega_dot[0:N:ith]
        a_dot = a_dot[0:N:ith]
        phi_dot = phi_dot[0:N:ith]
        N = len(time)  # length of data after reduction

    # Second and third options arguments specify the natural exponents
    # with which R the sphere radius should vary
    try:
        R_min = float(Option_Dictionary['R_min'])
        R_max = float(Option_Dictionary['R_max'])
        Number = int(Option_Dictionary['Number'])
    except KeyError:
        print ("You must specify R_min,R_max "
               " and Number in the Option_Dictionary")
        return

    R_list = py.logspace(R_min, R_max, Number)

    def abs_val(x1, y1, z1, x2, y2, z2):
        return py.sqrt((x1 - x2) ** 2.0 + (y1 - y2) ** 2.0 + (z1 - z2) ** 2.0)

    # Calculate C(R) for each R and record natural log of both.
    lnC_list = []
    lnR_list = []
    lnC_outsiders_list = []
    lnR_outsiders_list = []

    for R in R_list:
        sumV = 0.0
        for i in range(N):
            for j in range(i + 1 + w, N):
                if R > abs_val(omega_dot[i], a_dot[i], phi_dot[i],
                               omega_dot[j], a_dot[j], phi_dot[j]):
                    sumV += 1.0
        # Check there is a satisfactory number of points in the sum

        if sumV == 0.0:
            print ("No points in R={0} consider a larger R_min."
                  "Ignoring this point".format(R))
        else:
            C = 2.0 * sumV / ((float(N) - w) * (float(N) - w - 1.0))

            # Test lower bound
            if C < 10.0 / float(N):
                print ("Only {0} points in R={1}  consider a larger Rmin."
                       " This data will not be used in calculating"
                       " the best fit".format(sumV, R))

                # Add outsider to seperate lists
                lnC_outsiders_list.append(py.log(C))
                lnR_outsiders_list.append(py.log(R))

            # Test upper bound
            elif C > 0.1:
                print ("More than 10 percent of all points in the test sphere "
                       "of radius {}, this data will not be used "
                       "in calculating"" the best fit".format(R))

                lnC_outsiders_list.append(py.log(C))
                lnR_outsiders_list.append(py.log(R))

            # Add data to list
            else:
                lnC_list.append(py.log(C))
                lnR_list.append(py.log(R))
                # Print some data for the user
                if verbose:
                    print ("Point added R ={} ln(R)={} C ={} ln(C)={} "
                    " Sum_total = {}".format(R, py.log(R), C, py.log(C), sumV))
    # Linear fit
    (x_fit, y_fit, f_p) = Useful_Tools.Fit_Function(lnR_list, lnC_list, 1)

    # Plot
    fig = py.figure()
    ax = fig.add_subplot(111)
    ax.plot(x_fit, y_fit,
            color="b", label=("$\ln(c)={0} \ln(R)={1}$"
                        .format(str(round(f_p[0], 2)), str(round(f_p[1], 2)))))
    ax.plot(lnR_list, lnC_list,
            "o", color="r", label="Data used in fit")
    ax.plot(lnR_outsiders_list, lnC_outsiders_list,
            "x", color="r", label="Data not used in fit")

    # Give upper and lower bounds on C(R)
    ax.axhline(py.log(0.1), ls="--", color="k", alpha=0.6)
    ax.axhline(py.log(10.0 / float(N)),
        ls="--", color="k", label="Bounds on $\ln(C(R))$", alpha=0.6)

    leg = py.legend(loc=2, fancybox=True)
    leg.get_frame().set_alpha(0.6)
    ax.set_ylabel(r"$\ln(C)$")
    ax.set_xlabel(r"$\ln(R)$")

    #py.title(r"Correlation plot for $\chi = $"+file_name.split("_")[4])

    if 'save_fig' in Option_Dictionary:
        File_Functions.Save_Figure(file_name, "Correlation_Plot")
    else:
        py.show()


def Dotted_Variable(file_name):
    """

    Function takes the file imports it and produces
    the dotted variables as lists

    """

    (time, x, y, z) = File_Functions.One_Component_Import(file_name)

    # Transform to spherical polar coordinates in radians
    (omega, a, phi) = Physics_Functions.Cartesian_2_Spherical(
                                    x, y, z, Angle_Type="Radians")

    # Fix phi
    phi = Physics_Functions.Fix_Phi(phi, Angle_Type="Radians")

    # Import data from params
    Parameter_Dictionary = File_Functions.Parameter_Dictionary(file_name)
    epsI = float(Parameter_Dictionary["epsI"])
    epsA = float(Parameter_Dictionary["epsA"])
    # Careful with chi
    chi = float(Parameter_Dictionary["chi"])  #* py.pi / 180  # radians

    # Calculate some constants
    epsI_prime = epsI / (1 + epsI)
    Sx = sin(chi)
    Cx = cos(chi)
    Lambda = 2 * 1e6 / (3 * 3e10)  # 2R/3c

    # Calculate the differentials from Goldreich equations
    omega_dot = []
    a_dot = []
    phi_dot = []

    for i in xrange(len(omega)):
        cosa = cos(a[i])
        sina = sin(a[i])
        cosphi = cos(phi[i])
        sinphi = sin(phi[i])
        Tsx = Cx * Sx * cosa - Cx * Cx * sina * cosphi
        Tsy = -1.0 * sina * sinphi
        Tsz = Sx * Cx * sina * cosphi - Sx * Sx * cosa

        pre = (Sx * sina * cosphi + Cx * cosa)
        Tax = pre * sina * sinphi * Cx
        Tay = pre * (cosa * Sx - sina * cosphi * Cx)
        Taz = pre * (-1.0 * sina * sinphi * Sx)

        Tsdotomega = (2 * Sx * Cx * sina * cosa * cosphi - pow(sina * sinphi, 2)
                               - pow(Sx * cosa, 2) - pow(Cx * sina * cosphi, 2))

        omega_dot.append(Lambda * epsA * pow(omega[i], 3) *
                         (Tsdotomega - epsI_prime * Tsz * cosa)
                         - epsA * epsI_prime * pow(omega[i], 2) * Taz * cosa)

        a_dot.append(Lambda * epsA * pow(omega[i], 2) * pow(sina, -1)
                * (Tsdotomega * cosa - (1 - epsI_prime * pow(sina, 2)) * Tsz)
                - epsA * omega[i] * Taz *
                (1 - epsI_prime * pow(sina, 2)) * pow(sina, -1)
                )

        phi_dot.append(pow(omega[i], 2) * Lambda * epsA * pow(sina, -1)
                * (Tsy * cosphi - Tsx * sinphi)
                + omega[i] * epsA * pow(sina, -1)
                * (Tay * cosphi - Tax * sinphi)
                )

    return (time, omega_dot, a_dot, phi_dot)


def Dotted_Variable_Triaxial_Cartesian(file_name):
    """

    Function takes the file imports it and produces
    the dotted variables as lists

    """

    (time, x, y, z) = File_Functions.One_Component_Import(file_name)

    # Transform to spherical polar coordinates in radians
    #(omega, a, phi) = Physics_Functions.Cartesian_2_Spherical(
     #                               x, y, z, Angle_Type="Radians")

    # Fix phi
    #phi = Physics_Functions.Fix_Phi(phi, Angle_Type="Radians")

    # Import data from params
    Parameter_Dictionary = File_Functions.Parameter_Dictionary(file_name)
    epsI1 = float(Parameter_Dictionary["epsI1"])
    epsI3 = float(Parameter_Dictionary["epsI3"])
    epsA = float(Parameter_Dictionary["epsA"])
    chi = float(Parameter_Dictionary["chi"]) * py.pi / 180  # radians

    # Calculate some constants
    Sx = sin(chi)
    Cx = cos(chi)
    Lambda = 2 * 1e6 / (3 * 3e10)  # 2R/3c

    # Calculate the differentials from Goldreich equations
    w1_dot = []
    w2_dot = []
    w3_dot = []

    for i in xrange(len(time)):
        wx = x[i]
        wy = y[i]
        wz = z[i]
        w_2 = pow(wx, 2) + pow(wy, 2) + pow(wz, 2)

        w1_d = (epsA * (Lambda * w_2 * Cx * (wz * Sx - wx * Cx))
                * pow(1 + epsI1, -1) - wy * wz * epsI3 * pow(1 + epsI1, -1))

        w2_d = epsA * (- Lambda * w_2 * wy) - wx * wz * (epsI1 - epsI3)

        w3_d = (epsA * pow(1 + epsI3, -1) *
                (Lambda * w_2 * Sx * (wx * Cx - wz * Sx))
                + wx * wy * epsI1 * pow(1 + epsI3, -1))

        w1_dot.append(w1_d)

        w2_dot.append(w2_d)

        w3_dot.append(w3_d)

    return (time, w1_dot, w2_dot, w3_dot)


def Torque_over_Io(omega, epsA, chi, anom_torque=True, c=3e10, R=1e6):
    """ Returns the Goldreich torque for omega=[w1,w2,w3]"""

    # Check that chi is coming in radians
    if chi > 2 * py.pi:
        print " Check that chi is imported as radians and not degrees"

    m = [sin(chi), 0.0, cos(chi)]
    omega_squared = sum(pow(w, 2) for w in omega)

    T1 = (2 * R * pow(3 * c, -1) * epsA * omega_squared *
                        py.cross(py.cross(omega, m), m))

    T2 = epsA * py.dot(omega, m) * py.cross(omega, m)

    if anom_torque:
        return T1 + T2
    else:
        return T1


def Dotted_Variable_Triaxial(file_name, anom_torque=False):
    """

    Function takes the file, imports it and produces omega in the assuming
    a triaxial moment of inertia tensor

    """

    (time, x, y, z) = File_Functions.One_Component_Import(file_name)

    # Import data from params
    Parameter_Dictionary = File_Functions.Parameter_Dictionary(file_name)
    epsI1 = float(Parameter_Dictionary["epsI1"])
    epsI3 = float(Parameter_Dictionary["epsI3"])
    epsA = float(Parameter_Dictionary["epsA"])
    chi = float(Parameter_Dictionary["chi"]) * py.pi / 180.0

    # Calculate the differentials from Goldreich equations
    omega_dot = []

    # Note that the torque is T/Io in all of the following
    for i in xrange(len(time)):
        omega_vec = [x[i], y[i], z[i]]
        T = Torque_over_Io(omega_vec, epsA, chi, anom_torque=anom_torque)
        a = py.dot(T, omega_vec)
        b = epsI1 * omega_vec[0] * T[0] * pow(1 + epsI1, -1)
        c = epsI3 * omega_vec[2] * T[2] * pow(1 + epsI3, -1)
        d = (omega_vec[0] * omega_vec[1] * omega_vec[2] *
                                            (epsI1 * epsI3 * (epsI3 - epsI1)
                                           / ((1 + epsI1) * (1 + epsI3))))
        omega_dot.append(pow(py.norm(omega_vec), -1) * (
                             a - b - c + d))

    return (time, omega_dot)


def Embed(time, x, n, d):
    """

    Takes 1d signal x and produces a d-dimensional embedding calculating
    the delay integer to be

    the first minimum in something

    the root of something else

    """

    # Calculate the time delay
    # Subtract time average of the series
    xo = x - py.mean(x)

    # dt is fixed by x intervales, looks at n multiples
    ro = []
    var = (py.var(xo))
    for i in xrange(n):
        p = [xo[j] * xo[j + i] for j in xrange(len(xo) - i)]
        ro.append(py.mean(p) / var)

    # Find first minimum
    for i in xrange(1, n):
        if ro[i] > ro[i - 1]:
            delay_index = i - 1
            break

    ax1 = py.subplot(121)
    one_dt = time[1] - time[0]  # Assume linear spacing
    dt = py.linspace(0, n * one_dt, n)
    ax1.axvline(dt[delay_index], label="\tau")
    ax1.plot(dt, ro)
    ax1.set_xlabel(r"$\Delta t$")
    ax1.set_ylabel(r"$\rho $")

    ax2 = py.subplot(122, projection="3d")
    x_0 = x[0: - 2 * delay_index]
    x_1 = x[delay_index:-delay_index]
    x_2 = x[2 * delay_index:]
    ax2.plot(x_0, x_1, x_2)
    ax2.set_xlabel(r"$x(t)$")
    ax2.set_ylabel(r"$x(t+\tau)$")
    ax2.set_zlabel(r"$x(t+2\tau)$")
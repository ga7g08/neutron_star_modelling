#!/usr/bin/python

import numpy as np
import os
import one_component_model
import nsmod_two_component_model
import nsmod_two_component_model2
import nsmod_one_component_model_with_Euler
import pynotify
from File_Functions import vprint
import File_Functions


def Run(AnomTorque=True, chi0=None, epsI1=0.0, epsI3=None, epsA=None,
        omega0=None, T=1e12, error=1e-12, n=1000, eta=0.0, verbose=True,
        a0=50.0):
    """

    Run a simulation of the one component model

    :param epsI1: Value of the deformation to the moment of inertia along the
                 1 - axis e.g :math:`I_{xx} = I_{0}(1+\epsilon_{I1})`
    :type epsI1: float
    :param epsI3: Value of the deformation to the moment of inertia along the
                 3 - axis e.g :math:`I_{zz} = I_{0}(1+\epsilon_{I3})`
    :type epsI3: float
    :param epsA: Magnetic deformation
    :type epsA: float
    :param omega0: Initial rotational speed in :math:`Hz/rad`
    :type omega0: float
    :param t1: End time of simulation, if eta is defined then the simulation
               will halt once either eta is satisfied or at t1
    :type t1: float
    :param n: Number of points to save, superseeds eta parameter
    :type n: int
    :param eta: A small value for which the simulation will stop EDIT
    :type eta: float

    :returns: file name of a .hdf5 file containing the saved data
    """

    file_name = one_component_model.main(
                      chi0=chi0,
                      n=n,
                      epsA=epsA,
                      epsI1=epsI1,
                      epsI3=epsI3,
                      omega0=omega0,
                      T=T,
                      eta=eta,
                      AnomTorque=AnomTorque,
                      a0=a0,
                      error=float(error),
                      )

    return file_name

#def Run(Input_Dictionary):
    #"""

    #Run a simulation of the one component model using the paramaters
    #defined in Input_Dictionary

    #A typical Input_Dictionary:
    #pulsar = {'epsI':'1.0e-9', 'epsA':"5.0e-11", 'omega0':"1.0e4",
    #'eta':"1.0e-4", 'error':"1e-14"}

    #:param epsI: Value of the deformation to the moment of inertia along the
                 #3 - axis e.g :math:`I_{zz} = I_{0}(1+\epsilon_{I})`
    #:type epsI: float
    #:param epsA: Magnetic deformation defined by
    #:type epsA: float
    #:param omega0: Initial rotational speed in :math:`Hz/rad`
    #:type omega0: float
    #:param t1: End time of simulation, if eta is defined then the simulation
               #will halt once either eta is satisfied or at t1
    #:type t1: float
    #:param n: Number of points to save, superseeds eta parameter
    #:type n: int
    #:param eta: A small value for which the simulation will stop EDIT
    #:type eta: float

    #:returns: file name of a .hdf5 file containing the saved data
    #"""

    ##  Required paramaters

    #file_name_list = []

    ## Errors may come out of this..
    #if 'AnomTorque' in Input_Dictionary:
        #AnomTorque = Input_Dictionary['AnomTorque']
        #if Input_Dictionary['AnomTorque'] is False:
            #file_name_list .append("no_anom_")
    #else:
        #AnomTorque = True

    #if Input_Dictionary.get('no_anom'):
        #print ("no_anom in Input_Dictionary is no longer supported, please"
              #" use AnomTorque instead")

    #try:
        #chi0_degrees = Input_Dictionary['chi0']
        #file_name_list.append("chi0_" + str(Input_Dictionary['chi0']))
    #except KeyError:
        #print " ERROR: You need to specify chi0 in the input dictionary"
        #return

    ## Triaxial test
    #try:
        #epsI1 = str(Input_Dictionary['epsI1'])
        #epsI3 = str(Input_Dictionary['epsI3'])
        #file_name_list.append("_epsI1_{}".format(Input_Dictionary['epsI1']))
        #file_name_list.append("_epsI3_{}".format(Input_Dictionary['epsI3']))
    #except KeyError:
        ## If not trixial test for biaxial
        #try:
            #epsI1 = "0"
            #epsI3 = str(Input_Dictionary['epsI'])
            #file_name_list.append("_epsI_{}".format(Input_Dictionary['epsI']))
        #except KeyError:
            #print (" ERROR: You need to specify epsI1 and epsI2,"
                  #" or epsI (Biaxial case) in the input dictionary")
            #return

    #try:
        #epsA = str(Input_Dictionary['epsA'])
        #file_name_list.append("_epsA_" + str(Input_Dictionary['epsA']))
    #except KeyError:
        #print " ERROR: You need to specify epsA in the input dictionary"
        #return

    #try:
        #omega0 = str(Input_Dictionary['omega0'])
        #file_name_list.append("_omega0_" + str(Input_Dictionary['omega0']))
    #except KeyError:
        #print " ERROR: You need to specify omega0 in the input dictionary"
        #return

    #try:
        #eta = str(Input_Dictionary['eta'])
        #file_name_list.append("_eta_" + str(Input_Dictionary['eta']))
        #eta_relative = str(float(eta) * pow(float(omega0), 2))
    #except KeyError:
        #eta = 0.0

    #try:
        #t1 = str(Input_Dictionary['t1'])
        #file_name_list.append("_t1_" + str(Input_Dictionary['t1']))
    #except KeyError:
        #print "ERROR: t1 not specified using a default "
        #t1 = 1e12

##   Additional Arguments
    #try:
        #error = str(Input_Dictionary['error'])
    #except KeyError:
        ## Use a default value
        #error = 1e-12

    #try:
        #n = int(Input_Dictionary['n'])
    #except KeyError:
        ## Don't save at n discrete intervals...
        #n = None

    ## Create file name
    #file_name_list.append(".hdf5")
    #file_name = "".join(file_name_list)

    ## Tempory hack to remove old files seems to cause issues
    #if file_name in os.listdir("."):
        #os.remove(file_name)

    #nsmod_one_component_model.main(
                      #chi0_degrees=float(chi0_degrees),
                      #file_name=file_name,
                      #n=n,
                      #epsA=float(epsA),
                      #epsI1=float(epsI1),
                      #epsI3=float(epsI3),
                      #omega0=float(omega0),
                      #t1=float(t1),
                      #eta=float(eta),
                      #AnomTorque=AnomTorque,
                      #error=float(error)
                      #)


        ##pynotify.init("Basic")
    ##
        ##n = pynotify.Notification("Run 1CM complete",
          ##"output saved as {}".format(file_name)
        ##)
    ##
        ##n.show()
    #return file_name


def Run_Cython_Two_Component(Input_Dictionary):
    """ Function to run the two component model.

    Keyword arguments must be passed as a dictionary
    chi0:float [degrees] -- angle between magnetic dipole and z axis
    epsI:float []-- elastic deformation
    epsA :float []-- magnetic deformation
    omega0 :float [Hz]-- initial spin period
    t1:float [s] -- Time for which to run simulation for
    eta: float
    K:float -- Coupling constant between the two components
    Ishell:MOI of the biaxial crust
    Icore:MOI of the spherical core

    Optional arguments
    err : float[] -- Error argument to pass to the GCC compiler

    For help with the GCC compiler see documentation at
    http://www.gnu.org/software/gsl/manual/html_node/
    Ordinary-Differential-Equations.html
    """

    #  Required paramaters

    # Initiate the file_name list
    file_name_list = []

    # Check the AnomTorque condition
    if Input_Dictionary.get('no_anom'):
        file_name_list .append("no_anom_")
        AnomTorque = False
    else:
        AnomTorque = True

    # At the moment these errors do not raise correctly.

    try:
        chi0_degrees = Input_Dictionary['chi0']
        file_name_list.append("chi0_" + str(Input_Dictionary['chi0']))
    except KeyError:
        print " ERROR: You need to specify chi0 in the input dictionary"
        return

    try:
        epsI = str(Input_Dictionary['epsI'])
        file_name_list.append("_epsI_" + str(Input_Dictionary['epsI']))
    except KeyError:
        print " ERROR: You need to specify epsI in the input dictionary"
        return

    try:
        epsA = str(Input_Dictionary['epsA'])
        file_name_list.append("_epsA_" + str(Input_Dictionary['epsA']))
    except KeyError:
        print " ERROR: You need to specify epsA in the input dictionary"
        return

    try:
        omega0 = str(Input_Dictionary['omega0'])
        file_name_list.append("_omega0_" + str(Input_Dictionary['omega0']))
    except KeyError:
        print " ERROR: You need to specify omega0 in the input dictionary"
        return

    try:
        t1 = str(Input_Dictionary['t1'])
        file_name_list.append("_t1_" + str(Input_Dictionary['t1']))
    except KeyError:
        t1 = "1e15"
        print "ERROR: You have not yet specified t1, \
                using default value t1 = {}".format(t1)

    try:
        eta = str(Input_Dictionary['eta'])
        file_name_list.append("_eta_" + str(Input_Dictionary['eta']))
        eta_relative = str(float(eta) * pow(float(omega0), 2))
    except KeyError:
        eta = "0.0"
        print "ERROR: You have not yet specified eta, \
         using default values  eta ={}".format(eta)

    try:
        K = str(Input_Dictionary['K'])
        file_name_list.append("_K_" + str(Input_Dictionary['K']))
    except KeyError:
        print "ERROR: You must specify K"
        return

    try:
        Ishell = str(Input_Dictionary['Ishell'])
        file_name_list.append("_Ishell_" + str(Input_Dictionary['Ishell']))
    except KeyError:
        Ishell = 1e45
        print "ERROR: Ishell not specified \
            using default Ishell={}".format(Ishell)

    try:
        Icore = str(Input_Dictionary['Icore'])
        file_name_list.append("_Icore_" + str(Input_Dictionary['Icore']))
    except KeyError:
        Icore = 1e45
        print "ERROR: Icore not specified using default Icore={}".format(Icore)

    try:
        aw_int = str(Input_Dictionary['aw_int'])
        file_name_list.append("_aw_int_" + str(Input_Dictionary['aw_int']))
    except KeyError:
        aw_int = "50.0"
        print ("ERROR: aw_int not specified"
              " using default aw_int={}".format(aw_int))

    try:
        aW_int = str(Input_Dictionary['aW_int'])
        file_name_list.append("_aW_int_" + str(Input_Dictionary['aW_int']))
    except KeyError:
        aW_int = "50.0"
        print ("ERROR: aW_int not specified"
              " using default aW_int={}".format(aw_int))

#   Additional Arguments
    try:
        error = str(Input_Dictionary['error'])
    except KeyError:
        # Use a default value
        error = 1e-5

    try:
        n = int(Input_Dictionary['n'])
        #if "_t1_" not in file_name_list:
            #print "Warning: Specifying n
            #without t1 means you may get a very course save "
    except KeyError:
        # Don't save at n discrete intervals...
        n = None

    # Create file name
    file_name_list.append(".hdf5")
    file_name = "".join(file_name_list)

    # Tempory hack to remove old files seems to cause issues
    if file_name in os.listdir("."):
        os.remove(file_name)

    nsmod_two_component_model.main(
        chi0_degrees=float(chi0_degrees),
        file_name=file_name,
        epsA=float(epsA),
        epsI=float(epsI),
        n=n,
        omega0=float(omega0),
        t1=float(t1),
        AnomTorque=AnomTorque,
        error=float(error),
        Ishell=float(Ishell),
        Icore=float(Icore),
        K=float(K),
        aw_int=float(aw_int),
        aW_int=float(aW_int)
        )

    pynotify.init("Basic")

    n = pynotify.Notification("Run 2CM complete",
      "output saved as {}".format(file_name)
    )

    n.show()
    return file_name


def Run_Cython_Two_Component2(Input_Dictionary):
    """ Function to run the two component model.

    Keyword arguments must be passed as a dictionary
    chi0:float [degrees] -- angle between magnetic dipole and z axis
    epsI:float []-- elastic deformation
    epsA :float []-- magnetic deformation
    omega0 :float [Hz]-- initial spin period
    t1:float [s] -- Time for which to run simulation for
    eta: float
    K:float -- Coupling constant between the two components
    Ishell:MOI of the biaxial crust
    Icore:MOI of the spherical core

    Optional arguments
    err : float[] -- Error argument to pass to the GCC compiler

    For help with the GCC compiler see documentation at
    http://www.gnu.org/software/gsl/manual/html_node/
    Ordinary-Differential-Equations.html
    """

    #  Required paramaters

    # Initiate the file_name list
    file_name_list = []

    # Check the AnomTorque condition
    if Input_Dictionary.get('no_anom'):
        file_name_list .append("no_anom_")
        AnomTorque = False
    else:
        AnomTorque = True

    # At the moment these errors do not raise correctly.

    try:
        chi0_degrees = Input_Dictionary['chi0']
        file_name_list.append("chi0_" + str(Input_Dictionary['chi0']))
    except KeyError:
        print " ERROR: You need to specify chi0 in the input dictionary"
        return

    try:
        epsI = str(Input_Dictionary['epsI'])
        file_name_list.append("_epsI_" + str(Input_Dictionary['epsI']))
    except KeyError:
        print " ERROR: You need to specify epsI in the input dictionary"
        return

    try:
        epsA = str(Input_Dictionary['epsA'])
        file_name_list.append("_epsA_" + str(Input_Dictionary['epsA']))
    except KeyError:
        print " ERROR: You need to specify epsA in the input dictionary"
        return

    try:
        t1 = str(Input_Dictionary['t1'])
        file_name_list.append("_t1_" + str(Input_Dictionary['t1']))
    except KeyError:
        t1 = "1e15"
        print "ERROR: You have not yet specified t1, \
                using default value t1 = {}".format(t1)

    try:
        K = str(Input_Dictionary['K'])
        file_name_list.append("_K_" + str(Input_Dictionary['K']))
    except KeyError:
        print "ERROR: You must specify K"
        return

    try:
        Ishell = str(Input_Dictionary['Ishell'])
        file_name_list.append("_Ishell_" + str(Input_Dictionary['Ishell']))
    except KeyError:
        Ishell = 1e45
        print "ERROR: Ishell not specified \
            using default Ishell={}".format(Ishell)

    try:
        Icore = str(Input_Dictionary['Icore'])
        file_name_list.append("_Icore_" + str(Input_Dictionary['Icore']))
    except KeyError:
        Icore = 1e45
        print "ERROR: Icore not specified using default Icore={}".format(Icore)

    # Ugly hack
    core_int_str = Input_Dictionary['core_int']
    core_int = [float(p) for p in
        core_int_str.lstrip("[").rstrip("]").split(",")]

    shell_int_str = Input_Dictionary['shell_int']
    shell_int = [float(p) for p in
        shell_int_str.lstrip("[").rstrip("]").split(",")]

#   Additional Arguments
    try:
        error = str(Input_Dictionary['error'])
    except KeyError:
        # Use a default value
        error = 1e-5

    try:
        n = int(Input_Dictionary['n'])
        #if "_t1_" not in file_name_list:
            #print "Warning: Specifying n
            #without t1 means you may get a very course save "
    except KeyError:
        # Don't save at n discrete intervals...
        n = None

    # Create file name
    file_name_list.append(".hdf5")
    file_name = "".join(file_name_list)

    # Tempory hack to remove old files seems to cause issues
    if file_name in os.listdir("."):
        os.remove(file_name)

    nsmod_two_component_model2.main(
        chi0_degrees=float(chi0_degrees),
        file_name=file_name,
        epsA=float(epsA),
        epsI=float(epsI),
        n=n,
        t1=float(t1),
        error=float(error),
        Ishell=float(Ishell),
        Icore=float(Icore),
        K=float(K),
        core_int=core_int,
        shell_int=shell_int
        )

    pynotify.init("Basic")

    n = pynotify.Notification("Run 2CM complete",
      "output saved as {}".format(file_name)
    )

    n.show()
    return file_name



def Run_with_Euler(AnomTorque=True, chi0=None, epsI1=0.0, epsI3=None, epsA=None,
        omega0=None, t1=1e12, error=1e-12, n=1000, verbose=True, a_int=5.0,
        overwrite=False
        ):
    """
    Run a simulation of the one component model solving both the body frame equations 
    and the Euler angle equations

    :param AnomTorque: If true will include the anomalous part of the torque equations
    :type AnomTorque: bool
    :param chi0: Angle in degrees made by the magenetic dipole with the body frame z axis
    :type chi0: float
    :param epsI1: Value of the deformation to the moment of inertia along the
                 1 - axis e.g :math:`I_{xx} = I_{0}(1+\epsilon_{I1})`
    :type epsI1: float
    :param epsI3: Value of the deformation to the moment of inertia along the
                 3 - axis e.g :math:`I_{zz} = I_{0}(1+\epsilon_{I3})`
    :type epsI3: float
    :param epsA: Magnetic deformation
    :type epsA: float
    :param omega0: Initial rotational speed in :math:`Hz/rad`
    :type omega0: float
    :param t1: End time of simulation, if eta is defined then the simulation
               will halt once either eta is satisfied or at t1
    :type t1: float
    :param n: Number of points to save 
    :type n: int
    :a_int: Initial polar angle of the spin vector
    :a_int: float

    :param overwrite: If true it will overwrite files with the same name
    :typw overwrite: bool

    :returns: file name of a .hdf5 file containing the saved data
    """

    file_name_list = []

    if AnomTorque is False:
        file_name_list .append("no_anom_")

    if type(chi0) in [float, int, np.float32, np.float64]:
        file_name_list.append("chi0_{:.1f}".format(chi0))
    elif type(chi0) is str:
        file_name_list.append("chi0_{}".format(chi0))
        chi0 = float(chi0)
    else:
        print (" ERROR: You need to specify chi0 in degrees")
        return

    if type(epsI1) in [float, int, np.float32, np.float64]:
        file_name_list.append("_epsI1_{:.2e}".format(epsI1))
    elif type(epsI1) is str:
        file_name_list.append("_epsI1_{}".format(epsI1))
        epsI1 = float(epsI1)
    else:
        print (" ERROR: You need to specify epsI1")
        return

    if type(epsI3) in [float, int, np.float32, np.float64]:
        file_name_list.append("_epsI3_{:.2e}".format(epsI3))
    elif type(epsI3) is str:
        file_name_list.append("_epsI3_{}".format(epsI3))
        epsI3 = float(epsI3)
    else:
        print (" ERROR: You need to specify epsI3")
        return

    if type(epsA) in [float, int, np.float32, np.float64]:
        file_name_list.append("_epsA_{:.2e}".format(epsA))
    elif type(epsA) is str:
        file_name_list.append("_epsA_{}".format(epsA))
        epsA = float(epsA)
    else:
        print (" ERROR: You need to specify epsA")
        return
    
    if type(omega0) in [float, int, np.float32, np.float64]:
        file_name_list.append("_omega0_{:.2f}".format(omega0))
    elif type(omega0) is str:
        file_name_list.append("_omega0_{}".format(omega0))
        omega0 = float(omega0)
    else:
        print (" ERROR: You need to specify omega0")
        return

    if a_int != 50.0:
        file_name_list.append("_aint_{}".format(a_int))
        a_int = float(a_int)

    if type(t1) in [float, int, np.float32, np.float64]:
        file_name_list.append("_t1_{:.2e}".format(t1))
    elif type(t1) is str:
        file_name_list.append("_t1_{}".format(t1))
        t1 = float(t1)
    else:
        print (" ERROR: t1 must be a float, int or string")
        return

    # Create file name
    file_name_list.append(".hdf5")
    file_name = "".join(file_name_list)

    # Check if file already exists
    if file_name in os.listdir("."):
        if overwrite:
            os.remove(file_name)
        else:
            vprint(True, "overwrite=False, therefore I will not delete this file")
            return file_name


    nsmod_one_component_model_with_Euler.main(
      chi0=chi0,
      file_name=file_name,
      n=int(n),
      epsA=epsA,
      epsI1=epsI1,
      epsI3=epsI3,
      omega0=omega0,
      t1=t1,
      AnomTorque=AnomTorque,
      error=float(error),
      a_int=a_int
      )

    return file_name

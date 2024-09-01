# -*- coding: mbcs -*-
# Do not delete the following import lines
from odbAccess import *
from abaqus import *
from abaqusConstants import *
from caeModules import *
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
from driverUtils import executeOnCaeStartup
import regionToolset
import csv
import os
from material import createMaterialFromDataString
import time
import traceback

import part
import assembly
import csv
import numpy as np

cliCommand(
        """session.journalOptions.setValues(replayGeometry=INDEX,recoverGeometry=INDEX)""")

roi = ['17', '53']
disp = 'displacement_MLP_'
# disp = 'displacement_'

folder = 'D:/DATA/ADNI/sample_data'
log_file_path = "D:/DATA/ADNI/sample_data/error_log_step2.txt"

with open(log_file_path, "a") as log_file:
    for j in os.listdir(folder):
        subfolder_path = os.path.join(folder, j)
        if os.path.isdir(subfolder_path):
            for m in os.listdir(subfolder_path):
                for i in roi:
                    try:
                        file_name = 'aparc.a2009s+aseg'
                        part_name = file_name + '_' + i +'.igs'             # 'aparc.a2009s+aseg_53.igs'
                        mdb_name = 'aparca2009s+aseg_' + i                  # 'aparca2009s+aseg_53'          
                        mdb_name_instance = mdb_name + '-1'                 # 'aparca2009s+aseg_53-1'
                        cae_name = 'model_' + i + '.cae'                    # 'model_53.cae'
                        Job_name = 'Job-' + i                               # 'Job-53'
                        odb_name = 'Job-' + i + '.odb'                      # 'Job-53.odb'
                        disp_name = disp + i + '.txt'                       # 'displacement_53.txt'
                        output_file_name = 'abaqus_output_' + i + '.csv'    # 'abaqus_output_53.csv'
                        
                        path = '%s/%s/%s' % (folder, j, m)
                        part_location = '%s/%s/%s/%s' % (folder, j, m, part_name)
                        model_cae = '%s/%s/%s/%s' % (folder, j, m, cae_name)
                        File_Odb = '%s/%s/%s/%s' % (folder, j, m, odb_name)
                        File_disp = '%s/%s/%s/%s' % (folder, j, m, disp_name)
                        output_file = '%s/%s/%s/%s' % (folder, j, m, output_file_name)
                        # print(path)

                        if os.path.exists(output_file):
                            continue

                        if os.path.exists(part_location) == False:
                            # print(part_location, ' not exist')
                            continue

                        if os.path.exists(File_disp) == False:
                            print(File_disp)
                            print('displacement file does not exist')
                            print('--------------------------DONE--------------------------')
                            continue

                        import os
                        print('part_location:', part_location)
                        os.chdir(path)
                        mdb.openAuxMdb(pathName=model_cae)
                        mdb.copyAuxMdbModel(fromName='Model-1', toName='Model-1')
                        mdb.closeAuxMdb()
                        a = mdb.models['Model-1'].rootAssembly
                        session.viewports['Viewport: 1'].setValues(displayedObject=a)
                        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                                predefinedFields=ON, connectors=ON)
                        session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')

                        a = mdb.models['Model-1'].rootAssembly
                        c1 = a.instances[mdb_name_instance].cells
                        cells1 = c1[0:1]
                        region = a.Set(cells=cells1, name='Set-4')
                        mdb.models['Model-1'].Gravity(name='Load-1', createStepName='Step-1',
                                                    comp2=-9800.0, distributionType=UNIFORM, field='', region=region)
                        session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Initial')

                        a = mdb.models['Model-1'].rootAssembly
                        c1 = a.instances[mdb_name_instance].cells
                        cells1 = c1[0:1]
                        f1 = a.instances[mdb_name_instance].faces
                        faces1 = f1[0:]
                        e1 = a.instances[mdb_name_instance].edges
                        edges1 = e1[0:]
                        v1 = a.instances[mdb_name_instance].vertices
                        verts1 = v1[0:]
                        region = a.Set(vertices=verts1, edges=edges1, faces=faces1, cells=cells1,
                                    name='Set-5')
                        mdb.models['Model-1'].PorePressureBC(name='BC-1', createStepName='Initial',
                                                            region=region, distributionType=UNIFORM, fieldName='', magnitude=0.0)

                        a = mdb.models['Model-1'].rootAssembly
                        c1 = a.instances[mdb_name_instance].cells
                        cells1 = c1[0:1]
                        f1 = a.instances[mdb_name_instance].faces
                        faces1 = f1[0:]
                        e1 = a.instances[mdb_name_instance].edges
                        edges1 = e1[0:]
                        v1 = a.instances[mdb_name_instance].vertices
                        verts1 = v1[0:]
                        region = a.Set(vertices=verts1, edges=edges1, faces=faces1, cells=cells1,
                                    name='Set-6')
                        mdb.models['Model-1'].VoidsRatio(name='Predefined Field-1', region=region,
                                                        voidsRatio1=0.2, distributionType=UNIFORM, variation=CONSTANT_RATIO)
                        
                        #-----------------------displacement-----------------------
                        input1 = disp_name
                        input2 = 'Model-1'
                        input3 = 'aparca2009s+aseg_%s-1' % i
                        input4 = 'Step-1'

                        data = np.loadtxt(input1)
                        node = data[:, 0]
                        new_coeffs = []
                        def function(coeffs):    
                            coeffs = np.round(coeffs, 2)
                            for w in range(len(coeffs)):
                                if int(coeffs[w]) == coeffs[w]:
                                    new_coeffs.append(int(coeffs[w]))
                                else:
                                    new_coeffs.append(coeffs[w])
                        function(node)
                        X_U = data[:,1]
                        Y_u = data[:,2]
                        Z_u = data[:,3]
                        Rootassembly = mdb.models[input2].rootAssembly
                        n1 = Rootassembly.instances[input3].nodes
                        i = 0
                        for (x,X,Y,Z) in zip(new_coeffs,X_U,Y_u,Z_u):
                            d = x - 1
                            nodes1 = n1[d:x]
                            myRegion = regionToolset.Region(nodes = nodes1)
                            i = i + 1
                            title = 'BC-(%d)'%i
                            mdb.models[input2].DisplacementBC(name = title , createStepName= input4, 
                                region=myRegion, u1 = X, u2 = Y, u3 = Z, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
                                amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
                                localCsys=None)
                        print("displacement done")
                        

                        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                                predefinedFields=OFF, connectors=OFF)
                        mdb.Job(name=Job_name, model='Model-1', description='', type=ANALYSIS,
                                atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
                                memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                                scratch='', resultsFormat=ODB, numThreadsPerMpiProcess=1,
                                multiprocessingMode=DEFAULT, numCpus=7, numDomains=7, numGPUs=1)
                        mdb.jobs[Job_name].submit(consistencyChecking=OFF)
                        session.mdbData.summary()
                        mdb.jobs[Job_name].waitForCompletion()

                        o3 = session.openOdb(
                            name=File_Odb)
                        session.viewports['Viewport: 1'].setValues(displayedObject=o3)
                        session.viewports['Viewport: 1'].makeCurrent()
                        session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
                            variableLabel='LE', outputPosition=INTEGRATION_POINT, refinement=(
                                INVARIANT, 'Max. Principal'), )
                        session.viewports['Viewport: 1'].odbDisplay.display.setValues(
                            plotState=CONTOURS_ON_DEF)

                        odb = session.odbs[File_Odb]
                        nf = NumberFormat(numDigits=9, format=ENGINEERING)
                        session.fieldReportOptions.setValues(printLocalCSYS=ON,
                                                            reportFormat=COMMA_SEPARATED_VALUES, numberFormat=nf)
                        
                        session.writeFieldReport(fileName=output_file_name, append=OFF, step=0, frame=26,
                                                sortItem='Node Label', odb=odb, outputPosition=NODAL,
                                                variable=(('RF', NODAL), ('U', NODAL), ('LE', INTEGRATION_POINT), ('S',
                                                                                                                    INTEGRATION_POINT),
                                                        ('VOIDR', INTEGRATION_POINT),), stepFrame=SPECIFY)
                        
                        mdb.saveAs(pathName=model_cae)
                        mdb.save()
                        Mdb()
                        session.viewports['Viewport: 1'].setValues(displayedObject=None)

                        o7 = session.odbs[File_Odb]
                        session.viewports['Viewport: 1'].setValues(displayedObject=o7)
                        session.odbs[File_Odb].close()
                        session.mdbData.summary()
                        time.sleep(1)
                        print('--------------------------DONE--------------------------')

                    except Exception as e:

                        log_file.write("Error occurred while processing folder '%s' and file '%s':\n" % (j, m))
                        traceback.print_exc(file=log_file)
                        log_file.write("\n")

                        continue
                print('---------------------------------------------------DONE---------------------------------------------------')


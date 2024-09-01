# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
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
import os
import numpy as np
import traceback

print('---------------------------------------------------BEGIN---------------------------------------------------')

cliCommand(
    """session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)""")

roi = ['17', '53']

folder = 'D:/DATA/ADNI/sample data'
log_file_path = "D:/DATA/ADNI/sample data/error_log_step1.txt"

# Record the error details in the log file
with open(log_file_path, "a") as log_file:
    for j in os.listdir(folder):
        if not os.path.isdir(os.path.join(folder, j)):
            continue
        for m in os.listdir(os.path.join(folder, j)):
            for i in roi:
                try:
                    file_name = 'aparc.a2009s+aseg'
                    part_name = file_name + '_' + i +'.igs'     # 'aparc.a2009s+aseg_53.igs'
                    mdb_name = 'aparca2009s+aseg_' + i          # 'aparca2009s+aseg_53'          
                    mdb_name_instance = mdb_name + '-1'         # 'aparca2009s+aseg_53-1'
                    save_name = 'model_' + i + '.cae'           # 'model_53.cae'
                    JobName = 'Job-' + i                        # 'Job-53'
                    output_file_name = 'abaqus_output_' + i + '.csv'    # 'abaqus_output_53.csv'
                    
                    path = '%s/%s/%s' % (folder, j, m)
                    part_location = '%s/%s/%s/%s' % (folder, j, m, part_name)
                    save_path = '%s/%s/%s/%s' % (folder, j, m, save_name)
                    FilePath = '%s/%s/%s/%s.inp' % (folder, j, m, JobName)
                    # File_disp = '%s/%s/%s/displacement.txt' % (folder, j, m)
                    output_file = '%s/%s/%s/%s' % (folder, j, m, output_file_name)

                    if os.path.exists(output_file):
                        continue

                    if os.path.exists(part_location) == False:
                        print(part_location, ' not exist')
                        continue

                    if os.path.exists(FilePath):
                        continue

                    else:
                        print(part_location)
                        import os
                        os.chdir(path)
                        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
                                                                            engineeringFeatures=OFF)
                        session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
                            referenceRepresentation=ON)

                        iges = mdb.openIges(
                            part_location,
                            msbo=False, trimCurve=DEFAULT, scaleFromFile=OFF)

                        mdb.models['Model-1'].PartFromGeometryFile(name=mdb_name,
                                                                geometryFile=iges, combine=False, stitchTolerance=1.0,
                                                                dimensionality=THREE_D, type=DEFORMABLE_BODY, convertToAnalytical=1,
                                                                stitchEdges=1)

                        p = mdb.models['Model-1'].parts[mdb_name]
                        session.viewports['Viewport: 1'].setValues(displayedObject=p)
                        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON,
                                                                            engineeringFeatures=ON)
                        session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
                            referenceRepresentation=OFF)

                        from material import createMaterialFromDataString

                        createMaterialFromDataString('Model-1', 'Material-4', '2022',
                                                    """{'description': '', 'density': {'temperatureDependency': OFF, 'table': ((1.04e-09,),), 'dependencies': 0, 'fieldName': '', 'distributionType': UNIFORM}, 
                                                    'hyperelastic': {'temperatureDependency': OFF, 'type': OGDEN, 'materialType': ISOTROPIC, 'compressible': OFF, 'testData': OFF, 
                                                    'beta': FITTED_VALUE, 'deviatoricResponse': UNIAXIAL, 'volumetricResponse': VOLUMETRIC_DATA, 'localDirections': 0, 'behaviorType': INCOMPRESSIBLE, 
                                                    'dependencies': 0, 'anisotropicType': FUNG_ANISOTROPIC, 'formulation': STRAIN, 'table': ((0.000794, -2.8, 840.0),), 'n': 1, 'moduliTimeScale': LONG_TERM, 
                                                    'properties': 0, 'poissonRatio': 0.0}, 'materialIdentifier': '', 'permeability': {'temperatureDependency': OFF, 'inertialDragCoefficient': 0.142887, 'dependencies': 0, 
                                                    'specificWeight': 9779.0, 'table': ((1.57e-06, 0.2),), 'type': ISOTROPIC}, 'viscoelastic': {'errtol': 0.01, 'nmax': 13, 'domain': TIME, 'frequency': FORMULA, 
                                                    'type': ISOTROPIC, 'time': PRONY, 'table': ((0.13, 0.0, 14.0), (0.32, 0.0, 333.0)), 'volumetricTable': (), 'preload': NONE}, 'name': 'Material-4'}""")
                        mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1',
                                                                    material='Material-4', thickness=None)
                        p = mdb.models['Model-1'].parts[mdb_name]
                        c = p.cells
                        cells = c.getSequenceFromMask(mask=('[#1 ]',), )
                        region = p.Set(cells=cells, name='Set-1')
                        p = mdb.models['Model-1'].parts[mdb_name]
                        p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
                                            offsetType=MIDDLE_SURFACE, offsetField='',
                                            thicknessAssignment=FROM_SECTION)

                        a = mdb.models['Model-1'].rootAssembly
                        session.viewports['Viewport: 1'].setValues(displayedObject=a)
                        session.viewports['Viewport: 1'].assemblyDisplay.setValues(
                            optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)

                        a = mdb.models['Model-1'].rootAssembly
                        a.DatumCsysByDefault(CARTESIAN)
                        p = mdb.models['Model-1'].parts[mdb_name]
                        a.Instance(name=mdb_name_instance, part=p, dependent=OFF)
                        session.viewports['Viewport: 1'].assemblyDisplay.setValues(
                            adaptiveMeshConstraints=ON)
                        mdb.models['Model-1'].SoilsStep(name='Step-1', previous='Initial',
                                                        timePeriod=10000000.0, maxNumInc=100000, initialInc=1.0, minInc=0.0001,
                                                        maxInc=10000000.0, utol=None, cetol=1.0, nlgeom=ON)
                        session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
                        session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=ON,
                                                                                adaptiveMeshConstraints=OFF)
                        session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
                            meshTechnique=ON)
                        a = mdb.models['Model-1'].rootAssembly
                        c1 = a.instances[mdb_name_instance].cells
                        pickedRegions = c1.getSequenceFromMask(mask=('[#1 ]',), )
                        a.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
                        elemType1 = mesh.ElemType(elemCode=C3D20R)
                        elemType2 = mesh.ElemType(elemCode=C3D15)
                        elemType3 = mesh.ElemType(elemCode=C3D10)
                        a = mdb.models['Model-1'].rootAssembly
                        c1 = a.instances[mdb_name_instance].cells
                        cells = c1.getSequenceFromMask(mask=('[#1 ]',), )
                        pickedRegions = (cells,)
                        a.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2,
                                                                        elemType3))
                        elemType1 = mesh.ElemType(elemCode=C3D8P, elemLibrary=STANDARD)
                        elemType2 = mesh.ElemType(elemCode=C3D6P, elemLibrary=STANDARD)
                        elemType3 = mesh.ElemType(elemCode=C3D4P, elemLibrary=STANDARD)
                        a = mdb.models['Model-1'].rootAssembly
                        c1 = a.instances[mdb_name_instance].cells
                        cells1 = c1.getSequenceFromMask(mask=('[#1 ]',), )
                        pickedRegions = (cells1,)
                        a.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2,
                                                                        elemType3))
                        a = mdb.models['Model-1'].rootAssembly
                        partInstances = (a.instances[mdb_name_instance],)
                        a.seedPartInstance(regions=partInstances, size=2.0, deviationFactor=0.1,
                                        minSizeFactor=0.1)
                        a = mdb.models['Model-1'].rootAssembly
                        partInstances = (a.instances[mdb_name_instance],)
                        a.generateMesh(regions=partInstances)
                        session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF)
                        session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
                            meshTechnique=OFF)
                        mdb.Job(name=JobName, model='Model-1', description='', type=ANALYSIS,
                                atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
                                memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                                scratch='', resultsFormat=ODB, numThreadsPerMpiProcess=1,
                                multiprocessingMode=DEFAULT, numCpus=7, numDomains=7, numGPUs=1)
                        mdb.jobs[JobName].writeInput(consistencyChecking=ON)
                        mdb.saveAs(pathName=save_path)
                        Mdb()
                        a = mdb.models['Model-1'].rootAssembly
                        session.viewports['Viewport: 1'].setValues(displayedObject=a)
                    print('--------------------------DONE--------------------------')

                except Exception as e:
                    log_file.write("Error occurred while processing folder '%s' and file '%s':\n" % (j, m))
                    traceback.print_exc(file=log_file)
                    log_file.write("\n")
                    continue
            print('---------------------------------------------------DONE---------------------------------------------------')
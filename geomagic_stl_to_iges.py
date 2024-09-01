
import numpy as np
import pandas as pd
import os
import glob

import SimpleITK as sitk
import vtk

import warnings
warnings.filterwarnings('ignore')
import nibabel as nib


def get_subfolders(path):
    all_folders = []
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            full_path = os.path.join(root, dir)
            full_path_converted = full_path.replace('\\', '/')
            all_folders.append(full_path_converted)
    return all_folders

folderpath = 'ADNI'
mainpath = f'D:/DATA/{folderpath}/Cross/aparc.a2009s+aseg'
folder_list = get_subfolders(mainpath)

rois = ["17", "53"]

# --------------------------extract to stl format------------------------------
rois_integers = [int(item) for item in rois]
for i in folder_list:
    path = i + '/aparc.a2009s+aseg.nii.gz'
    if os.path.exists(path) == False:
        # print(path, ' not exist')
        continue
    else:
        filename_nii =  path
        filename = filename_nii.split(".nii.gz")[0]
#             print(filename)

        # read all the labels present in the file
        multi_label_image=sitk.ReadImage(filename_nii)
        img_npy = sitk.GetArrayFromImage(multi_label_image)
        labels = np.unique(img_npy)

        # read the file
        reader = vtk.vtkNIFTIImageReader()
        reader.SetFileName(filename_nii)
        reader.Update()

        # for all labels presented in the segmented file
        for label in labels:
            if int(label) in rois_integers:
                input_stl_file = i + '/aparc.a2009s+aseg_%s.stl' % int(label)
                if os.path.exists(input_stl_file):
                    # print(input_stl_file, 'already exists')
                    continue
                else:
                # apply marching cube surface generation
                    print(input_stl_file, 'is processing')
                    surf = vtk.vtkDiscreteMarchingCubes()
                    surf.SetInputConnection(reader.GetOutputPort())
                    surf.SetValue(0, int(label)) # use surf.GenerateValues function if more than one contour is available in the file
                    surf.Update()

                    #smoothing the mesh
                    smoother= vtk.vtkWindowedSincPolyDataFilter()
                    if vtk.VTK_MAJOR_VERSION <= 5:
                        smoother.SetInput(surf.GetOutput())
                    else:
                        smoother.SetInputConnection(surf.GetOutputPort())

                    # increase this integer set number of iterations if smoother surface wanted
                    smoother.SetNumberOfIterations(30) 
                    smoother.NonManifoldSmoothingOn()
                    smoother.NormalizeCoordinatesOn() #The positions can be translated and scaled such that they fit within a range of [-1, 1] prior to the smoothing computation
                    smoother.GenerateErrorScalarsOn()
                    smoother.Update()

                    # save the output
                    writer = vtk.vtkSTLWriter()
                    writer.SetInputConnection(smoother.GetOutputPort())
                    writer.SetFileTypeToASCII()

                    # file name need to be changed
                    # save as the .stl file, can be changed to other surface mesh file
                    writer.SetFileName(f'{filename}_{label}.stl')
                    writer.Write()
print('------------------------------------stl done-------------------------------------')


# --------------------------geomagic studio------------------------------
filename = 'C:/Users/Public/Documents/Geomagic/Geomagic Studio 2014/macros/macro_%s.py' % folderpath
with open(filename, 'w') as file:
    file.write('# -*- coding:utf-8 -*-')
    file.write('\r\n')
    for i in folder_list:
    # for i in folder_list_geo:
        for roi in rois:
            path = i + "/aparc.a2009s+aseg_%s.stl" % roi
            outputfile = i + "/aparc.a2009s+aseg_%s.igs" % roi
            if os.path.exists(path) == False:
                continue
            elif os.path.exists(outputfile):
                continue
            else:
                input = "geo.open(0, 1, u'%s')" % path
                output = "geo.saveas(u'%s', 2, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, -1, 0, 1, 0)" % outputfile

                file.write(input+'\r\n')
                file.write('geo.mesh_doctor("smallcompsize", 0.0029, "smalltunnelsize", 0.0015, "holesize", 0.0015, "spikesens", 50, "spikelevel", 0.5, "defeatureoption", 2, "fillholeoption", 2, "autoexpand", 2, "operations", "IntersectionCheck+", "SmallComponentCheck+", "SmallTunnelCheck+", "SpikeCheck+", "HighCreaseCheck+", "Update", "Auto-Repair")\r\n')
                file.write('geo.start_exact_surfacing(0, 0, 0, 0)\r\n')
                file.write('geo.auto_surface(-1, 3, 0, 0, 1, 1, 2.6e-005, 1, 0, 500, 1, 1)\r\n')
                file.write('geo.fit_surfaces(0, 30, 2.1e-005, 0.25, 0.5, 2, 0.5, 0, 0, 1, 0, 0)\r\n')
                file.write(output+'\r\n')
                file.write('\r\n')

print('-----------------------Please continue running in geomagic-----------------------')
print(filename)
print('--------------------------------------DONE---------------------------------------')
import numpy as np
import nibabel as nib
import glob
import functools

from numpy.core.numeric import cross

def sa_from_voxels(voxel_list, resolution):
    total_area = len(voxel_list) * 6 * resolution**2
    overlaps = 0
    for element1 in voxel_list:
        for element2 in voxel_list:
            if element1[0] + 1 == element2[0] and element1[1] == element2[1] and element1[2] == element2[2]:
                overlaps += 1
            elif element1[0] - 1 == element2[0] and element1[1] == element2[1] and element1[2] == element2[2]:
                overlaps += 1
            elif element1[0] == element2[0] and element1[1] + 1 == element2[1] and element1[2] == element2[2]:
                overlaps += 1
            elif element1[0] == element2[0] and element1[1] - 1 == element2[1] and element1[2] == element2[2]:
                overlaps += 1
            elif element1[0] == element2[0] and element1[1] == element2[1] and element1[2] + 1 == element2[2]:
                overlaps += 1
            elif element1[0] == element2[0] and element1[1] == element2[1] and element1[2] - 1 == element2[2]:
                overlaps += 1
    area = total_area - (overlaps * resolution**2)
    return area

for fname in list(glob.glob('simulation_parameters/branching.txt')):
    file = open(fname, "r")
    # clear extraneous file info
    for i in range(8):
        file.readline()
    res = float(file.readline()[:-1])
    # set roi info
    numrois = int(file.readline()[:-1])
    roi_info = []
    for i in range(numrois):
        roi = [file.readline()[:-1]]
        if roi[0] != "manual":
            roi.append(file.readline()[:-1])
            roi.append(file.readline()[:-1])
        else:
            roi.append(file.readline()[:-1])
        roi_info.append(roi)
    file.close()

    sa = np.zeros(numrois)
    for i in range(len(roi_info)):
        if roi_info[i][0] == "cuboid":
            voxel = roi_info[i][2].split(sep=', ')
            for j in range(len(voxel)):
                if '(' in voxel[j]:
                    voxel[j] = voxel[j][1:]
                if ')' in voxel[j]:
                    voxel[j] = voxel[j][:len(voxel[j]) - 1]
            sizes = np.array([int(voxel[0]), int(voxel[1]), int(voxel[2])])
            sa[i] = res**2 * (2 * sizes[0] * sizes[1] + 2 * sizes[0] * sizes[2] + 2 * sizes[1] * sizes[2])
        elif roi_info[i][0] == "sphere":
            radius = float(roi_info[i][2])
            sa[i] = 4 * np.pi * (radius ** 2) * res**2
        elif roi_info[i][0] == "manual":
            print("not implemented")
    roi_mask = nib.load("nifti_images/" + fname[22:-4] + "_roi.nii.gz").get_fdata()
    for s in range(2, 3):
        adj_mat = np.zeros((numrois, numrois))
        for exemplar in list(glob.glob("nifti_images/" + fname[22:-4] + "_exemplars_" + str(s) + "/*")):
            cross_sectional_area_voxels = [[]] * 2
            node1 = int(exemplar[-7]) - 1
            node2 = int(exemplar[-5]) - 1
            nodes = [node1, node2]
            tracks = nib.streamlines.load(exemplar, lazy_load=True)
            gen = iter(tracks.tractogram.streamlines)
            for streamline in gen:
                for i in range(len(streamline)):
                    test_point = [round(streamline[i][0]), round(streamline[i][1]), round(streamline[i][2])]
                    if roi_mask[test_point[0], test_point[1], test_point[2]] != 0:
                        node_index = int(roi_mask[test_point[0], test_point[1], test_point[2]]) - 1
                        if node_index is node1:
                            found = False
                            for element in cross_sectional_area_voxels[0]:
                                if element[0] == test_point[0] and element[1] == test_point[1] and element[2] == test_point[2]:
                                    found = True
                            if not found:
                                cross_sectional_area_voxels[0].append(test_point)
                        elif node_index is node2:
                            found = False
                            for element in cross_sectional_area_voxels[1]:
                                if element[0] == test_point[0] and element[1] == test_point[1] and element[2] == test_point[2]:
                                    found = True
                            if not found:
                                cross_sectional_area_voxels[1].append(test_point)
            filtered_cross_sec_area_voxels = []
            for l in range(2):
                voxels = []
                for element in cross_sectional_area_voxels[l]:
                    for i in range(np.shape(roi_mask)[0]):
                        for j in range(np.shape(roi_mask)[1]):
                            for k in range(np.shape(roi_mask)[2]):
                                if roi_mask[i, j, k] == nodes[l] + 1:
                                    if element[0] == i and element[1] == j and element[2] == k:
                                        voxels.append(element)
                filtered_cross_sec_area_voxels.append(voxels)
            
            # surface area calculation
            cross_sec_area = []
            for i in range(2):
                cross_sec_area.append(sa_from_voxels(filtered_cross_sec_area_voxels[i], res))
            # print(cross_sectional_area_voxels)
            # edge weight calculation
            adj_mat[node1, node2] = (cross_sec_area[0] + cross_sec_area[1]) / (sa[node1] + sa[node2])
            adj_mat[node2, node1] = adj_mat[node1, node2]
        print(adj_mat)
        # np.savetxt(fname[22:-4] + "_area_ew" + str(s) + ".txt", adj_mat, delimiter=" ")
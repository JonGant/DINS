import numpy as np
import nibabel as nib
import glob

for fname in list(glob.glob('simulation_parameters/*.txt')):
    file = open(fname, "r")
    # clear extraneous file info
    for i in range(8):
        print(file.readline())
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
    print(sa)
    for s in range(2, 6):
        adj_mat = np.zeros((numrois, numrois))
        print(fname[22:-4])
        for exemplar in list(glob.glob("nifti_images/" + fname[22:-4] + "_exemplars_" + str(s) + "/*")):
            node1 = int(exemplar[-7]) - 1
            node2 = int(exemplar[-5]) - 1
            if adj_mat[node1, node2] == 0 or adj_mat[node2, node1] == 0:
                tracks = nib.streamlines.load(exemplar, lazy_load=True)
                gen = iter(tracks.tractogram.streamlines)
                sum = 0
                for streamline in gen:
                    length = 0
                    for i in range(len(streamline) - 1):
                        length += np.linalg.norm(streamline[i + 1] - streamline[i])
                    sum += (1 / length)
                # edge weight calculation
                adj_mat[node1, node2] = ((res**3)/(s**3)) * (2 / (sa[node1] + sa[node2])) * sum
                adj_mat[node2, node1] = adj_mat[node1, node2]
        np.savetxt(fname[22:-4] + "_cp_ew" + str(s) + ".txt", adj_mat, delimiter=" ")
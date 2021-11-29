import numpy as np
import matplotlib.pyplot as plt
import glob

for file in list(glob.glob('branching*_cp_e*.txt')):
    # sn = np.genfromtxt(file, delimiter=' ', dtype='float')
    # plt.imshow(sn, cmap='hot', interpolation='nearest')
    # plt.colorbar()
    # plt.suptitle(file[13:-4] + "_w1")
    # plt.savefig(file[13:-4] + "_w1.png")
    # plt.show()
    sn = np.genfromtxt(file, delimiter=' ', dtype='float')
    plt.imshow(sn, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.suptitle(file[:-4] + "_w3")
    plt.savefig(file[:-4] + "_w3.png")
    plt.show()
    # node_strength = 0
    # for i in range(7):k
    #     node_strength += sn[0, i]
    # print(node_strength)
    # new_sn = np.zeros(np.shape(sn))
    # for i in range(np.shape(sn)[0]):
    #     for j in range(np.shape(sn)[1]):
    #         row_sum = np.sum(sn[i, :])
    #         col_sum = np.sum(sn[:, j])
    #         if row_sum != 0 or col_sum != 0:
    #             new_sn[i][j] = ((2 * sn[i][j]) / (row_sum + col_sum))
    #         else:
    #             print("WARNING: There was a row and column of zeros in the adjacency matrix")
    #             new_sn[i][j] = 0
    # plt.imshow(new_sn, cmap='hot', interpolation='nearest')
    # plt.clim(0, 1)
    # plt.colorbar()
    # plt.suptitle(file[13:-4] + "_w2")
    # plt.savefig(file[13:-4] + "_w2.png")
    # plt.show()

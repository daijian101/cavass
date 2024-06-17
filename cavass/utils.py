import numpy as np


def one_hot(data, num_classes):
    one_hot_arr = np.zeros(data.shape + (num_classes,))

    for class_idx in range(num_classes):
        one_hot_arr[..., class_idx][data == class_idx] = 1

    one_hot_arr = one_hot_arr.astype(np.uint8)
    return one_hot_arr

import torch
from torch import nn
import numpy as np
from sklearn.cluster import KMeans
import copy
from .tools import *


def KMeanAcc(cluster_id, gt_id, layer):
    '''
    Use IoU as Acc
    '''
    # TODO 
    pass

def KMeanCLustering(features, input_id, gt_clusters, layer):
    '''
    features: input features, [0:512] is img feature, [512:1024] is text feature
    input_id : input id list, are mapped one-to-one with features
    gt_clusters: cluster into n group, from layer_clip/clip_to_scene/scene_input_id
    layer: cluster layer 'scene', 'shot'

    For example dataset val/0:
    layer='scene':
        input_id = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ,10, 11, 12]
        gt_cluster = [[0, 5, 6, 9], [1, 4, 11], [2, 3, 7, 8, 12], [10]]
        pred_cluster = [[0, 5, 6], [1, 4], [3, 7, 10, 12], [2, 8, 9, 11]]

    layer='shot':
        input_id = [[10], [0, 5, 6, 9], [2, 3, 7, 8, 12], [1, 4, 11]]
        gt_cluster = [[10], [[0, 5, 6], [9]], [[3, 7, 12], [2,8]], [[1,4], [11]]] 
    '''
    
    assert layer in ['scene', 'shot'], "layer value error"

    if layer == 'scene':
        n_clusters = min(len(input_id), len(gt_clusters))
        kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init='auto').fit([i.detach().numpy() for i in features])
        kmeans_labels = kmeans.labels_
        output_id = group_by_class(input_id, kmeans_labels)
        features_clustered = group_same_with(features, output_id)
    else:
        # layer == 'shot'
        features_clustered, output_id = [], []
        for features_ele, input_id_ele, gt_clusters_ele in zip(features, input_id, gt_clusters):
            features_clustered_ele, output_id_ele = KMeanCLustering(
                                                                    features=features_ele,
                                                                    input_id=input_id_ele,
                                                                    gt_clusters=gt_clusters_ele,
                                                                    layer='scene'
                                                                )
            features_clustered.append(features_clustered_ele)
            output_id.append(output_id_ele)
    
    return features_clustered, output_id


if __name__ == '__main__':
    gt_clusters = [[[10]], [[0, 5, 6], [9]], [[3, 7, 12], [2, 8]], [[1, 4], [11]]]
    input_id = [[3, 7, 10, 12], [2, 8, 9, 11], [0, 4], [1, 5, 6]]
    X = torch.load('./a.pt')
    features_clustered, output_id = KMeanCLustering(X, input_id, gt_clusters, 'shot')
    print(features_clustered, output_id)


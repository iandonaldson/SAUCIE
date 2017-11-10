import sys, os, time, math, argparse, pickle
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import pandas as pd
from loader import Loader
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
#from sklearn.metrics import adjusted_rand_score
from sklearn.manifold import TSNE
#from sklearn.metrics.pairwise import pairwise_distances
from utils import *
#from sklearn.feature_selection import mutual_info_classif

def restore_model(model_folder, loadername='LoaderZika'):
    tf.reset_default_graph()

    with open('{}/args.pkl'.format(model_folder), 'rb') as f:
        args = pickle.load(f)
    args.dropout_p = 1.
    args.loader = loadername
    loader = get_loader(args)

    sess = tf.Session()
    ckpt = tf.train.get_checkpoint_state(args.save_folder)
    saver = tf.train.import_meta_graph('{}.meta'.format(ckpt.model_checkpoint_path))
    saver.restore(sess, ckpt.model_checkpoint_path)

    return args, sess, loader

def color_by_marker(args, sess, loader, recon=False):
    if not recon:
        x, labels = get_layer(sess, loader, 'x:0')
        fn = 'embedding_by_markers_orig'
    else:
        x, labels = get_layer(sess, loader, 'layer_output_activation:0')
        fn = 'embedding_by_markers_recon'

    with open('/home/krishnan/data/zika_data/gated/markers.csv') as f:
        cols = f.read().strip()
        cols = [c.strip().split('_')[1] for c in cols.split('\n')]


    embedding, labels = get_layer(sess, loader, 'layer_embedding_activation:0')

    normalizer = colors.Normalize(0, 1)

    g = math.ceil(math.sqrt(x.shape[1]))
    fig, axes = plt.subplots(g,g, figsize=(20,20))
    plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0, wspace=0.0, hspace=0.0)
    for i in range(len(axes.flatten())):
        ax = axes.flatten()[i]
        ax.set_xticks([])
        ax.set_yticks([])
    for i in range(x.shape[1]):
        ax = axes.flatten()[i]
        #normalizer = colors.Normalize(x[:,i].min(), x[:,i].max())
        ax.scatter(embedding[:,0], embedding[:,1], c=cm.jet(normalizer(x[:,i])), s=8, alpha=.7)
        ax.annotate("{}".format(cols[i]), xy=(.1,.9), xycoords='axes fraction', size=24)

    fig.savefig(os.path.join(args.save_folder,fn))

def cluster_on_embeddings(folder_embeddings, folder_clusters):
    # get embeddings
    args, sess, loader = restore_model(folder_embeddings)
    with sess:
        embeddings, labels = get_layer(sess, loader, 'layer_embedding_activation:0')

    # get clusters
    args, sess, loader = restore_model(folder_clusters)
    with sess:
        layer = args.layers_entropy[0]
        count, clusters = count_clusters(args, sess, loader, layer, thresh=.5, return_clusters=True)
        embeddings = embeddings[clusters!=-1,:]
        clusters = clusters[clusters!=-1]

    plot(args, embeddings, clusters, 'Embedding layer by cluster', 'embedding_by_cluster')  
 

def analyze():
    model_folders = sys.argv[1:]

    for model_folder in model_folders:
        #cluster_on_embeddings('saved_zika_2d', model_folder)

        args, sess, loader = restore_model(model_folder)
        print(args.save_folder)
        with sess:
            #activations_heatmap(args, sess, loader, 2)
            
            # color_by_marker(args, sess, loader, recon=False)
            # color_by_marker(args, sess, loader, recon=True)
            # activations_heatmap(args, sess, loader, 2)

            # embeddings, labels = get_layer(sess, loader, 'layer_embedding_activation:0')
            embeddings, labels = get_layer(sess, loader, 'layer_decoder_0_bninput:0', 'train')
            # input_layer, labels = get_layer(sess, loader, 'x:0')
            # reconstruction, labels = get_layer(sess, loader, 'layer_output_activation:0')

            plot(args, embeddings, labels, '', 'zika_tmp')
            sys.exit()

            plot(args, embeddings, labels, 'Embedding layer by label', 'embedding_by_label')
            if not args.layers_entropy:
                plot(args, embeddings, np.zeros(embeddings.shape[0]), 'Embedding layer', 'embedding_without_idreg')
            else:
                for l in args.layers_entropy:
                    count, clusters = count_clusters(args, sess, loader, l, thresh=args.thresh, return_clusters=True)
                    print(input_layer.shape)
                    print(clusters.shape)
                    np.savez('testzika', x=input_layer, clusters=clusters, embedding=embeddings)
                    embeddings = embeddings[clusters!=-1,:]
                    clusters = clusters[clusters!=-1]
                    plot(args, embeddings, clusters, 'Embedding layer by cluster', 'embedding_by_cluster_{}'.format(l))
                    # print("layer: {} entropy lambdas: {} Number of clusters: {}".format(l, args.lambdas_entropy, count))
                    # if args.data=='MNIST':
                    #     decode_cluster_means(args, sess, loader, clusters)
                    #     confusion_matrix(args, sess, loader, l, clusters)
                    # activations_heatmap(args, sess, loader, l)
                    # channel_by_cluster(args, sess, loader, l)




            # if args.layers[-1]==2:
            #     if args.data=='MNIST':
            #         plot_mnist(args, input_layer, labels, embeddings, 'orig')
            #         plot_mnist(args, reconstruction, labels, embeddings, 'recon')
            # if args.data=='MNIST':
            #     show_result(args, input_layer, 'original_images.png')
            #     show_result(args, reconstruction, 'reconstructed_images.png')
            # if args.dropout_input or args.add_noise:
            #     input_layer_noisy = input_layer
            #     if args.add_noise:
            #         input_layer_noisy = input_layer + np.random.normal(0,args.add_noise, input_layer.shape)
            #         input_layer_noisy = np.maximum(np.minimum(input_layer_noisy, 1.), 0.)
            #     if args.dropout_input:
            #         input_layer_noisy *= np.random.binomial(1,args.dropout_input, input_layer_noisy.shape)
            #     if args.data=='MNIST':
            #         show_result(args, input_layer_noisy, 'original_images_noisy.png')


                
            





if __name__=='__main__':
    analyze()
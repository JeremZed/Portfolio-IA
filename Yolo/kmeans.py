# Source : https://medium.com/towards-data-science/how-to-cluster-images-based-on-visual-similarity-cd6e7209fe34

import os
import numpy as np
import matplotlib.pyplot as plt
from random import randint
import pandas as pd
import pickle

from keras.preprocessing.image import load_img, img_to_array
from keras.applications.vgg16 import preprocess_input

# models
from keras.applications.vgg16 import VGG16
from keras.models import Model

# clustering and dimension reduction
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


# Importing Image class from PIL module
from PIL import Image

np.random.seed(1)

n=3
start = 0
end = 60000
nb = end - start
dirpath = './resources/all-visages/'
save_pickle_features = './resources/usv-features.pkl'
shape = (224,224)

images = []

# Resize des images
# with os.scandir(dirpath) as files:
#   # loops through each file in the directory
#     for file in files:
#         if file.name.endswith('.jpg'):
#             img = Image.open(f'{dirpath}{file.name}')
#             img = img.resize(shape)
#             img.save(f'{dirpath}{file.name}')


with os.scandir(dirpath) as files:
  # loops through each file in the directory
    for file in files:
        if file.name.endswith('.jpg'):
          # adds only the image files to the flowers list
            images.append(f'{dirpath}{file.name}')

np.random.shuffle(images)

model = VGG16()
model = Model(inputs = model.inputs, outputs = model.layers[-2].output)

def extract_features(file, model):
    # load the image as a 224x224 array
    img = load_img(file, target_size=shape)
    # convert from 'PIL.Image.Image' to numpy array
    img = np.array(img)
    # reshape the data for the model reshape(num_of_samples, dim 1, dim 2, channels)
    reshaped_img = img.reshape((1,) + img.shape)
    # prepare image for model
    imgx = preprocess_input(reshaped_img)
    # get the feature vector
    features = model.predict(imgx)
    return features

data = {}
i = 0
total = len(images[start:end])
# lop through each image in the dataset
# for img in images[start:end]:
#     feat = extract_features(img,model)
#     data[img] = feat
#     print(img, " : " ,i, "/", total)
#     i+=1

# Save pickle
# with open(save_pickle_features,'wb') as file:
#     pickle.dump(data,file)

# Load pickle
with open(save_pickle_features, 'rb') as f:
    data = pickle.load(f)

filenames = np.array(list(data.keys()))

# get a list of just the features
feat = np.array(list(data.values()))
print(feat.shape)

# reshape so that there are 210 samples of 4096 vectors
feat = feat.reshape(-1,4096)
print(feat.shape)

# get the unique labels (from the flower_labels.csv)
n_clusters = 50

print("PCA...")
# reduce the amount of dimensions in the feature vector
pca = PCA(n_components=250, random_state=22)
pca.fit(feat)
x = pca.transform(feat)

print("Kmeans")
# cluster feature vectors
kmeans = KMeans(n_clusters=n_clusters,random_state=22)
kmeans.fit(x)

# holds the cluster id and the images { id: [images] }
groups = {}
for file, cluster in zip(filenames,kmeans.labels_):
    if cluster not in groups.keys():
        groups[cluster] = []
        groups[cluster].append(file)
    else:
        groups[cluster].append(file)

# # function that lets you view a cluster (based on identifier)
def view_cluster(cluster):
    plt.figure(figsize = (25,25))
    # gets the list of filenames for a cluster
    files = groups[cluster]
    # only allow up to 30 images to be shown at a time
    # if len(files) > 30:
    #     print(f"Clipping cluster size from {len(files)} to 30")
    #     files = files[:29]
    # # plot each image in the cluster
    # for index, file in enumerate(files):
    #     plt.subplot(10,10,index+1)
    #     img = load_img(file)
    #     img = np.array(img)
    #     plt.imshow(img)
    #     plt.axis('off')

    dirpath = f"./resources/a-classer/{cluster}"

    if os.path.exists(dirpath) == False:
        os.makedirs(dirpath, mode=0o750, exist_ok=True)

    for i, file in enumerate(files):
        print(file)
        name = file.split("/")
        img = Image.open(f'{file}')
        img.save(f'{dirpath}/{name[-1]}')

    # plt.show()

for i,g in enumerate(groups):
    print("groupe : ", i)
    view_cluster(i)


# # this is just incase you want to see which value for k might be the best
# sse = []
# list_k = list(range(3, 250))

# for k in list_k:
#     km = KMeans(n_clusters=k, random_state=22)
#     km.fit(x)

#     sse.append(km.inertia_)

# # Plot sse against k
# plt.figure(figsize=(6, 6))
# plt.plot(list_k, sse)
# plt.xlabel(r'Number of clusters *k*')
# plt.ylabel('Sum of squared distance')
# plt.show()

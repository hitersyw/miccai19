import os
import numpy as np

import utils
from cfg import *

from torch.utils import data
from torchvision import datasets, transforms
from torch.utils.data import Dataset
from torchvision.datasets.folder import default_loader


class CleansingDataset(Dataset):
    def __init__(self, root, transform, dataset, special_list, filter_type, feature_folder, ground_truth_folder):
        '''
        :param root: root path for the dataset
        :param transform: transforms for the image
        :param dataset: m2cai16-workflow-5 or cholec80-workflow-5
        :param special_list: list of video names, will be seperate from others by the filter_type
        :param filter_type: in or not_in
        :param feature_folder: image folder
        :param ground_truth_folder: ground_truth_folder
        '''
        self.img_labels = []
        self.img_names = []

        self.transform = transform
        self.dataset = dataset

        img_folder = os.path.join(root, feature_folder)
        ground_truth_folder = os.path.join(root, ground_truth_folder)

        for video in os.listdir(img_folder):
            if video not in special_list and filter_type == 'in':
                continue
            if video in special_list and filter_type == 'not_in':
                continue

            annotation_dict = utils.annotation_to_dict(os.path.join(ground_truth_folder, '{}.txt'.format(video)))

            for img in os.listdir(os.path.join(img_folder, video)):
                # img start from 0.jpg
                img_index = img.split('.')[0]
                if img_index in annotation_dict.keys():
                    self.img_labels.append(config[dataset]['mapping_dict'][annotation_dict[img_index]])
                    self.img_names.append(os.path.join(img_folder, video, img))

        print('[INFO] length of dataset {} is {}'.format(root, len(self.img_labels)))

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, index):
        img, label, img_name = default_loader(self.img_names[index]), self.img_labels[index], self.img_names[index]
        if self.transform is not None:
            img = self.transform(img)
        return img, label, img_name


class VideoDataset_:
    def __init__(self, root, dataset, special_list, filter_type, feature_folder, ground_truth_folder):
        '''
        Return the images of one video with order perserved.
        :param root: root path for the dataset
        :param dataset: m2cai16-workflow-5 or cholec80-workflow-5
        :param special_list: list of video names, will be seperate from others by the filter_type
        :param filter_type: in or not_in
        :param feature_folder: image folder
        :param ground_truth_folder: ground_truth_folder
        '''
        self.video_labels = []
        self.video_img_names = []
        self.video_name = []

        img_folder = os.path.join(root, feature_folder)
        ground_truth_folder = os.path.join(root, ground_truth_folder)

        for video in os.listdir(img_folder):
            if video not in special_list and filter_type == 'in':
                continue
            if video in special_list and filter_type == 'not_in':
                continue

            self.video_name.append(video)

            annotation_dict = utils.annotation_to_dict(os.path.join(ground_truth_folder, '{}.txt'.format(video)))
            sorted_pics = []

            for img in os.listdir(os.path.join(img_folder, video)):
                img_index = img.split('.')[0]

                if img_index in annotation_dict.keys():
                    sorted_pics.append(
                        (os.path.join(img_folder, video, img),
                         config[dataset]['mapping_dict'][annotation_dict[img_index]], int(img_index))
                    )


            sorted_pics = sorted(sorted_pics, key=lambda a: a[2])
            self.video_img_names.append([a[0] for a in sorted_pics])
            self.video_labels.append([a[1] for a in sorted_pics])
            print('video {} has {} pics'.format(video, len(sorted_pics)))
        print('[INFO] length of dataset {} is {}'.format(root, len(self.video_labels)))

    def __len__(self):
        return len(self.video_labels)

    def __getitem__(self, start, end):
        return self.video_img_names[start:end], self.video_labels[start:end], self.video_name[start:end]


class VideoDataset(Dataset):
    def __init__(self, video_imgs, video_labels, transform):
        '''
        Construct use the _VideoDataset.__getitem__()
        :param video_imgs: img names that come from the same video
        :param video_labels: img labels that come from the same video
        :param transform: transform for image
        '''
        self.imgs, self.labels = self._merge(video_imgs, video_labels)
        self.transform = transform
        print('[INFO] length of dataset is {}'.format(len(self.imgs)))

    def __len__(self):
        return len(self.imgs)

    def _merge(self, video_imgs, video_labels):
        imgs = []
        labels = []

        for video_index in range(len(video_imgs)):
            imgs += video_imgs[video_index]
            labels += video_labels[video_index]
        return imgs, labels

    def __getitem__(self, index):
        img, img_name, label = default_loader(self.imgs[index]), self.imgs[index], self.labels[index]
        if self.transform is not None:
            img = self.transform(img)

        return img, label, img_name


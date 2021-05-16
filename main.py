#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 20:02:18 2021

@author: Rebin Silva V

Main function to download dataset
"""

from download import download_audio, ydl_opts
import tqdm

import sys
import os
import os.path
import csv
import argparse
from concurrent import futures



def download_split(split_dataset, no_workers, out_dir):
    with futures.ThreadPoolExecutor(max_workers=no_workers) as executor:
        to_do_map = {}
        for row in split_dataset:
            video_id = row[0]
            start_time = float(row[1].strip())
            end_time = float(row[2].strip())
            # print(video_id, start_time, end_time)
            future = executor.submit(download_audio, video_id, start_time, end_time, out_dir)
            to_do_map[future] = video_id

        done_iter = futures.as_completed(to_do_map)
        done_iter = tqdm.tqdm(done_iter, total=len(split_dataset))

        for future in done_iter:
            # future.result()
            try:
                future.result()
            except:
                print("Unexpected error in audio" + to_do_map[future] + " :", sys.exc_info()[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--no_workers", type=int, help="number of subprocesses to spawn for parallel download", default=10)
    parser.add_argument("-o", "--out_dir", help="path to store dataset", default=".")
    parser.add_argument("-u", "--username", help="login with this youtube account Id")
    parser.add_argument("-p", "--password", help="account password")
    parser.add_argument("--cookies", help="cookies file")
    args = parser.parse_args()

    out_dir = args.out_dir
    username = args.username
    password = args.password
    cookies = args.cookies


    if username is not None:
        if password is None:
            password = input("Enter your account password:")
        ydl_opts['username'] = username
        ydl_opts['password'] = password

    if cookies is not None:
        ydl_opts['cookiefile'] = cookies

    dataset_splits = ('eval_segments.csv', 'balanced_train_segments.csv', 'unbalanced_train_segments.csv')

    for split in dataset_splits:
        split_dir = os.path.join(out_dir, os.path.splitext(split)[0])
        try:
            os.mkdir(split_dir)
        except FileExistsError:
            pass
        with open(split) as csvfile:
            split_reader = csv.reader(csvfile)
            # skip first three lines
            for i in range(3):
                next(split_reader)
            split_dataset = tuple(split_reader)

        download_split(split_dataset, args.no_workers, split_dir)

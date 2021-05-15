#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 20:02:18 2021

@author: Rebin Silva V

Helper function to download partial audio
"""

from __future__ import unicode_literals
import youtube_dl

import subprocess
import os.path


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'geo_bypass': True,
    'format': 'bestaudio',
    'youtube_skip_dash_manifest': True,
#     'postprocessors': [{
#         'key': 'FFmpegExtractAudio',
#         'preferredcodec': 'mp3',
#         'preferredquality': '192',
#     }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


def convert_format(time):
    mins, secs = divmod(time, 60)
    mins = int(mins)
    hrs, mins = divmod(mins, 60)
    return f'{hrs:02}:{mins:02}:{secs:05.2f}'


def download_audio(video_id, start_time, end_time, out_dir = './', overwrite=False):
    """
    Parameters
    ----------
    video_id : youtube video id.
    start_time : in secs.
    end_time : in secs.
    overwrite : if true, output file is overwritten if exists

    Returns
    -------
    None.

    """
    # https://unix.stackexchange.com/a/388148/378846
    out_file_name = os.path.join(out_dir, f'{video_id}_{start_time}_{end_time}.mp4')

    if (not overwrite) and os.path.isfile(out_file_name):
        return

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info('https://youtu.be/'+video_id, download=False)

    url = info['url']
    start = convert_format(start_time)
    duration = convert_format(end_time-start_time)
    # ffmpeg -ss 00:00:30.00 -i "OUTPUT-OF-FIRST URL" -t 00:00:10.00 -c copy out.mp4
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', start, '-i', url, '-ss', '0', '-t', duration, '-c', 'copy', '-strict', 'experimental', '--', out_file_name])


if __name__ == '__main__':
    download_audio('-Vo4CAMX26U', 0, 9)

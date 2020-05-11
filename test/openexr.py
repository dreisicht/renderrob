import OpenEXR
import os
import threading
from multiprocessing.pool import ThreadPool
from multiprocessing import Process, Queue
from datetime import datetime
# import glob

# exrfiles = glob.glob("./*.exr")

os.chdir("C:/Users/peter/Documents/repositories/RenderRob/test/")


def is_complete(filename):
    pass


def get_channels(exr_object):
    return exr_object.header().get("channels").items()


def compare_exr_channels(filename1, filename2, channel_name):
    print(channel_name)
    exr1 = OpenEXR.InputFile(filename1)  # pylint: disable=maybe-no-member
    exr2 = OpenEXR.InputFile(filename2)  # pylint: disable=maybe-no-member
    ch1 = exr1.channel(channel_name)
    ch2 = exr2.channel(channel_name)
    if ch1 != ch2:
        return False
    return True


def solution_standard(filename1, filename2, exr1, exr2):
    for channel_name in get_channels(exr1):
        if compare_exr_channels(filename1, filename2, channel_name[0]) is False:
            return False


def solution_pool(filename1, filename2, exr1, exr2):
    pool = ThreadPool(processes=24)
    for channel_name in get_channels(exr1):
        async_result = pool.apply_async(
            compare_exr_channels, (filename1, filename2, channel_name[0]))
    return_val = async_result.get()
    print(return_val)


def compare_exr_files(filename1, filename2):
    # compare size of files
    if os.path.getsize(filename1) != os.path.getsize(filename2):
        return False

    exr1 = OpenEXR.InputFile(filename1)  # pylint: disable=maybe-no-member
    exr2 = OpenEXR.InputFile(filename2)  # pylint: disable=maybe-no-member

    # if files have different ammount of channels, don't check
    if len(get_channels(exr1)) != len(get_channels(exr2)):
        return False

    # compare every channel
    if solution_standard(filename1, filename2, exr1, exr2) is False:
        return False
    return True


if __name__ == '__main__':
    a = datetime.now()
    print(compare_exr_files("1.exr", "1-1.exr"))
    print(datetime.now()-a)
    a = datetime.now()
    print(compare_exr_files("1.exr", "2.exr"))
    print(datetime.now()-a)

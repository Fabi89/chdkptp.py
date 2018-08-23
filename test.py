import logging
import os
import tempfile

import chdkptp


logging.basicConfig(level=logging.DEBUG)

tmp_dir = tempfile.mkdtemp()
dev = chdkptp.ChdkDevice(chdkptp.list_devices()[0])

print("Test files can be found under {0}".format(tmp_dir))

print("Checking connectivity")
assert dev.is_connected

print("Checking mode switch")
if dev.mode == 'record':
    dev.switch_mode('play')
    assert dev.mode == 'play'
dev.switch_mode('record')
assert dev.mode == 'record'

for fmt_type in ('ppm', 'jpg', 'png'):
    print("Checking get {} viewport frames".format(fmt_type))
    c = 0
    for imgdata in dev.get_frames(format=fmt_type):
        if c > 5:
            break
        c += 1
        fpath = os.path.join(tmp_dir, "viewport_{0:02}.{1}".format(c, fmt_type))
        imgdata = bytearray(imgdata, 'latin-1')
        with open(fpath, 'wb') as fp:
            fp.write(imgdata)

for fmt_type in ('jpg', 'dng'):
    print("Checking {} stream capture".format(fmt_type))
    for i in range(5):
        fpath = os.path.join(tmp_dir, "stream_{0:02}.{1}".format(i, fmt_type))
        imgdata = dev.shoot(stream=True)  # default
        imgdata = bytearray(imgdata, 'latin-1')
        with open(fpath, 'wb') as fp:
            fp.write(imgdata)

print("Checking downloading JPEG capture")
for i in range(5):
    fpath = os.path.join(tmp_dir, "download_{0:02}.jpg".format(i))
    imgdata = dev.shoot(stream=False, download_after=True, remove_after=True)
    imgdata = bytearray(imgdata, 'latin-1')
    with open(fpath, 'wb') as fp:
        fp.write(imgdata)

print("Checking file upload")
with open('/tmp/test.txt', 'w') as fp:
    fp.write('test')
dev.upload_file('/tmp/test.txt', 'A/')
assert 'a/test.txt' in [x.lower() for x in dev.list_files()]

print("Checking file removal")
dev.delete_files('A/test.txt')
assert 'a/test.txt' not in [x.lower() for x in dev.list_files()]

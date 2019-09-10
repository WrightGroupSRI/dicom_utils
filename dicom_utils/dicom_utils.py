"""Implements misc dicom util stuff."""

import glob
import numpy
import pydicom as dicom
from collections import defaultdict


def dicom_trigger_time(d):
    """Read the trigger time from the given dicom."""
    return float(d.TriggerTime)


def dicom_resp_signal(d):
    """Read the respiratory signal from the given dicom."""
    return float(d[0x99, 0x99].value)


def dicom_orientation(d):
    """Read the given dicom's image orientation."""
    return numpy.array(d[0x20, 0x37].value)


def dicom_position(d):
    """Read the given dicom's image position."""
    return numpy.array(d[0x20, 0x32].value)


def dicom_spacing(d):
    """Read the given dicom's voxel size."""
    return numpy.array(d[0x28, 0x30].value)


def dicom_transform(d):
    """Read image orientation and position from the given dicom and produce
    an affine transform."""

    o = dicom_orientation(d)
    s = dicom_spacing(d)
    p = dicom_position(d)

    t = numpy.eye(4)
    t[0:3, 0] = o[0:3] * s[0]
    t[0:3, 1] = o[3:6] * s[1]
    t[0:3, 2] = numpy.cross(o[0:3], o[3:6]) * (s[2] if len(s) > 2 else 1)
    t[0:3, 3] = p

    v = numpy.eye(4)
    v[1, 1] = -1

    return t @ v


def dicom_slice_direction(d, point):
    """Get the slice direction coordinate of the point in the given dicom's
    coordinates."""
    o = dicom_orientation(d)
    v = numpy.cross(o[0:3], o[3:6])
    r = numpy.dot(point, v)
    return r


def dicom_self_slice_direction(d):
    """Get the dicom image's own slice position in the slice direction."""
    return dicom_slice_direction(d, dicom_position(d))


def read_cine_dir(cine_dirname):
    """Find all dicoms in the given dir and separate them by phase and slice
    location."""

    cine_data = defaultdict(dict)
    for filename in sorted(glob.glob(cine_dirname + "/*.dcm")):
        image = dicom.read_file(filename)
        cine_data[dicom_self_slice_direction(image)][dicom_trigger_time(image)] = image

    return cine_data

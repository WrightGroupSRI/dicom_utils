"""Implements misc dicom util stuff."""

import glob
from collections import defaultdict

import numpy
import pydicom as dicom


def trigger_time(d):
    """Read the trigger time from the given dicom."""
    return float(d.TriggerTime)


def resp(d):
    """Read the respiratory signal from the given dicom."""
    return float(d[0x99, 0x99].value)


def orientation(d):
    """Read the given dicom's image orientation."""
    return numpy.array(d[0x20, 0x37].value)


def position(d):
    """Read the given dicom's image position."""
    return numpy.array(d[0x20, 0x32].value)


def spacing(d):
    """Read the given dicom's voxel size."""
    return numpy.array(d[0x28, 0x30].value)


def pixel_to_image(d):
    """Get the transform that sends pixel coordinates to image coordinates."""
    s = spacing(d)
    # We need a length 4 diagonal, assume that all unspecified directions have
    # a resolution of 1 mm. len(s) should be 2 or 3.
    assert len(s) < 4, "Too many values in s"
    s = numpy.append(s, numpy.ones(4 - len(s)))
    return numpy.diag(s)


def image_to_pixel(d):
    """Get the transform that sends image coordinates to pixel coordinates."""
    return numpy.linalg.inv(pixel_to_image(d))


def image_to_world(d):
    """Get the transform that sends image coordinates to world coordinates."""

    o = orientation(d)
    p = position(d)
    t = numpy.eye(4)

    t[0:3, 0] = o[0:3]
    t[0:3, 1] = o[3:6]
    t[0:3, 2] = numpy.cross(o[0:3], o[3:6])
    t[0:3, 3] = p

    return t


def world_to_image(d):
    """Get the transform that sends world coordinates to image coordinates."""
    return numpy.linalg.inv(image_to_world(d))


def pixel_to_world(d):
    """Get the transform that sends pixel coordinates to world coordinates."""
    return image_to_world(d) @ pixel_to_image(d)


def world_to_pixel(d):
    """Get the transform that sends world coordinates to pixel coordinates."""
    return numpy.linalg.inv(pixel_to_world(d))


def dicom_slice_direction(d, point):
    """Get the slice direction coordinate of the point in the given dicom's
    coordinates."""
    o = orientation(d)
    v = numpy.cross(o[0:3], o[3:6])
    r = numpy.dot(point, v)
    return r


def dicom_self_slice_direction(d):
    """Get the dicom image's own slice position in the slice direction."""
    return dicom_slice_direction(d, position(d))


def read_cine_dir(cine_dirname):
    """Find all dicoms in the given dir and separate them by phase and slice
    location."""

    cine_data = defaultdict(dict)
    for filename in sorted(glob.glob(cine_dirname + "/*.dcm")):
        image = dicom.read_file(filename)
        cine_data[dicom_self_slice_direction(image)][trigger_time(image)] = image

    return cine_data

"""
EXIF metadata parser; also parses TIFF file headers.

Author: Victor Stinner, Robert Xiao

References:
- Exif 2.2 Specification (JEITA CP-3451)
    http://www.exif.org/Exif2-2.PDF
- TIFF 6.0 Specification
    http://partners.adobe.com/public/developer/en/tiff/TIFF6.pdf
"""

from hachoir_core.field import (FieldSet, SeekableFieldSet, ParserError,
    UInt8, UInt16, UInt32,
    Int8, Int16, Int32,
    Float32, Float64,
    Enum, String, Bytes, SubFile,
    NullBits, NullBytes, createPaddingField)
from hachoir_core.endian import LITTLE_ENDIAN, BIG_ENDIAN, NETWORK_ENDIAN
from hachoir_core.text_handler import textHandler, hexadecimal
from hachoir_core.tools import createDict

MAX_COUNT = 1000 # maximum number of array entries in an IFD entry (excluding string types)

def rationalFactory(class_name, size, field_class):
    class Rational(FieldSet):
        static_size = size

        def createFields(self):
            yield field_class(self, "numerator")
            yield field_class(self, "denominator")

        def createValue(self):
            return float(self["numerator"].value) / self["denominator"].value
    cls = Rational
    cls.__name__ = class_name
    return cls

RationalInt32 = rationalFactory("RationalInt32", 64, Int32)
RationalUInt32 = rationalFactory("RationalUInt32", 64, UInt32)

class ASCIIString(String):
    def __init__(self, parent, name, nbytes, description=None, strip=' \0', charset='ISO-8859-1', *args, **kwargs):
        String.__init__(self, parent, name, nbytes, description, strip, charset, *args, **kwargs)

class IFDTag(UInt16):
    def getTag(self):
        return self.parent.TAG_INFO.get(self.value, (hex(self.value), ""))
    def createDisplay(self):
        return self.getTag()[0]

class BasicIFDEntry(FieldSet):
    TYPE_BYTE = 0
    TYPE_UNDEFINED = 7
    TYPE_RATIONAL = 5
    TYPE_SIGNED_RATIONAL = 10
    TYPE_INFO = {
         1: (UInt8, "BYTE (8 bits)"),
         2: (ASCIIString, "ASCII (8 bits)"),
         3: (UInt16, "SHORT (16 bits)"),
         4: (UInt32, "LONG (32 bits)"),
         5: (RationalUInt32, "RATIONAL (2x LONG, 64 bits)"),
         6: (Int8, "SBYTE (8 bits)"),
         7: (Bytes, "UNDEFINED (8 bits)"),
         8: (Int16, "SSHORT (16 bits)"),
         9: (Int32, "SLONG (32 bits)"),
        10: (RationalInt32, "SRATIONAL (2x SLONG, 64 bits)"),
        11: (Float32, "FLOAT (32 bits)"),
        12: (Float64, "DOUBLE (64 bits)"),
    }
    ENTRY_FORMAT = createDict(TYPE_INFO, 0)
    TYPE_NAME = createDict(TYPE_INFO, 1)
    TAG_INFO = {}

    def createFields(self):
        yield IFDTag(self, "tag", "Tag")
        yield Enum(UInt16(self, "type", "Type"), self.TYPE_NAME)
        self.value_cls = self.ENTRY_FORMAT.get(self['type'].value, Bytes)
        if issubclass(self.value_cls, Bytes):
            self.value_size = 8
        else:
            self.value_size = self.value_cls.static_size
        yield UInt32(self, "count", "Count")

        if not issubclass(self.value_cls, Bytes) \
          and self["count"].value > MAX_COUNT:
            raise ParserError("EXIF: Invalid count value (%s)" % self["count"].value)

        count = self['count'].value
        totalsize = self.value_size * count
        if count == 0:
            yield NullBytes(self, "padding", 4)
        elif totalsize <= 32:
            name = "value"
            if issubclass(self.value_cls, Bytes):
                yield self.value_cls(self, name, count)
            else:
                if count > 1:
                    name += "[]"
                for i in xrange(count):
                    yield self.value_cls(self, name)
            if totalsize < 32:
                yield NullBits(self, "padding", 32-totalsize)
        else:
            yield UInt32(self, "offset", "Value offset")

    def createValue(self):
        if "value" in self:
            return self['value'].value
        return None

    def createDescription(self):
        return "Entry: "+self["tag"].getTag()[1]

class IFDEntry(BasicIFDEntry):
    EXIF_IFD_POINTER = 0x8769
    GPS_IFD_POINTER = 0x8825
    INTEROP_IFD_POINTER = 0xA005

    TAG_INFO = {
        # image data structure
        0x0100: ("ImageWidth", "Image width"),
        0x0101: ("ImageLength", "Image height"),
        0x0102: ("BitsPerSample", "Number of bits per component"),
        0x0103: ("Compression", "Compression scheme"),
        0x0106: ("PhotometricInterpretation", "Pixel composition"),
        0x0112: ("Orientation", "Orientation of image"),
        0x0115: ("SamplesPerPixel", "Number of components"),
        0x011C: ("PlanarConfiguration", "Image data arrangement"),
        0x0212: ("YCbCrSubSampling", "Subsampling ratio of Y to C"),
        0x0213: ("YCbCrPositioning", "Y and C positioning"),
        0x011A: ("XResolution", "Image resolution in width direction"),
        0x011B: ("YResolution", "Image resolution in height direction"),
        0x0128: ("ResolutionUnit", "Unit of X and Y resolution"),
        # recording offset
        0x0111: ("StripOffsets", "Image data location"),
        0x0116: ("RowsPerStrip", "Number of rows per strip"),
        0x0117: ("StripByteCounts", "Bytes per compressed strip"),
        0x0201: ("JPEGInterchangeFormat", "Offset to JPEG SOI"),
        0x0202: ("JPEGInterchangeFormatLength", "Bytes of JPEG data"),
        # image data characteristics
        0x012D: ("TransferFunction", "Transfer function"),
        0x013E: ("WhitePoint", "White point chromaticity"),
        0x013F: ("PrimaryChromaticities", "Chromaticities of primaries"),
        0x0211: ("YCbCrCoefficients", "Color space transformation matrix coefficients"),
        0x0214: ("ReferenceBlackWhite", "Pair of black and white reference values"),
        # other tags
        0x0132: ("DateTime", "File change date and time"),
        0x010E: ("ImageDescription", "Image title"),
        0x010F: ("Make", "Image input equipment manufacturer"),
        0x0110: ("Model", "Image input equipment model"),
        0x0131: ("Software", "Software used"),
        0x013B: ("Artist", "Person who created the image"),
        0x8298: ("Copyright", "Copyright holder"),
        # TIFF-specific tags
        0x00FE: ("NewSubfileType", "NewSubfileType"),
        0x00FF: ("SubfileType", "SubfileType"),
        0x0107: ("Threshholding", "Threshholding"),
        0x0108: ("CellWidth", "CellWidth"),
        0x0109: ("CellLength", "CellLength"),
        0x010A: ("FillOrder", "FillOrder"),
        0x010D: ("DocumentName", "DocumentName"),
        0x0118: ("MinSampleValue", "MinSampleValue"),
        0x0119: ("MaxSampleValue", "MaxSampleValue"),
        0x011D: ("PageName", "PageName"),
        0x011E: ("XPosition", "XPosition"),
        0x011F: ("YPosition", "YPosition"),
        0x0120: ("FreeOffsets", "FreeOffsets"),
        0x0121: ("FreeByteCounts", "FreeByteCounts"),
        0x0122: ("GrayResponseUnit", "GrayResponseUnit"),
        0x0123: ("GrayResponseCurve", "GrayResponseCurve"),
        0x0124: ("T4Options", "T4Options"),
        0x0125: ("T6Options", "T6Options"),
        0x0129: ("PageNumber", "PageNumber"),
        0x013C: ("HostComputer", "HostComputer"),
        0x013D: ("Predictor", "Predictor"),
        0x0140: ("ColorMap", "ColorMap"),
        0x0141: ("HalftoneHints", "HalftoneHints"),
        0x0142: ("TileWidth", "TileWidth"),
        0x0143: ("TileLength", "TileLength"),
        0x0144: ("TileOffsets", "TileOffsets"),
        0x0145: ("TileByteCounts", "TileByteCounts"),
        0x014C: ("InkSet", "InkSet"),
        0x014D: ("InkNames", "InkNames"),
        0x014E: ("NumberOfInks", "NumberOfInks"),
        0x0150: ("DotRange", "DotRange"),
        0x0151: ("TargetPrinter", "TargetPrinter"),
        0x0152: ("ExtraSamples", "ExtraSamples"),
        0x0153: ("SampleFormat", "SampleFormat"),
        0x0154: ("SMinSampleValue", "SMinSampleValue"),
        0x0155: ("SMaxSampleValue", "SMaxSampleValue"),
        0x0156: ("TransferRange", "TransferRange"),
        0x0200: ("JPEGProc", "JPEGProc"),
        0x0203: ("JPEGRestartInterval", "JPEGRestartInterval"),
        0x0205: ("JPEGLosslessPredictors", "JPEGLosslessPredictors"),
        0x0206: ("JPEGPointTransforms", "JPEGPointTransforms"),
        0x0207: ("JPEGQTables", "JPEGQTables"),
        0x0208: ("JPEGDCTables", "JPEGDCTables"),
        0x0209: ("JPEGACTables", "JPEGACTables"),
        # IFD pointers
        EXIF_IFD_POINTER: ("IFDExif", "Exif IFD Pointer"),
        GPS_IFD_POINTER: ("IFDGPS", "GPS IFD Pointer"),
        INTEROP_IFD_POINTER: ("IFDInterop", "Interoperability IFD Pointer"),
    }

class ExifIFDEntry(BasicIFDEntry):
    TAG_INFO = {
        # version
        0x9000: ("ExifVersion", "Exif version"),
        0xA000: ("FlashpixVersion", "Supported Flashpix version"),
        # image data characteristics
        0xA001: ("ColorSpace", "Color space information"),
        # image configuration
        0x9101: ("ComponentsConfiguration", "Meaning of each component"),
        0x9102: ("CompressedBitsPerPixel", "Image compression mode"),
        0xA002: ("PixelXDimension", "Valid image width"),
        0xA003: ("PixelYDimension", "Valid image height"),
        # user information
        0x927C: ("MakerNote", "Manufacturer notes"),
        0x9286: ("UserComment", "User comments"),
        # related file information
        0xA004: ("RelatedSoundFile", "Related audio file"),
        # date and time
        0x9003: ("DateTimeOriginal", "Date and time of original data generation"),
        0x9004: ("DateTimeDigitized", "Date and time of digital data generation"),
        0x9290: ("SubSecTime", "DateTime subseconds"),
        0x9291: ("SubSecTimeOriginal", "DateTimeOriginal subseconds"),
        0x9292: ("SubSecTimeDigitized", "DateTimeDigitized subseconds"),
        # picture-taking conditions
        0x829A: ("ExposureTime", "Exposure time"),
        0x829D: ("FNumber", "F number"),
        0x8822: ("ExposureProgram", "Exposure program"),
        0x8824: ("SpectralSensitivity", "Spectral sensitivity"),
        0x8827: ("ISOSpeedRatings", "ISO speed rating"),
        0x8828: ("OECF", "Optoelectric conversion factor"),
        0x9201: ("ShutterSpeedValue", "Shutter speed"),
        0x9202: ("ApertureValue", "Aperture"),
        0x9203: ("BrightnessValue", "Brightness"),
        0x9204: ("ExposureBiasValue", "Exposure bias"),
        0x9205: ("MaxApertureValue", "Maximum lens aperture"),
        0x9206: ("SubjectDistance", "Subject distance"),
        0x9207: ("MeteringMode", "Metering mode"),
        0x9208: ("LightSource", "Light source"),
        0x9209: ("Flash", "Flash"),
        0x920A: ("FocalLength", "Lens focal length"),
        0x9214: ("SubjectArea", "Subject area"),
        0xA20B: ("FlashEnergy", "Flash energy"),
        0xA20C: ("SpatialFrequencyResponse", "Spatial frequency response"),
        0xA20E: ("FocalPlaneXResolution", "Focal plane X resolution"),
        0xA20F: ("FocalPlaneYResolution", "Focal plane Y resolution"),
        0xA210: ("FocalPlaneResolutionUnit", "Focal plane resolution unit"),
        0xA214: ("SubjectLocation", "Subject location"),
        0xA215: ("ExposureIndex", "Exposure index"),
        0xA217: ("SensingMethod", "Sensing method"),
        0xA300: ("FileSource", "File source"),
        0xA301: ("SceneType", "Scene type"),
        0xA302: ("CFAPattern", "CFA pattern"),
        0xA401: ("CustomRendered", "Custom image processing"),
        0xA402: ("ExposureMode", "Exposure mode"),
        0xA403: ("WhiteBalance", "White balance"),
        0xA404: ("DigitalZoomRatio", "Digital zoom ratio"),
        0xA405: ("FocalLengthIn35mmFilm", "Focal length in 35 mm film"),
        0xA406: ("SceneCaptureType", "Scene capture type"),
        0xA407: ("GainControl", "Gain control"),
        0xA408: ("Contrast", "Contrast"),
        0xA409: ("Saturation", "Saturation"),
        0xA40A: ("Sharpness", "Sharpness"),
        0xA40B: ("DeviceSettingDescription", "Device settings description"),
        0xA40C: ("SubjectDistanceRange", "Subject distance range"),
        # other tags
        0xA420: ("ImageUniqueID", "Unique image ID"),
    }

class GPSIFDEntry(BasicIFDEntry):
    TAG_INFO = {
        0x0000: ("GPSVersionID", "GPS tag version"),
        0x0001: ("GPSLatitudeRef", "North or South Latitude"),
        0x0002: ("GPSLatitude", "Latitude"),
        0x0003: ("GPSLongitudeRef", "East or West Longitude"),
        0x0004: ("GPSLongitude", "Longitude"),
        0x0005: ("GPSAltitudeRef", "Altitude reference"),
        0x0006: ("GPSAltitude", "Altitude"),
        0x0007: ("GPSTimeStamp", "GPS time (atomic clock)"),
        0x0008: ("GPSSatellites", "GPS satellites used for measurement"),
        0x0009: ("GPSStatus", "GPS receiver status"),
        0x000A: ("GPSMeasureMode", "GPS measurement mode"),
        0x000B: ("GPSDOP", "Measurement precision"),
        0x000C: ("GPSSpeedRef", "Speed unit"),
        0x000D: ("GPSSpeed", "Speed of GPS receiver"),
        0x000E: ("GPSTrackRef", "Reference for direction of movement"),
        0x000F: ("GPSTrack", "Direction of movement"),
        0x0010: ("GPSImgDirectionRef", "Reference for direction of image"),
        0x0011: ("GPSImgDirection", "Direction of image"),
        0x0012: ("GPSMapDatum", "Geodetic survey data used"),
        0x0013: ("GPSDestLatitudeRef", "Reference for latitude of destination"),
        0x0014: ("GPSDestLatitude", "Latitude of destination"),
        0x0015: ("GPSDestLongitudeRef", "Reference for longitude of destination"),
        0x0016: ("GPSDestLongitude", "Longitude of destination"),
        0x0017: ("GPSDestBearingRef", "Reference for bearing of destination"),
        0x0018: ("GPSDestBearing", "Bearing of destination"),
        0x0019: ("GPSDestDistanceRef", "Reference for distance to destination"),
        0x001A: ("GPSDestDistance", "Distance to destination"),
        0x001B: ("GPSProcessingMethod", "Name of GPS processing method"),
        0x001C: ("GPSAreaInformation", "Name of GPS area"),
        0x001D: ("GPSDateStamp", "GPS date"),
        0x001E: ("GPSDifferential", "GPS differential correction"),
    }

class InteropIFDEntry(BasicIFDEntry):
    TAG_INFO = {
        0x0001: ("InteroperabilityIndex", "Interoperability Identification"),
    }

class IFD(SeekableFieldSet):
    EntryClass = IFDEntry
    def __init__(self, parent, name, base_addr):
        self.base_addr = base_addr
        SeekableFieldSet.__init__(self, parent, name)

    def createFields(self):
        yield UInt16(self, "count", "Number of entries")
        count = self["count"].value
        if count == 0:
            raise ParserError("IFDs cannot be empty.")
        for i in xrange(count):
            yield self.EntryClass(self, "entry[]")
        yield UInt32(self, "next", "Offset to next IFD")
        for i in xrange(count):
            entry = self['entry[%d]'%i]
            if 'offset' not in entry:
                continue
            self.seekByte(entry['offset'].value+self.base_addr//8, relative=False)
            count = entry['count'].value
            name = "value[%s]"%i
            if issubclass(entry.value_cls, Bytes):
                yield entry.value_cls(self, name, count)
            else:
                if count > 1:
                    name += "[]"
                for i in xrange(count):
                    yield entry.value_cls(self, name)

    def getEntryValues(self, entry):
        n = int(entry.name.rsplit('[',1)[1].strip(']'))
        if 'offset' in entry:
            field = 'value[%d]'%n
            base = self
        else:
            field = 'value'
            base = entry
        if field in base:
            return [base[field]]
        else:
            return base.array(field)

class ExifIFD(IFD):
    EntryClass = ExifIFDEntry

class GPSIFD(IFD):
    EntryClass = GPSIFDEntry

class InteropIFD(IFD):
    EntryClass = InteropIFDEntry

IFD_TAGS = {
    IFDEntry.EXIF_IFD_POINTER: ('exif', ExifIFD),
    IFDEntry.GPS_IFD_POINTER: ('exif_gps', GPSIFD),
    IFDEntry.INTEROP_IFD_POINTER: ('exif_interop', InteropIFD),
}

def TIFF(self):
    iff_start = self.absolute_address + self.current_size
    yield String(self, "endian", 2, "Endian ('II' or 'MM')", charset="ASCII")
    if self["endian"].value not in ("II", "MM"):
        raise ParserError("Invalid endian!")
    if self["endian"].value == "II":
       self.endian = LITTLE_ENDIAN
    else:
       self.endian = BIG_ENDIAN

    yield UInt16(self, "version", "TIFF version number")
    yield UInt32(self, "img_dir_ofs", "Next image directory offset")
    offsets = [(self['img_dir_ofs'].value, 'ifd[]', IFD)]
    while offsets:
        offset, name, klass = offsets.pop(0)
        self.seekByte(offset+iff_start//8, relative=False)
        ifd = klass(self, name, iff_start)
        yield ifd
        for entry in ifd.array('entry'):
            tag = entry['tag'].value
            if tag in IFD_TAGS:
                name, klass = IFD_TAGS[tag]
                offsets.append((ifd.getEntryValues(entry)[0].value, name+'[]', klass))
        if ifd['next'].value != 0:
            offsets.append((ifd['next'].value, 'ifd[]', IFD))

class Exif(SeekableFieldSet):
    def createFields(self):
        # Headers
        yield String(self, "header", 6, "Header (Exif\\0\\0)", charset="ASCII")
        if self["header"].value != "Exif\0\0":
            raise ParserError("Invalid EXIF signature!")
        iff_start = self.absolute_address + self.current_size
        ifds = []
        for field in TIFF(self):
            yield field
            if isinstance(field, IFD):
                ifds.append(field)

        for ifd in ifds:
            data = {}
            for i, entry in enumerate(ifd.array('entry')):
                data[entry['tag'].display] = entry
            if 'JPEGInterchangeFormat' in data and 'JPEGInterchangeFormatLength' in data:
                offs = ifd.getEntryValues(data['JPEGInterchangeFormat'])[0].value
                size = ifd.getEntryValues(data['JPEGInterchangeFormatLength'])[0].value
                if size == 0: continue
                self.seekByte(offs + iff_start//8, relative=False)
                yield SubFile(self, "thumbnail[]", size, "Thumbnail (JPEG file)", mime_type="image/jpeg")

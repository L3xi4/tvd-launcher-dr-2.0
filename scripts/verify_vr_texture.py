"""Exercise real D3D11 uploads/readback on Windows WARP, without a headset.

This validates COM/ABI, RGBA layout, resource reuse and cleanup, not SteamVR or a HMD.
"""
import ctypes as C
from pathlib import Path
import sys


def verify(root):
    sys.path.insert(0, str(root / 'app'))
    import vr
    import overlay
    assert C.sizeof(vr._Texture) == 16
    texture = vr._D3DTexture(software=True)
    staging = C.c_void_p()
    try:
        width, height = 16, 8
        frame = bytearray(bytes([255, 0, 0, 255]) * width * height)
        handle = texture.upload(frame, width, height)
        for i in range(2000):
            frame[:4] = bytes([i % 256, 23, 47, 255])
            assert texture.upload(frame, width, height) == handle
        class Desc(C.Structure):
            _fields_ = [(name, C.c_uint32) for name in (
                'width', 'height', 'mips', 'array', 'format', 'samples', 'quality',
                'usage', 'bind', 'cpu', 'misc')]
        desc = Desc(width, height, 1, 1, 28, 1, 0, 3, 0, 0x20000, 0)
        vr._check_hr(vr._com(texture.device, 5, C.c_int32, C.POINTER(Desc), C.c_void_p,
                            C.POINTER(C.c_void_p))(texture.device, C.byref(desc), None,
                                                  C.byref(staging)), 'staging texture')
        vr._com(texture.context, 47, None, C.c_void_p, C.c_void_p)(
            texture.context, staging, texture.texture)
        class Mapped(C.Structure):
            _fields_ = [('data', C.c_void_p), ('row_pitch', C.c_uint32), ('depth_pitch', C.c_uint32)]
        mapped = Mapped()
        vr._check_hr(vr._com(texture.context, 14, C.c_int32, C.c_void_p, C.c_uint32,
                            C.c_uint32, C.c_uint32, C.POINTER(Mapped))(
            texture.context, staging, 0, 1, 0, C.byref(mapped)), 'Map readback')
        try:
            for y in range(height):
                assert C.string_at(mapped.data + y * mapped.row_pitch, width * 4) == frame[y * width * 4:(y + 1) * width * 4]
        finally:
            vr._com(texture.context, 15, None, C.c_void_p, C.c_uint32)(texture.context, staging, 0)
        # Exercise the actual GDI+ panel and resizing to its real dimensions.
        canvas = vr._Canvas()
        w, h, ops = overlay.layout_vr({'kmh': 120, 'gear': 4, 'rpm': 6000, 'rpm_max': 8000, 't': 42})
        texture.upload(canvas.render(w, h, ops), w, h)
        assert texture.size == (900, 320)
        try:
            texture.upload(bytearray(3), 1, 1)
            raise AssertionError('invalid frame accepted')
        except ValueError:
            pass
    finally:
        if staging.value:
            vr._com(staging, 2, C.c_uint32)(staging)
        texture.close()
        texture.close()
    assert not texture.device.value and not texture.context.value and not texture.texture.value
    print('PASS: Windows D3D11 2000 uploads, resource reuse, RGBA pixel readback, GDI+ panel, resize and cleanup')


if __name__ == '__main__':
    verify(Path(sys.argv[1]))

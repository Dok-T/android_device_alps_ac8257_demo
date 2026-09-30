#!/usr/bin/env python3
"""
mkboot.py - boot.img stock UJC201 + menu de demarrage (bootmenu en /init du ramdisk)

  1. noyau : skip_initramfs -> want_initramfs (sinon le LK fait ignorer le ramdisk du boot),
     recompression gzip -9, DTB colle en queue conserve ;
  2. ramdisk cpio (gzip) : /init = bootmenu, /dev/console, /proc, /sys, /dev, /system_root ;
  3. en-tete boot v1 et cmdline inchanges ;
  4. footer AVB : vbmeta du boot stock repose (taille d'image mise a jour) ; la partition garde
     sa taille (10 Mo sur le firmware 250718).

Usage : mkboot.py <boot stock.img> <sortie.img> [--init tools/bootmenu/bootmenu]
Retour arriere : fastboot flash boot <boot stock.img>
"""
import argparse, gzip, hashlib, os, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from ujc201_postprocess import unpack, repack, cpio_build  # noqa: E402

def log(*a): print('[mkboot]', *a)

def ent(ino, name, mode, data=b'', rdev=(0, 0)):
    # champs newc : ino mode uid gid nlink mtime filesize devmaj devmin rdevmaj rdevmin namesize check
    nlink = 2 if mode & 0o040000 else 1
    return [[ino, mode, 0, 0, nlink, 0, len(data), 0, 0, rdev[0], rdev[1], 0, 0], name, bytearray(data)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stock'); ap.add_argument('out')
    ap.add_argument('--init', default=os.path.join(HERE, 'bootmenu'))
    a = ap.parse_args()

    img = open(a.stock, 'rb').read()
    part = len(img)
    foot = img[-64:]
    if foot[:4] != b'AVBf':
        sys.exit('pas de footer AVB : donner le dump brut de la partition boot (10 Mo)')
    _, _, _, orig, voff, vsz = struct.unpack('>4sIIQQQ', foot[:36])
    vbmeta = img[voff:voff + vsz]
    assert vbmeta[:4] == b'AVB0'
    p = unpack(img[:orig])
    if p['ramdisk']:
        sys.exit('le boot a deja un ramdisk (%d octets) : partir du boot STOCK' % len(p['ramdisk']))

    # 1. noyau
    k = p['kernel']
    assert k[:2] == b'\x1f\x8b', 'noyau gzip attendu (Image.gz-dtb)'
    d = zlib.decompressobj(31); raw = d.decompress(k); tail = d.unused_data
    n = raw.count(b'skip_initramfs\0')
    if n != 1:
        sys.exit('motif skip_initramfs trouve %d fois (attendu 1)' % n)
    raw = raw.replace(b'skip_initramfs\0', b'want_initramfs\0')
    c = zlib.compressobj(9, zlib.DEFLATED, 31, 9)
    p['kernel'] = c.compress(raw) + c.flush() + tail
    log('noyau : want_initramfs, %d -> %d octets (DTB en queue : %d)' % (len(k), len(p['kernel']), len(tail)))

    # 2. ramdisk
    init = open(a.init, 'rb').read()
    assert init[:4] == b'\x7fELF' and init[18] == 0xB7, 'bootmenu doit etre un ELF aarch64'
    ents = [ent(300001, b'dev', 0o040755), ent(300002, b'dev/console', 0o020600, rdev=(5, 1)),
            ent(300003, b'proc', 0o040755), ent(300004, b'sys', 0o040755),
            ent(300005, b'system_root', 0o040755), ent(300006, b'init', 0o100750, init),
            ent(0, b'TRAILER!!!', 0)]
    p['ramdisk'] = gzip.compress(cpio_build(ents), 9, mtime=0)
    log('ramdisk : %d octets (bootmenu %d)' % (len(p['ramdisk']), len(init)))

    # 3. image + 4. footer AVB
    out = repack(p)
    vo = (len(out) + 4095) // 4096 * 4096
    free = part - 64 - (vo + len(vbmeta))
    if free < 0:
        sys.exit('trop grand pour la partition boot : %d octets en trop' % -free)
    o = bytearray(part); o[:len(out)] = out; o[vo:vo + len(vbmeta)] = vbmeta
    o[-64:] = b'AVBf' + struct.pack('>IIQQQ', 1, 0, len(out), vo, len(vbmeta)) + b'\0' * 28
    open(a.out, 'wb').write(o)
    log('ecrit : %s (%d octets, marge %d octets)' % (a.out, part, free))
    log('sha256 :', hashlib.sha256(o).hexdigest())

if __name__ == '__main__':
    main()

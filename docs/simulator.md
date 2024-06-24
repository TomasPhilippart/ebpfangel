# Simulator

## Installation

```shell
$ python3 -m pip install -r requirements.txt
```

## Encrypt files

```shell
# encrypt temporary files in /tmp/tmpxxx
$ ./simulator.py --password xu18d7wfe2edt

# encrypt files in given directory
$ ./simulator --dir /path/to/dir --password xu18d7wfe2edt
```

## Decrypt files

```shell
# decrypt temporary files in /tmp/tmpxxx
$ ./simulator.py --mode decrypt --password xu18d7wfe2edt

# decrypt files in given directory
$ ./simulator.py --mode decrypt --dir /path/to/dir --password xu18d7wfe2edt
```

## Tracing python execution flow

```shell
$ ./simulator.py --password b12hn736bxe & sudo uflow -l python $!
```

## View encrypted files

```shell
$ xxd UTC.aes

00000000: 4145 5302 0000 1b43 5245 4154 4544 5f42  AES....CREATED_B
00000010: 5900 7079 4165 7343 7279 7074 2036 2e30  Y.pyAesCrypt 6.0
00000020: 2e30 0080 0000 0000 0000 0000 0000 0000  .0..............
00000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000040: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000060: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000070: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000080: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000090: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000000a0: 0000 0000 0000 f7d0 323f b478 ca7d 211c  ........2?.x.}!.
000000b0: aa4a 3ef4 ffa7 f154 8553 7128 93e9 4d9d  .J>....T.Sq(..M.
000000c0: 34be 8dcb 4a92 a35e 7338 dc0c 7791 0a54  4...J..^s8..w..T
000000d0: 3466 fd28 646f bc3f ddd2 aecf d238 ae56  4f.(do.?.....8.V
000000e0: 4080 bb9f a40b c9f3 648f 7b32 79ed 5cd7  @.......d.{2y.\.
000000f0: 7429 40e8 5468 ee62 2b2d 6637 1ec7 9522  t)@.Th.b+-f7..."
00000100: b4d9 3bd2 0df9 72c5 db10 bf1f 3314 cc9c  ..;...r.....3...
00000110: 904b 191f 1f6c 2ea8 c246 eef7 3ffe f8ac  .K...l...F..?...
00000120: 802b 66ce f193 32a0 f452 d56d 472b 6363  .+f...2..R.mG+cc
00000130: 0c47 454d d950 9d55 7c96 c968 d8f4 536c  .GEM.P.U|..h..Sl
00000140: f120 19cb c166 e198 11f4 41ed 7410 81f5  . ...f....A.t...
00000150: c6f7 2c38 c40f 1ed5 01bf a44c 19c5 866e  ..,8.......L...n
00000160: 9908 d6be 64f1 a6e7 73e4 8a99 9898 2f19  ....d...s...../.
00000170: 15df 1cab 2eef 27e2 2036 6245 f546 386c  ......'. 6bE.F8l
00000180: 17bf 4dbf 0aac 0620 f849 1426 1a72 e67a  ..M.... .I.&.r.z
00000190: c204 7612 111d b86b aa83 1e7a 5ad8 76e7  ..v....k...zZ.v.
000001a0: 12e0 22c0 3b22 21                        ..".;"!
```

import sys, struct, socket, math, random, time

if sys.version_info.major < 3:
    print('This is a python3 script')
    sys.exit(-1)

objects = []
frame_num = 0
pkt_size = 1024

try:
    s_addr = sys.argv[1]
    s_port = int(sys.argv[2])
    for a in sys.argv[3:]:
        assert len(a) <= 24
        objects.append({'name': a})
    assert len(objects) > 0
except (IndexError, ValueError, AssertionError) as e:
    print('Usage: python3 DemoDataSource.py 127.0.0.1 12345 ObjectName1 ObjectName2_BoneName ...')
    print('Names must be <= 24 characters')
    sys.exit(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def SendUpdate():
    global frame_num
    objsperpacket = (pkt_size - 5) // 75
    npackets = (len(objects) + objsperpacket - 1) // objsperpacket
    oi = 0
    for pktidx in range(npackets):
        objsinthispacket = min(objsperpacket, len(objects) - oi)
        pkt = struct.pack('<IB', frame_num, objsinthispacket)
        for oip in range(objsinthispacket):
            o = objects[oi]
            pkt += struct.pack('<BH24s6d', 0, 72, o['name'].encode('ascii', 'ignore'),
                o['tx'], o['ty'], o['tz'], o['rx'], o['ry'], o['rz'])
            oi += 1
        assert len(pkt) == objsinthispacket * 75 + 5
        assert len(pkt) <= pkt_size
        print(pkt.hex())
        sock.sendto(pkt, (s_addr, s_port))
    frame_num += 1

for o in objects:
    o['tx'] = random.uniform(-1.0, -0.5)
    o['ty'] = random.uniform(-0.2, 0.2)
    o['tz'] = random.uniform(0.0, 2.0)
    for f in ['vx', 'vy', 'vz']:
        o[f] = random.uniform(-0.01, 0.01)
    for f in ['rx', 'ry', 'rz']:
        o[f] = random.uniform(0.0, 2.0 * math.pi)
    for f in ['srx', 'sry', 'srz']:
        o[f] = random.uniform(-0.01, 0.01)

def MoveObj(o):
    for t, v in zip(['tx', 'ty', 'tz', 'rx', 'ry', 'rz'], ['vx', 'vy', 'vz', 'srx', 'sry', 'srz']):
        o[t] += o[v]
    o['tx'] += 0.6
    for t, v in zip(['tx', 'ty', 'tz'], ['vx', 'vy', 'vz']):
        if o[t] >= 0.2:
            o[v] -= 0.001
        if o[t] <= (0.8 if t == 'tz' else -0.2):
            o[v] += 0.001
    o['tx'] -= 0.6
    o['tz'] = 1.0
    for r in ['rx', 'ry', 'rz']:
        if o[r] >= 2.0 * math.pi:
            o[r] -= 2.0 * math.pi
        elif o[r] < 0.0:
            o[r] += 2.0 * math.pi

try:
    while True:
        time.sleep(1.0 / 60.0)
        for o in objects:
            MoveObj(o)
        SendUpdate()
except KeyboardInterrupt:
    print('^C Exiting')

sock.close()

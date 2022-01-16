import socket, struct, math
from mathutils import Vector

sock = None

frame_num = 0
vicon_state = {}

def ParsePacket(d):
    global frame_num, vicon_state
    try:
        assert len(d) <= 1024
        assert len(d) >= 5
        frame_num, items = struct.unpack('!IB', d[0:5])
        assert items >= 1 and items <= 50
        a = 5
        rec_items = []
        for i in range(items):
            assert len(d) >= a+3
            item_id, item_sz = struct.unpack('!BH', d[a:a+3])
            a += 3
            assert item_id == 0
            assert item_sz == 72
            assert a + item_sz <= len(d)
            item_name, tx, ty, tz, rx, ry, rz = struct.unpack('!24s6d', d[a:a+item_sz])
            a += item_sz
            assert all(math.isfinite(f) and -1e6 < f < 1e6 for f in (tx, ty, tz, rx, ry, rz))
            vicon_state[item_name] = (Vector(tx, ty, tz), Vector(rx, ry, rz))
            rec_items.append(item_name)
        assert a == len(d)
        dotdotdot = False
        if len(rec_items) > 3:
            rec_items = rec_items[0:3]
            dotdotdot = True
        print('Vicon UDP pkt frame {:012d} items {}'.format(frame_num,
            ''.join(rec_items) + ('...' if dotdotdot else '')))
    except AssertionError as e:
        print(e)

def ReceiveUpdate():
    global sock
    while True:
        try:
            d = sock.recvfrom(1024)
            ParsePacket(d)
        except BlockingIOError:
            return

def NetConnect(port):
    global sock
    if sock is None:
        print('Binding to port {}'.format(port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.bind(('', port))
    else:
        print('Closing socket')
        sock.close()
        del sock
        sock = None
    
def NetIsConnected():
    return sock is not None

def NetStatusMsg():
    return 'TODO'

import socket, struct, math
from mathutils import Vector, Euler

sock = None
frame_num = -1
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
            item_name = item_name.decode('ascii').rstrip('\x00')
            a += item_sz
            assert all(math.isfinite(f) and -1e6 < f < 1e6 for f in (tx, ty, tz, rx, ry, rz))
            vicon_state[item_name] = (Vector((tx, ty, tz)), Euler((rx, ry, rz), 'XYZ'))
            rec_items.append(item_name)
        assert a == len(d)
        dotdotdot = False
        if len(rec_items) > 3:
            rec_items = rec_items[0:3]
            dotdotdot = True
        print('Vicon UDP pkt frame {:012d} items {}'.format(frame_num,
            ''.join(rec_items) + ('...' if dotdotdot else '')))
    except AssertionError as e:
        print('Invalid packet received: ' + d.hex())
        raise

def ReceiveUpdate():
    global sock
    if sock is None:
        return
    while True:
        try:
            d = sock.recvfrom(1024)
            #print('Received packet from ' + str(d[1]))
            ParsePacket(d[0])
        except BlockingIOError:
            return

def NetConnect(port):
    global sock
    assert sock is None
    print('Binding to port {}'.format(port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    sock.bind(('', port))
    
def NetDisconnect():
    global sock, frame_num, vicon_state
    assert sock is not None
    print('Closing socket')
    sock.close()
    del sock
    sock = None
    vicon_state.clear()
    frame_num = -1
    
def NetIsConnected():
    return sock is not None

def NetStatusMsg():
    if sock is None:
        return 'Not connected'
    return 'Frame {}, {} objs'.format(frame_num, len(vicon_state))

def Network_register():
    pass
    
def Network_unregister():
    global sock
    if sock is not None:
        sock.close()
        del sock

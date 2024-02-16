import numpy as np
import sys
sys.path.append('/usr/local/opt/opencv3/lib/python2.7/site-packages')
import cv2
import xmltodict, json
import urllib2

# url2 = "http://cs.mwsu.edu/~griffin/p-lot/api/proxy.php?route=pk-lot-def"
# lots = json.loads(urllib2.urlopen(url2).read())
# lot_ids = lots['data'].keys()

# print(lot_ids)

# spaces = lots['data'][lot_ids[0]].keys()
# data = lots['data'][lot_ids[0]]

# print(data)

# idx = spaces.index('lot_id')
# del spaces[idx]
# spaces = map(int,spaces)
# spaces = sorted(spaces)

# print(spaces)

#{u'rectangle': {u'angle': u'-86', u'center': {u'y': u'538', u'x': u'653'}, u'size': {u'h': u'54', u'w': u'65'}}, 
#u'space': [{u'y': u'569', u'x': u'624'}, {u'y': u'509', u'x': u'629'}, {u'y': u'507', u'x': u'683'}, {u'y': u'570', u'x': u'679'}]}

def pklotToCVarray(dict):
    coords = []
    for xy in dict:
        coords.append([int(xy['x']),int(xy['y'])])
    return coords

def url_to_image(url):
	# download the image, convert it to a NumPy array, and then read
	# it into OpenCV format
	resp = urllib2.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
 
	# return the image
	return image

def readXML(fname):

    xml = urllib2.urlopen(fname).read()

    lot = xmltodict.parse(xml)

    lot_id = lot['parking']['@id']

    #OrderedDict([(u'@id', u'40'), (u'@occupied', u'1'), (u'rotatedRect', OrderedDict([(u'center', OrderedDict([(u'@x', u'1031'), (u'@y', u'57')])), (u'size', OrderedDict([(u'@w', u'55'), (u'@h', u'58')])), (u'angle', OrderedDict([(u'@d', u'-83')]))])), (u'contour', OrderedDict([(u'point', [OrderedDict([(u'@x', u'1005'), (u'@y', u'39')]), OrderedDict([(u'@x', u'1000'), (u'@y', u'81')]), OrderedDict([(u'@x', u'1058'), (u'@y', u'88')]), OrderedDict([(u'@x', u'1064'), (u'@y', u'33')])])]))])

    lotJson = {}
    lotSnapshot = {}

    for space in lot['parking']['space']:
        id = space['@id']
        if '@occupied' in space:
            occupied = space['@occupied']
        else:
            occupied = 0
        
        rotatedRect = {}
        x = space['rotatedRect']['center']['@x']
        y = space['rotatedRect']['center']['@y']
        w = space['rotatedRect']['size']['@w']
        h = space['rotatedRect']['size']['@h']
        d = space['rotatedRect']['angle']['@d']
    
        rotatedRect['center'] = {'x':x,'y':y}
        rotatedRect['size'] = {'w':w,'h':h}
        rotatedRect['angle'] = d
    
        contour = [] 
        if 'contour' in space:
            if 'point' in space['contour']:
                for p in space['contour']['point']:
                    contour.append({'x':p['@x'],'y':p['@y']})
        
        lotJson['lot_id'] = lot_id
        lotJson[id] = {}
        lotJson[id]['space'] = contour
        lotJson[id]['rectangle'] = rotatedRect
        lotSnapshot[id] = occupied
    return (lotJson,lotSnapshot)




files = json.loads(urllib2.urlopen('http://cs.mwsu.edu/~griffin/p-lot/api/proxy.php?route=pk-lot-image&lot_id=pucpr&weather=sunny&dayOfYear=315').read())
files_dict = {}

for file in files['data']:
    if not file['unix'] in files_dict:
        files_dict[file['unix']] = {}
    if 'xml' in file['name']:
        files_dict[file['unix']]['xml'] = file['url'] + file['path'] + file['name']
    else:
        files_dict[file['unix']]['jpg'] = file['url'] + file['path'] + file['name']


for unix,pair in files_dict.items():

    img = url_to_image(pair['jpg'])
    lotJson,lotSnapshot = readXML(pair['xml'])

    del lotJson['lot_id']

    #cv2.line(img,(0,0),(200,300),(255,255,255),50)
    #cv2.rectangle(img,(500,250),(1000,500),(0,0,255),15)
    #cv2.circle(img,(447,63), 63, (0,255,0), -1)
    for id,spot in lotJson.items():
        lotcoords = pklotToCVarray(spot['space'])

        if str(lotSnapshot[id]) == str(1):
            color = (0,0,255)
            line = 2
        else:
            color = (0,255,0)
            line = 1
        pts = np.array(lotcoords, np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(img, [pts], True, color, line)

    font = cv2.FONT_HERSHEY_SIMPLEX
    #cv2.putText(img,'OpenCV Tuts!',(10,500), font, 6, (200,255,155), 13, cv2.LINE_AA)
    cv2.imwrite('identified_images/'+unix+'.jpg',img)
    print('identified_images/'+unix+'.jpg')
    # cv2.imshow('image',img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    
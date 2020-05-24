import os
import re
import time
import itchat
from itchat.content import *

# {msg_id: (msg_from, msg_to, msg_time, msg_time_rec, msg_type, msg_content, msg_share_url)}
msg_dict = {}

# 文件存储目录
rev_tmp_dir = '/file/'
if not os.path.exists(rev_tmp_dir):
    os.mkdir(rev_tmp_dir)
face_bug = None


@itchat.msg_register([TEXT, PICTURE, MAP, CARD, SHARING, RECORDING, ATTACHMENT, VIDEO])
def handler_receive_msg(msg):
    global face_bug, msg_dict

    msg_time_rec = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    msg_id = msg['MsgId']
    msg_time = msg['CreateTime']
    msg_from = (itchat.search_friends(userName=msg['FromUserName']))['NickName']
    msg_content = None
    msg_share_url = None
    if msg['Type'] in ['Text', 'Friends']:
        msg_content = msg['Text']
    elif msg['Type'] in ['Recording', 'Attachment', 'Video', 'Picture']:
        msg_content = r'' + msg['FileName']
        msg['Text'](rev_tmp_dir + msg['FileName'])
    elif msg['Type'] in ['Card']:
        msg_content = msg['RecommendInfo']['NickName'] + r' 的名片'
    elif msg['Type'] in ['Map']:
        x, y, location = re.search(r'<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*', msg['OriContent']).group(1, 2, 3)
        if location is None:
            msg_content = r'维度:' + x.__str__() + ' 经度：' + y.__str__()
        else:
            msg_content = r'' + location
    elif msg['Type'] in ['Sharing']:
        msg_content = msg['Text']
        msg_share_url = msg['Url']
    face_bug = msg_content

    time_stamp = int(time.time())
    msg_dict[msg_id] = {'msg_from': msg_from,
                        'msg_time': msg_time,
                        'msg_timestamp': time_stamp,
                        'msg_time_rec': msg_time_rec,
                        'msg_type': msg['Type'],
                        'msg_content': msg_content,
                        'msg_share_url': msg_share_url
                        }
    keys = []
    for i in msg_dict:
        if time_stamp - msg_dict[i]['msg_timestamp'] > 120:
            keys.append(i)
    for key in keys:
        msg_dict.pop(key)


@itchat.msg_register([NOTE])
def send_msg_helper(msg):
    global face_bug
    if re.search(r'\<\!\[CDATA\[.*撤回了一条消息\]\]\>', msg['Content']) is not None:
        print('recall')
        old_msg_id = re.search(r'\<msgid\>(.*?)\<\/msgid\>', msg['Content']).group(1)
        old_msg = msg_dict[old_msg_id]
        if len(old_msg_id) < 11:
            itchat.send_file(rev_tmp_dir + face_bug, toUserName='filehelper')
            os.remove(rev_tmp_dir + face_bug)
        else:
            msg_body = old_msg['msg_from'] + ' 撤回了 ' + old_msg.get('msg_type') + ' 消息' + '\n' \
                       + old_msg['msg_time_rec'] + '\n' \
                       r'' + old_msg['msg_content']
            if old_msg['msg_type'] == 'Shareing':
                msg_body += '链接：' + old_msg['msg_share_url']

            itchat.send(msg_body, toUserName='filehelper')
            if old_msg['msg_type'] in ['Recording', 'Attachment', 'Video', 'Picture']:
                file = '@fil@%s' % (rev_tmp_dir + old_msg['msg_content'])
                itchat.send(msg=file, toUserName='filehelper')
                os.remove(rev_tmp_dir + old_msg['msg_content'])
        msg_dict.pop(old_msg_id)


def main():
    itchat.auto_login(enableCmdQR=2)
    itchat.run()


if __name__ == '__main__':
    main()

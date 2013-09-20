#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
from email.header import decode_header
import getpass
import poplib
import sys

def _info(pop3):
  num, size = pop3.stat()
  print '{0} mail ({1} bytes.)'.format(str(num), str(size))


def _list(pop3, search=False):
    if search:
        word = raw_input('input search word: ')

    res, data, octets = pop3.list()
    print res
    index = [i.split(' ', 1)[0] for i in data]
    for i in index:
        if not search:
            print 'mail-' + str(i) + ':'

        for header in pop3.top(i, 0)[1]:
            encoded = '  '
            if header.lower().startswith(('subject:', 'from:')):
                for header_parts in decode_header(header):
                    tmp, encoding = header_parts
                    if encoding is not None:
                        tmp = " " + tmp.decode(encoding)
          
                    encoded += tmp

                if not search:
                    print encoded.encode('utf-8')
                else:
                    if encoded.find(word.decode('utf-8')) != -1:
                        print 'mail-' + str(i) + ':'
                        print encoded.encode('utf-8')


def _delete(pop3):
    print 'input numbers to delete(split by white space or TAB)'
    delete = raw_input('(ex: 1 5-10 12): ')
    for number_to_delete in delete.split():
        l = len(number_to_delete)
        if l == 1:
            try:
                n = int(number_to_delete)
            except ValueError:
                print 'ignoring...', number_to_delete
                continue

            try:
                print 'deleting...', number_to_delete
                print pop3.dele(n)
            except Exception as e:
                #print e
                print "error occured. '%s' is wrong number?" % number_to_delete

        elif l == 3 and number_to_delete.find('-') == 1:
            first, last = number_to_delete.split('-', 1)
            try:
                first_num = int(first) 
                last_num = int(last) 
                if last_num < first_num:
                    raise ValueError
            except ValueError:
                print 'ignoring...', number_to_delete
                continue

            for i in range(first_num, last_num + 1):
                try:
                    print 'deleting...', i
                    print pop3.dele(i)
                except Exception as e:
                    #print e
                    print "error occured. '%s' include wrong number?" % number_to_delete
                    continue

        else:
            print 'ignoring...', number_to_delete
            continue

  
def _rset(pop3):
    confirm = raw_input('unset all delete flag[y/n]: ')
    if confirm.lower() in ('y', "yes"):
        print pop3.rset()
    else:
        print "cancel..."


def _help():
    print 'q, quit: quit'
    print 'i, info: show inbox information'
    print 'l, list: show index, from-address and subject of all mails'
    print 's, search: search mails from from-address and subject'
    print 'd, dele: set flag to delete'
    print 'r, rset: unset all delete flag'
 

if __name__ == '__main__':
    usage = "usage: %prog [options] servername"
    parser = OptionParser(usage)
    parser.add_option("-u", dest="username", help="pop3 user name")
    parser.add_option("-p", dest="port", help="pop3 server port", type='int')
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments.')

    server = args[0]
    username = getpass.getuser()
    if options.username:
        username = options.username

    port = 110
    if options.port:
        port = options.port

    password = getpass.getpass('input pop3 password: ')
  
    pop3 = None
    try:
        print 'connecting to ' + server + ':' + str(port)
        try:
            pop3 = poplib.POP3(server, port)
            pop3.user(username)
            pop3.pass_(password)
        except Exception as e:
            print 'confirm server, port, user and password...'
            sys.exit(e)

        print 'connected'
        print pop3.getwelcome()
        _info(pop3)

        while True:
            cmd = raw_input('input command: ')
            if cmd in ('q', 'quit'):
                break
            elif cmd in ('i', 'info'):
                _info(pop3)
            elif cmd in ('l', 'list'):
                _list(pop3)
            elif cmd in ('s', 'search'):
                _list(pop3, True)
            elif cmd in ('d', 'dele'):
                _delete(pop3)
            elif cmd in ('r', 'rset'):
                _rset(pop3)
            else:
                _help()

    except Exception as e:
        #print e
        raise
    finally:
        print 'quit'
        if pop3 is not None:
            pop3.quit()
 


from gevent.pywsgi import WSGIServer


from multiprocessing import cpu_count, Process

from flask import Flask, jsonify, request

from flask_cors import CORS

import json
from ldap3 import Server, Connection,SUBTREE
ldap_host = 'LDAP://LTDC.theil.com' #ldap服务器地址
ldap_port = 389 #默认389
ldap_admin_user = 'cimtheil@theil.com' #ldap管理员账户用户名
ldap_admin_password = 'Theil@4893701' #ldap管理员账户密码
ldap_base_search = 'DC=theil,DC=com' #查询域

app = Flask(__name__)
CORS(app)
@app.route('/ldap/', methods=['POST'],strict_slashes=False)

def ldap_auth():
    '''
    ldap验证方法
    :param username: 用户名
    :param password: 密码
    :return: 
    '''
    username = request.get_json()[0]['username']    
    password = request.get_json()[0]['password']    
    s = Server(host=ldap_host, port=ldap_port, use_ssl=False, get_info='ALL')

    #连接ldap服务器
    ldapz_admin_connection = Connection(s, user=ldap_admin_user, password=ldap_admin_password, auto_bind='NONE',
                                        version=3,
                                        authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True,
                                        check_names=True,
                                        read_only=False, lazy=False,
                                        raise_exceptions=False)


    # 连上以后必须bind才能有值
    ldapz_admin_connection.bind()


    # 这个是为了查询你输入的用户名的入口搜索地址
    res = ldapz_admin_connection.search(search_base=ldap_base_search,
                                        search_filter='(sAMAccountName={})'.format(username),
                                        search_scope=SUBTREE,
                                        attributes=['cn', 'givenName', 'mail', 'sAMAccountName'],
                                        )

    try:
        if res:
            entry = ldapz_admin_connection.response[0]
#             logger.info(entry)
            dn = entry['dn']
            attr_dict = entry['attributes']
#             logger.info('attr_dic:%s' %attr_dict)

            try:
                # 这个connect是通过你的用户名和密码还有上面搜到的入口搜索来查询的
                conn2 = Connection(s, user=dn, password=password, check_names=True, lazy=False, raise_exceptions=False)
                conn2.bind()
                # logger.info(conn2.result["description"])

                # 正确-success 不正确-invalidCredentials
                if conn2.result["description"] == "success":
                    print(attr_dict)
                    result = [{'Result':'PASS','Message':'Password Matched'}]
#                     print('pass')
#                     logger.info("ldap auth pass!")
#                     return True
                    return jsonify(result)
                else:
                    print('error')
#                     logger.info("username or password error!")
                    result = [{'Result':'FAIL','Message':'Password error!'}]
                    return result
            except Exception as e:
                #print(e)
                result = [{'Result':'FAIL','Message':'Username error!'}]
                return result
    except KeyError as e:
        print(e)
#         logger.info("username or password error!")
#         logger.info(e)
        result = [{'Result':'FAIL','Message':'Username error!'}]
        return result
        


server = WSGIServer(('10.21.98.21',4444),app,log=None)
server.start()

def server_forever():
    server.start_accepting()
    server._stop_event.wait()




if __name__ == '__main__':

        print('----')
        for i in range(cpu_count()):
                p = Process(target=server_forever)
                p.start()

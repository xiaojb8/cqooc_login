import requests,time,json,random,hashlib
class course():
    def __init__(self,account,password):
        self.account = account
        self.password = password
        self.connect = requests.session()
    def Get_nonce(self):
        url = 'http://www.cqooc.net/user/login?ts=' + str(round(time.time() * 1000))
        nonce_text = self.connect.get(url=url)
        nonce_json = nonce_text.json()
        return nonce_json['nonce']
    def Get_Cnonce(self):
        cnonce = ''
        choice = '0123456789ABCDEF'
        for i in range(0, 16):
            cnonce += random.sample(choice, 1)[0]
        return cnonce
    def Sha256(self,str:str):
        sha256 = hashlib.sha256()
        sha256.update(str.encode('utf-8'))
        return sha256.hexdigest().upper()
    def Encrypt_Password(self,nonce,cnonce):
        pw = nonce
        pw += self.Sha256(self.password)
        pw += cnonce
        return self.Sha256(pw)
    def Login(self):
        nonce = self.Get_nonce()
        cnonce = self.Get_Cnonce()
        encrypted_password = self.Encrypt_Password(nonce,cnonce)
        url = 'http://www.cqooc.net/user/login?username=%s&password=%s&nonce=%s&cnonce=%s' %(self.account,encrypted_password,nonce,cnonce)
        data = {
            'username': self.account,
            'password': encrypted_password,
            'nonce': nonce,
            'cnonce': cnonce
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        login_result = self.connect.post(url=url,data=data,headers=headers)
        login_json = login_result.json()
        if (login_json['code'] == 31):
            print('登陆失败，请自行官网登陆一次后重试')
            exit()
        elif (login_json['code'] != 0):
            print(login_json['msg'] + '请重试!')
            exit()
        elif (login_json['xsid']):
            self.Xsid = login_json['xsid']
        else:
            print('登陆失败，服务器返回：' + login_json['msg'])
            exit()
        return
    def Get_Session(self):
        ts = str(round(time.time() * 1000))
        url = 'http://www.cqooc.net/user/session?xsid=%s&ts=%s' % (self.Xsid, ts)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        cookies = {
            'xsid': self.Xsid,
            'flogin': '1'
        }
        result = self.connect.get(url=url, headers=headers,cookies=cookies)
        result_json = result.json()
        self.user_id = result_json['id']
        return
    def Get_Course_List(self):
        self.Get_Session()
        url = 'http://www.cqooc.net/json/mcs?sortby=id&reverse=true&del=2&courseType=2&ownerId=%s&limit=50&ts=%s' % (
        self.user_id, str(round(time.time() * 1000)))
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Referer': 'http://www.cqooc.net/my/learn'}
        result = requests.get(url=url, headers=headers)
        course_list = json.loads(result.text)['data']
        list = []
        for course in course_list:
            course_id = course['course']['id']
            course_name = course['course']['title']
            list.append({'id': course_id,
                         'name': course_name})
        self.course_list = list
        return
if __name__ == '__main__':
    cqooc = course('账号','密码')
    cqooc.Login()
    cqooc.Get_Course_List()
    print(cqooc.course_list)


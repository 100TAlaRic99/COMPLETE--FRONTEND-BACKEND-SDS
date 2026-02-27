import requests
base='http://localhost:5000'
# register and ignore failure if already exists
try:
    r=requests.post(base+'/api/register', json={'username':'test2','email':'test2@example.com','password':'pass123'})
    print('register',r.status_code,r.text)
except Exception as e:
    print('register error', e)
# login
r=requests.post(base+'/api/login', json={'email':'test2@example.com','password':'pass123'})
print('login',r.status_code,r.text)
if r.status_code==200:
    token=r.json()['access_token']
    headers={'Authorization':f'Bearer {token}'}
    for analyzer in ['hybrid','vader','llm']:
        r2=requests.post(base+'/api/analyze', json={'text':'hello how are you','analyzer':analyzer},headers=headers)
        print('analyze', analyzer, r2.status_code, r2.text)

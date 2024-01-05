import time
import base64
from typing import List, Union
import os
from urllib.parse import urljoin
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
from common.config.path_utils import config





project_name = config['metersphere']['project_name']
test_plan_name = config['metersphere']['test_plan_name']
env_name = config['metersphere']['env_name']

def aes_encrypt(src: str, secret_key: str, iv: str) -> str:
    if not secret_key:
        raise ValueError("secret_key is empty")

    try:
        # Convert secret_key and iv to bytes
        secret_key = secret_key.encode('utf-8')
        iv = iv.encode('utf-8')

        # Create AES cipher object in CBC mode with PKCS5 padding
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)

        # Pad the input data to a multiple of AES block size
        padded_data = pad(src.encode('utf-8'), AES.block_size)

        # Encrypt the data
        encrypted = cipher.encrypt(padded_data)

        # Return the encrypted data as a base64-encoded string
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        raise RuntimeError("AES encrypt error") from e


def get_headers(access_key: str, secret_key: str) -> dict:
    timestamp = int(round(time.time() * 1000))

    combox_key = access_key + '|padding|' + str(timestamp)
    signature = aes_encrypt(combox_key, secret_key, access_key)

    return {'accessKey': access_key, 'signature': signature}


class MeterSphere:
    def __init__(self, domain: str, access_key: str, secret_key: str):
        self.domain = domain
        self.access_key = access_key
        self.secret_key = secret_key

    def _request(self, path: str, body: dict = None) -> Union[dict, list]:
        """
        :param path:
        :param body: if body is empty, will use get method
        :return:
        """
        #url = f"{self.domain.rstrip('/')}/{path.lstrip('/')}"
        url = urljoin(self.domain.rstrip('/'), path.lstrip('/'))
        #print(f"Requesting URL: {url}")
        headers = {'Content-Type': 'application/json', 'ACCEPT': 'application/json'}
        headers.update(get_headers(self.access_key, self.secret_key))

        if body:
            resp = requests.post(url, headers=headers, json=body)
        else:
            resp = requests.get(url, headers=headers)
        #print(resp.json())
        return resp.json()

    def get_test_plans_by_project_id(self, project_id: str) -> List[dict]:
        path = 'track/test/plan/list/all'
        # projectId 是必须的，其他参数完全没用😂
        body = {
            "projectId": project_id,
        }

        res = self._request(path, body)

        ret = []
        for r in res.get('data', []):
            ret.append({
                "id": r.get('id'),
                "name": r.get('name'),
                "status": r.get('status'),
            })

        return ret

    def get_test_plan_status(self, name: str, project_id: str) -> str:
        test_plans = self.get_test_plans_by_project_id(project_id)
        test_plan = list(filter(lambda item: item['name'] == name, test_plans))[0]
        return test_plan['status']

    def get_projects(self) -> List[dict]:
        path = '/setting/project/list'

        res = self._request(path)

        ret = []
        for r in res.get('data', []):
            ret.append({
                "name": r.get('name'),
                "id": r.get('id'),
            })

        return ret

    def get_envs_by_project_id(self, project_id: str):
        path = f'/api/environment/list/{project_id}'

        res = self._request(path)

        ret = []
        for r in res.get('data', []):
            ret.append({
                "name": r.get('name'),
                "id": r.get('id'),
            })

        return ret

    def run_test_plan(self, project_id: str, test_plan_id: str, env_id: str):
        path = f"/track/test/plan/run/save"

        body = {
            "mode": "serial",
            "reportType": "iddReport",
            # 遇到失败是否直接结束 testplan
            "onSampleError": False,
            "runWithinResourcePool": False,
            "envMap": {
                # project-id: env-id
                project_id: env_id,
            },
            "testPlanId": test_plan_id,
            "projectId": project_id,
            "userId": "dcr_wuwfb",
            "triggerMode": "MANUAL",
            "environmentType": "JSON",
            "environmentGroupId": "",
            "requestOriginator": "TEST_PLAN"
        }

        res = self._request(path, body)

        return res

    def get_test_plan_failure(self, test_plan_id: str):
        path = f"/test/plan/scenario/case/list/failure/{test_plan_id}"
        res = self._request(path)

        path = f'/test/plan/api/case/list/failure/{test_plan_id}'
        res2 = self._request(path)

        ret = res.get('data', [])
        ret.extend(res2.get('data', []))

        return ret

    def get_share_test_plan(self, domain: str, test_plan_id: str) -> str:
        path = '/share/info/generateShareInfoWithExpired'

        body = {"customData": test_plan_id, "shareType": "PLAN_REPORT"}

        res = self._request(path, body)

        return f'{domain.rstrip("/")}/sharePlanReport{res.get("data", {}).get("shareUrl")}'


def start(domain: str, access_key: str, secret_key: str):
    m = MeterSphere(domain, access_key, secret_key)
    '

    projects = m.get_projects()

    project_id = list(filter(lambda item: item['name'] == project_name, projects))[0]['id']

    test_plans = m.get_test_plans_by_project_id(project_id)
    #print(test_plans)
    test_plan_id = list(filter(lambda item: item['name'] == test_plan_name, test_plans))[0]['id']

    envs = m.get_envs_by_project_id(project_id)
    env_id = list(filter(lambda item: item['name'] == env_name, envs))[0]['id']

    #print(f'running test plan {project_id} {test_plan_name} {env_name}')
    sult_stuat = m.run_test_plan(project_id, test_plan_id, env_id)
    print(sult_stuat)
    # wait testplan end
    # while True:
    #     status = m.get_test_plan_status(test_plan_name, project_id)
    #     if status != 'Underway' or status == 'Completed':
    #         break
    #     print('waiting for test plan end')
    #     time.sleep(3)
    #
    # res = m.get_test_plan_failure(test_plan_id)
    # if len(res) > 0:
    #     # if test plan failed, print test plan report link and errors
    #     print(f'check errors {len(res)} -> {m.get_share_test_plan(domain, test_plan_id)}')
    #     print(json.dumps(res))
    #     exit(1)




def meter_run():
    # meterspere apikey
    api_key = config['metersphere']['api_key']
    # meterspere api-secret
    api_secret = config['metersphere']['api_secret']

    # metersphere endpoint
    endpoint = config['metersphere']['endpoint']

    #
    # api_key = os.getenv('API_KEY', api_keys)
    # api_secret = os.getenv('API_SECRET', api_secrets)
    # endpoint = os.getenv('ENDPOINT', endpoints)

    start(endpoint, api_key, api_secret)


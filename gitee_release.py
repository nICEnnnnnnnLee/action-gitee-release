#!/usr/bin/env python
# coding:utf-8
import os
import requests,json
from requests_toolbelt import MultipartEncoder

class Gitee:
    def __init__(self, owner, token):
        self.owner = owner
        self.token = token
        
    def create_release(self, repo, tag_name, name, body = '-', target_commitish = 'master'):
        url = f'https://gitee.com/api/v5/repos/{self.owner}/{repo}/releases'
        data = {
            'access_token': self.token,
            'tag_name': tag_name,
            'name': name,
            'body': body,
            'target_commitish': target_commitish,
        }
        response = requests.post(url, data=data)
        res = response.json() 
        if response.status_code < 200 or response.status_code > 300:
            return False, res["message"] if "message" in res else f"Response status_code is {response.status_code}"
        
        if "id" in res:
            return True, res["id"]
        else:
            return False, "No 'id' in response"
            
    def upload_asset(self, repo, release_id, file_name, file_path):
        m = MultipartEncoder(
            fields={
                'access_token': self.token,
                'file': (file_name, open(file_path, 'rb'), 'application/octet-stream'),
            })
        url = f"https://gitee.com/api/v5/repos/{self.owner}/{repo}/releases/{release_id}/attach_files"
        response = requests.post(url, data=m, headers={'Content-Type': m.content_type})
        # print(response.text)
        res = response.json()
        if response.status_code < 200 or response.status_code > 300:
            return False, res["message"] if "message" in res else f"Response status_code is {response.status_code}"
        
        if "browser_download_url" in res:
            return True, res["browser_download_url"]
        else:
            return False, "No 'browser_download_url' in response"

def get(key):
    val = os.environ.get(key)
    if not val:
        raise ValueError(f'{key} not set in the environment')
    return val
    
def set_result(name, result):
    github_out = os.environ.get("GITHUB_OUTPUT")
    if github_out:
        with open(github_out, 'w', encoding='utf-8') as output:
            output.write(f"{name}={result}")
        
def create_release():
    gitee_owner = get('gitee_owner')
    gitee_token = get('gitee_token')
    gitee_repo = get('gitee_repo')
    gitee_tag_name = get('gitee_tag_name')
    gitee_release_name = get('gitee_release_name')
    gitee_release_body = get('gitee_release_body')
    gitee_target_commitish = get('gitee_target_commitish')
    
    gitee_file_name = os.environ.get('gitee_file_name')
    gitee_file_path = os.environ.get('gitee_file_path')
    if (gitee_file_name and not gitee_file_path) or (gitee_file_path and not gitee_file_name):
        raise ValueError('gitee_file_name and gitee_file_path should be set together')
       
    if gitee_file_path and not os.path.isfile(gitee_file_path):
        raise ValueError('gitee_file_path not exists: ' + gitee_file_path)
    
    gitee_client = Gitee(owner = gitee_owner, token = gitee_token)
    success, release_id = gitee_client.create_release(repo = gitee_repo, tag_name = gitee_tag_name, name = gitee_release_name, 
                body = gitee_release_body, target_commitish = gitee_target_commitish)
    if success:
        print(release_id) # 421675
        if gitee_file_path:
            success, msg = gitee_client.upload_asset(gitee_repo, release_id, file_name = gitee_file_name, file_path = gitee_file_path)
            if not success:
                raise Exception("Upload file asset failed: " + msg)
        set_result("release_id", release_id)
    else:
        raise Exception("Create release failed: " + release_id)

def upload_asset():
    gitee_release_id = get('gitee_release_id')
    gitee_owner = get('gitee_owner')
    gitee_repo = get('gitee_repo')
    gitee_token = get('gitee_token')
    gitee_file_name = get('gitee_file_name')
    gitee_file_path = get('gitee_file_path')

    if not os.path.isfile(gitee_file_path):
        raise ValueError('gitee_file_path not exists: ' + gitee_file_path)
    
    gitee_client = Gitee(owner = gitee_owner, token = gitee_token)
    success, msg = gitee_client.upload_asset(gitee_repo, gitee_release_id, file_name = gitee_file_name, file_path = gitee_file_path)
    if not success:
        raise Exception("Upload file asset failed: " + msg)
    set_result("download_url", msg)
        
if __name__ == "__main__":
    gitee_release_id = os.environ.get("gitee_release_id")
    if gitee_release_id:
        upload_asset()
    else:
        create_release()
    print(os.environ.get("test_array"))
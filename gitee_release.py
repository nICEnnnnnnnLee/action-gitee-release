#!/usr/bin/env python
# coding:utf-8
import os
import glob
import requests
import time
from requests_toolbelt import MultipartEncoder
from functools import wraps

retry_times = os.environ.get("gitee_upload_retry_times", "0")
try:
    retry_times = int(retry_times)
except Exception:
    retry_times = 0
    
def Retry(retry, include_exceptions = [Exception], exclude_exceptions = [ValueError], sleep = 1):
    def decoratedRetry(func):
        def checkRun(retry, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if no_catch(e, exclude_exceptions) or not need_catch(e, include_exceptions):
                    raise e
                if(retry == 0):
                    raise e
                else:
                    print('error catched:', e)
                    if sleep > 0:
                        time.sleep(sleep)
                    return checkRun(retry-1, *args, **kwargs)
                    
        @wraps(func)      
        def run(*args, **kwargs):
            return checkRun(retry, *args, **kwargs)
        return run
    return decoratedRetry

def need_catch(exception, include_exceptions):
    for ex in include_exceptions:
        if isinstance(exception, ex):
            return True
    return False
    
def no_catch(exception, exclude_exceptions):
    for ex in exclude_exceptions:
        if isinstance(exception, ex):
            return True
    return False
    
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
        if response.status_code < 200 or response.status_code >= 300:
            return False, res["message"] if "message" in res else f"Response status_code is {response.status_code}"
        
        if "id" in res:
            return True, res["id"]
        else:
            return False, "No 'id' in response"

    @Retry(retry_times)
    def upload_asset(self, repo, release_id, files = None, file_name = None, file_path = None):
        if files:
            fields = [('access_token', self.token)]
            idx = 1
            file_handles = []  # Track file handles for proper cleanup
            try:
                for file_path in files:
                    file_path = file_path.strip()
                    if not os.path.isfile(file_path):
                        raise ValueError('file_path not exists: ' + file_path)
                    file_handle = open(file_path, 'rb')
                    file_handles.append(file_handle)
                    file = ('file', (os.path.basename(file_path), file_handle, 'application/octet-stream'))
                    idx = idx + 1
                    fields.append(file)
                
                m = MultipartEncoder(fields=fields)
                url = f"https://gitee.com/api/v5/repos/{self.owner}/{repo}/releases/{release_id}/attach_files"
                response = requests.post(url, data=m, headers={'Content-Type': m.content_type})
            finally:
                # Close all file handles
                for handle in file_handles:
                    handle.close()
        elif file_name and file_path:
            with open(file_path, 'rb') as f:
                fields = {
                    'access_token': self.token,
                    'file': (file_name, f, 'application/octet-stream'),
                }
                m = MultipartEncoder(fields=fields)
                url = f"https://gitee.com/api/v5/repos/{self.owner}/{repo}/releases/{release_id}/attach_files"
                response = requests.post(url, data=m, headers={'Content-Type': m.content_type})
        else:
            raise ValueError('files or (file_name and file_path) should not be False at the same time')
        
        # print(response.text)
        res = response.json()
        if response.status_code < 200 or response.status_code >= 300:
            return False, res["message"] if "message" in res else f"Response status_code is {response.status_code}"
        
        if "browser_download_url" in res:
            return True, res["browser_download_url"]
        else:
            return False, "No 'browser_download_url' in response"

    def get_release_by_tag(self, repo, tag_name):
        url = f'https://gitee.com/api/v5/repos/{self.owner}/{repo}/releases/tags/{tag_name}'
        params = {'access_token': self.token}
        response = requests.get(url, params=params)
        res = response.json()
        if response.status_code != 200:
            return False, res.get("message", f"Status code {response.status_code}")
        if "id" in res:
            return True, res["id"]
        else:
            return False, "No release id found"

    def get_asset_id(self, repo, release_id, filename):
        url = f'https://gitee.com/api/v5/repos/{self.owner}/{repo}/releases/{release_id}/attach_files'
        params = {'access_token': self.token, "per_page": 100}
        response = requests.get(url, params=params)
        res = response.json()
        if response.status_code != 200:
            return False, res.get("message", f"Status code {response.status_code}")
        for asset in res:
            if asset['name'] == filename:
                return True, asset['id']
        return False, "Asset not found"

    @Retry(retry_times)
    def update_asset(self, repo, tag_name, filename, new_file_path):
        success, release_id = self.get_release_by_tag(repo, tag_name)
        if not success:
            return False, release_id
        
        success, asset_id = self.get_asset_id(repo, release_id, filename)
        if not success:
            return False, asset_id
        
        success, msg = self.delete_asset(repo, release_id, asset_id)
        if not success:
            return False, msg
        
        return self.upload_asset(repo, release_id, file_name=filename, file_path=new_file_path)

    def delete_release_by_tag(self, repo, tag_name):
        success, release_id = self.get_release_by_tag(repo, tag_name)
        if not success:
            return False, release_id
        return self.delete_release(repo, release_id)

    def delete_release(self, repo, release_id):
        url = f'https://gitee.com/api/v5/repos/{self.owner}/{repo}/releases/{release_id}'
        params = {'access_token': self.token}
        response = requests.delete(url, params=params)
        if response.status_code == 204:
            return True, "Release deleted successfully"
        else:
            res = response.json()
            return False, res.get("message", f"Status code {response.status_code}")

    def delete_asset_by_filename(self, repo, tag_name, filename):
        success, release_id = self.get_release_by_tag(repo, tag_name)
        if not success:
            return False, release_id
        
        success, asset_id = self.get_asset_id(repo, release_id, filename)
        if not success:
            return False, asset_id
        return self.delete_asset(repo, release_id, asset_id)

    def delete_asset(self, repo, release_id, asset_id):
        url = f'https://gitee.com/api/v5/repos/{self.owner}/{repo}/releases/{release_id}/attach_files/{asset_id}'
        params = {'access_token': self.token}
        response = requests.delete(url, params=params)
        if response.status_code == 204:
            return True, "Asset deleted successfully"
        else:
            res = response.json()
            return False, res.get("message", f"Status code {response.status_code}")

def get(key):
    val = os.environ.get(key)
    if not val:
        raise ValueError(f'{key} not set in the environment')
    return val
    
def set_result(name, result):
    print("result: ", f"{name}={result}")
    github_out = os.environ.get("GITHUB_OUTPUT")
    if github_out:
        with open(github_out, 'a', encoding='utf-8') as output:
            if '\n' not in str(result):
                output.write(f"{name}={result}\n")
                print(f"{name}={result}\n")
            else:
                delimiter = 'EOF'
                output.write(f"{name}<<{delimiter}\n{result}\n{delimiter}\n")
                print(f"{name}<<{delimiter}\n{result}\n{delimiter}\n")
                
def upload_assets(gitee_files, gitee_client, gitee_repo, gitee_release_id):
    result = []
    uploaded_path = set()
    for file_path_pattern in gitee_files:
        file_path_pattern = file_path_pattern.strip()
        recursive = True if "**" in file_path_pattern else False
        files = glob.glob(file_path_pattern, recursive = recursive)
        if len(files) == 0:
            raise ValueError('file_path_pattern does not match: ' + file_path_pattern)
        for file_path in files:
            if file_path in uploaded_path or os.path.isdir(file_path):
                continue
            success, msg = gitee_client.upload_asset(gitee_repo, gitee_release_id, file_name = os.path.basename(file_path), file_path = file_path)
            if not success:
                raise Exception("Upload file asset failed: " + msg)
            result.append(msg)
            uploaded_path.add(file_path)
    return result
    
def create_release():
    gitee_owner = get('gitee_owner')
    gitee_token = get('gitee_token')
    gitee_repo = get('gitee_repo')
    gitee_tag_name = get('gitee_tag_name')
    gitee_release_name = get('gitee_release_name')
    gitee_release_body = get('gitee_release_body')
    gitee_target_commitish = get('gitee_target_commitish')
    
    gitee_files = os.environ.get('gitee_files')
    if gitee_files:
        gitee_files = gitee_files.strip().split("\n")
    else:
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
        print(f"Release created successfully with ID: {release_id}")
        set_result("release-id", release_id)
        
        # Upload files if provided
        if gitee_files:
            result = upload_assets(gitee_files, gitee_client, gitee_repo, release_id)
            if result:
                set_result("download-url", '\n'.join(result))
        elif gitee_file_path:
            success, msg = gitee_client.upload_asset(gitee_repo, release_id, file_name = gitee_file_name, file_path = gitee_file_path)
            if not success:
                raise Exception("Upload file asset failed: " + msg)
            set_result("download-url", msg)
    else:
        raise Exception("Create release failed: " + str(release_id))

def upload_asset():
    gitee_owner = get('gitee_owner')
    gitee_repo = get('gitee_repo')
    gitee_token = get('gitee_token')
    gitee_files = os.environ.get('gitee_files')
    
    gitee_client = Gitee(owner = gitee_owner, token = gitee_token)

    gitee_release_id = os.environ.get('gitee_release_id')
    if not gitee_release_id:
        gitee_tag_name = get('gitee_tag_name')
        success, gitee_release_id = gitee_client.get_release_by_tag(gitee_repo, gitee_tag_name)
        if not success:
            raise Exception(f"Failed to get release by tag {gitee_tag_name}")

    if gitee_files:
        gitee_files = gitee_files.strip().split("\n")
        result = upload_assets(gitee_files, gitee_client, gitee_repo, gitee_release_id)
        set_result("download-url", '\n'.join(result))
    else:
        gitee_file_name = get('gitee_file_name')
        gitee_file_path = get('gitee_file_path')
        if gitee_file_path and not os.path.isfile(gitee_file_path):
            raise ValueError('gitee_file_path not exists: ' + gitee_file_path)
        success, msg = gitee_client.upload_asset(gitee_repo, gitee_release_id, file_name = gitee_file_name, file_path = gitee_file_path)
        if not success:
            raise Exception("Upload file asset failed: " + msg)
        set_result("download-url", msg)

def delete_release():
    gitee_owner = get('gitee_owner')
    gitee_repo = get('gitee_repo')
    gitee_token = get('gitee_token')
    gitee_tag_name = get('gitee_tag_name')
    
    gitee_client = Gitee(owner=gitee_owner, token=gitee_token)
    success, msg = gitee_client.delete_release_by_tag(gitee_repo, gitee_tag_name)
    if not success:
        raise Exception("Delete release failed: " + msg)
    print("Release deleted successfully")

def delete_asset():
    gitee_owner = get('gitee_owner')
    gitee_repo = get('gitee_repo')
    gitee_token = get('gitee_token')
    gitee_tag_name = get('gitee_tag_name')
    
    gitee_delete_assets = get('gitee_delete_assets')
    asset_names = [name.strip() for name in gitee_delete_assets.strip().split('\n') if name.strip()]
    
    gitee_client = Gitee(owner=gitee_owner, token=gitee_token)
    
    for asset_name in asset_names:
        success, msg = gitee_client.delete_asset_by_filename(gitee_repo, gitee_tag_name, asset_name)
        if not success:
            raise Exception(f"Delete asset {asset_name} failed: " + msg)
        print(f"Asset {asset_name} deleted successfully")

def update_asset():
    gitee_owner = get('gitee_owner')
    gitee_repo = get('gitee_repo')
    gitee_token = get('gitee_token')
    gitee_tag_name = get('gitee_tag_name')
    gitee_old_asset_name = get('gitee_old_asset_name')
    gitee_new_file_path = get('gitee_new_file_path')
    
    if not os.path.isfile(gitee_new_file_path):
        raise ValueError('gitee_new_file_path not exists: ' + gitee_new_file_path)
    
    gitee_client = Gitee(owner=gitee_owner, token=gitee_token)
    success, msg = gitee_client.update_asset(gitee_repo, gitee_tag_name, gitee_old_asset_name, gitee_new_file_path)
    if not success:
        raise Exception("Update asset failed: " + msg)
    print(f"Asset {gitee_old_asset_name} updated successfully")
    set_result("download-url", msg)
        
if __name__ == "__main__":
    gitee_action = os.environ.get("gitee_action")
    
    if gitee_action == "create_release":
        create_release()
    elif gitee_action == "upload_asset":
        upload_asset()
    elif gitee_action == "delete_release":
        delete_release()
    elif gitee_action == "delete_asset":
        delete_asset()
    elif gitee_action == "update_asset":
        update_asset()
    else:
        raise ValueError(f"Unknown action: {gitee_action}. Supported actions: create_release, upload_asset, delete_release, delete_asset, update_asset")
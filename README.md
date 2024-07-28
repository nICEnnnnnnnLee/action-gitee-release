# action-gitee-release
在Gitee项目发布release(可以上传附件)

## 示例

```
- name: Test create release
  id: create_release
  uses: ./
  with:
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v1.0.0
    gitee_release_name: Test v1.0.0
    gitee_release_body: Release 描述
    gitee_target_commitish: master
    gitee_file_name: 文件名称
    gitee_file_path: 文件本地路径

      
- name: Test upload file to exist release
  uses: ./
  with:
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    release_id: ${{ steps.create_release.outputs.release_id }}
    gitee_file_name: 文件名称2
    gitee_file_path: 文件本地路径2
```

- `gitee_owner`：Gitee 用户名, 项目URL中可获取
- `gitee_repo`：Gitee 项目名, 项目URL中可获取
- `gitee_token`：Gitee api token
- `gitee_tag_name`：Gitee Tag 名称, 提倡以v字母为前缀做为Release名称，例如v1.0或者v2.3.4
- `gitee_release_name`：Gitee release 名称
- `gitee_release_body`：Gitee release 描述
- `gitee_target_commitish`：Gitee 分支名称或者commit SHA
- `gitee_file_name`：上传的附件名称
- `gitee_file_path`：上传的附件的本地路径
- `release_id`：上传附件对应的release的id。该值存在的话，不会再去尝试创建release。
- 注意：Token需要以 [Secrets](https://docs.github.com/cn/actions/reference/encrypted-secrets) 方式给出，以保证token不被泄露



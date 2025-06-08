# action-gitee-release

在 Gitee 项目发布、更新、删除 release

## 功能概览

支持以下 5 种操作，通过 `gitee_action` 参数指定：

- `create_release`: 创建 release，可选择性上传附件
- `upload_asset`: 向已有 release 上传附件（通过 tag 或 id 定位）
- `delete_release`: 删除指定 tag 的 release
- `delete_asset`: 删除指定 release 的指定附件（支持多个）
- `update_asset`: 更新指定 release 的指定附件

## 示例

### 1. 仅创建 release

```yaml
- name: Create Release Only
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: create_release
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
    gitee_release_name: Test v2.0.0
    gitee_release_body: Release 描述
    gitee_target_commitish: master
```

### 2. 创建 release 并上传单个附件

```yaml
- name: Create Release with Single File
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: create_release
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
    gitee_release_name: Test v2.0.0
    gitee_release_body: Release 描述
    gitee_target_commitish: master
    gitee_upload_retry_times: 3
    gitee_file_name: 文件名称
    gitee_file_path: 文件本地路径
```

### 3. 创建 release 并上传多个附件

```yaml
- name: Create Release with Multiple Files
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: create_release
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
    gitee_release_name: Test v2.0.0
    gitee_release_body: Release 描述
    gitee_target_commitish: master
    gitee_upload_retry_times: 3
    gitee_files: |
      文件路径1
      文件路径2
```

### 4.1. 向已有 release 上传单个附件（通过 tag 定位）

```yaml
- name: Upload Single Asset to Existing Release by Tag
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: upload_asset
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
    gitee_upload_retry_times: 3
    gitee_file_name: 新附件名称
    gitee_file_path: 新附件本地路径
```

### 4.2. 向已有 release 上传多个附件（通过 tag 定位）

```yaml
- name: Upload Multiple Assets to Existing Release by Tag
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: upload_asset
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
    gitee_upload_retry_times: 3
    gitee_files: |
      文件路径1
      文件路径2
```

### 4.3. 向已有 release 上传单个附件（通过 release_id 定位）

```yaml
- name: Upload Single Asset to Existing Release by ID
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: upload_asset
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_release_id: 12345
    gitee_upload_retry_times: 3
    gitee_file_name: 新附件名称
    gitee_file_path: 新附件本地路径
```

### 4.4. 向已有 release 上传多个附件（通过 release_id 定位）

```yaml
- name: Upload Multiple Assets to Existing Release by ID
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: upload_asset
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_release_id: 12345
    gitee_upload_retry_times: 3
    gitee_files: |
      文件路径1
      文件路径2
```

### 5. 删除指定 tag 的 release

```yaml
- name: Delete Release
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: delete_release
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
```

### 6.1. 删除 release 中的单个附件

```yaml
- name: Delete Single Asset
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: delete_asset
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
    gitee_delete_assets: 文件名
```

### 6.2. 删除 release 中的多个附件

```yaml
- name: Delete Multiple Assets
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: delete_asset
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
    gitee_delete_assets: |
      文件名1
      文件名2
      文件名3
```

### 7. 更新 release 中的附件

```yaml
- name: Update Asset
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: update_asset
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
    gitee_old_asset_name: 旧文件名称
    gitee_new_file_path: 新文件本地路径
```

### 8. 使用 Action 输出的综合示例

```yaml
- name: Create Release and Use Output
  id: create_release
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: create_release
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_tag_name: v2.0.0
    gitee_release_name: Test v2.0.0
    gitee_release_body: Release 描述
    gitee_target_commitish: master

- name: Upload Additional Assets Using Release ID
  uses: nicennnnnnnlee/action-gitee-release@master
  with:
    gitee_action: upload_asset
    gitee_owner: Gitee用户名
    gitee_repo: Gitee项目名
    gitee_token: ${{ secrets.gitee_token }}
    gitee_release_id: ${{ steps.create_release.outputs.release-id }}
    gitee_files: |
      additional_file1.txt
      additional_file2.txt
```

## 参数说明

### 通用参数

- `gitee_action`：执行的操作类型，可选值：`create_release`, `upload_asset`, `delete_release`, `delete_asset`, `update_asset`
- `gitee_owner`：Gitee 用户名, 项目 URL 中可获取
- `gitee_repo`：Gitee 项目名, 项目 URL 中可获取
- `gitee_token`：Gitee api token
- `gitee_tag_name`：Gitee Tag 名称, 提倡以 v 字母为前缀做为 Release 名称，例如 v1.0 或者 v2.3.4

### create_release 专用参数

- `gitee_release_name`：Gitee release 名称
- `gitee_release_body`：Gitee release 描述
- `gitee_target_commitish`：Gitee 分支名称或者 commit SHA

### 文件上传相关参数（create_release, upload_asset 可用）

- `gitee_files`：上传的附件列表(多个文件)。此处的文件路径支持规则匹配，参考[python-glob](https://docs.python.org/zh-cn/dev/library/glob.html)
- `gitee_file_name`：上传的附件名称(单个文件)
- `gitee_file_path`：上传的附件的本地路径(单个文件)
- `gitee_release_id`：指定的 release ID (仅 upload_asset 操作时可用，如果指定则优先使用，否则通过 tag_name 查找)
- `gitee_upload_retry_times`：上传附件失败后的尝试次数。默认为 0，不再尝试。

### delete_asset 专用参数

- `gitee_delete_assets`：要删除的附件名称，每行一个文件名

### update_asset 专用参数

- `gitee_old_asset_name`：要更新的旧附件名称
- `gitee_new_file_path`：新附件的本地路径

## 输出说明

### create_release 操作输出

- `release-id`：创建的 release 的 ID，可用于后续的 upload_asset 操作

## 注意事项

- Token 需要以 [Secrets](https://docs.github.com/cn/actions/reference/encrypted-secrets) 方式给出，以保证 token 不被泄露

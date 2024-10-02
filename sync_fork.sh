#!/bin/bash

# 腳本名稱: sync_fork.sh

# 設置變量
MAIN_BRANCH="main"  # 或者 "master"，取決於您的倉庫設置
UPSTREAM_URL="https://github.com/DjangoPeng/GitHubSentinel.git"  # 請替換為實際的上游倉庫 URL

# 檢查是否已經添加了上游倉庫
if ! git remote | grep -q "^upstream$"; then
    echo "添加上游倉庫..."
    git remote add upstream $UPSTREAM_URL
fi

# 獲取上游的更新
echo "從上游倉庫獲取更新..."
git fetch upstream

# 更新本地主分支
echo "更新本地 $MAIN_BRANCH 分支..."
git checkout $MAIN_BRANCH
git merge upstream/$MAIN_BRANCH

# 更新標籤
echo "更新標籤..."
git fetch upstream --tags

# 推送更新到 origin
echo "推送更新到您的 GitHub fork..."
git push origin $MAIN_BRANCH
git push --tags

echo "同步完成！"

# 詢問是否要檢出特定標籤
read -p "是否要檢出特定標籤？(y/n) " answer
if [[ $answer = y ]] ; then
    read -p "請輸入要檢出的標籤名稱: " tag_name
    if git rev-parse "$tag_name" >/dev/null 2>&1; then
        echo "檢出標籤 $tag_name..."
        git checkout tags/$tag_name
    else
        echo "錯誤：標籤 $tag_name 不存在。"
    fi
fi

echo "腳本執行完畢。"

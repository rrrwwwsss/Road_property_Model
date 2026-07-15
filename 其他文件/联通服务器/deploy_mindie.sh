#!/bin/bash

# ============================================
# 脚本名称: deploy_mindie.sh
# 功能: 每天晚上10点重启容器，早上6点部署服务
# 容器: Qwen2.5-VL-72B-03
# ============================================

# ===== 配置区域 =====
CONTAINER_NAME="Qwen2.5-VL-72B-03"
WORK_DIR="/usr/local/Ascend/mindie/latest/mindie-service/"
LOG_FILE="/var/log/mindie_deploy.log"
STATE_FILE="/tmp/mindie_restart.flag"

# ===== 日志函数 =====
# 功能：记录带时间戳的日志，同时输出到屏幕和文件
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# ===== 重启函数 =====
# 功能：重启容器并创建标记文件
# 执行时间：晚上10点
do_restart() {
    log "=========================================="
    log "开始执行晚上10点任务"
    log "=========================================="
    
    log "正在重启容器: $CONTAINER_NAME"
    
    # 执行容器重启
    if docker restart "$CONTAINER_NAME"; then
        log "✓ 容器重启成功"
        
        # 创建标记文件，通知早上6点需要部署
        echo "NEED_DEPLOY" > "$STATE_FILE"
        log "✓ 已创建部署标记文件: $STATE_FILE"
        log "✓ 将在早上6点自动执行部署"
    else
        log "✗ 错误：容器重启失败"
        # 清理标记文件
        rm -f "$STATE_FILE"
        exit 1
    fi
    
    log "=========================================="
    log "晚上10点任务完成"
    log "=========================================="
}

# ===== 部署函数 =====
# 功能：在容器内启动 mindieservice_daemon 并等待成功
# 执行时间：早上6点
do_deploy() {
    log "=========================================="
    log "开始执行早上6点任务"
    log "=========================================="
    
    # 检查是否需要部署（标记文件是否存在）
    if [ ! -f "$STATE_FILE" ]; then
        log "没有待部署的任务标记，跳过部署"
        log "（可能昨晚没有重启，或者已经部署过了）"
        exit 0
    fi
    
    log "检测到部署标记，开始部署服务"
    log "目标容器: $CONTAINER_NAME"
    log "工作目录: $WORK_DIR"
    
    # 等待容器完全启动（给容器10秒稳定时间）
    log "等待10秒，让容器稳定..."
    sleep 10
    
    # 在容器内执行部署命令
    log "开始在容器内执行部署命令..."
    
    docker exec "$CONTAINER_NAME" bash -c "
        # 切换到工作目录
        cd $WORK_DIR || { 
            echo '错误：无法进入目录 $WORK_DIR'
            exit 1
        }
        
        echo '当前工作目录: ' && pwd
        
        # 检查 mindieservice_daemon 是否存在
        if [ ! -f ./bin/mindieservice_daemon ]; then
            echo '错误：找不到 ./bin/mindieservice_daemon 文件'
            exit 1
        fi
        
        echo '启动 mindieservice_daemon 进程...'
        # 后台启动服务，输出重定向到 output.log
        nohup ./bin/mindieservice_daemon > output.log 2>&1 &
        
        echo '等待服务启动，检查日志中的 Daemon start success 关键字...'
        echo '（最长等待5分钟）'
        
        # 设置超时时间（300秒 = 5分钟）
        timeout=300
        count=0
        
        while [ \$count -lt \$timeout ]; do
            # 检查日志中是否包含 Daemon start success
            if tail -n 100 output.log 2>/dev/null | grep -q 'Daemon start success'; then
                echo ''
                echo '✓✓✓ 检测到 Daemon start success，服务启动成功！ ✓✓✓'
                exit 0
            fi
            
            # 每2秒检查一次
            sleep 2
            count=\$((count + 2))
            
            # 每30秒显示一次进度（让用户知道还在等待）
            if [ \$((count % 30)) -eq 0 ]; then
                echo \"等待中... 已等待 \${count} / \${timeout} 秒\"
                # 显示最后一行日志
                echo \"最新日志: \$(tail -n 1 output.log 2>/dev/null)\"
            fi
        done
        
        # 超时退出
        echo ''
        echo '✗✗✗ 错误：等待超时（5分钟），未检测到 Daemon start success ✗✗✗'
        echo '最后50行日志内容：'
        tail -n 50 output.log
        exit 1
    "
    
    # 保存部署结果
    DEPLOY_RESULT=$?
    
    # 根据结果记录日志
    if [ $DEPLOY_RESULT -eq 0 ]; then
        log "✓✓✓ 部署成功！ ✓✓✓"
        # 删除标记文件，表示部署完成
        rm -f "$STATE_FILE"
        log "已删除部署标记文件"
    else
        log "✗✗✗ 错误：部署失败！ ✗✗✗"
        log "请手动检查容器内日志: $WORK_DIR/output.log"
        # 保留标记文件，下次执行时会重试
    fi
    
    log "=========================================="
    log "早上6点任务完成"
    log "=========================================="
}

# ===== 主程序 =====
# 获取当前小时（24小时制）
CURRENT_HOUR=$(date +%H)

# 显示脚本被调用的信息（便于调试）
echo ""
log "脚本被调用"
log "当前系统时间: $(date '+%Y-%m-%d %H:%M:%S')"
log "当前小时数: $CURRENT_HOUR"

# 根据小时执行不同的任务
case "$CURRENT_HOUR" in
    22)
        # 晚上10点：重启容器
        log "匹配到晚上10点任务"
        do_restart
        ;;
    06)
        # 早上6点：部署服务
        log "匹配到早上6点任务"
        do_deploy
        ;;
    *)
        # 其他时间：不执行任何操作
        log "当前时间($CURRENT_HOUR点)不是执行时间，无需操作"
        log "脚本将在22点或6点执行实际任务"
        echo ""
        exit 0
        ;;
esac

echo ""
log "脚本执行完毕"
echo ""
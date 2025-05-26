#!/bin/bash

# zabbix config
ZBX_SRV="192.168.229.10"
ZBX_HOST="Zabbix server"
ZBX_PORT="10051"


# Interval
INTERVAL=60


# Function to get CPU usage
get_cpu_usage() {

        local cpu_usage=$(top -bn1 | awk '/Cpu/{print 100 - $8}')
        echo $cpu_usage
}

# Function to get MEMORY usage
get_mem_usage() {

        local mem_usage=$(free | grep Mem | awk '{print $3/$2 * 100}')
        echo $mem_usage
}

# Function to get root disk usage (/)
get_disk_usage() {

        local disk_usage=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
        echo $disk_usage
}

# Function to send data to zabbix
send_to_zabbix() {
        local key=$1
        local value=$2

        zabbix_sender -z "$ZBX_SRV" -p "$ZBX_PORT" -s "$ZBX_HOST" -k "$key" -o "$value" > /dev/null 2>&1
}


echo "Starting Zabbix monitoring loop. Press Ctrl+C to stop"

while true; do
        TIMESTAMP=$(date +%s)

        # collect metric
        CPU_USAGE=$(get_cpu_usage)
        MEM_USAGE=$(get_mem_usage)
        DISK_USAGE=$(get_disk_usage)

        # send metric to zabbix
        send_to_zabbix "cpu-util" "$CPU_USAGE"
        send_to_zabbix "mem-util" "$MEM_USAGE"
        send_to_zabbix "disk-util" "$DISK_USAGE"
        send_to_zabbix "system-uptime" "$(cat /proc/uptime | awk '{print $1}')"

        echo "[$(date)] Sent metrics to zabbix: CPU=$CPU_USAGE%, MEM=$MEM_USAGE%, DISK=$DISK_USAGE"

        sleep $INTERVAL
done
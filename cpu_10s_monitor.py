import schedule
import time
import pymysql
import datetime

conn = pymysql.connect(
   host='localhost',
   user='xxxx',
   passwd='xxxxx',
   database='xx'
)

cursor = conn.cursor()

def ten_seconds_granularity():
   # open file
   file_path = '/proc/stat'

   try:
      with open(file_path,'r') as file:
        # read file
        file_line = file.readline()
        # save to mysql and calculate
        if file_line:
           cpu_info = file_line.split()
           cpu_usage_rate = cal_cpu_usage_rate(cpu_info)
           format_cpu_usage_rate = "{:.2f}".format(cpu_usage_rate)
           print(str(format_cpu_usage_rate)+"%  "+str(datetime.datetime.now()))
           insert_sql = "INSERT INTO cpu_10seconds (user,nice,system,idle,iowait,irq,softirq,stealstolen,guest,guest_nice) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
           data_to_insert = (int(cpu_info[1]),int(cpu_info[2]),int(cpu_info[3]),int(cpu_info[4]),int(cpu_info[5]),
                             int(cpu_info[6]),int(cpu_info[7]),int(cpu_info[8]),int(cpu_info[9]),int(cpu_info[10]))
           cursor.execute(insert_sql,data_to_insert)
           conn.commit()
           print('cpu status saved to mysql')
           # save to table
   except Exception as e:
      # rollaback
      conn.rollback()
      print('cpu status saved failed')
   except FileNoFoundError:
      print("file does not exist!")
   except IOError:
      print("can not open the file")

# calcute cpu usage rate
def cal_cpu_usage_rate(cpu_info):
   # 当前cpu总时间
   total_cpu2 = int(cpu_info[1])+int(cpu_info[2])+int(cpu_info[3])+int(cpu_info[4])+int(cpu_info[5])+int(cpu_info[6])+int(cpu_info[7])+int(cpu_info[8])+int(cpu_info[9])+int(cpu_info[10])
   #读取十秒前 cpu 总时间
   pre_data_sql = "SELECT * FROM cpu_10seconds ORDER BY id DESC LIMIT 1"
   cursor.execute(pre_data_sql)
   res = cursor.fetchone()
   if res:
      total_cpu1 = res[1]+res[2]+res[3]+res[4]+res[5]+res[6]+res[7]+res[8]+res[9]+res[10]
      total = total_cpu2 - total_cpu1
      idle = int(cpu_info[4]) - res[4]
      used_time = total - idle
      usage_rate = (used_time/total)*100
      return usage_rate


schedule.every(10).seconds.do(ten_seconds_granularity)

while True:
   schedule.run_pending()
   time.sleep(1)
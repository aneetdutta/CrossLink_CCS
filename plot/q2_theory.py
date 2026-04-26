import os, sys
sys.path.append(os.getcwd())

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Define marker interval
marker_interval = 50

plt.figure(figsize=(10, 6))



randomize_transmit=[(0.00166666666,0.01666666666,0.00111111111,0.01666666666),(0.00333333333,0.01666666666,0.00166666666,0.01666666666),(0.00166666666,0.00833333333,0.00111111111,0.00833333333),(0.00333333333,0.00833333333,0.00166666666,0.00833333333)]


T_duration=[20,40,60,80,100,120,140,160,180,200,250,300,350,400,450,500,600,700,800,900,1000,2000,3000,4000,5000,6000,7000,7200]

marker1=['*','v','^','D']
#color1=["#fdc086","#a6d854","#e7298a","#000000"]
color1=["#000000","#a6d854","#fdc086","#e7298a"]
i=0
for item in randomize_transmit:
    
    r1=item[0]
    t1=item[1]
    r2=item[2]
    t2=item[3]
    file_path='/home/aneet_wisec/usenix_2025/path-leakage/data/analytical_plot/lambda_r='+str(r1)+"_lambda_t="+str(t1)+'lambda_r='+str(r2)+"_lambda_t="+str(t2)+"exp.npy"
    file_path1='/home/aneet_wisec/usenix_2025/path-leakage/data/analytical_plot/lambda_r='+str(r1)+"_lambda_t="+str(t1)+'lambda_r='+str(r2)+"_lambda_t="+str(t2)+"theory.npy"
    r1=int((1/r1)/60)
    t1=int((1/t1)/60)
    r2=int((1/r2)/60)
    t2=int((1/t2)/60)
    
    exp=np.load(file_path)
    theory=np.load(file_path1)
    
    plt.plot(T_duration,exp, label='LTE RI:'+str(r2)+ 'minutes, BLE RI:'+str(r1)+'minutes, LTE TI:'+str(t2)+'minutes, BLE TI:'+str(t1)+'minutes', alpha=0.7, linewidth=3, color=color1[i], marker=marker1[i], markevery=marker_interval)
    plt.plot(T_duration,theory,label="LTE RI:"+str(r2)+ "minutes, BLE RI:"+str(r1)+"minutes, LTE TI:"+str(t2)+"minutes, BLE TI:"+str(t1)+"minutes upper bound",linestyle=':', alpha=0.7, linewidth=3, color=color1[i], marker=marker1[i], markevery=marker_interval)
    i=i+1
    
    

#xticks = np.linspace(min(multi_protocol_users), max(multi_protocol_users), math.floor(len(multi_protocol_users)/50))
#xticks = np.round(xticks).astype(int)
#plt.xticks(xticks, fontsize=22)
plt.yticks(fontsize=22)
plt.xlabel('Mix zone Duration', fontsize=22)
plt.ylabel('Probability of Mixing', fontsize=22)
plt.legend(loc='lower right', fontsize=15)
plt.grid(True)
plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
plt.savefig(f'output/images/privacy_leakage_q2_analytics.pdf', dpi=600, bbox_inches='tight')
plt.show()

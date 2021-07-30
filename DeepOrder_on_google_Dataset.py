#!/usr/bin/env python
# coding: utf-8



# Importing all neccessary libraries
import pandas as pd
import numpy as np
from statistics import mean, stdev
from matplotlib import pyplot as plt
import os
import seaborn as sns
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import keras.backend as K
import sklearn
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split as tts
from datetime import datetime
import warnings
warnings.simplefilter(action='ignore')
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
import seaborn as sns
sns.set_context('paper')
sns.set_palette(sns.color_palette("Set1", n_colors=8, desat=.5))
sns.set_style('whitegrid')
from matplotlib.ticker import FormatStrFormatter, MultipleLocator

startTime = datetime.now()

def mish(inputs):
    return inputs * tf.nn.tanh(tf.nn.softplus(inputs))


# Reading the dataset
df = pd.read_csv('Datasets/gsdtsr_updated.csv')
df.head()
values = pd.DataFrame()
values['Id'] =  range(0, 1)
values['env'] = 'Gsdtsr'


X = df[['Duration', 'E1','E2','E3', 'LastRunFeature','DIST','CHANGE_IN_STATUS']] # Defining feature variable
Y = df['PRIORITY_VALUE'] # Defining label variable
MSE_list=[] # mean square error list
R2_list = []
def split_dataset():
    # splitting dataset, 80% training and 20% testing
    X_train, X_test, y_train, y_test = tts(X, Y, test_size=0.2) 

    # Scaling both training and testing input data.
    data_scaler = MinMaxScaler()
    X_train = data_scaler.fit_transform(X_train)
    X_test = data_scaler.transform(X_test)
    
    return X_train, X_test, y_train, y_test



def soft_acc(y_true, y_pred):
    return K.mean(K.equal(K.round(y_true), K.round(y_pred)))


# ### Defining function to plot correlation between loss and epochs

def loss_function(information):
    
    history_dict=information.history
    loss_values = history_dict['loss']
    val_loss_values=history_dict['val_loss']
    plt.plot(loss_values,'b--',label='training loss') # Training data loss
    plt.plot(val_loss_values,'r',label='training loss val') # Validation data loss
    plt.xlabel('Epochs',fontsize=22)
    plt.ylabel('Loss',fontsize=22)
    plt.title('Loss Curve',fontsize=22)
    save_figures(plt, 'loss_function_gsdtsr')
    plt.close()

# ###  Defining function to plot the comparision between 'Actual' and 'Predicted' value.

def actual_vs_prediction(y_test, y_test_pred):

    outcome = pd.DataFrame({'Actual': y_test,'Predicted': y_test_pred.flatten()})
    df_sorted = outcome.head(40).sort_values(by="Actual")

    df_sorted.plot(kind='bar', figsize=(12,7))
    plt.grid(which='major', linestyle='-', linewidth = '0.5', color='green')
    plt.grid(which='minor', linestyle=':', linewidth = '0.5', color='black')
    plt.xlabel('Test Cases',fontsize=22)
    plt.ylabel('Priority Values',fontsize=22)
    plt.title("Comparision between 'Actual' and 'Predicted' values",fontsize=22)
    save_figures(plt, 'actual_vs_prediction_gsdtsr')
    plt.close()

    plt.plot(df_sorted['Actual'].tolist(), label='Actual')
    plt.plot(df_sorted['Predicted'].tolist(), label='prediction')
    plt.xlabel('Test cases',fontsize=22)
    plt.ylabel('Priority Values',fontsize=22)
    plt.title("Comparision between 'Actual' and 'Predicted' values",fontsize=22)
    plt.grid(which='major', linestyle='-', linewidth = '0.5', color='green')
    plt.grid(which='minor', linestyle=':', linewidth = '0.5', color='black')
    plt.legend()
    save_figures(plt, 'actual_vs_prediction_2_gsdtsr')
    plt.close()

# ###  Defining function to test the model


def prediction_function(X_train,X_test):

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    return y_test_pred

def save_figures(fig, filename):

    FIGURE_DIR = os.path.abspath(os.getcwd())
    fig.savefig(os.path.join(FIGURE_DIR+'/Google', filename + '.pdf'), bbox_inches='tight')


# ###  Defining function to plot the regression line for the model


def regression_line(y_test, y_test_pred):
    
    fig, ax = plt.subplots()
    ax.scatter(y_test, y_test_pred)
    ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=4)
    ax.set_xlabel('Calculated by DeepOrder algorithm',fontsize=22)
    ax.set_ylabel('Predicted by Neural Network',fontsize=22)
    plt.title("Neural Network Regression Line",fontsize=22)
    plt.grid(which='major', linestyle='-', linewidth = '0.5', color='green')
    plt.grid(which='minor', linestyle=':', linewidth = '0.5', color='black')
    save_figures(plt, 'regression_line_gsdtsr')
    plt.close()

# ### Deep Neural Network 
    
X_train, X_test, y_train, y_test = split_dataset()
  
model = Sequential()
model.add(Dense(10, input_shape=(7,), activation=mish))
model.add(Dense(20, activation=mish))
model.add(Dense(15, activation=mish))
model.add(Dense(1,))
model.compile(Adam(lr=0.001), loss='mean_squared_error', metrics=[soft_acc])    

information = model.fit(X_train, y_train, validation_data= (X_test, y_test), epochs = 2
                        , validation_split = 0.2,
                        shuffle = True, verbose = 1)

y_test_pred = prediction_function(X_train, X_test)    

MSE_list.append(mean_squared_error(y_test, y_test_pred))
R2_list.append(r2_score(y_test, y_test_pred))


outcome = pd.DataFrame({'Actual': y_test, 'Predicted': y_test_pred.flatten()})
outcome.head(10)

'''
# serialize model to JSON
model_json = model.to_json()
with open("gsdtsr_model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("gsdtsr_model.h5")
print("Saved model to disk")
  
# load json and create model
json_file = open('gsdtsr_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("gsdtsr_model.h5")
print("Loaded model from disk")
'''
#---------------------#

values['MSE_list'] = mean(MSE_list)
print('Average Mean Squared Error: %.6f'% mean(MSE_list))
if (len(MSE_list) >1):
    
    print('Standard Deviation of MSE: %.6f'% stdev(MSE_list))

values['R2_list'] = mean(R2_list)

print('Average R2 Score: %.6f'% mean(R2_list))
if (len(R2_list) >1):

    print('Standard Deviation of R2 Score: %.6f'% stdev(R2_list))
preparation_time = datetime.now() - startTime


loss_function(information) # displaying performance based on loss

actual_vs_prediction(y_test, y_test_pred)

regression_line(y_test, y_test_pred)


data_scaler = MinMaxScaler()
# m is number of fault in dataset
_,m=df['Verdict'].value_counts()
n=df.shape[0]
values['Number of Failed Tests'] = m
values['Total Test Cases'] = n

start_prio_time = datetime.now()
XX = data_scaler.fit_transform(df[['DurationFeature', 'E1','E2','E3', 'LastRunFeature','DIST','CHANGE_IN_STATUS']])
A = model.predict(XX)
df['CalcPrio'] = A
final_df = df.sort_values(by=['CalcPrio'], ascending=False)
final_df['ranking'] = range(1, 1+len(df))
available_time = sum(final_df['Duration'])
prioritization_time = datetime.now() - start_prio_time



scheduled_time = 0
detection_ranks = []
undetected_failures = 0
rank_counter = 1

for index, row in final_df.iterrows():
    if scheduled_time + row['Duration'] <= available_time:
        if row['Verdict'] == 1:
            detection_ranks.append(rank_counter)
        scheduled_time += row['Duration']
        rank_counter += 1
    else:
        undetected_failures += row['Id']


detected_failures = len(detection_ranks)/2


p = 0
if undetected_failures > 0:
    p = (detected_failures / m)
else:
    p = 1
print ("recall: ",p)    


if p==1:
    apfd = p - sum(detection_ranks) / (m * n) + p / (2 * n)
    print ("apfd: ",apfd)
    print ("napfd equals apfd")
else:
    napfd = p - sum(detection_ranks) / (m * n) + p / (2 * n)
    print ("napfd: ",napfd)

values['APFD'] = apfd


# ## Calculating NAPFD per cycle
# 


missing = []
Last_cycle = df['Cycle'].iloc[-1]
print (Last_cycle, " will be last cycle")
i=1
NAPFD=[]
prev_cycle=0
for index in range (1,Last_cycle):
    
    if (i<=Last_cycle and i in df['Cycle']):
        #print ("Cycle :",i)
        df_temp=df.loc[df['Cycle']==(i)]
        i= i+1
        if (df_temp.empty):
            missing.append(i-1) 
            continue
            
        
        XX = data_scaler.fit_transform(df_temp[['DurationFeature', 'E1','E2','E3', 'LastRunFeature','DIST','CHANGE_IN_STATUS']])
        A = model.predict(XX)
        df_temp['CalcPrio'] = A
        
        final_df_temp = df_temp.sort_values(by=['CalcPrio'], ascending=False)
        available_time = sum(final_df_temp['Duration'])
        
        counts = final_df_temp['Verdict'].value_counts().to_dict()
        
        if 1 in counts:
            m=counts[1]
        else:
            m=0

            
                 
        n=final_df_temp.shape[0]
        #print ("m : ",m)
        #print (final_df_temp)
        
       
        scheduled_time = 0
        detection_ranks = []

        
        undetected_failures = 0
        rank_counter = 1
        
        for index, row in final_df_temp.iterrows():
            if scheduled_time + row['Duration'] <= available_time:    
                if row['Verdict'] == 1:

                    detection_ranks.append(rank_counter)
                scheduled_time += row['Duration']
                #scheduled_testcases.append(row[:])
                rank_counter += 1
            else:
                undetected_failures = undetected_failures +1
        detected_failures = len(detection_ranks)
        #print ("Detected: ",detected_failures, " Total: ",m)

        if m>0:
            p = 0
            if undetected_failures > 0:
                p = (detected_failures / m)
            else:
                p = 1
            #print ("recall: ",p)
            if (m==1 and n==1):
                NAPFD.append(1)
            elif p==1:
                apfd = p - sum(detection_ranks) / (m * n) + p / (2 * n)
                #print ("apfd: ",apfd)
                NAPFD.append(apfd)
                #print ("napfd equals apfd")
            else:
                napfd = p - sum(detection_ranks) / (m * n) + p / (2 * n)
                NAPFD.append(napfd)
                #print ("napfd: ",napfd)
        else:
            NAPFD.append(0)
            
        #print ("-----------------------------------------------------------------------------------")

    

Cycle = df['Cycle'].unique()
plt.plot(Cycle[1:], NAPFD, color='red', marker='o')
plt.title('NAPFD over cycles paintcontrol', fontsize=14)
plt.xlabel('Cycles', fontsize=24)
plt.ylabel('NAPFD', fontsize=24)
plt.grid(True)
plt.gcf().set_size_inches(25, 10)

save_figures(plt, 'NAPFD_per_cycle_cisco')
plt.close()

mean(NAPFD)
values['Avg NAPFD per cycle'] = mean(NAPFD)


# ## Saving results to output.csv for visualizations

output = pd.DataFrame()
#length = df['Cycle'].iloc[-1]   
output['step'] =  df['Cycle'][1:].unique()
output['env'] = 'gsdtsr'
output['model'] = 'DeepOrder'
output['NAPFD'] = NAPFD
output.to_csv('output.csv', mode='a', sep=";",header=False, index = False)



df_output = pd.read_csv('output.csv', sep=";")
df_output.head()
def figsize_column(scale, height_ratio=1.0):
    fig_width_pt = 240  # Get this from LaTeX using \the\textwidth
    inches_per_pt = 1.0 / 72.27  # Convert pt to inch
    golden_mean = (np.sqrt(5.0) - 1.0) / 2.0  # Aesthetic ratio (you could change this)
    fig_width = fig_width_pt * inches_per_pt * scale  # width in inches
    fig_height = fig_width * golden_mean * height_ratio  # height in inches
    fig_size = [fig_width, fig_height]
    return fig_size

def figsize_text(scale, height_ratio=1.0):
    fig_width_pt = 504  # Get this from LaTeX using \the\textwidth
    inches_per_pt = 1.0 / 72.27  # Convert pt to inch
    golden_mean = (np.sqrt(5.0) - 1.0) / 2.0  # Aesthetic ratio (you could change this)
    fig_width = fig_width_pt * inches_per_pt * scale  # width in inches
    fig_height = fig_width * golden_mean * height_ratio  # height in inches
    fig_size = [fig_width, fig_height]
    return fig_size


env_names = {
    'paintcontrol': 'ABB Paint Control',
    'iofrol': 'ABB IOF/ROL',
    'gsdtsr': 'GSDTSR',
    'Cisco' : 'Cisco'
}



fig, axarr = plt.subplots(1, 4, sharey=True, sharex=True, figsize=figsize_text(2.3, 0.3))
plotname = 'rq1_napfd'
FIGURE_DIR = ''
subplot_labels = ['(a)']
row =0
for column, env in enumerate(sorted(df_output['env'].unique(), reverse=True)):
    #for row, rewardfun in enumerate(df_output['rewardfun'].unique()):
        for agidx, (labeltext, model, linestyle) in enumerate(
                [('DeepOrder', 'DeepOrder', '-')]):
            rel_df = df_output[(df_output['env'] == env)]
            #print (rel_df)

            rel_df[rel_df['model'] == model].plot(x='step', y='NAPFD', label=labeltext, ylim=[0, 1], linewidth=0.8,
                                                  style=linestyle, color=sns.color_palette()[agidx], ax=axarr[column])

            x = rel_df.loc[rel_df['model'] == model, 'step']
            y = rel_df.loc[rel_df['model'] == model, 'NAPFD']
            trend = np.poly1d(np.polyfit(x, y, 1))
            axarr[column].plot(x, trend(x), linestyle, color='k', linewidth=0.8)
        if (column !=0 ):
            axarr[column].legend_.remove()

        axarr[column].set_xticks(np.arange(0, 350, 30), minor=False)
        axarr[column].set_xticklabels([0, '', 60, '', 120, '', 180, '', 240, '', 300], minor=False,fontsize=15)
        axarr[column].xaxis.grid(True, which='major')
        axarr[column].set_xlabel('CI Cycle',fontsize=15)
        axarr[column].set_ylabel('NAPFD',fontsize=15)
        axarr[column].set_title(env_names[env] + '\n')
        #if column == 1:
        #    axarr[ column].set_title('hhdhdh')

        if column == 0:
            axarr[column].legend(loc=2, ncol=2, frameon=True, bbox_to_anchor=(0.6, 1.0),fontsize=11)
        '''

            if column == 1:

                axarr[column].set_title(env_names[env] + '\n')

        elif row == 2:
            axarr[row, column].set_xlabel('CI Cycle')

        if column == 0:
            axarr[row, column].set_ylabel('NAPFD')


        '''
#fig.suptitle('Sharing x per column, y per row',)

#fig.suptitle('ROCKET Algorithm', fontsize=10) # or plt.suptitle('Main title')
#fig.tight_layout()
fig.subplots_adjust(wspace=0.06, hspace=0.3)
save_figures(fig, plotname)
plt.clf()


# ## Calculating Time related metrics
# 
# Plotting Prioritized test cases class distribution
sns.FacetGrid(final_df, hue="Verdict", height=6) \
   .map(sns.kdeplot, "ranking") 
plt.legend(title='Verdict', loc='upper right', labels=['Passed', 'Failed'])
save_figures(plt, 'Prioritized_test_cases_class_distribution_gsdtsr')
plt.close()
# Plotting Non-Prioritized test cases class distribution
sns.FacetGrid(df, hue="Verdict", height=6) \
   .map(sns.kdeplot, "Id") 
plt.legend(title='Verdict', loc='upper right', labels=['Passed', 'Failed'])
save_figures(plt, 'Non_Prioritized_test_cases_class_distribution_gsdtsr')
plt.close()

# For ['Verdict'] based binary visualization
plt.plot(df['Verdict'].tolist(), label='Actual')
plt.plot(final_df['Verdict'].tolist(), label='Prediction')
plt.xlabel('Test cases')
plt.ylabel('Time')
plt.title("Comparision between 'Actual' and 'Predicted' values")
plt.grid(which='major', linestyle='-', linewidth = '0.5', color='green')
plt.grid(which='minor', linestyle=':', linewidth = '0.5', color='black')
plt.legend(fontsize=16,loc = 'upper right')
plt.gcf().set_size_inches(20, 10)
save_figures(plt, 'binary_visualization_verdict_gsdtsr')
plt.close()

# For ['Duration'] based visualization
plt.plot(df['Duration'].tolist(), label='Actual')
plt.plot(final_df['Duration'].tolist(), label='Prediction')
plt.xlabel('Test cases', fontsize=22)
plt.ylabel('Time', fontsize=22)
plt.title("Comparision between 'Actual' and 'Predicted' values w.r.t Execution time", fontsize=22)
plt.grid(which='major', linestyle='-', linewidth = '0.5', color='green')
plt.grid(which='minor', linestyle=':', linewidth = '0.5', color='black')
plt.legend(fontsize=16)
plt.gcf().set_size_inches(20, 10)
save_figures(plt, 'Test_execution_time_overall_gsdtsr')
plt.close()

#For pririotized  
chunk1,chunk2,chunk3,chunk4,chunk5,chunk6,chunk7,chunk8,chunk9,chunk10 = np.array_split(final_df['Duration'],10)
mean_chunk=[mean(chunk1),mean(chunk2),mean(chunk3),mean(chunk4),mean(chunk5),mean(chunk6),mean(chunk7),mean(chunk8),mean(chunk9),mean(chunk10)]
add_chunk=[sum(chunk1),sum(chunk2),sum(chunk3),sum(chunk4),sum(chunk5),sum(chunk6),sum(chunk7),sum(chunk8),sum(chunk9),sum(chunk10)]

#For non-pririotized
chunk1_non,chunk2_non,chunk3_non,chunk4_non,chunk5_non,chunk6_non,chunk7_non,chunk8_non,chunk9_non,chunk10_non = np.array_split(df['Duration'],10)
mean_chunk_non=[mean(chunk1_non),mean(chunk2_non),mean(chunk3_non),mean(chunk4_non),mean(chunk5_non),mean(chunk6_non),mean(chunk7_non),mean(chunk8_non),mean(chunk9_non),mean(chunk10_non)]
add_chunk_non=[sum(chunk1_non),sum(chunk2_non),sum(chunk3_non),sum(chunk4_non),sum(chunk5_non),sum(chunk6_non),sum(chunk7_non),sum(chunk8_non),sum(chunk9_non),sum(chunk10_non)]

#For pririotized 
sum_chunk = []    
chunk1,chunk2,chunk3,chunk4,chunk5,chunk6,chunk7,chunk8,chunk9,chunk10 = np.array_split(final_df['Verdict'],10)

counts = chunk1.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)

counts = chunk2.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)

counts = chunk3.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)

counts = chunk4.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)

counts = chunk5.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)
    
counts = chunk6.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)

counts = chunk7.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)
    
counts = chunk8.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)
    
counts = chunk9.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)
    
counts = chunk10.value_counts().to_dict()
if 1 in counts: 
    sum_chunk.append(counts[1])
else:
    sum_chunk.append(0)    
    
print (sum_chunk)    

#For non-pririotized 
sum_chunk_non = []    
chunk1_non,chunk2_non,chunk3_non,chunk4_non,chunk5_non,chunk6_non,chunk7_non,chunk8_non,chunk9_non,chunk10_non = np.array_split(df['Verdict'],10)

counts = chunk1_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)

counts = chunk2_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)

counts = chunk3_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)

counts = chunk4_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)

counts = chunk5_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)
    
counts = chunk6_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)

counts = chunk7_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)
    
counts = chunk8_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)
    
counts = chunk9_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)
    
counts = chunk10_non.value_counts().to_dict()
if 1 in counts: 
    sum_chunk_non.append(counts[1])
else:
    sum_chunk_non.append(0)    
    
print (sum_chunk_non)    

# Visualizing frequency of fault detection cases per 10 intervals
length = np.array([0.1,0.2,0.3, 0.4,0.5, 0.6,0.7,0.8,0.9,1.0])
#Year =  range(0, length)
newList = [x / max(sum_chunk) for x in sum_chunk]
newList
newList2 = [x / max(sum_chunk_non) for x in sum_chunk_non]  
plt.plot(length, sum_chunk, color='green', marker='o', label='Prioritized')
plt.plot(length, sum_chunk_non, color='red', marker='o', label='Actual')

plt.title('Frequency of Failed test cases in gsdtsr', fontsize=14)
plt.xlabel('Fault test cases', fontsize=18)
plt.ylabel('Verdict Frequency', fontsize=18)
plt.grid(True)
plt.legend(fontsize=16)

plt.gcf().set_size_inches(15, 8)
save_figures(plt, 'frequency_of_fault_detection_per_interval_gsdtsr')
plt.close()


# Visualizing average time of all test cases per 10 intervals
length = np.array([0.1,0.2,0.3, 0.4,0.5, 0.6,0.7,0.8,0.9,1.0])
#Year =  range(0, length)
newList = [x / max(mean_chunk) for x in mean_chunk]
newList
newList2 = [x / max(mean_chunk_non) for x in mean_chunk_non]  
plt.plot(length, mean_chunk, color='green', marker='o',label='Prioritized')
plt.plot(length, mean_chunk_non, color='red', marker='o',label='Non-Prioritized')
plt.legend()
plt.title('time over test cases gsdtsr', fontsize=14)
plt.xlabel('test cases', fontsize=18)
plt.ylabel('time (average per interval))', fontsize=18)
plt.grid(True)
plt.legend(fontsize=16)
save_figures(plt, 'average_time_of_all_tests_per_interval_gsdtsr')
plt.close()


# Visualizing summed time of all test cases per 10 intervals
length = np.array([0.1,0.2,0.3, 0.4,0.5, 0.6,0.7,0.8,0.9,1.0])
#Year =  range(0, length)
newList = [x / max(add_chunk) for x in add_chunk]
newList
newList2 = [x / max(add_chunk_non) for x in add_chunk_non]  
plt.plot(length, add_chunk, color='green', marker='o', label='Prioritized')
plt.plot(length, add_chunk_non, color='red', marker='o',label='Non-Prioritized')

plt.title('time over test cases gsdtsr', fontsize=14)
plt.xlabel('test cases', fontsize=18)
plt.ylabel('time (sum per interval))', fontsize=18)
plt.grid(True)
plt.legend(fontsize=16)

plt.gcf().set_size_inches(15, 8)
save_figures(plt, 'total_time_of_all_tests_per_interval_gsdtsr')
plt.close()



# ---------------------------------------------------------------------------- 


# For pririotized test cases
start = datetime.now() 

Rank = final_df.ranking[final_df['Verdict'] == 1].tolist()
rank_counter = 1
first_rank = False
for index, row in final_df.iterrows():
    
    if row['Verdict'] == 1 and first_rank == False:
        FT = datetime.now()-start
         
        print (rank_counter)
        first_rank = True
        
    if row['Verdict'] == 1 and  Rank[-1]  == rank_counter:
        LT = datetime.now()-start

        print (rank_counter)
    rank_counter += 1

AT = (FT+LT)/2

print("AT ",AT, " seconds", ":", "FT ",FT, " seconds",":", "LT ",LT, " seconds")

'''
FT_milliseconds = FT.microsecond
FT_seconds = FT.second
LT_milliseconds = LT.microsecond
LT_seconds = LT.second
AT_milliseconds   = (FT_milliseconds+LT_milliseconds)/2
AT_seconds = (FT_seconds+LT_seconds)/2
print("AT ",AT_milliseconds, " milliseconds", ":", "FT ",FT_milliseconds, " milliseconds",":", "LT ",LT_milliseconds, " milliseconds")
print("AT ",AT_seconds, " seconds", ":", "FT ",FT_seconds, " seconds",":", "LT ",LT_seconds, " seconds")
'''

# For non-pririotized test cases
start = datetime.now() 

Rank = df.Id[final_df['Verdict'] == 1].tolist()
rank_counter = 1
first_rank = False
for index, row in df.iterrows():
    
    if row['Verdict'] == 1 and first_rank == False:
        FT_non = datetime.now()-start
         
        print (rank_counter)
        first_rank = True
        
    if row['Verdict'] == 1 and  Rank[-1]  == rank_counter:
        LT_non = datetime.now()-start

        print (rank_counter)
    rank_counter += 1

AT_non = (FT_non+LT_non)/2

print("AT ",AT_non, " seconds", ":", "FT ",FT_non, " seconds",":", "LT ",LT_non, " seconds")


'''
FT_milliseconds_non = FT_non.microsecond
FT_seconds_non = FT_non.second
LT_milliseconds_non = LT_non.microsecond
LT_seconds_non = LT_non.second
AT_milliseconds_non   = (FT_milliseconds_non+LT_milliseconds_non)/2
AT_seconds_non = (FT_seconds_non+LT_seconds_non)/2
print("AT ",AT_milliseconds_non, " milliseconds", ":", "FT ",FT_milliseconds_non, " milliseconds",":", "LT ",LT_milliseconds_non, " milliseconds")
print("AT ",AT_seconds_non, " seconds", ":", "FT ",FT_seconds_non, " seconds",":", "LT ",LT_seconds_non, " seconds")
'''



time = pd.DataFrame()
time['Id'] =  range(0, 1)
time['env'] = 'Gsdtsr'
time['FT'] = FT
time['LT'] = LT
time['AT'] = AT
time['FT non-prio'] = FT_non
time['LT non-prio'] = LT_non
time['AT non-prio'] = AT_non
time.to_csv('time'+'.csv', sep=";",index = False)

time 

total_time = datetime.now() - startTime


print ("Preparation Time : ",preparation_time)
print ("Pririotization Time : ",prioritization_time)
print ("Total Algorithm Time : ",total_time)
values['Preparation Time'] = preparation_time
values['Pririotization Time'] = prioritization_time
values['Total Algorithm Time'] = total_time


values.to_csv('values'+'.csv', sep=";", index = False)






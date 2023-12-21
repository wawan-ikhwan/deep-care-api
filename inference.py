import pandas as pd
import numpy as np
import tensorflow as tf

# load default value
df_default_value = pd.read_csv('./utils/default-value.csv')

# load column names
colnames = np.load('./utils/feature_cols.npy', allow_pickle=True).reshape(1,-1)[0].tolist()
feature_names = [colname.split('_')[1] for colname in colnames] # ambil tengah-tengah (NAME) pada NAME_521
print(feature_names)

# load column names
feature_names_readm = ['calculatedbicarbonatewholeblood', 'oxygen',
       'po2', 'bilirubintotal', 'creatinine',
       'potassium', 'sodium', 'ureanitrogen',
       'hematocrit', 'plateletcount', 'wbccount',
       'heartrate', 'arterialbloodpressuremean',
       'noninvasivebloodpressuresystolic',
       'respiratoryrate', 'temperaturefahrenheit']

# load model here
model_los = tf.keras.models.load_model('./utils/model_los')
model_mor = tf.keras.models.load_model('./utils/model_mor')
model_rea = tf.keras.models.load_model('./utils/model_readm')

def list_of_dict_to_dataframe(data:list[dict], colnames: list[str], time_colname='timestamp'):
  '''
  konversi dari fitur-fitur model input dengan timestampnya ke dataframe di mana timestamp menjadi indeks
  '''

  # Initialize DataFrame with 24 rows
  # print(data[0][time_colname])
  # start_time = pd.to_datetime(int(data[0][time_colname]), unit='s')
  # df = pd.DataFrame(index=pd.date_range(start_time, periods=24, freq='H'), columns=colnames)

  df = pd.DataFrame(columns=colnames)

  if time_colname not in colnames:
    colnames.append(time_colname)
  
  print(df)

  for d in data:
    d_filtered = {key: d[key] for key in d if key in colnames}
    df = pd.concat([df, pd.DataFrame([d_filtered])], ignore_index=True)
    
  # Convert the "timestamp" column to datetime format
  df[time_colname] = pd.to_datetime(df[time_colname].astype('int64'), unit='s')
  df.set_index(time_colname, inplace=True)
  df.sort_index(inplace=True)

  # dtypes conversion
  colnames.remove(time_colname)
  df[colnames] = df[colnames].astype('float64')

  return df

#@title Define Resample, Interpolate, Backward/Forward Fill Function
def resample_interpolate_fbfill(df, date_colname = 'charttime'):
  try:
    ret = df.set_index(date_colname)
  except:
    ret = df
  ret = ret.resample('1s').interpolate()
  ret = ret.bfill()
  ret = ret.ffill()
  ret = ret.resample('1H').bfill().ffill()
  ret = ret.bfill()
  ret = ret.ffill()
  return ret

#@title Define Get Default Value Function from BigQuery

def get_default_value(df, df_default_val):

  '''
  gdf_default_value column name must be started  with prefix `avg_`
  '''

  if df_default_val is None:
    global df_default_value
    df_default_val = df_default_value

  # Get columns with the prefix 'avg_%'
  df_filtered = df_default_val.filter(like='avg_', axis=1)

  # Iterate over the selected columns
  for column in df_filtered.columns:
    feature_name = column.split('_')[2]
    df[feature_name].fillna(df_filtered[column][0], inplace=True)

  return df

def fix_shape_to_24(df):
  if len(df) < 24:
    print('The number of rows is less than 24, forward filling until 24.')
    new_index = pd.date_range(start=df.index[0], periods=25, freq='H')
    df = df.reindex(new_index).ffill()

  df = df.iloc[:24, :]

  return df

def preprocess_model_input(modelInput, feature_names, time_colname = 'timestamp'):
  global df_default_value

  df = list_of_dict_to_dataframe(modelInput, feature_names, time_colname)
  df.to_csv('./temp/temp1.csv')
  df = resample_interpolate_fbfill(df.copy(), date_colname = 'timestamp')
  df.to_csv('./temp/temp2.csv')
  df = get_default_value(df.copy(), df_default_value)
  df.to_csv('./temp/temp3.csv')
  df = fix_shape_to_24(df.copy())
  df.to_csv('./temp/temp4.csv')
  nparr = df.values
  nparr = nparr.reshape(1, nparr.shape[0], nparr.shape[1])
  print(nparr.shape)
  return nparr

# data dummy
# data = [
#   {"arterialbloodpressuremean": None, "temps": 20, "timestamp": "1702990863"},
#   {"temperature": 25, "fitur lainnya": 50,  "timestamp": "1702991014"},
#   {"fitur lainnya": 50, "temps": 20, "timestamp": "1702991056"},
#   {"arterialbloodpressuremean": 40, "temps": 20, "timestamp": "1702991539"},
#   {"arterialbloodpressuremean": 50, "temperature": 20, "timestamp": "1702993096"}
# ]

# print(preprocess_model_input(data, feature_names, 'timestamp'))

def get_inference_result(modelInput: list[dict]) -> dict:
  global feature_names, model_los, model_mor, model_rea, feature_names_readm
  # Preprocess model input here...
  X_pred = preprocess_model_input(modelInput, feature_names, 'timestamp')

  X_pred_readm = preprocess_model_input(modelInput, feature_names_readm, 'timestamp')

  # Inference here...
  y_pred_los = model_los.predict(X_pred)[0]
  y_pred_mor = model_mor.predict(X_pred)[0]
  y_pred_rea = model_rea.predict(X_pred_readm)[0]

  modelOutput = {
    "mortality": round(float(y_pred_mor*100), 2),
    "los": round(float(y_pred_los*100), 2),
    "readmission": round(float(y_pred_rea*100), 2)
  }
  return modelOutput

# print(get_inference_result(data))
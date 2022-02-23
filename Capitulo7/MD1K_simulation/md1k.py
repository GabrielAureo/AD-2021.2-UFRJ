import pandas as pd
import numpy as np
import math

def md1k_queue(lamda, mu, k, max_time = 1000, max_events = 1000):
  time = 0
  nevents = 0
  ledger = []
  #fila de eventos, arrival @ t = 0
  equeue = [[time, 'a']]

  waits = []

  N = 0
  while(nevents < max_events and time < max_time):
    
    nevents += 1
    event = equeue.pop(0)
    time, etype = event
    if(etype == 'a'):
      #se a fila estiver na capacidade máxima, rejeitar a chegada e agendar a próxima 
      if(N >= k):
        equeue.append([time +  np.random.exponential(1/lamda), 'a'])
        equeue = sorted(equeue, key = lambda x : x[0])
        continue

      N += 1
      if(N == 1):
        service_time = time + 1/mu
        equeue.append([service_time, 's'])
      equeue.append([time +  np.random.exponential(1/lamda), 'a'])
      equeue = sorted(equeue, key = lambda x : x[0])
    else:
      N -= 1
      if(N > 0):
        service_time = time + 1/mu
        equeue.append([service_time, 's'])
        equeue = sorted(equeue, key = lambda x : x[0])
        
    ledger.append([time, N, etype])
  return ledger

def md1k_simulation(lamda, mu, k, max_time = 1000, max_events = 1000, runs = 10):
  ledger_df = []

  for i in range(runs):
      ledger = md1k_queue(lamda, mu, k, max_time = max_time, max_events = max_events)
      ledger = pd.DataFrame(ledger, columns = ['time','N', 'op'])
      ledger['run'] = i
      ledger['holding'] = ledger.time.shift(-1) - ledger.time
      ledger_df.append(ledger)

  ledger_df = pd.concat(ledger_df)

  ledger_df.dropna(how = 'any', axis = 0, inplace = True)
  return ledger_df

def customers_mean(ledger):
  runs_groupby = ledger.groupby('run')
  total_time = runs_groupby.time.last()
  temp_df = ledger.copy()
  temp_df['area'] = temp_df.holding * temp_df.N
  areas = temp_df.groupby('run').area.sum()

  return_data = {
    'mean' : (areas/total_time).mean(),
    'ci' : confidence_interval(areas/total_time),
  }

  return return_data

def mean_wait(ledger):
  services_df = ledger[ledger.op =='s']
  services_by_run = services_df.groupby('run')
  arrivals_df = ledger[ledger.op =='a']
  arrivals_by_run = arrivals_df.groupby('run')
  means = []
  for idx, services in services_by_run:
    services_count = services.shape[0]
    corresponding_arrivals = arrivals_by_run.get_group(idx).head(services_count)
    waits = services.time.reset_index() - corresponding_arrivals.time.reset_index()
    means.append(waits.time.mean())

  means = pd.Series(means)

  ci = confidence_interval(means)
  
  return_data = {
    'mean' : means.mean(),
    'ci' : ci,
  }

  return return_data 

def confidence_interval(samples, confidence_rate = 1.95):
  x = samples.mean()
  n = samples.count()
  s = samples.std()
  z = confidence_rate
  return (x - z*(s/ math.sqrt(n) ), x+ z*(s/  math.sqrt(n) ))
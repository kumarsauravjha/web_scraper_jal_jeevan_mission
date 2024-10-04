#%%
import pandas as pd

data_2020 = pd.read_csv('data_2020_2021\jjm_all_states.csv')

data_2021 = pd.read_csv('data_2021_2022\jjm_all_states.csv')

data_2022 = pd.read_csv('data_2022_2023\jjm_all_states.csv')

data_2023 = pd.read_csv('data_2023_2024\jjm_all_states.csv')

data_2024 = pd.read_csv('data_2024_2025\jjm_all_states.csv')

#%%
data_2020.insert(0, 'Year','2020')

data_2021.insert(0, 'Year','2021')

data_2022.insert(0, 'Year','2022')

data_2023.insert(0, 'Year','2023')

data_2024.insert(0, 'Year','2024')
# %%
data_2024.columns = data_2023.columns

jjm_all_data = pd.concat([data_2024, data_2023],ignore_index=True)

#%%

data_2022.columns = jjm_all_data.columns

jjm_all_data = pd.concat([jjm_all_data, data_2022],ignore_index=True)


# %%
data_2021.columns = jjm_all_data.columns

jjm_all_data = pd.concat([jjm_all_data, data_2021],ignore_index=True)
# %%
data_2020.columns = jjm_all_data.columns

jjm_all_data = pd.concat([jjm_all_data, data_2020],ignore_index=True)
# %%
jjm_all_data.to_csv('jjm_all_data.csv')
# %%

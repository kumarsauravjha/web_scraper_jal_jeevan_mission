#%%
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from io import StringIO
import os
# %%
url = 'https://ejalshakti.gov.in/JJM/JJMReports/Physical/JJMRep_FHTCCoverage.aspx'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()
driver.get(url)

time.sleep(5)
#for the Year
year_dropdown = Select(driver.find_element(By.NAME, 'ctl00$CPHPage$ddFinyear'))
year_dropdown.select_by_value('2024-2025')

# Select State from dropdown
state_dropdown = Select(driver.find_element(By.NAME, 'ctl00$CPHPage$ddState'))

states = [(option.get_attribute("value"), option.text) for option in state_dropdown.options if option.get_attribute("value") and option.text != "All State"]

os.makedirs('data', exist_ok=True)

print(states)

final_df = pd.DataFrame()
final_df_all = pd.DataFrame()
failed_districts = pd.DataFrame()
count=0
for state_value, state_name in states:
    try:
        #to refresh state dropdown to avoid staleElement exception
        state_dropdown = Select(driver.find_element(By.NAME, 'ctl00$CPHPage$ddState'))

        state_dropdown.select_by_value(state_value)
        time.sleep(2)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'ctl00$CPHPage$ddDistrict'))
        )

        district_dropdown = Select(driver.find_element(By.NAME, 'ctl00$CPHPage$ddDistrict'))

        districts = [(option.get_attribute("value"), option.text) for option in district_dropdown.options if option.get_attribute("value") and option.text != "All District"]
        # district_cols = districts.columns

        for district_value, district_name in districts:
            try:
            # Refresh the dropdown list and options within each loop iteration to avoid StaleElementReferenceException
                district_dropdown = Select(driver.find_element(By.NAME, 'ctl00$CPHPage$ddDistrict'))

                district_dropdown.select_by_value(district_value)
                time.sleep(5)

                show_button = driver.find_element(By.NAME, 'ctl00$CPHPage$btnShow')
                show_button.click()

                time.sleep(5)

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table = soup.find('table', {'id':'tableReportTable'})

                # Assuming the table you want is the first one
                if table:
                    df = pd.DataFrame()
                    # print("Empty df shape", df.shape)
                    df = pd.read_html(StringIO(str(table)))[0]
                    # print("Empty df shape now", df.shape)
                
                    df = df[~df.apply(lambda x: x.astype(str).str.contains('Total', na=False)).any(axis=1)]

                    df.insert(0, 'State', state_name)
                
                    
                    df.insert(1, 'District', district_name)


                    if len(final_df) == 0:
                        final_df=df
                        print("1st final df shape", final_df.shape)
                    else:
                        # df2 = df.iloc[5:]
                        df.columns = final_df.columns
                        final_df = pd.concat([final_df, df], ignore_index=True)
                        # print(final_df)
                        print("2nd final df shape ", final_df.shape)

                    print(f"Done for {state_name}: {district_name}")
                else:
                    print(f"Table not found for district: {district_name}")
                    # failed_districts = pd.concat([district_value, district_name], district_cols)
            except Exception as e:
                print(f"Error processing district {district_name}: {str(e)}")
                # failed_districts = pd.concat([district_value, district_name], district_cols)
                continue
        print("final df shape", final_df.shape)
        if "S.No." in final_df.columns:
                        final_df.drop(columns=["S.No."], inplace=True)
        if final_df_all.empty:
            final_df_all = final_df
        else:
            final_df.columns = final_df_all.columns
            final_df_all = pd.concat([final_df_all, final_df], ignore_index=True)
        
        final_df.to_csv(f'data/jjm_{state_name}.csv', index=False)    
        final_df = pd.DataFrame()
        print("final df all shape", final_df_all.shape)
        # if not failed_districts.empty and count != 0:
        #      #go to statement 54 and count = count + 1
        #      count = count + 1
        #      districts = failed_districts
        # failed_districts = pd.DataFrame()
             
    except Exception as e:
                print(f"Error processing state {state_name}: {str(e)}")
                continue
    
    

if not final_df_all.empty:
    final_df_all.to_csv('data/jjm_all_states.csv', index=False)
    print("Data scraped successfully and saved to CSV.")
else:
    print("No data to save.")

driver.quit()


# %%

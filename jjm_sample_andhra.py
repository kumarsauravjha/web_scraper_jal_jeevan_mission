#%%
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from io import StringIO
# %%
url = 'https://ejalshakti.gov.in/JJM/JJMReports/Physical/JJMRep_FHTCCoverage.aspx'
driver = webdriver.Chrome()
driver.get(url)

time.sleep(5)
#for the Year
year_dropdown = Select(driver.find_element(By.NAME, 'ctl00$CPHPage$ddFinyear'))
year_dropdown.select_by_value('2022-2023')

# Select State from dropdown
state_dropdown = Select(driver.find_element(By.NAME, 'ctl00$CPHPage$ddState'))

#replace with the name of the state you want to scrape for
state_dropdown.select_by_visible_text('Uttar Pradesh')

# state_dropdown.select_by_value('31')

final_df = pd.DataFrame()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, 'ctl00$CPHPage$ddDistrict'))
)

time.sleep(5)

district_dropdown = Select(driver.find_element(By.NAME, 'ctl00$CPHPage$ddDistrict'))

districts = [(option.get_attribute("value"), option.text) for option in district_dropdown.options if option.get_attribute("value") and option.text != "All District"]

for district_value, district_name in districts:
    try:
    # Refresh the dropdown list and options within each loop iteration to avoid StaleElementReferenceException
        district_dropdown = Select(driver.find_element(By.NAME, 'ctl00$CPHPage$ddDistrict'))


        district_dropdown.select_by_value(district_value)
        time.sleep(2)

        show_button = driver.find_element(By.NAME, 'ctl00$CPHPage$btnShow')
        show_button.click()

        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', {'id':'tableReportTable'})

        # Assuming the table you want is the first one
        if table:
            df = pd.DataFrame()
            print("Empty df shape", df.shape)
            df = pd.read_html(StringIO(str(table)))[0]
            print("Empty df shape now", df.shape)
        
            df = df[~df.apply(lambda x: x.astype(str).str.contains('Total', na=False)).any(axis=1)]
            df.drop(columns=["S.No."], inplace=True)

            df.insert(0, 'State', 'Andhra Pradesh')
        
            
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
        else:
            print(f"Table not found for district: {district_name}")
    except Exception as e:
        print(f"Error processing district {district_name}: {str(e)}")
        continue

if not final_df.empty:
    # combined_df = pd.concat(all_data, ignore_index=True)
    # Save the DataFrame to CSV
    # final_df.to_csv('andhra_pradesh_all_districts.csv', index=False)
    final_df.to_csv('jjm_uttar_pradesh.csv', index=False)
    print("Data scraped successfully and saved to CSV.")
else:
    print("No data to save.")

driver.quit()

# %%

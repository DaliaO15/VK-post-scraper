import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import utils
import argparse

"""
** Usage:

- General:
python your_script.py --user A_VK_USER_NAME --input-file PATH/TO/INPUT/FILE/test.xlsx --output_folder_path PATH/TO/OUTPUT/FOLDER/ 
- Example:
python your_script.py --user tsargradtv --input-file ../../../Data/2022/test.xlsx --output_folder_path ../../../Data/2022/out_folder/

"""

def main():
    """ 
    This is the driver code. It needs arguments to run (see "usage"). What it does is to read an xlsx file that contains
    the links to the posts, and uses the functions in the documente utils.py to collect and organise the new metadata
    into a new .xlsx file. 
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Scrape VK posts information.')
    parser.add_argument('-u','--user', required=True, help='VK target user')
    parser.add_argument('-i','--input_file_path', required=True, help='Path to the input Excel file')
    parser.add_argument('-o','--output_folder_path', required=True, help='Path to the output folder')
    args = parser.parse_args()

    # Set VK target user 
    user = args.user

    # Access metadata 
    input_file = args.input_file_path
    data = pd.read_excel(input_file)
    data = data.drop(columns=['web-scraper-order','web-scraper-start-url'])
    data.dropna(subset=['post_id'], inplace=True)

    # Set up the driver 
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    driver = webdriver.Chrome(options=options)

    # Get data 
    print('Starting')
    full_data = utils.scrape_posts_info(data, user, driver)

    # Close the WebDriver instance after processing all posts
    driver.quit()
    print('Finished')

    # Convert the list to a DataFrame
    df = pd.DataFrame(full_data)

    try: 
        output_folder = args.output_folder_path
        file_name = input_file.split('/')[-1].split('.')[0]
        print(f'Final document saved to: {output_folder}+{file_name}+.xlsx')
        # Save DataFrame to Excel
        df.to_excel(output_folder + file_name + '_final.xlsx', index=False)
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")
        # Save DataFrame to a default location as a fallback
        print('Final document saved to this same folder')
        df.to_excel('output_data.xlsx', index=False)


if __name__ == "__main__":
    main()


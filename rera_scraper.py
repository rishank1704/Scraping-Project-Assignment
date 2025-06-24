
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Step 6: Configure Chrome for headless mode (for GitHub Codespaces)
options = Options()
options.add_argument("--headless")  # No GUI
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

# Initialize WebDriver
driver = webdriver.Chrome(options=options)

# Open the RERA project list page
driver.get("https://rera.odisha.gov.in/projects/project-list")
driver.maximize_window()

# Wait for the table to load
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "project-table")))

# Scroll to ensure all elements are loaded
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

projects_data = []

# Grab the first 6 "View Details" buttons
view_buttons = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Details')]")[:6]

for i, button in enumerate(view_buttons):
    print(f"Scraping project {i+1}...")

    # Open in a new tab
    driver.execute_script("window.open(arguments[0]);", button.get_attribute('href'))
    driver.switch_to.window(driver.window_handles[1])

    try:
        # Wait for Project Details to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h3[text()='Project Details']")))

        rera_no = driver.find_element(By.XPATH, "//label[contains(text(),'RERA Regd. No')]/following-sibling::div").text.strip()
        project_name = driver.find_element(By.XPATH, "//label[contains(text(),'Project Name')]/following-sibling::div").text.strip()

        # Switch to "Promoter Details" tab
        promoter_tab = driver.find_element(By.XPATH, "//a[contains(text(),'Promoter Details')]")
        promoter_tab.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'Company Name')]")))

        promoter_name = driver.find_element(By.XPATH, "//label[contains(text(),'Company Name')]/following-sibling::div").text.strip()
        promoter_address = driver.find_element(By.XPATH, "//label[contains(text(),'Registered Office Address')]/following-sibling::div").text.strip()
        gst_no = driver.find_element(By.XPATH, "//label[contains(text(),'GST No')]/following-sibling::div").text.strip()

        projects_data.append({
            "RERA Regd. No": rera_no,
            "Project Name": project_name,
            "Promoter Name": promoter_name,
            "Address of the Promoter": promoter_address,
            "GST No": gst_no
        })

    except Exception as e:
        print("Error extracting data:", e)

    # Close tab and return
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)

driver.quit()

# Save data to CSV
if projects_data:
    with open("rera_projects.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=projects_data[0].keys())
        writer.writeheader()
        writer.writerows(projects_data)
    print("\n Data saved to rera_projects.csv")

# Print data
for i, data in enumerate(projects_data, 1):
    print(f"\n--- Project {i} ---")
    for key, value in data.items():
        print(f"{key}: {value}")

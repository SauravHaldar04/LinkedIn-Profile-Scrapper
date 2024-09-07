from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
#from dotenv import load_dotenv
import os
import time

# load_dotenv()

# session_cookie = os.getenv("SESSION_COOKIE")

def scrape_linkedin_profile(profile_url, session_cookie):
    """
    Scrapes a LinkedIn profile using Selenium and session cookie.

    Args:
        profile_url (str): URL of the LinkedIn profile to scrape.
        session_cookie (str): Session cookie of the LinkedIn account.

    Returns:
        dict: Scraped profile data (name, description, location, experiences, education, skills, profile picture URL).
    """
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    # driver = webdriver.Chrome(chrome_options=chrome_options)
    options = webdriver.ChromeOptions()
    #options.add_argument("--incognito") 
    # Adjust the path to your ChromeDriver binary if needed
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.linkedin.com/login")
    driver.implicitly_wait(5)
    # Set session cookie
    try:
        driver.add_cookie({"name": "li_at", "value": session_cookie})
    except Exception as e:
        print(f"Error setting session cookie: {e}")
    driver.refresh()
    driver.get(profile_url)

    profile_data = {}
    profile_data["url"] = profile_url

    # Extract name
    profile_data["name"] = ""
    try:
        name_element = driver.find_element(By.CSS_SELECTOR, "h1.text-heading-xlarge.inline.t-24.v-align-middle.break-words")
        profile_data["name"] = name_element.text.strip()
    except Exception as e:
        print(f"Error extracting name: {e}")

    #Extract cover picture
    profile_data["Cover Page"] = ""
    try:
        
        cover_pic_element = driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[1]/div[1]/div/div/img')
        cover_pic_url = cover_pic_element.get_attribute("src")
        profile_data["Cover Page"] = cover_pic_url
    except Exception as e:
        print(f"Error extracting profile picture: {e}")
    # Extract profile picture
    profile_data["Profile Pic"] = ""
    try:
        
        profile_pic_element = driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[1]/div[1]/div/button/img')
        profile_pic_url = profile_pic_element.get_attribute("src")
        profile_data["Profile Pic"] = profile_pic_url
    except Exception as e:
        print(f"Error extracting profile picture: {e}")
    # Extract number of connections
    profile_data["connections"] = ""   
    try:
        
        connections_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/ul/li/span/span'))
        )
        connections_text = connections_element.text.strip()
        profile_data['connections'] = connections_text
    except Exception as e:
        print(f"Error extracting connections: {e}")
    
    # Extract number of followers
    profile_data["followers"] = ""   
    try:
        # Locate the div with ID "content_collections"
        content_collections_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'content_collections'))
        )
        
        # Find the next div which contains the followers information
        followers_div = content_collections_div.find_element(By.XPATH, './following-sibling::div')
        
        # Extract the number of followers
        try:
            followers_text_element = followers_div.find_element(By.CSS_SELECTOR, 'p.pvs-header__optional-link span')
            profile_data["followers"] = followers_text_element.text.strip()
        except Exception as e:
            print(f"Error extracting followers text: {e}")

    except TimeoutException as e:
        print(f"Error locating content_collections div: {e}")
    except NoSuchElementException as e:
        print(f"Error finding followers information: {e}")

    # Extract description
        profile_data["headline"] = ""
    try:
       
        description_element = driver.find_element(By.CSS_SELECTOR, ".text-body-medium.break-words")
        profile_data["headline"] = description_element.text.strip()
    except Exception as e:
        print(f"Error extracting description: {e}")
    
        # Extract location
    try:
        profile_data["location"] = ""
        location_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[1]'))
        )
        location_text = location_element.text.strip()
        profile_data['location'] = location_text
    except Exception as e:
        print(f"Error extracting about: {e}")

    # Extract about
    profile_data["Summary"] = ""
    try:
        # Locate the div with ID "about"
        about_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'about'))
        )
        
        # Find the next sibling div and then the div two levels down
        target_div = about_section.find_element(By.XPATH, './following-sibling::div/following-sibling::div')
        # Extract the text content
        try:
            about_text_element = target_div.find_element(By.CSS_SELECTOR, 'span[aria-hidden="true"]')
            profile_data["Summary"] = about_text_element.text.strip()
        except Exception as e:
            print(f"Error extracting About section text: {e}")

    except TimeoutException as e:
        print(f"Error locating About section: {e}")
    except NoSuchElementException as e:
        print(f"Error finding About section: {e}")
    
    # Extract experiences
    profile_data["experiences"] = []
    experience_url = f"{profile_url}details/experience/"
    driver.get(experience_url)
    try:
        experience_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul'))
        )

        experience_elements = experience_section.find_elements(By.TAG_NAME, "li")
        for element in experience_elements:
            experience = {}
            try:
                title_element = element.find_element(By.CSS_SELECTOR, ".mr1.t-bold span")
                experience["title"] = title_element.text.strip()
            except Exception as e:
                print(f"Error extracting title for experience: {e}")
                continue

            try:
                company_element = element.find_element(By.CSS_SELECTOR, "a.optional-action-target-wrapper")
                company_name = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal span.visually-hidden").text.strip()
                company_link = company_element.get_attribute("href")
                experience["company_link"] = company_link
                experience["company_name"] = company_name    
            except Exception as e:
                print(f"Error extracting company information: {e}")
                continue

            try:
                duration_element = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal.t-black--light span.pvs-entity__caption-wrapper")
                experience["duration"] = duration_element.text.strip()
            except Exception as e:
                print(f"Error extracting duration: {e}")

            try:
                location_element = element.find_element(By.CSS_SELECTOR, ".t-14 t-normal.t-black--light span.visually-hidden")
                experience["location"] = location_element.text.strip()
            except Exception as e:
                print(f"Error extracting location: {e}")

            try:
                skills_element = element.find_element(By.CSS_SELECTOR, ".pvs-entity__sub-components span[aria-hidden='true']")
                experience["skills/description"] = skills_element.text.strip()
            except Exception as e:
                print(f"Error extracting skills: {e}")

            profile_data["experiences"].append(experience)
    except TimeoutException as e:
        print(f"Error finding experiences: {e}")
    except NoSuchElementException as e:
        print(f"Error finding experiences: {e}")

    # Extract education
    profile_data["education"] = []
    education_url = f"{profile_url}details/education/"
    driver.get(education_url)
    try:
        education_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul'))
        )

        education_elements = education_section.find_elements(By.TAG_NAME, "li")
        for element in education_elements:
            education = {}
            try:
                school_element = element.find_element(By.CSS_SELECTOR, ".mr1.hoverable-link-text.t-bold span")
                education["school"] = school_element.text.strip()
            except Exception as e:
                print(f"Error extracting school for education: {e}")
                continue

            try:
                degree_element = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal span[aria-hidden='true']")
                education["degree"] = degree_element.text.strip()
            except Exception as e:
                print(f"Error extracting degree for education: {e}")

            try:
                dates_element = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal.t-black--light span.pvs-entity__caption-wrapper")
                education["dates"] = dates_element.text.strip()
            except Exception as e:
                print(f"Error extracting dates for education: {e}")

            try:
                grade_element = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal.t-black span[aria-hidden='true']")
                education["grade"] = grade_element.text.strip()
            except Exception as e:
                print(f"Error extracting grade for education: {e}")

            try:
                skills_element = element.find_element(By.XPATH, '//*[@id="profilePagedListComponent-ACoAAEV128YBUk2Q2pk94NW-HSVHCmM8-RW2A34-EDUCATION-VIEW-DETAILS-profile-ACoAAEV128YBUk2Q2pk94NW-HSVHCmM8-RW2A34-NONE-en-US-0"]/div/div/div[2]/div[2]/ul/li[2]/div/ul')
                skills_text = skills_element.text.strip()
                education["skills"] = skills_text
            except Exception as e:
                print(f"Error extracting skills for education: {e}")

            profile_data["education"].append(education)
    except TimeoutException as e:
        print(f"Error finding education: {e}")
    except NoSuchElementException as e:
        print(f"Error finding education: {e}")
    # Extract licenses and certifications
    profile_data["licenses_and_certifications"] = []
    licenses_certifications_url = f"{profile_url}details/certifications/"
    driver.get(licenses_certifications_url)
    try:
        licenses_certifications_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul'))
        )

        licenses_certifications_elements = licenses_certifications_section.find_elements(By.TAG_NAME, "li")
        for element in licenses_certifications_elements:
            license_certification = {}
            try:
                name_element = element.find_element(By.CSS_SELECTOR, ".mr1.t-bold span")
                license_certification["name"] = name_element.text.strip()
            except Exception as e:
                print(f"Error extracting name for license/certification: {e}")
                continue

            try:
                organization_element = element.find_element(By.CSS_SELECTOR, "a.optional-action-target-wrapper")
                organization_link = organization_element.get_attribute("href")
                license_certification["organization_link"] = organization_link
                organization_name = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal span.visually-hidden").text.strip()
                license_certification["organization_name"] = organization_name
            except Exception as e:
                print(f"Error extracting organization information: {e}")
                continue

            try:
                issue_date_element = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal.t-black--light span.pvs-entity__caption-wrapper")
                license_certification["issue_date"] = issue_date_element.text.strip()
            except Exception as e:
                print(f"Error extracting issue date: {e}")

            profile_data["licenses_and_certifications"].append(license_certification)
    except TimeoutException as e:
        print(f"Error finding licenses and certifications: {e}")
    except NoSuchElementException as e:
        print(f"Error finding licenses and certifications: {e}")
    # Extract skills
    profile_data["skills"] = []
    skills_url = f"{profile_url}details/skills/"
    driver.get(skills_url)
    try:
        skills_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div[2]/div/div/div[1]/ul'))
        )

        skills_elements = skills_section.find_elements(By.TAG_NAME, 'li')
        for element in skills_elements:
            try:
                skill_element = element.find_element(By.CSS_SELECTOR, '.mr1.hoverable-link-text.t-bold span.visually-hidden')
                profile_data["skills"].append(skill_element.text.strip())
            except Exception as e:
                print(f"Error extracting skill: {e}")
    except TimeoutException as e:
        print(f"Error finding skills: {e}")
    except NoSuchElementException as e:
        print(f"Error finding skills: {e}")

    # Extract recommendations received
    profile_data["recommendations_received"] = []
    recommendations_received_url = f"{profile_url}details/recommendations/?detailScreenTabIndex=0"
    driver.get(recommendations_received_url)
    try:
        recommendations_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div[2]/div/div/div[1]/ul"))
        )

        recommendations_elements = recommendations_section.find_elements(By.XPATH, "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div[2]/div/div/div[1]/ul/li")
        for element in recommendations_elements:
            recommendation = {}
            try:
                name_element = element.find_element(By.CSS_SELECTOR, ".display-flex.align-items-center.mr1.hoverable-link-text.t-bold span")
                recommendation["name"] = name_element.text.strip()
            except Exception as e:
                print(f"Error extracting name for recommendation: {e}")
                continue

            try:
                date_and_relationship_element = element.find_element(By.CSS_SELECTOR, ".pvs-entity__caption-wrapper")
                recommendation["date_and_relationship"] = date_and_relationship_element.text.strip()
            except Exception as e:
                print(f"Error extracting date and relationship for recommendation: {e}")

            try:
                content_element = element.find_element(By.CSS_SELECTOR, ".display-flex.align-items-center.t-14.t-normal.t-black span[aria-hidden='true']")
                recommendation["content"] = content_element.text.strip()
            except Exception as e:
                print(f"Error extracting content for recommendation: {e}")

            profile_data["recommendations_received"].append(recommendation)
    except TimeoutException as e:
        print(f"Error finding recommendations received: {e}")
    except NoSuchElementException as e:
        print(f"Error finding recommendations received: {e}")
    # Extract recommendations given
    profile_data["recommendations_given"] = []
    recommendations_given_url = f"{profile_url}details/recommendations/?detailScreenTabIndex=1"
    driver.get(recommendations_given_url)
    try:
        recommendations_given_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div[3]/div/div/div[1]/ul"))
        )

        recommendations_elements = recommendations_given_section.find_elements(By.TAG_NAME, "li")
        for element in recommendations_elements:
            recommendation = {}
            try:
                name_element = element.find_element(By.CSS_SELECTOR, ".display-flex.align-items-center.mr1.hoverable-link-text.t-bold span")
                recommendation["name"] = name_element.text.strip()
            except Exception as e:
                print(f"Error extracting name for recommendation: {e}")
                continue

            try:
                date_and_relationship_element = element.find_element(By.CSS_SELECTOR, ".pvs-entity__caption-wrapper")
                recommendation["date_and_relationship"] = date_and_relationship_element.text.strip()
            except Exception as e:
                print(f"Error extracting date and relationship for recommendation: {e}")

            try:
                content_element = element.find_element(By.CSS_SELECTOR, ".display-flex.align-items-center.t-14.t-normal.t-black span[aria-hidden='true']")
                recommendation["content"] = content_element.text.strip()
            except Exception as e:
                print(f"Error extracting content for recommendation: {e}")

            profile_data["recommendations_given"].append(recommendation)
    except TimeoutException as e:
        print(f"Error finding recommendations given: {e}")
    except NoSuchElementException as e:
        print(f"Error finding recommendations given: {e}")
    # Extract projects
    profile_data["projects"] = []
    projects_url = f"{profile_url}details/projects/"
    driver.get(projects_url)

    try:
        projects_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul'))
        )

        project_elements = projects_section.find_elements(By.TAG_NAME, "li")

        for element in project_elements:
            project = {}

            # Extract project name
            try:
                project_name_element = element.find_element(By.CSS_SELECTOR, ".t-bold span")
                project["name"] = project_name_element.text.strip()
            except Exception as e:
                print(f"Error extracting project name: {e}")
                continue

            # Extract project date
            try:
                project_date_element = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal.t-black--light span.pvs-entity__caption-wrapper")
                project["date"] = project_date_element.text.strip()
            except Exception as e:
                print(f"Error extracting project date: {e}")

            # Extract project link
            try:
                project_link_element = element.find_element(By.TAG_NAME, "a")
                project["link"] = project_link_element.get_attribute("href")
            except Exception as e:
                print(f"Error extracting project link: {e}")

            profile_data["projects"].append(project)
    except TimeoutException as e:
        print(f"Error finding projects: {e}")
    except NoSuchElementException as e:
        print(f"Error finding projects: {e}")
    # Extract publications
    profile_data["publications"] = []
    publications_url = f"{profile_url}details/publications/"
    driver.get(publications_url)

    try:
        publications_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div/div[1]/ul'))
        )

        publication_elements = publications_section.find_elements(By.XPATH, '//li[contains(@class, "pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column")]')

        for element in publication_elements:
            publication = {}

            # Extract publication title
            try:
                publication_title_element = element.find_element(By.CSS_SELECTOR, ".t-bold span")
                publication["title"] = publication_title_element.text.strip()
            except Exception as e:
                print(f"Error extracting publication title: {e}")
                continue

            # Extract publication date and publisher
            try:
                publication_info_element = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal")
                publication["info"] = publication_info_element.text.strip()
            except Exception as e:
                print(f"Error extracting publication info: {e}")

            # Extract publication link
            try:
                publication_link_element = element.find_element(By.TAG_NAME, "a")
                publication["link"] = publication_link_element.get_attribute("href")
            except Exception as e:
                print(f"Error extracting publication link: {e}")

            profile_data["publications"].append(publication)
    except TimeoutException as e:
        print(f"Error finding publications: {e}")
    except NoSuchElementException as e:
        print(f"Error finding publications: {e}")

    # Extract groups
    profile_data["groups"] = []
    groups_url = f"{profile_url}details/interests/?detailScreenTabIndex=2"
    driver.get(groups_url)
    try:
        groups_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div[4]/div/div/div[1]/ul'))
        )

        groups_elements = groups_section.find_elements(By.TAG_NAME, "li")
        for element in groups_elements:
            group = {}
            try:
                name_element = element.find_element(By.CSS_SELECTOR, ".display-flex.align-items-center.mr1.hoverable-link-text.t-bold span")
                group["name"] = name_element.text.strip()
            except Exception as e:
                print(f"Error extracting name for group: {e}")
                continue

            try:
                members_element = element.find_element(By.CSS_SELECTOR, ".t-14.t-normal.t-black--light span.pvs-entity__caption-wrapper")
                group["members"] = members_element.text.strip()
            except Exception as e:
                print(f"Error extracting members for group: {e}")

            profile_data["groups"].append(group)
    except TimeoutException as e:
        print(f"Error finding groups: {e}")
    except NoSuchElementException as e:
        print(f"Error finding groups: {e}")

    # Extract posts
    profile_data["posts"] = []
    posts_url = f"{profile_url}recent-activity/all/"
    driver.get(posts_url)
    try:
        posts_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/div/section/div[2]/div/div/div[1]/ul'))
        )
        
        # Scroll to the bottom of the page to load all posts
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        posts_elements = posts_section.find_elements(By.TAG_NAME, 'li')

        for post_element in posts_elements:
            post_data = {}
            # Caption
            try:
                caption = post_element.find_element(By.CSS_SELECTOR, ".break-words").text.strip()
                post_data["caption"] = caption
            except Exception as e:
                print(f"Error extracting caption: {e}")
                continue

            # Post URL
            try:
                post_url = post_element.find_element(By.CSS_SELECTOR, "a.app-aware-link").get_attribute("href")
                post_data["post_url"] = post_url
            except Exception as e:
                print(f"Error extracting post URL: {e}")
                continue
            # Time of Upload
            try:
                time_element = post_element.find_element(By.CSS_SELECTOR, ".update-components-actor__sub-description.t-12.t-normal.t-black--light span[aria-hidden='true']")
                time_ele = time_element.text.strip()
                post_data["time"] = time_ele
            except Exception as e:
                print(f"Error extracting time: {e}")
                continue
            # Number of likes
            try:
                likes_element = post_element.find_element(By.CSS_SELECTOR, ".social-details-social-counts__reactions")
                likes = likes_element.text.strip()
                post_data["likes"] = likes
            except Exception as e:
                print(f"Error extracting likes: {e}")
                continue

            # Number of comments
            try:
                comments_element = post_element.find_element(By.CSS_SELECTOR, ".social-details-social-counts__comments")
                comments = comments_element.text.strip()
                post_data["comments"] = comments
            except Exception as e:
                print(f"Error extracting comments: {e}")
                continue

            profile_data["posts"].append(post_data)
    except TimeoutException as e:
        print(f"Error finding posts: {e}")
    except NoSuchElementException as e:
        print(f"Error finding posts: {e}")
             
        profile_data["posts"].append(post_data)   
    driver.quit()
    return profile_data

def save_to_json(profile_data, file_name="linkedin_profile.json"):
    """
    Saves profile data to a JSON file.

    Args:
        profile_data (dict): Profile data to save.
        file_name (str): Name of the JSON file to save to.

    Returns:
        None
    """
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=4)

    return profile_data

# #Example usage (replace with your session cookie and profile URL)
session_cookie = input("Enter your LinkedIn Session Cookie: ")
profile_name = input("Enter the LinkedIn Profile Name: ")
profile_url = f"https://www.linkedin.com/in/{profile_name}/"
profile_data = scrape_linkedin_profile(profile_url, session_cookie)


print(profile_data)
save_to_json(profile_data, f"linkedin_profile_{profile_name}.json")
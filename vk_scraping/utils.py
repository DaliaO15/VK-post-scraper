from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import unquote

def get_html_content(url, driver):
    """Access post information by opening the provided URL in the browser."""
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "wl_post")))
    return driver.page_source

def process_comments(soup):
    """Process post comments into a list if any."""
    replies_data = []
    replies_div = soup.find("div", class_="wl_replies")
    if replies_div:
        for reply in replies_div.find_all("div", class_="reply"):
            reply_text = reply.find("div", class_="reply_text").get_text()
            replies_data.append(reply_text)
    return replies_data

def extract_actual_url(url):
    """Extract the actual URL by splitting the provided URL."""
    # Split the URL at '&to=' and take the second part
    actual_url = url.split('to=')[1]
    
    # Remove '&utf=1' if it exists at the end
    if actual_url.endswith('&utf=1'):
        actual_url = actual_url[:-6]

    return unquote(actual_url)

def get_post_content(soup):
    """Extract text from the 'wall_post_text' div."""
    wl_post_body_wrap = soup.find('div', class_='wl_post_body_wrap')
    wall_post_text_div = wl_post_body_wrap.find('div', class_='wall_post_text')
    return wall_post_text_div.get_text(strip=True, separator='\n')

def extract_post_urls(soup):
    """Extract URLs from the 'wall_post_text' div"""
    wl_post_body_wrap = soup.find('div', class_='wl_post_body_wrap')
    wall_post_text_div = wl_post_body_wrap.find('div', class_='wall_post_text')
    return [a['href'] for a in wall_post_text_div.find_all('a', href=True)]

def get_reaction_count(soup):
    """Get reaction count by finding the relevant element in the soup."""
    return soup.find("div", class_="ReactionsPreview__count").get_text()


def scrape_posts_info(data, user, driver):
    """Retrieve information for all posts and store it in a list."""
    full_data = []

    for index, post in data.iterrows():
        post_id = post['post_id']
        post_link = 'https://vk.com/' + user + '?w=wall' + post_id

        # Print progress information for every 50 posts
        if index % 50 == 0:
            print(f"In post number {index} --- Id:{post_id}")

        post_dict = {
            'Post_ID': post_id,
            'Post_link': post_link, 
            'User': user, 
            'User_post_date': post['user-post-date'], 
            'Subuser': post['subuser-name'],
            'Subuser_post_date': post["subuser-post-date"],
            'Embeded_link_name': post['link-subuser'], 
            'Embeded_link': post['link-subuser-href']
        }

        try:
            html = get_html_content(post_link, driver)
            soup = BeautifulSoup(html, "html.parser")

            # Check if the post is found
            if not soup or not soup.find("div", class_="wl_post"):
                raise ValueError("Post not found")
            
            # Extract post content, URLs, reaction count, and comments
            post_content = get_post_content(soup)
            post_urls = extract_post_urls(soup)
            reaction_count = get_reaction_count(soup)
            comments = process_comments(soup)

            post_dict.update({
                'Post_content': post_content,
                'Urls_in_post_content': post_urls,
                'Reactions': reaction_count, 
                'Comments': comments
            })
        except Exception as e:
            # Handle errors and update the dictionary with error information
            print(f"Error processing post {post_id}: {str(e)}")
            post_dict.update({
                'Post_content': "ERROR",
                'Urls_in_post_content': "ERROR",
                'Reactions': "ERROR", 
                'Comments': "ERROR"
            })

        # Append the post dictionary to the list
        full_data.append(post_dict)

    return full_data

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import unquote

def get_html_content(url, driver):
    """Access post information by opening the provided URL in the browser."""
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "wl_post")))
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

def extract_post_content_and_urls(soup, id):
    """
    Extract URLs from the 'wall_post_text' div.

    Returns:
        tuple: (post_content, post_urls)
               - post_content: The text content as a string.
               - post_urls: A list of URLs.
    """
    target_id = "wpt" + str(id)
    container_selector = f"div#{target_id}.wall_post_cont._wall_post_cont"
    container = soup.select_one(container_selector)

    if container:
        text_div = container.find("div", class_="vkitShowMoreText__text--ULCyL")
        if text_div:
            #post_content = text_div.get_text(strip=True)
            post_urls = [a.get('href') for a in text_div.find_all('a', href=True)]
        else:
            #post_content = None
            post_urls = []
    else:
        #post_content = None
        post_urls = []

    return post_urls #post_content, 


def get_reaction_count(soup):
    """Get reaction count by finding the relevant element in the soup."""
    return soup.find("div", class_="ReactionsPreview__count").get_text()

def safe_extract(func, default_value, *args, **kwargs):
    # Extract info from post and leave as none if empty
    try:
        return func(*args, **kwargs)
    except:
        return default_value

def scrape_posts_info(data, user, driver):
    """Retrieve information for all posts and store it in a list."""
    full_data = []

    for index, post in data.iterrows():
        post_id = post['post_id']
        post_link = 'https://vk.com/' + user + '?w=wall' + post_id

        # Print progress information for every 50 posts
        if index % 50 == 0:
            print(f"In post number {index} --- Id:{post_id}")

        # Store info in a dictionary
        post_dict = {
            'Post_ID': post_id,
            'Post_link': post_link, 
            'User': user, 
            'User_post_date': post['user-post-date'], 
            'Subuser': post['subuser-name'],
            'Embeded_link': post['link-subuser-href'],
            'Post_content': post['post_content']
        }

        # Try to get the new content
        try:
            html = get_html_content(post_link, driver)
            soup = BeautifulSoup(html, "html.parser")

            # Check if the post is found
            if not soup or not soup.find("div", class_="wl_post"):
                raise ValueError("Post not found")
            
        except Exception as e:
            # Handle errors and update the dictionary with error information
            print(f"Error processing post {post_id}: {str(e)}")
            post_dict.update({
                'Urls_in_post_content': "ERROR",
                'Reactions': "ERROR", 
                'Comments': "ERROR"
            })
        else:
            # Extract post content, URLs, reaction count, and comments
            # For single-value functions
            reaction_count = safe_extract(get_reaction_count, "None", soup)
            comments = safe_extract(process_comments, [], soup)

            # For the combined function
            print("Fetch info")
            post_urls = extract_post_content_and_urls(soup, post_id)
            
            post_dict.update({
                'Urls_in_post_content': post_urls,
                'Reactions': reaction_count, 
                'Comments': comments
            })

        # Append the post dictionary to the list
        full_data.append(post_dict)

    return full_data

import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
if "://" not in API_BASE_URL:
    API_BASE_URL = f"http://{API_BASE_URL}"

st.set_page_config(page_title="Blog UI", page_icon="✍️")
st.title("✍️ Blog")
st.caption("A simple interface for the existing FastAPI blog API.")

if "token" not in st.session_state:
    st.session_state.token = ""

with st.sidebar:
    st.subheader("API")
    st.code(API_BASE_URL)
    if st.session_state.token:
        st.success("Signed in")
        if st.button("Sign out"):
            st.session_state.token = ""
            st.rerun()
    else:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Sign in")
        if login:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/login",
                    data={"username": username, "password": password},
                    timeout=10,
                )
                response.raise_for_status()
                st.session_state.token = response.json()["access_token"]
                st.rerun()
            except requests.HTTPError as error:
                st.error("Sign-in failed. Check your username and password.")
            except (requests.RequestException, ValueError, KeyError) as error:
                st.error(f"Could not log in to the API: {error}")

headers = (
    {"Authorization": f"Bearer {st.session_state.token}"}
    if st.session_state.token
    else {}
)

search = st.text_input("Search blog titles")
page = st.number_input("Page", min_value=1, value=1, step=1)
limit = st.selectbox("Posts per page", [5, 10, 20], index=0)

try:
    response = requests.get(
        f"{API_BASE_URL}/blogs",
        params={"page": page, "limit": limit, "search": search},
        timeout=10,
    )
    response.raise_for_status()
    result = response.json()
except (requests.RequestException, ValueError) as error:
    st.error(f"Could not load posts from the API: {error}")
    st.stop()

posts = result.get("data", [])
st.caption(f"{result.get('total', len(posts))} matching post(s)")

if st.session_state.token:
    with st.expander("Write a post"):
        with st.form("create_post"):
            title = st.text_input("Title")
            content = st.text_area("Content")
            create = st.form_submit_button("Publish")
        if create:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/blogs/",
                    json={"title": title, "content": content},
                    headers=headers,
                    timeout=10,
                )
                response.raise_for_status()
                st.success("Post published.")
                st.rerun()
            except requests.RequestException as error:
                st.error(f"Could not publish the post: {error}")
else:
    st.info("Enable editing from the sidebar to create, edit, or delete posts.")

if not posts:
    st.info("No posts found.")

for post in posts:
    with st.expander(post["title"]):
        st.write(post["content"])
        if st.session_state.token:
            with st.form(f"edit_{post['id']}"):
                title = st.text_input("Title", value=post["title"])
                content = st.text_area("Content", value=post["content"])
                save = st.form_submit_button("Save")
            if save:
                try:
                    response = requests.put(
                        f"{API_BASE_URL}/blog/{post['id']}",
                        json={"title": title, "content": content},
                        headers=headers,
                        timeout=10,
                    )
                    response.raise_for_status()
                    st.success("Post updated.")
                    st.rerun()
                except requests.RequestException as error:
                    st.error(f"Could not update the post: {error}")

            if st.button("Delete", key=f"delete_{post['id']}"):
                try:
                    response = requests.delete(
                        f"{API_BASE_URL}/blog/{post['id']}",
                        headers=headers,
                        timeout=10,
                    )
                    response.raise_for_status()
                    st.success("Post deleted.")
                    st.rerun()
                except requests.RequestException as error:
                    st.error(f"Could not delete the post: {error}")

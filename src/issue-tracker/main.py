import streamlit as st
import pandas as pd
import httpx

base_url = "http://api:8080"

def main():
    st.title("Ticket Viewer")
    st.subheader("View all tickets")

    if st.button("Load Tickets"):
        tickets = get_tickets()
        if tickets:
            df = pd.DataFrame(tickets)
            st.dataframe(df)
        else:
            st.write("No tickets found.")

def get_tickets():
    try:
        response = httpx.get(f"{base_url}/tickets")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        st.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        st.error(f"Request error occurred: {e.request.url}")
    return []

if __name__ == "__main__":
    main()

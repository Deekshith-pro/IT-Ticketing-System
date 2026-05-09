import streamlit as st
import sqlite3
import pandas as pd
import time
from auth import hash_password
import database

# DATABASE CONNECTION
conn = sqlite3.connect("helpdesk.db", check_same_thread=False)
cursor = conn.cursor()

# PAGE CONFIG
st.set_page_config(
    page_title="Help Desk Ticketing System",
    page_icon="🎫",
    layout="centered"
)

st.title("🎫 Help Desk Ticketing System")

# SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "profession" not in st.session_state:
    st.session_state.profession = ""

# PROFESSION LIST
profession_list = [
    "Select Profession",
    "Software Engineer",
    "Desktop Support Engineer",
    "HR",
    "Accountant",
    "Manager",
    "Network Engineer",
    "System Administrator",
    "Student",
    "Teacher",
    "Sales Executive",
    "Data Analyst",
    "Cybersecurity Analyst",
    "Cloud Engineer",
    "Business Analyst",
    "Other"
]

# LOGOUT FUNCTION
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.profession = ""

# SIDEBAR MENU
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# REGISTER PAGE
if choice == "Register" and not st.session_state.logged_in:

    st.subheader("📝 Create Account")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    role = st.selectbox(
        "Role",
        ["User", "Technician"]
    )

    profession = st.selectbox(
        "Profession",
        profession_list
    )

    if st.button("Register"):

        if profession == "Select Profession":
            st.warning("Please select a profession")

        else:

            try:

                cursor.execute(
                    """
                    SELECT * FROM users
                    WHERE username=? AND role=?
                    """,
                    (username, role)
                )

                existing_user = cursor.fetchone()

                if existing_user:
                    st.error("User already exists")

                else:

                    cursor.execute(
                        """
                        INSERT INTO users(
                            username,
                            password,
                            role
                        )
                        VALUES(?,?,?)
                        """,
                        (
                            username,
                            hash_password(password),
                            role
                        )
                    )

                    conn.commit()

                    success_message = st.success(
                        f"{role} Account Created Successfully"
                    )

                    time.sleep(3)

                    success_message.empty()

            except Exception as e:
                st.error(f"Error: {e}")

# LOGIN PAGE
elif choice == "Login" and not st.session_state.logged_in:

    st.subheader("🔐 Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    role = st.selectbox(
        "Role",
        ["User", "Technician"]
    )

    profession = st.selectbox(
        "Profession",
        profession_list
    )

    if st.button("Login"):

        if profession == "Select Profession":
            st.warning("Please select a profession")

        else:

            cursor.execute(
                """
                SELECT * FROM users
                WHERE username=? AND password=? AND role=?
                """,
                (
                    username,
                    hash_password(password),
                    role
                )
            )

            user = cursor.fetchone()

            if user:

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.session_state.profession = profession

                success_message = st.success(
                    f"Welcome {username}"
                )

                time.sleep(2)

                success_message.empty()

                st.rerun()

            else:
                st.error("Invalid Credentials")

# AFTER LOGIN
if st.session_state.logged_in:

    st.sidebar.success(
        f"""
Logged in as:
{st.session_state.username}

Role:
{st.session_state.role}

Profession:
{st.session_state.profession}
"""
    )

    st.sidebar.button(
        "Logout",
        on_click=logout
    )

    username = st.session_state.username
    role = st.session_state.role

    # USER PANEL
    if role == "User":

        st.header("🖥️ Raise IT Support Ticket")

        issue_type = st.selectbox(
            "Select Issue Type",
            [
                "Laptop Not Powering On",
                "Desktop Slow Performance",
                "Blue Screen Error",
                "WiFi/Network Issue",
                "Printer Not Working",
                "Keyboard/Mouse Issue",
                "Software Installation",
                "Outlook/Email Issue",
                "Password Reset",
                "VPN Connection Problem",
                "System Hanging",
                "Audio Issue",
                "Display/Flickering Issue",
                "Battery Charging Problem",
                "Other"
            ]
        )

        issue_description = st.text_area(
            "Describe the Issue"
        )

        issue = (
            f"{issue_type} - "
            f"{issue_description}"
        )

        priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High"]
        )

        if st.button("Submit Ticket"):

            cursor.execute(
                """
                INSERT INTO tickets(
                    username,
                    issue,
                    priority,
                    status
                )
                VALUES(?,?,?,?)
                """,
                (
                    username,
                    issue,
                    priority,
                    "Open"
                )
            )

            conn.commit()

            success_message = st.success(
                "Ticket Raised Successfully"
            )

            time.sleep(3)

            success_message.empty()

            st.rerun()

        st.header("📋 My Tickets")

        cursor.execute(
            """
            SELECT * FROM tickets
            WHERE username=?
            """,
            (username,)
        )

        tickets = cursor.fetchall()

        df = pd.DataFrame(
            tickets,
            columns=[
                "ID",
                "Username",
                "Issue",
                "Priority",
                "Status"
            ]
        )

        st.dataframe(df)

    # TECHNICIAN PANEL
    elif role == "Technician":

        tech_menu = st.sidebar.selectbox(
            "Technician Options",
            [
                "View Tickets",
                "Update Ticket Status",
                "Ticket Analytics"
            ]
        )

        # VIEW TICKETS
        if tech_menu == "View Tickets":

            st.header("📋 All Tickets")

            cursor.execute(
                "SELECT * FROM tickets"
            )

            tickets = cursor.fetchall()

            df = pd.DataFrame(
                tickets,
                columns=[
                    "ID",
                    "Username",
                    "Issue",
                    "Priority",
                    "Status"
                ]
            )

            st.dataframe(df)

        # UPDATE TICKETS
        elif tech_menu == "Update Ticket Status":

            st.header("🔄 Update Ticket Status")

            cursor.execute(
                "SELECT * FROM tickets"
            )

            tickets = cursor.fetchall()

            df = pd.DataFrame(
                tickets,
                columns=[
                    "ID",
                    "Username",
                    "Issue",
                    "Priority",
                    "Status"
                ]
            )

            st.dataframe(df)

            ticket_id = st.number_input(
                "Ticket ID",
                min_value=1,
                step=1
            )

            new_status = st.selectbox(
                "Update Status",
                [
                    "Open",
                    "In Progress",
                    "Resolved"
                ]
            )

            technician_description = st.text_area(
                "Technician Update Notes"
            )

            if st.button("Update Ticket"):

                cursor.execute(
                    """
                    UPDATE tickets
                    SET status=?,
                        issue = issue || ' | Technician Notes: ' || ?
                    WHERE id=?
                    """,
                    (
                        new_status,
                        technician_description,
                        ticket_id
                    )
                )

                conn.commit()

                success_message = st.success(
                    "Ticket Updated Successfully"
                )

                time.sleep(3)

                success_message.empty()

                st.rerun()

        # TICKET ANALYTICS
        elif tech_menu == "Ticket Analytics":

            st.header("📊 Ticket Analytics")

            cursor.execute(
                """
                SELECT status, COUNT(*)
                FROM tickets
                GROUP BY status
                """
            )

            data = cursor.fetchall()

            if data:

                analytics_df = pd.DataFrame(
                    data,
                    columns=[
                        "Status",
                        "Count"
                    ]
                )

                st.dataframe(analytics_df)

                st.bar_chart(
                    analytics_df.set_index("Status")
                )

            else:
                st.warning("No tickets available")
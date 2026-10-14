
import math
import streamlit as st
import pandas as pd

# ---------------- SETTINGS ----------------
MAX_DISTANCE = 500
MIN_ORDER_VALUE = 200
MAX_GROUP_SIZE = 4

# ---------------- SAMPLE USERS ----------------
USERS = [
    {"id": 1, "name": "A", "latitude": 18.5204,
     "longitude": 73.8567, "cart_value": 50},
    {"id": 2, "name": "B", "latitude": 18.5210,
     "longitude": 73.8571, "cart_value": 100},
    {"id": 3, "name": "C", "latitude": 18.5199,
     "longitude": 73.8559, "cart_value": 70},
    {"id": 4, "name": "D", "latitude": 18.5300,
     "longitude": 73.8700, "cart_value": 150},
]


# ---------------- DISTANCE ----------------
def calculate_distance(user1, user2):
    lat1 = math.radians(user1["latitude"])
    lon1 = math.radians(user1["longitude"])
    lat2 = math.radians(user2["latitude"])
    lon2 = math.radians(user2["longitude"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a), math.sqrt(1 - a)
    )

    return 6371000 * c


# ---------------- NEARBY USERS ----------------
def find_nearby_users(main_user):
    nearby = []

    for user in USERS:
        if user["id"] == main_user["id"]:
            continue

        distance = calculate_distance(main_user, user)

        if distance <= MAX_DISTANCE:
            nearby.append((user, distance))

    return nearby


# ---------------- GREEDY ALGORITHM ----------------
def greedy_group(main_user, nearby_users):
    members = [main_user]
    total = main_user["cart_value"]

    # Highest cart value first
    sorted_users = sorted(
        nearby_users,
        key=lambda item: item[0]["cart_value"],
        reverse=True
    )

    for user, distance in sorted_users:
        if len(members) >= MAX_GROUP_SIZE:
            break

        members.append(user)
        total += user["cart_value"]

        if total >= MIN_ORDER_VALUE:
            break

    return members, total


# ---------------- PAGE DESIGN ----------------
st.set_page_config(
    page_title="GroupDrop",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #f5f8f5;
}
h1, h2, h3 {
    color: #176b45;
}
[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #dce8df;
}
</style>
""", unsafe_allow_html=True)

st.title("🛒 GroupDrop")
st.subheader("Shop together. Reach the minimum. Save on delivery.")
st.caption(
    "A cart-pooling demonstration using distance calculation "
    "and a greedy algorithm."
)

st.divider()

# ---------------- CUSTOMER INPUT ----------------
st.header("1. Create your order")

col1, col2 = st.columns(2)

with col1:
    customer_name = st.text_input(
        "Your name", value="You"
    )

with col2:
    cart_value = st.number_input(
        "Your cart value (₹)",
        min_value=1,
        max_value=100000,
        value=50,
        step=10
    )

# Use the first sample user's location for the demo.
# Real GPS integration can be added later.
main_user = {
    "id": 999,
    "name": customer_name.strip() or "You",
    "latitude": USERS[0]["latitude"],
    "longitude": USERS[0]["longitude"],
    "cart_value": int(cart_value)
}

st.info(
    f"Free-delivery target: ₹{MIN_ORDER_VALUE} | "
    f"Nearby radius: {MAX_DISTANCE} m | "
    f"Maximum group size: {MAX_GROUP_SIZE}"
)

# ---------------- FIND NEARBY ----------------
st.header("2. Nearby shoppers")

nearby_users = find_nearby_users(main_user)

if nearby_users:
    nearby_data = []

    for user, distance in nearby_users:
        nearby_data.append({
            "Customer": user["name"],
            "Distance (m)": round(distance, 2),
            "Cart Value (₹)": user["cart_value"],
            "Within 500 m": "Yes"
        })

    st.dataframe(
        pd.DataFrame(nearby_data),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("No nearby shoppers found.")

# ---------------- GREEDY RECOMMENDATION ----------------
st.header("3. Recommended group")

members, total = greedy_group(main_user, nearby_users)

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Group members", len(members))

with m2:
    st.metric("Combined cart", f"₹{total}")

with m3:
    st.metric(
        "Amount remaining",
        f"₹{max(0, MIN_ORDER_VALUE - total)}"
    )

st.write(
    "**Selected shoppers:** "
    + ", ".join(member["name"] for member in members)
)

if total >= MIN_ORDER_VALUE:
    st.success("🎉 Free-delivery target reached!")
else:
    st.warning(
        f"₹{MIN_ORDER_VALUE - total} more is needed "
        "to reach the target."
    )

st.caption(
    "The recommendation uses a greedy strategy: "
    "it considers nearby shoppers in descending order "
    "of cart value and stops when the target is reached "
    "or the group reaches its size limit."
)

# ---------------- GROUP SUMMARY ----------------
st.header("4. Order summary")

st.table(pd.DataFrame([
    {
        "Customer": member["name"],
        "Cart value": f"₹{member['cart_value']}"
    }
    for member in members
]))

st.divider()

st.markdown(
    "### How GroupDrop works\n"
    "1. Calculate distances between shoppers.\n"
    "2. Find shoppers within 500 metres.\n"
    "3. Sort eligible shoppers by cart value.\n"
    "4. Select shoppers until the ₹200 target "
    "or group-size limit is reached."
)

st.caption(
    "Academic prototype • Uses sample customer locations "
    "and simulated cart values."
)

# import streamlit as st
# from agents import graph, cars, banks, CarDealState
#
# st.title("🚗 Car Deal Multi-Agent Workflow")
#
# # Step 1: Prompt → Car Listing
# prompt = st.text_input("Enter car keyword (make/model/year/body/fuel/trim)")
#
# if "selected_car" not in st.session_state:
#     st.session_state.selected_car = None
#
# if prompt and st.session_state.selected_car is None:
#     p = prompt.lower()
#     filtered = cars[
#         cars.apply(
#             lambda r: p in str(r['make']).lower()
#                    or p in str(r['model']).lower()
#                    or p in str(r['year']).lower()
#                    or p in str(r['body']).lower()
#                    or p in str(r['fuel']).lower()
#                    or p in str(r['trim']).lower(),
#             axis=1
#         )
#     ]
#
#     st.subheader("Available Cars")
#     st.markdown(
#         """
#         <style>
#         .scroll-box {
#             max-height: 250px;
#             overflow-y: auto;
#             border: 1px solid #ddd;
#             padding: 8px;
#             background-color: #f9f9f9;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )
#
#     st.markdown('<div class="scroll-box">', unsafe_allow_html=True)
#     for idx, row in filtered.iterrows():
#         if st.checkbox(
#             f"{row['make']} {row['model']} ({row['year']}) | Body: {row['body']} | Price: {row['price']}",
#             key=row['id']
#         ):
#             st.session_state.selected_car = row['id']
#     st.markdown('</div>', unsafe_allow_html=True)
#
# # Step 2: Show Selected Car & Exchange Option
# exchange = False
# if st.session_state.selected_car:
#     car = cars[cars['id'] == st.session_state.selected_car].iloc[0]
#     st.success(f"✅ Selected Car: {car['make']} {car['model']} ({car['year']})")
#     st.write(f"Trim: {car['trim']} | Fuel: {car['fuel']} | Body: {car['body']}")
#     st.write(f"Price: {car['price']}")
#     st.info("Car list disabled. Proceed to exchange option.")
#
#     exchange = st.radio("Is this car being exchanged?", ["No", "Yes"]) == "Yes"
#
# # Step 3: Negotiation
# neg_rounds = st.session_state.get("neg_rounds", 0)
# car_price = float(cars[cars['id'] == st.session_state.selected_car]['price']) if st.session_state.selected_car else 0
# negotiated_price = st.session_state.get("negotiated_price", car_price)
# customer_happy = False
#
# if st.session_state.selected_car:
#     if st.button("Negotiate Price"):
#         if neg_rounds < 3:
#             negotiated_price *= 0.98
#             st.session_state["neg_rounds"] = neg_rounds + 1
#             st.session_state["negotiated_price"] = negotiated_price
#             st.write(f"Negotiated Price: {negotiated_price}")
#         else:
#             st.error("Max 3 negotiations reached. Customer not satisfied.")
#
#     customer_happy = st.checkbox("Customer Accepts Negotiated Price?")
#
# # Step 4: Finance
# finance = False
# selected_bank = None
# if customer_happy:
#     finance = st.radio("Finance option?", ["No", "Yes"]) == "Yes"
#     if finance:
#         st.dataframe(banks)
#         selected_bank = st.selectbox("Select Bank", banks['bank_name'])
#
# # Step 5: Run Graph
# if st.button("Run Workflow"):
#     state: CarDealState = {
#         "log": [],
#         "prompt": prompt,
#         "selected_car": st.session_state.selected_car,
#         "exchange": exchange,
#         "negotiated_price": negotiated_price,
#         "neg_rounds": st.session_state.get("neg_rounds", 0),
#         "customer_happy": customer_happy,
#         "finance": finance,
#         "selected_bank": selected_bank,
#         "draft": "",
#         "pdf_bytes": b""
#     }
#     result = graph.invoke(state)
#
#     st.subheader("📄 Deal Draft")
#     st.write(result["draft"])
#
#     st.subheader("📝 Agent Logs")
#     for entry in result["log"]:
#         st.write(entry)
#
#     st.download_button("📄 Download Deal Draft (PDF)", data=result["pdf_bytes"],
#                        file_name="car_deal_draft.pdf", mime="application/pdf")
#     # Generate graph PNG after workflow run
#     png_data = graph.get_graph().draw_mermaid_png()
#
#     # Save locally (optional)
#     with open("CarDeal.png", "wb") as f:
#         f.write(png_data)
#
#     # Streamlit download button
#     st.download_button(
#         "📊 Download Workflow Graph (PNG)",
#         data=png_data,
#         file_name="CarDeal.png",
#         mime="image/png"
#     )

import streamlit as st
from agents import graph, cars, banks, CarDealState

st.title("🚗 Car Deal Multi-Agent Workflow")

# Step 1: Prompt → Car Listing
prompt = st.text_input("Enter car keyword (make/model/year/body/fuel/trim)")

if "selected_car" not in st.session_state:
    st.session_state.selected_car = None

# Two columns: left for workflow, right for car list
col_left, col_right = st.columns([3, 2])

with col_right:
    if prompt:
        p = prompt.lower()
        filtered = cars[
            cars.apply(
                lambda r: p in str(r['make']).lower()
                       or p in str(r['model']).lower()
                       or p in str(r['year']).lower()
                       or p in str(r['body']).lower()
                       or p in str(r['fuel']).lower()
                       or p in str(r['trim']).lower(),
                axis=1
            )
        ]

        st.subheader("Available Cars")
        st.markdown(
            """
            <style>
            .scroll-box {
                max-height: 500px;
                overflow-y: auto;
                border: 1px solid #ddd;
                padding: 8px;
                background-color: #f9f9f9;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="scroll-box">', unsafe_allow_html=True)

        # ✅ Add "None" option at the top
        options = ["None"] + [
            f"{row['make']} {row['model']} ({row['year']}) | Body: {row['body']} | Price: {row['price']}"
            for _, row in filtered.iterrows()
        ]

        # Default to first value ("None")
        selected_option = st.selectbox("Select a car:", options, index=0)

        if selected_option != "None":
            selected_row = filtered.iloc[options.index(selected_option) - 1]  # adjust index
            st.session_state.selected_car = selected_row['id']
        else:
            st.session_state.selected_car = None

        st.markdown('</div>', unsafe_allow_html=True)

with col_left:
    exchange = False
    customer_happy = False
    negotiated_price = 0
    selected_bank = None
    finance = False

    if st.session_state.selected_car:
        car = cars[cars['id'] == st.session_state.selected_car].iloc[0]
        st.success(f"✅ Selected Car: {car['make']} {car['model']} ({car['year']})")
        st.write(f"Trim: {car['trim']} | Fuel: {car['fuel']} | Body: {car['body']}")
        st.write(f"Price: {car['price']}")

        # Exchange option
        exchange_choice = st.radio("Is this car being exchanged?", ["No", "Yes"])
        exchange = exchange_choice == "Yes"

        # Negotiation
        neg_rounds = st.session_state.get("neg_rounds", 0)
        car_price = float(car['price'])
        negotiated_price = st.session_state.get("negotiated_price", car_price)

        if st.button("Negotiate Price"):
            if neg_rounds < 3:
                negotiated_price *= 0.98
                st.session_state["neg_rounds"] = neg_rounds + 1
                st.session_state["negotiated_price"] = negotiated_price
                st.write(f"Negotiated Price: {negotiated_price}")
            else:
                st.error("Max 3 negotiations reached. Customer not satisfied.")

        customer_happy = st.checkbox("Customer Accepts Negotiated Price?")

        # Finance
        if customer_happy:
            finance = st.radio("Finance option?", ["No", "Yes"]) == "Yes"
            if finance:
                st.dataframe(banks)
                selected_bank = st.selectbox("Select Bank", banks['bank_name'])

        # Run workflow
        if st.button("Run Workflow"):
            state: CarDealState = {
                "log": [],
                "prompt": prompt,
                "selected_car": st.session_state.selected_car,
                "exchange": exchange,
                "negotiated_price": negotiated_price,
                "neg_rounds": st.session_state.get("neg_rounds", 0),
                "customer_happy": customer_happy,
                "finance": finance,
                "selected_bank": selected_bank,
                "draft": "",
                "pdf_bytes": b""
            }
            result = graph.invoke(state)

            st.subheader("📄 Deal Draft")
            st.write(result["draft"])

            st.subheader("📝 Agent Logs")
            for entry in result["log"]:
                st.write(entry)

            st.download_button("📄 Download Deal Draft (PDF)", data=result["pdf_bytes"],
                               file_name="car_deal_draft.pdf", mime="application/pdf")

            # 👉 New: Graph visualization download
            png_data = graph.get_graph().draw_mermaid_png()
            st.download_button("📊 Download Workflow Graph (PNG)",
                               data=png_data,
                               file_name="CarDeal.png",
                               mime="image/png")

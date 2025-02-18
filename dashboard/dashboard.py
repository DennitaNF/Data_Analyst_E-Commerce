# -*- coding: utf-8 -*-
"""Dashboard.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1X-4IcN94hpCxmCdCnP651KZIJRFFiSgy
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import datetime as dt


path = 'all_data.csv'

all_data = pd.read_csv(path)

datetime_columns = ["order_approved_at"]
for column in datetime_columns:
    all_data[column] = pd.to_datetime(all_data[column])

def number_order_monthly(df):
    monthly = df.resample(rule='M', on='order_approved_at').agg({
        "order_id": "size",
    })
    monthly.index = monthly.index.strftime('%B') 
    monthly = monthly.reset_index()
    monthly.rename(columns={
        "order_id": "order_count",
    }, inplace=True)
    monthly = monthly.sort_values('order_count').drop_duplicates('order_approved_at', keep='last')
    month_mapping = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    monthly["month_numeric"] = monthly["order_approved_at"].map(month_mapping)
    monthly = monthly.sort_values("month_numeric")
    monthly = monthly.drop("month_numeric", axis=1)
    return monthly

def customer_spend(df):
    total_spend = df.resample(rule='M', on='order_approved_at').agg({
            "price": "sum"
    })
    total_spend = total_spend.reset_index()
    total_spend.rename(columns={
                "price": "total_cust_spend"
            }, inplace=True)
    total_spend['order_approved_at'] = total_spend['order_approved_at'].dt.strftime('%B')
    total_spend = total_spend.sort_values('total_cust_spend').drop_duplicates('order_approved_at', keep='last')
    montly_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    total_spend['month_cat'] = pd.Categorical(total_spend['order_approved_at'], categories=montly_order, ordered=True)

    sorted = total_spend.sort_values(by='month_cat')

    sorted = sorted.drop(columns=['month_cat'])
    return sorted


def create_by_producd(df):
    product_counts = df.groupby('product_category_name_english')['product_id'].count().reset_index()
    sorted = product_counts.sort_values(by='product_id', ascending=False)
    return sorted

def rating_cusd(df):
    rating = df['review_score'].value_counts().sort_values(ascending=False)

    max_score = rating.idxmax()

    df_cust=df['review_score']

    return (rating,max_score,df_cust)

def create_rfm(df):
    now=dt.datetime(2018,10,20)

    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    recency = (now - df.groupby('customer_id')['order_purchase_timestamp'].max()).dt.days
    frequency = df.groupby('customer_id')['order_id'].count()
    monetary = df.groupby('customer_id')['price'].sum()

    rfm = pd.DataFrame({
        'customer_id': recency.index,
        'Recency': recency.values,
        'Frequency': frequency.values,
        'Monetary': monetary.values
    })

    col_list = ['customer_id','Recency','Frequency','Monetary']
    rfm.columns = col_list
    return rfm


with st.sidebar:
    st.subheader('About Me')
    st.write('Dennita Noor Febianty')



daily_orderd=number_order_monthly(all_data)
most_and_least_productd=create_by_producd(all_data)
rating_service,max_score,df_rating_service=rating_cusd(all_data)
customer_spend=customer_spend(all_data)
rfm=create_rfm(all_data)


st.header('E-Commerce')

col1, col2 = st.columns(2)

with col1:
    high_order_num = daily_orderd['order_count'].max()
    high_order_month=daily_orderd[daily_orderd['order_count'] == daily_orderd['order_count'].max()]['order_approved_at'].values[0]
    st.markdown(f"Highest orders in {high_order_month} : **{high_order_num}**")

with col2:
    low_order = daily_orderd['order_count'].min()
    low_order_month=daily_orderd[daily_orderd['order_count'] == daily_orderd['order_count'].min()]['order_approved_at'].values[0]
    st.markdown(f"Lowest orders in {low_order_month} : **{low_order}**")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orderd["order_approved_at"],
    daily_orderd["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9",
)
plt.xticks(rotation=45)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader('Customer Spend')
col1, col2 = st.columns(2)

with col1:
    total_cust_spend=customer_spend['total_cust_spend'].sum()
    formatted_total_cust_spend = "%.2f" % total_cust_spend
    st.markdown(f"Total Spend : **{formatted_total_cust_spend}**")

with col2:
    avg_spend=customer_spend['total_cust_spend'].mean()
    formatted_avg_spend = "%.2f" % avg_spend
    st.markdown(f"Average Spend : **{formatted_avg_spend}**")

plt.figure(figsize=(16, 8))
min_total_cust_spend = customer_spend['total_cust_spend'].min()
max_total_cust_spend = customer_spend['total_cust_spend'].max()

plt.axhline(y=max_total_cust_spend, color='green', linestyle='-', linewidth=0.5, label=f'Max ({max_total_cust_spend:.2f})')
plt.axhline(y=min_total_cust_spend, color='red', linestyle='-', linewidth=0.5, label=f'Min ({min_total_cust_spend:.2f})')
sns.barplot(
    x='order_approved_at',
    y='total_cust_spend',
    data=customer_spend,
    linewidth=2,
    linestyle='-',
    color="#90CAF9",

)
plt.xlabel('')
plt.ylabel('Total Spend Customers')
plt.xticks(fontsize=10, rotation=25)
plt.yticks(fontsize=10)
plt.legend()
st.pyplot(plt)

st.subheader("Most And Least Product")
col1, col2 = st.columns(2)

with col1:
    highest_product_sold=most_and_least_productd['product_id'].max()
    st.markdown(f"Higest Number : **{highest_product_sold}**")

with col2:
    lowest_product_sold=most_and_least_productd['product_id'].min()
    st.markdown(f"Lowest Number : **{lowest_product_sold}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 8))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]



sns.barplot(
    x="product_id",
    y="product_category_name_english",
    data=most_and_least_productd.head(5),
    palette=colors,
    ax=ax[0],
    )
ax[0].set_ylabel('')
ax[0].set_xlabel('')
ax[0].set_title("products with the highest sales", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

sns.barplot(
    x="product_id",
    y="product_category_name_english",
    data=most_and_least_productd.sort_values(by="product_id", ascending=True).head(5),
    palette=colors,
    ax=ax[1],)
ax[1].set_ylabel('')
ax[1].set_xlabel('')
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("products with the lowest sales", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

plt.suptitle("The most and least products", fontsize=20)
st.pyplot(fig)


st.subheader("Rating Customer")
st.markdown(f"Average  : **{df_rating_service.mean():.2f}**")



plt.figure(figsize=(16, 8))
sns.barplot(
            x=rating_service.index,
            y=rating_service.values,
            order=rating_service.index,
            palette=["#00FFFF" if score == max_score else "#D3D3D3" for score in rating_service.index]
            )

plt.title("Rating customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Customer")
plt.xticks(fontsize=12)
st.pyplot(plt)

st.subheader("RFM Best Value")


colors = ["#00FFFF", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]


tab1, tab2, tab3 = st.tabs(["Recency", "Frequency", "Monetary"])

with tab1:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Recency",
        x="customer_id",
        data=rfm.sort_values(by="Recency", ascending=True).head(5),
        palette=colors,

        )
    plt.title("By Recency", loc="center", fontsize=18)
    plt.ylabel('')
    plt.xlabel("customer")
    plt.tick_params(axis ='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

with tab2:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Frequency",
        x="customer_id",
        data=rfm.sort_values(by="Frequency", ascending=False).head(5),
        palette=colors,

        )
    plt.ylabel('')
    plt.xlabel("customer")
    plt.title("By Frequency", loc="center", fontsize=18)
    plt.tick_params(axis ='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

with tab3:
    plt.figure(figsize=(16, 8))
    sns.barplot(
        y="Monetary",
        x="customer_id",
        data=rfm.sort_values(by="Monetary", ascending=False).head(5),
        palette=colors,
        )
    plt.ylabel('')
    plt.xlabel("customer")
    plt.title("By Monetary", loc="center", fontsize=18)
    plt.tick_params(axis ='x', labelsize=15)
    plt.xticks([])
    st.pyplot(plt)

